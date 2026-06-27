import io
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models import Count, Q
from django.http import JsonResponse, HttpResponse
from django.template.loader import render_to_string
from django.views.decorators.http import require_POST
from django.urls import reverse
from django.core.paginator import Paginator

from .models import Client, Call, ClientDocument, ClientActivity, LEGAL_STATUSES
from .forms import ClientForm

FORM_LEGAL_STATUSES = [('', '—')] + list(LEGAL_STATUSES)


def _manager_required(view_func):
    @login_required(login_url='/cabinet/login/')
    def _wrapped(request, *args, **kwargs):
        role = getattr(getattr(request.user, 'profile', None), 'role', 'admin')
        if role != 'manager' and not request.user.is_superuser:
            return redirect('/cabinet/')
        return view_func(request, *args, **kwargs)
    _wrapped.__name__ = view_func.__name__
    return _wrapped


def _ns(request):
    return 'sales' if request.path.startswith('/cabinet/manager-panel/') else 'cabinet'


def _can_modify(request, client):
    if request.user.is_superuser:
        return True
    if client.assigned_manager is None:
        return True
    return client.assigned_manager == request.user


def _base_template(request):
    return 'sales/base.html' if request.path.startswith('/cabinet/manager-panel/') else 'cabinet/base.html'


def _list_viewname(ns, section):
    map = {
        'called': f'{ns}:called_list',
        'in_progress': f'{ns}:in_progress_list',
        'archive': f'{ns}:archive_list',
        'completed': f'{ns}:completed_list',
    }
    return reverse(map.get(section, f'{ns}:client_list'))


def _ctx(request, **kw):
    ns = _ns(request)
    kw.setdefault('base_template', _base_template(request))
    kw.setdefault('ns', ns)
    kw.setdefault('form_legal_statuses', FORM_LEGAL_STATUSES)

    if ns == 'sales':
        kw.setdefault('sidebar_counts', {
            'clients': Client.objects.filter(is_archived=False).count(),
            'called': Client.objects.filter(calls__isnull=False, is_archived=False).distinct().count(),
            'in_progress': Client.objects.filter(
                calls__isnull=False, is_archived=False
            ).exclude(calls__status__in=['refusal', 'completed']).distinct().count(),
            'completed': Client.objects.filter(calls__status='completed', is_archived=False).distinct().count(),
        })
    elif ns == 'cabinet':
        kw.setdefault('sidebar_counts', {
            'clients': Client.objects.filter(is_archived=False).count(),
            'in_progress': Client.objects.filter(
                calls__isnull=False, is_archived=False
            ).exclude(calls__status__in=['refusal', 'completed']).distinct().count(),
            'completed': Client.objects.filter(calls__status='completed', is_archived=False).distinct().count(),
        })

    if ns == 'cabinet':
        kw.setdefault('url_clients', reverse('cabinet:clients'))
        kw.setdefault('url_call_update', '/cabinet/calls/{pk}/update/')
        kw.setdefault('url_in_progress', reverse('cabinet:in_progress_list'))
    else:
        kw.setdefault('url_clients', reverse('sales:client_list'))
        kw.setdefault('url_call_update', '/cabinet/manager-panel/calls/{pk}/update/')
        kw.setdefault('url_in_progress', reverse('sales:in_progress_list'))
    return kw


@_manager_required
def dashboard(request):
    total_clients = Client.objects.count()
    uncalled = Client.objects.filter(
        ~Q(calls__isnull=False), is_archived=False
    ).count()
    in_progress = Call.objects.exclude(status__in=['refusal', 'completed']).count()
    archived = Client.objects.filter(is_archived=True).count()
    my_clients = Client.objects.filter(assigned_manager=request.user).count()

    status_counts = list(
        Call.objects.values('status')
        .annotate(count=Count('id'))
        .order_by('status')
    )
    total_calls = sum(s['count'] for s in status_counts) or 1

    return render(request, 'sales/dashboard.html', _ctx(request,
        title='Дашборд',
        total_clients=total_clients,
        uncalled=uncalled,
        in_progress=in_progress,
        archived=archived,
        my_clients=my_clients,
        status_counts=status_counts,
        total_calls=total_calls,
    ))


STATUS_SEARCH_MAP = {
    'согласование': 'negotiation',
    'создание тз': 'tz_creation',
    'согласование тз': 'tz_approval',
    'подписание договора': 'contract_signing',
    'в работе': 'in_progress',
    'выполнено': 'completed',
    'отказ': 'refusal',
    'новый': '__new__',
}

STATUS_TEXT_SEARCH = {
    'negotiation': 'Согласование',
    'tz_creation': 'Создание ТЗ',
    'tz_approval': 'Согласование ТЗ',
    'contract_signing': 'Подписание договора',
    'in_progress': 'В работе',
    'completed': 'Выполнено',
    'refusal': 'Отказ',
}


def _apply_search(qs, search):
    if not search:
        return qs
    search_lower = search.lower()
    matched_status = STATUS_SEARCH_MAP.get(search_lower)
    if matched_status == '__new__':
        return qs.filter(calls__isnull=True).distinct()
    if matched_status:
        return qs.filter(calls__status=matched_status).distinct()
    status_pks = [pk for pk, txt in STATUS_TEXT_SEARCH.items() if search_lower in txt.lower()]
    q = (
        Q(name__icontains=search) | Q(phone__icontains=search) |
        Q(company_name__icontains=search) | Q(city__icontains=search) |
        Q(industry__icontains=search) | Q(comment__icontains=search) |
        Q(assigned_manager__first_name__icontains=search) |
        Q(assigned_manager__last_name__icontains=search) |
        Q(assigned_manager__email__icontains=search) |
        Q(legal_status__icontains=search)
    )
    if status_pks:
        q |= Q(calls__status__in=status_pks)
    return qs.filter(q).distinct()


@_manager_required
def client_list(request):
    qs = Client.objects.filter(is_archived=False).select_related('assigned_manager', 'imported_by')
    search = request.GET.get('q', '').strip()
    no_manager = request.GET.get('no_manager') == '1'
    if no_manager:
        qs = qs.filter(assigned_manager__isnull=True)
    qs = _apply_search(qs, search)

    per_page = qs.count() if request.GET.get('all') == '1' else 20
    paginator = Paginator(qs, max(per_page, 1))
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    clients = page_obj.object_list

    ctx = dict(
        clients=clients,
        page_obj=page_obj,
        search=search,
        no_manager=no_manager,
        active_section='clients',
        user=request.user,
    )

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        rows_html = render_to_string('sales/client_list_rows.html', ctx)
        footer_html = render_to_string('sales/client_list_footer.html', ctx)
        return JsonResponse({'rows': rows_html, 'footer': footer_html})

    return render(request, 'sales/client_list.html', _ctx(request,
        title='База клиентов',
        clients=clients,
        page_obj=page_obj,
        active_section='clients',
        search=search,
        no_manager=no_manager,
    ))


@_manager_required
def called_list(request):
    qs = Client.objects.filter(calls__isnull=False, is_archived=False).distinct().select_related('assigned_manager', 'imported_by')
    search = request.GET.get('q', '').strip()
    qs = _apply_search(qs, search)
    per_page = qs.count() if request.GET.get('all') == '1' else 20
    paginator = Paginator(qs, max(per_page, 1))
    page_obj = paginator.get_page(request.GET.get('page', 1))
    ctx = dict(clients=page_obj.object_list, page_obj=page_obj, search=search, active_section='called', user=request.user)
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'rows': render_to_string('sales/client_list_rows.html', ctx), 'footer': render_to_string('sales/client_list_footer.html', ctx)})
    return render(request, 'sales/client_list.html', _ctx(request, title='Прозвоненные', **ctx))


@_manager_required
def in_progress_list(request):
    qs = Client.objects.filter(
        calls__isnull=False, is_archived=False
    ).exclude(
        calls__status__in=['refusal', 'completed']
    ).distinct().select_related('assigned_manager', 'imported_by')
    search = request.GET.get('q', '').strip()
    qs = _apply_search(qs, search)
    per_page = qs.count() if request.GET.get('all') == '1' else 20
    paginator = Paginator(qs, max(per_page, 1))
    page_obj = paginator.get_page(request.GET.get('page', 1))
    ctx = dict(clients=page_obj.object_list, page_obj=page_obj, search=search, active_section='in_progress', user=request.user)
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'rows': render_to_string('sales/client_list_rows.html', ctx), 'footer': render_to_string('sales/client_list_footer.html', ctx)})
    return render(request, 'sales/client_list.html', _ctx(request, title='В работе', **ctx))


@_manager_required
def archive_list(request):
    qs = Client.objects.filter(is_archived=True).select_related('assigned_manager', 'imported_by')
    search = request.GET.get('q', '').strip()
    qs = _apply_search(qs, search)
    per_page = qs.count() if request.GET.get('all') == '1' else 20
    paginator = Paginator(qs, max(per_page, 1))
    page_obj = paginator.get_page(request.GET.get('page', 1))
    ctx = dict(clients=page_obj.object_list, page_obj=page_obj, search=search, active_section='archive', user=request.user)
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'rows': render_to_string('sales/client_list_rows.html', ctx), 'footer': render_to_string('sales/client_list_footer.html', ctx)})
    return render(request, 'sales/client_list.html', _ctx(request, title='Архив', **ctx))


@_manager_required
def completed_list(request):
    qs = Client.objects.filter(
        calls__status='completed', is_archived=False
    ).distinct().select_related('assigned_manager', 'imported_by')
    search = request.GET.get('q', '').strip()
    qs = _apply_search(qs, search)
    per_page = qs.count() if request.GET.get('all') == '1' else 20
    paginator = Paginator(qs, max(per_page, 1))
    page_obj = paginator.get_page(request.GET.get('page', 1))
    ctx = dict(clients=page_obj.object_list, page_obj=page_obj, search=search, active_section='completed', user=request.user)
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'rows': render_to_string('sales/client_list_rows.html', ctx), 'footer': render_to_string('sales/client_list_footer.html', ctx)})
    return render(request, 'sales/client_list.html', _ctx(request, title='Выполненные', **ctx))


@_manager_required
def client_detail(request, pk):
    client = get_object_or_404(Client, pk=pk)
    calls = client.calls.select_related('manager').all()
    documents = client.documents.select_related('uploaded_by').all()
    activities = client.activities.select_related('user').all()
    form = ClientForm(instance=client)
    from_section = request.GET.get('from', 'clients')
    return render(request, 'sales/client_detail.html', _ctx(request,
        title=f'Клиент — {client.name or client.company_name or client.phone}',
        client=client,
        calls=calls,
        documents=documents,
        activities=activities,
        form=form,
        can_modify=_can_modify(request, client),
        active_section=from_section,
    ))


@_manager_required
@require_POST
def create_call(request, pk):
    client = get_object_or_404(Client, pk=pk)
    editable_fields = ['name', 'phone', 'company_name', 'city', 'industry', 'legal_status', 'comment']
    for field in editable_fields:
        if field in request.POST:
            old = str(getattr(client, field, ''))
            new = request.POST[field]
            if old != new:
                setattr(client, field, new)
                label = ClientForm._meta.model._meta.get_field(field).verbose_name or field
                model_field = ClientForm._meta.model._meta.get_field(field)
                choices = getattr(model_field, 'choices', None)
                if choices:
                    cmap = dict(choices)
                    old = cmap.get(old, old)
                    new = cmap.get(new, new)
                ClientActivity.objects.create(
                    client=client, user=request.user, activity_type='edit',
                    title=f'Изменено поле «{label}»',
                    old_value=old[:500], new_value=new[:500],
                )
    if not client.assigned_manager:
        client.assigned_manager = request.user
    client.save()
    status = request.POST.get('status', 'in_progress')
    if status not in dict(Call._meta.get_field('status').flatchoices):
        status = 'in_progress'
    call = Call.objects.create(client=client, manager=request.user, status=status)
    ClientActivity.objects.create(
        client=client, user=request.user, activity_type='call',
        title='Создан обзвон',
        new_value=dict(Call._meta.get_field('status').flatchoices).get(status, status),
    )
    messages.success(request, f'Обзвон создан для {client.name or client.phone}')
    ns = _ns(request)
    if ns == 'cabinet':
        return redirect('cabinet:clients')
    return redirect('sales:client_list')


@_manager_required
@require_POST
def toggle_archive(request, pk):
    client = get_object_or_404(Client, pk=pk)
    if not _can_modify(request, client):
        messages.error(request, 'Нет прав на изменение этого клиента')
        return redirect('sales:client_list')
    client.is_archived = not client.is_archived
    client.save()
    status = 'архивирован' if client.is_archived else 'извлечён из архива'
    messages.success(request, f'Клиент {status}')
    ns = _ns(request)
    if ns == 'cabinet':
        return redirect('cabinet:clients')
    return redirect('sales:client_list')


@_manager_required
@require_POST
def call_update(request, pk):
    call = get_object_or_404(Call, pk=pk)
    comment = request.POST.get('comment', '')
    status = request.POST.get('status', '')
    if status in dict(Call._meta.get_field('status').flatchoices):
        call.status = status
    call.comment = comment
    call.save()
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'ok': True})
    messages.success(request, 'Данные обновлены')
    ns = _ns(request)
    if ns == 'cabinet':
        return redirect('cabinet:client_detail', pk=call.client_id)
    return redirect('sales:client_detail', pk=call.client_id)


@_manager_required
def client_create(request):
    if request.method == 'POST':
        form = ClientForm(request.POST)
        if form.is_valid():
            client = form.save(commit=False)
            client.imported_by = request.user
            client.save()
            messages.success(request, f'Клиент {client.name or client.phone} создан')
            ns = _ns(request)
            if ns == 'cabinet':
                return redirect('cabinet:client_detail', pk=client.pk)
            return redirect('sales:client_detail', pk=client.pk)
    else:
        form = ClientForm()
    return render(request, 'sales/client_form.html', _ctx(request,
        title='Новый клиент',
        form=form,
    ))


@_manager_required
def client_export(request):
    import openpyxl
    from openpyxl.styles import Font, Alignment, PatternFill

    qs = Client.objects.filter(is_archived=False).select_related('assigned_manager').all()
    search = request.GET.get('q', '').strip()
    no_manager = request.GET.get('no_manager') == '1'
    if no_manager:
        qs = qs.filter(assigned_manager__isnull=True)
    qs = _apply_search(qs, search)

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = 'Клиенты'

    headers = ['Сфера', 'Город', 'Наименование', 'Имя', 'Телефон',
               'Правовой статус', 'Комментарий', 'Ответственный', 'Дата создания']
    header_font = Font(bold=True, color='FFFFFF')
    header_fill = PatternFill(start_color='2D8F5E', end_color='2D8F5E', fill_type='solid')
    for col, h in enumerate(headers, 1):
        cell = ws.cell(row=1, column=col, value=h)
        cell.font = header_font
        cell.fill = header_fill
        cell.alignment = Alignment(horizontal='center')

    status_map = dict(LEGAL_STATUSES)
    for row, client in enumerate(qs, 2):
        ws.cell(row=row, column=1, value=client.industry or '')
        ws.cell(row=row, column=2, value=client.city or '')
        ws.cell(row=row, column=3, value=client.company_name or '')
        ws.cell(row=row, column=4, value=client.name or '')
        ws.cell(row=row, column=5, value=client.phone)
        ws.cell(row=row, column=6, value=status_map.get(client.legal_status, ''))
        ws.cell(row=row, column=7, value=client.comment or '')
        ws.cell(row=row, column=8, value=client.assigned_manager.email if client.assigned_manager else '')
        ws.cell(row=row, column=9, value=client.created_at.strftime('%d.%m.%Y %H:%M'))

    for col in range(1, len(headers) + 1):
        ws.column_dimensions[openpyxl.utils.get_column_letter(col)].width = 20

    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename="clients.xlsx"'
    wb.save(response)
    return response


@_manager_required
def client_import(request):
    if request.method == 'POST' and request.FILES.get('file'):
        import openpyxl
        import csv
        import os

        file = request.FILES['file']
        ext = os.path.splitext(file.name)[1].lower()
        rows = []

        clients_url = 'cabinet:clients' if _ns(request) == 'cabinet' else 'sales:client_list'

        if ext in ('.xlsx', '.xls'):
            try:
                wb = openpyxl.load_workbook(file)
                ws = wb.active
                rows = list(ws.iter_rows(min_row=2, values_only=True))
            except Exception:
                messages.error(request, 'Не удалось прочитать файл. Загрузите .xlsx')
                return redirect(clients_url)
        elif ext == '.csv':
            try:
                decoded = file.read().decode('utf-8-sig')
                reader = csv.reader(io.StringIO(decoded))
                next(reader, None)
                rows = list(reader)
            except Exception:
                messages.error(request, 'Не удалось прочитать CSV. Проверьте кодировку (UTF-8)')
                return redirect(clients_url)
        else:
            messages.error(request, 'Поддерживаются только .xlsx, .xls и .csv')
            return redirect(clients_url)

        if not rows:
            messages.error(request, 'Файл пуст')
            return redirect(clients_url)

        status_map = {v: k for k, v in LEGAL_STATUSES}
        created = 0
        updated = 0
        skipped = 0
        for row in rows:
            industry = str(row[0]).strip() if len(row) >= 1 and row[0] else ''
            city = str(row[1]).strip() if len(row) >= 2 and row[1] else ''
            company = str(row[2]).strip() if len(row) >= 3 and row[2] else ''
            name = str(row[3]).strip() if len(row) >= 4 and row[3] else ''
            phone = str(row[4]).strip() if len(row) >= 5 and row[4] else None
            raw = str(row[5]).strip() if len(row) >= 6 and row[5] else ''
            comment = str(row[6]).strip() if len(row) >= 7 and row[6] else ''

            if not phone:
                skipped += 1
                continue

            existing = Client.objects.filter(phone=phone).first()
            if existing:
                changed = False
                for field, val in [('industry', industry), ('city', city),
                                   ('company_name', company), ('name', name),
                                   ('comment', comment)]:
                    if val and getattr(existing, field) != val:
                        setattr(existing, field, val)
                        changed = True
                legal_val = status_map.get(raw, '')
                if legal_val and existing.legal_status != legal_val:
                    existing.legal_status = legal_val
                    changed = True
                if changed:
                    existing.save()
                    updated += 1
                else:
                    skipped += 1
            else:
                Client.objects.create(
                    industry=industry, city=city, company_name=company,
                    name=name, phone=phone,
                    legal_status=status_map.get(raw, ''),
                    comment=comment, imported_by=request.user,
                )
                created += 1

        parts = []
        if created:
            parts.append(f'добавлено {created}')
        if updated:
            parts.append(f'обновлено {updated}')
        if skipped:
            parts.append(f'пропущено {skipped}')
        messages.success(request, 'Импорт завершён. ' + ', '.join(parts))
        return redirect(clients_url)

    return render(request, 'sales/client_import.html', _ctx(request,
        title='Импорт клиентов',
    ))


@_manager_required
def client_update(request, pk):
    client = get_object_or_404(Client, pk=pk)
    from_section = request.POST.get('from_section', request.GET.get('from', 'clients'))
    if request.method == 'POST':
        if not _can_modify(request, client):
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'ok': False, 'error': 'no permission'}, status=403)
            messages.error(request, 'Нет прав на изменение этого клиента')
            return redirect('sales:client_list')

        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            editable_fields = ['name', 'phone', 'company_name', 'city', 'industry', 'legal_status', 'comment']
            for field in editable_fields:
                if field in request.POST:
                    old = str(getattr(client, field, ''))
                    new = request.POST[field]
                    if old != new:
                        setattr(client, field, new)
                        label = ClientForm._meta.model._meta.get_field(field).verbose_name or field
                        model_field = ClientForm._meta.model._meta.get_field(field)
                        choices = getattr(model_field, 'choices', None)
                        if choices:
                            cmap = dict(choices)
                            old = cmap.get(old, old)
                            new = cmap.get(new, new)
                        ClientActivity.objects.create(
                            client=client, user=request.user, activity_type='edit',
                            title=f'Изменено поле «{label}»',
                            old_value=old[:500], new_value=new[:500],
                        )
            client.save()
            return JsonResponse({'ok': True})

        form = ClientForm(request.POST, instance=client)
        if not form.is_valid():
            for field, errors in form.errors.items():
                for err in errors:
                    messages.error(request, f'{form.fields[field].label or field}: {err}')
            return redirect(_list_viewname(_ns(request), from_section))

        changes = []
        for field in form.changed_data:
            old = str(form.initial.get(field, ''))
            new = str(form.cleaned_data.get(field, ''))
            if old != new:
                label = form.fields[field].label if field in form.fields else field
                changes.append((field, label, old, new))
        form.save()
        for field, label, old, new in changes:
            choices = getattr(form.fields.get(field), 'choices', None)
            if choices:
                cmap = dict(choices)
                old = cmap.get(old, old)
                new = cmap.get(new, new)
            ClientActivity.objects.create(
                client=client, user=request.user, activity_type='edit',
                title=f'Изменено поле «{label}»',
                old_value=old[:500], new_value=new[:500],
            )

        doc_file = request.FILES.get('doc_file')
        if doc_file:
            title = doc_file.name
            ClientDocument.objects.create(
                client=client, title=title, file=doc_file, uploaded_by=request.user,
            )
            ClientActivity.objects.create(
                client=client, user=request.user, activity_type='document',
                title=f'Загружен документ «{title}»',
            )
            messages.success(request, f'Документ "{title}" загружен')

        status = request.POST.get('status', '')
        last_call = client.calls.last()
        if last_call and status in dict(Call._meta.get_field('status').flatchoices):
            old_status = last_call.status
            if old_status != status:
                last_call.status = status
                last_call.save(update_fields=['status'])
                old_label = dict(Call._meta.get_field('status').flatchoices).get(old_status, old_status)
                new_label = dict(Call._meta.get_field('status').flatchoices).get(status, status)
                ClientActivity.objects.create(
                    client=client, user=request.user, activity_type='status',
                    title='Смена статуса',
                    old_value=old_label, new_value=new_label,
                )

        messages.success(request, 'Сохранено')
        ns = _ns(request)
        return redirect(_list_viewname(ns, from_section))
    else:
        form = ClientForm(instance=client)
    return render(request, 'sales/client_form.html', _ctx(request,
        title='Редактирование клиента',
        form=form, edit_mode=True,
    ))


@_manager_required
@require_POST
def client_delete(request, pk):
    client = get_object_or_404(Client, pk=pk)
    if not _can_modify(request, client):
        messages.error(request, 'Нет прав на удаление этого клиента')
        return redirect('sales:client_list')
    name = str(client)
    client.delete()
    messages.success(request, f'Клиент {name} удалён')
    ns = _ns(request)
    return redirect('cabinet:clients' if ns == 'cabinet' else 'sales:client_list')


@_manager_required
@require_POST
def delete_document(request, client_pk, doc_pk):
    document = get_object_or_404(ClientDocument, pk=doc_pk, client_id=client_pk)
    client = document.client
    if not _can_modify(request, client):
        messages.error(request, 'Нет прав на удаление документа')
        return redirect('sales:client_list')
    title = document.title
    ClientActivity.objects.create(
        client=client, user=request.user, activity_type='document',
        title=f'Удалён документ «{title}»',
    )
    document.delete()
    messages.success(request, f'Документ "{title}" удалён')
    ns = _ns(request)
    from_section = request.POST.get('from_section', 'clients')
    detail_url = 'sales:client_detail' if ns == 'sales' else 'cabinet:client_detail'
    return redirect(f'{reverse(detail_url, args=[client_pk])}?from={from_section}')
