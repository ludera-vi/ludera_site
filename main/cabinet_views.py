from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.contrib.auth.models import User
from django.db.models import Count, Min, Max, Q, Sum
from django.db.models.functions import TruncDate
from django.utils import timezone
from django.forms import inlineformset_factory, modelformset_factory
from django.urls import reverse
from django.core.paginator import Paginator
from datetime import timedelta
import uuid

from .models import (
    SiteSetting, HeroSection, NavLink, Service, Project,
    Product, ProductMetric, ProductDetail, Principle,
    BlogPost, PageView, ContactRequest, SocialLink,
)
from .forms import (
    ServiceForm, ProjectForm, ProductForm, BlogPostForm,
    SiteSettingForm, HeroSectionForm, NavLinkForm,
    PrincipleForm,
    LoginForm, GoodsForm, GoodsFileForm, SocialLinkForm,
)
from users.models import UserProfile, UserProduct, ProductFile, UserSetting, Goods, GoodsFile, UserGoods, CabinetPermission, ManagerSuggestion, SuggestionMessage
from users.forms import UserProfileForm, UserCreateForm
from sales.models import Client, Call, ClientActivity, CALL_STATUSES, InfoTopic, InfoTopicRead
from sales.views import _last_status_clients


@login_required(login_url='/cabinet/login/')
def dashboard(request):
    today = timezone.now().date()
    week_ago = today - timedelta(days=7)
    month_ago = today - timedelta(days=30)

    total_sessions = PageView.objects.exclude(session_key='').values('session_key').distinct().count()
    today_sessions = PageView.objects.filter(timestamp__date=today).exclude(session_key='').values('session_key').distinct().count()
    week_sessions = PageView.objects.filter(timestamp__date__gte=week_ago).exclude(session_key='').values('session_key').distinct().count()
    month_sessions = PageView.objects.filter(timestamp__date__gte=month_ago).exclude(session_key='').values('session_key').distinct().count()

    total_pageviews = PageView.objects.count()

    total_contacts = ContactRequest.objects.count()
    total_services = Service.objects.count()
    total_projects = Project.objects.count()
    total_products = Product.objects.count()
    total_blog = BlogPost.objects.count()

    top_pages = (
        PageView.objects.values('url')
        .annotate(count=Count('id'))
        .order_by('-count')[:10]
    )

    recent_contacts = ContactRequest.objects.order_by('-created_at')[:5]

    sessions_by_day = (
        PageView.objects
        .filter(timestamp__date__gte=month_ago)
        .exclude(session_key='')
        .annotate(day=TruncDate('timestamp'))
        .values('day')
        .annotate(count=Count('session_key', distinct=True))
        .order_by('day')
    )

    days_labels = []
    days_data = []
    sd_dict = {s['day']: s['count'] for s in sessions_by_day}
    for i in range(30):
        d = month_ago + timedelta(days=i)
        days_labels.append(d.strftime('%d.%m'))
        days_data.append(sd_dict.get(d, 0))

    avg_session_seconds = 0
    session_data = (
        PageView.objects.filter(timestamp__date__gte=month_ago)
        .exclude(session_key='')
        .values('session_key')
        .annotate(min_ts=Min('timestamp'), max_ts=Max('timestamp'))
    )
    durations = []
    for s in session_data:
        dur = (s['max_ts'] - s['min_ts']).total_seconds()
        if 5 < dur < 3600:
            durations.append(dur)
    if durations:
        avg_session_seconds = sum(durations) / len(durations)

    views_by_url = list(top_pages)
    top_urls = [v['url'][:40] for v in views_by_url]
    top_counts = [v['count'] for v in views_by_url]

    converting_sessions = set(
        PageView.objects.filter(
            Q(url__startswith='/contact/') | Q(url='/contact'),
            timestamp__date__gte=month_ago,
        ).exclude(session_key='')
        .values_list('session_key', flat=True)
        .distinct()
    )

    top_conversion_pages = (
        PageView.objects
        .filter(timestamp__date__gte=month_ago)
        .exclude(session_key='')
        .exclude(url__startswith='/contact/')
        .exclude(url__startswith='/admin')
        .exclude(url__startswith='/static')
        .exclude(url__startswith='/cabinet')
        .values('url')
        .annotate(sessions=Count('session_key', distinct=True))
        .filter(sessions__gte=5)
        .order_by('-sessions')[:10]
    )

    from django.urls import resolve, Resolver404
    page_name_map = {
        'index': 'Главная',
        'blog_detail': 'Запись блога',
        'project_detail': 'Проект',
        'service_detail': 'Услуга',
        'product_detail': 'Продукт',
        'contact_submit': 'Контакты',
    }
    conversion_data = []
    for item in top_conversion_pages:
        page_url = item['url']
        total_sesh = item['sessions']
        converters = PageView.objects.filter(
            url=page_url,
            session_key__in=converting_sessions,
            timestamp__date__gte=month_ago,
        ).values('session_key').distinct().count()
        rate = round(converters / total_sesh * 100, 1) if total_sesh else 0
        try:
            match = resolve(page_url.split('?')[0])
            name = page_name_map.get(match.url_name, page_url)
        except Resolver404:
            name = page_url
        conversion_data.append({
            'url': page_url,
            'name': name,
            'sessions': total_sesh,
            'converters': converters,
            'rate': rate,
        })
    conversion_data.sort(key=lambda x: x['rate'], reverse=True)
    conversion_data = conversion_data[:6]

    return render(request, 'cabinet/dashboard.html', {
        'title': 'Дашборд',
        'total_sessions': total_sessions,
        'today_sessions': today_sessions,
        'week_sessions': week_sessions,
        'month_sessions': month_sessions,
        'total_pageviews': total_pageviews,
        'total_contacts': total_contacts,
        'total_services': total_services,
        'total_projects': total_projects,
        'total_products': total_products,
        'total_blog': total_blog,
        'avg_session_seconds': int(avg_session_seconds),
        'recent_contacts': recent_contacts,
        'days_labels': days_labels,
        'days_data': days_data,
        'top_urls': top_urls,
        'top_counts': top_counts,
        'conversion_data': conversion_data,
    })


def cabinet_login(request):
    access_error = None
    if request.user.is_authenticated:
        if request.user.is_superuser:
            return redirect('cabinet:dashboard')
        access_error = 'У вас нет доступа к панели управления.'
    form = LoginForm()
    if request.method == 'POST':
        from django.contrib.auth import login, authenticate
        form = LoginForm(request, request.POST)
        if form.is_valid():
            user = form.get_user()
            role = getattr(getattr(user, 'profile', None), 'role', 'admin')
            if role == 'client' and not user.is_superuser:
                access_error = 'У вас нет доступа к панели управления. Пожалуйста, используйте <a href="/account/login/" style="color:var(--cab-primary);text-decoration:none;font-weight:600;">аккаунт пользователя</a> или перейдите на <a href="/" style="color:var(--cab-primary);text-decoration:none;font-weight:600;">главную страницу</a>.'
            else:
                login(request, user)
                if user.is_superuser:
                    return redirect('cabinet:dashboard')
                access_error = 'У вас нет доступа к панели управления.'
    return render(request, 'cabinet/login.html', {'form': form, 'access_error': access_error})


@login_required(login_url='/cabinet/login/')
def cabinet_logout(request):
    logout(request)
    return redirect('cabinet:login')


# ─── Generic CRUD helpers ──────────────────────────────────────

FIELDS_MAP = {
    'title': 'Название',
    'email': 'Email',
    'name': 'Имя',
    'number': 'Номер',
    'pill_label': 'Лейбл',
    'pill_number': 'Пилл',
    'badge_text': 'Бейдж',
    'order': 'Порядок',
    'status': 'Статус',
    'category': 'Категория',
    'date': 'Дата',
    'author': 'Автор',
    'is_visible': 'Видимость',
    'is_read': 'Прочитано',
    'is_active': 'Активен',
    'created_at': 'Дата',
    'updated_at': 'Обновлено',
    'url': 'URL',
    'timestamp': 'Время',
    'ip_address': 'IP',
    'username': 'Логин',
    'first_name': 'Имя',
    'last_name': 'Фамилия',
    'date_joined': 'Дата регистрации',
}


PAGE_SIZE = 50


def _list_view(request, model, model_name, title, fields, extra_context=None):
    items = model.objects.all()
    if hasattr(model, 'order'):
        items = items.order_by('order')
    elif hasattr(model, 'created_at'):
        items = items.order_by('-created_at')
    elif hasattr(model, 'date'):
        items = items.order_by('-date')
    paginator = Paginator(items, PAGE_SIZE)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    ctx = {
        'title': title,
        'items': page_obj,
        'fields': [(f, FIELDS_MAP.get(f, f)) for f in fields],
        'model_name': model_name,
        'can_add': True,
        'create_url': reverse(f'cabinet:{model_name}_create'),
        'edit_url': reverse(f'cabinet:{model_name}_edit', args=[0]).replace('/0/', '/'),
        'paginator': paginator,
        'page_obj': page_obj,
    }
    if extra_context:
        ctx.update(extra_context)
    return render(request, 'cabinet/list.html', ctx)


def _form_view(request, model, form_class, model_name, title, pk=None, extra_ctx=None, save_redirect=None):
    instance = None
    if pk:
        instance = get_object_or_404(model, pk=pk)
    if request.method == 'POST':
        form = form_class(request.POST, request.FILES, instance=instance)
        if form.is_valid():
            form.save()
            return redirect(save_redirect or reverse(f'cabinet:{model_name}_list'))
    else:
        form = form_class(instance=instance)
    ctx = {
        'title': title,
        'form': form,
        'model_name': model_name,
        'is_edit': pk is not None,
        'panel_fields': getattr(form_class, 'panel_fields', []),
    }
    if extra_ctx:
        ctx.update(extra_ctx)
    return render(request, 'cabinet/form.html', ctx)


def _delete_view(request, model, model_name, pk, redirect_url=None):
    obj = get_object_or_404(model, pk=pk)
    if request.method == 'POST':
        obj.delete()
        return redirect(redirect_url or reverse(f'cabinet:{model_name}_list'))
    return render(request, 'cabinet/confirm_delete.html', {
        'title': f'Удаление {model_name}',
        'obj': obj,
        'model_name': model_name,
    })


# ─── Services CRUD ─────────────────────────────────────────────

@login_required(login_url='/cabinet/login/')
def service_list(request):
    return _list_view(request, Service, 'service', 'Услуги',
                      ['title', 'pill_label', 'pill_number', 'order', 'created_at'])


@login_required(login_url='/cabinet/login/')
def service_form(request, pk=None):
    return _form_view(request, Service, ServiceForm, 'service',
                      'Редактировать услугу' if pk else 'Новая услуга', pk)


@login_required(login_url='/cabinet/login/')
def service_delete(request, pk):
    return _delete_view(request, Service, 'service', pk)


# ─── Products CRUD ─────────────────────────────────────────────

@login_required(login_url='/cabinet/login/')
def product_list(request):
    return _list_view(request, Product, 'product', 'Продукты',
                      ['title', 'badge_text', 'order', 'created_at'],
                      extra_context={'files_url': '/cabinet/product/'})


@login_required(login_url='/cabinet/login/')
def product_form(request, pk=None):
    instance = get_object_or_404(Product, pk=pk) if pk else None

    MetricFormSet = inlineformset_factory(
        Product, ProductMetric, fields=('label', 'value'), extra=1, can_delete=True,
    )
    DetailFormSet = inlineformset_factory(
        Product, ProductDetail, fields=('text',), extra=1, can_delete=True,
    )

    if request.method == 'POST':
        form = ProductForm(request.POST, instance=instance)
        metric_formset = MetricFormSet(request.POST, instance=instance or Product())
        detail_formset = DetailFormSet(request.POST, instance=instance or Product())

        if form.is_valid() and metric_formset.is_valid() and detail_formset.is_valid():
            obj = form.save()
            metric_formset.instance = obj
            detail_formset.instance = obj
            metric_formset.save()
            detail_formset.save()
            return redirect('cabinet:product_list')
    else:
        form = ProductForm(instance=instance)
        metric_formset = MetricFormSet(instance=instance)
        detail_formset = DetailFormSet(instance=instance)

    return render(request, 'cabinet/product_form.html', {
        'title': 'Редактировать продукт' if pk else 'Новый продукт',
        'form': form,
        'metric_formset': metric_formset,
        'detail_formset': detail_formset,
        'model_name': 'product',
        'is_edit': pk is not None,
    })


@login_required(login_url='/cabinet/login/')
def product_delete(request, pk):
    return _delete_view(request, Product, 'product', pk)


# ─── Product Files (inline in product form) ────────────────────

@login_required(login_url='/cabinet/login/')
def product_files(request, pk):
    product = get_object_or_404(Product, pk=pk)
    FormSet = inlineformset_factory(
        Product, ProductFile,
        fields=('title', 'file', 'file_type', 'order'),
        extra=1, can_delete=True,
    )
    if request.method == 'POST':
        formset = FormSet(request.POST, request.FILES, instance=product)
        if formset.is_valid():
            formset.save()
            return redirect('cabinet:product_list')
    else:
        formset = FormSet(instance=product)
    return render(request, 'cabinet/product_files.html', {
        'title': f'Файлы: {product.title}',
        'product': product,
        'formset': formset,
        'model_name': 'product',
    })


# ─── Goods CRUD ────────────────────────────────────────────────

@login_required(login_url='/cabinet/login/')
def goods_list(request):
    items = Goods.objects.all().order_by('order')
    return render(request, 'cabinet/goods_list.html', {
        'title': 'Товары',
        'items': items,
        'model_name': 'goods',
    })


@login_required(login_url='/cabinet/login/')
def goods_form(request, pk=None):
    instance = get_object_or_404(Goods, pk=pk) if pk else None

    if request.method == 'POST':
        form = GoodsForm(request.POST, instance=instance)
        if form.is_valid():
            obj = form.save()
            return redirect('cabinet:goods_list')
    else:
        form = GoodsForm(instance=instance)

    return render(request, 'cabinet/goods_form.html', {
        'title': 'Редактировать товар' if pk else 'Новый товар',
        'form': form,
        'model_name': 'goods',
        'is_edit': pk is not None,
    })


@login_required(login_url='/cabinet/login/')
def goods_delete(request, pk):
    return _delete_view(request, Goods, 'goods', pk,
                        redirect_url=reverse('cabinet:goods_list'))


@login_required(login_url='/cabinet/login/')
def goods_files(request, pk):
    goods = get_object_or_404(Goods, pk=pk)
    FormSet = inlineformset_factory(
        Goods, GoodsFile,
        fields=('title', 'file', 'file_type', 'order'),
        extra=1, can_delete=True,
    )
    if request.method == 'POST':
        formset = FormSet(request.POST, request.FILES, instance=goods)
        if formset.is_valid():
            formset.save()
            return redirect('cabinet:goods_list')
    else:
        formset = FormSet(instance=goods)
    return render(request, 'cabinet/goods_files.html', {
        'title': f'Файлы: {goods.title}',
        'goods': goods,
        'formset': formset,
        'model_name': 'goods',
    })


from django.http import JsonResponse
from django.views.decorators.http import require_POST
import os

@login_required(login_url='/cabinet/login/')
@require_POST
def goods_upload_file(request, pk):
    goods = get_object_or_404(Goods, pk=pk)
    file = request.FILES.get('file')
    if file:
        title = request.POST.get('title', '')
        if not title:
            title = file.name.rsplit('.', 1)[0]
        file_type = request.POST.get('file_type', '')
        gf = GoodsFile.objects.create(
            goods=goods,
            title=title,
            file=file,
            file_type=file_type,
        )
        return JsonResponse({'ok': True, 'id': gf.pk, 'title': gf.title,
                             'filename': gf.filename, 'file_type': gf.file_type})
    return JsonResponse({'ok': False, 'error': 'Файл не передан'}, status=400)


@login_required(login_url='/cabinet/login/')
def goods_delete_file(request, pk, file_pk):
    gf = get_object_or_404(GoodsFile, pk=file_pk, goods_id=pk)
    gf.delete()
    return JsonResponse({'ok': True})


# ─── Users CRUD (admin management) ─────────────────────────────

@login_required(login_url='/cabinet/login/')
def user_list(request):
    items = User.objects.select_related('profile').order_by('-date_joined')
    return render(request, 'cabinet/list.html', {
        'title': 'Пользователи',
        'items': items,
        'fields': [
            ('email', 'Email'), ('username', 'Логин'),
            ('first_name', 'Имя'), ('last_name', 'Фамилия'),
            ('profile.role', 'Роль'), ('is_staff', 'Админ'),
            ('is_active', 'Активен'), ('date_joined', 'Дата регистрации'),
        ],
        'model_name': 'user',
        'can_add': True,
        'create_url': reverse('cabinet:user_create'),
        'edit_url': '/cabinet/user/',
    })


@login_required(login_url='/cabinet/login/')
def user_detail(request, pk):
    if not request.user.is_superuser:
        messages.error(request, 'Доступ запрещён')
        return redirect('cabinet:dashboard')
    user = get_object_or_404(User, pk=pk)
    profile, _ = UserProfile.objects.get_or_create(user=user)
    user_goods = UserGoods.objects.filter(user=user).select_related('goods')
    user_products = UserProduct.objects.filter(user=user).select_related('product')
    user_sections = set(user.cabinet_permissions.values_list('section', flat=True))

    if request.method == 'POST':
        if 'save_role' in request.POST:
            new_role = request.POST.get('role', 'client')
            if new_role in dict(UserProfile.ROLES):
                profile.role = new_role
                profile.save()
                if new_role == 'admin':
                    user.is_staff = True
                else:
                    user.is_staff = False
                if new_role == 'client':
                    user.cabinet_permissions.all().delete()
                user.save()
                messages.success(request, f'Роль изменена на "{profile.get_role_display()}"')
            return redirect('cabinet:user_detail', pk=pk)
        if 'save_profile' in request.POST:
            form = UserProfileForm(request.POST, request.FILES, instance=profile)
            if form.is_valid():
                form.save()
            return redirect('cabinet:user_detail', pk=pk)
        elif 'save_permissions' in request.POST:
            selected = request.POST.getlist('sections')
            user.cabinet_permissions.all().delete()
            for section in selected:
                CabinetPermission.objects.create(user=user, section=section)
            messages.success(request, 'Права доступа обновлены')
            return redirect('cabinet:user_detail', pk=pk)
        elif 'set_password' in request.POST:
            new_password = request.POST.get('new_password', '')
            new_password2 = request.POST.get('new_password2', '')
            if new_password != new_password2:
                messages.error(request, 'Пароли не совпадают')
            elif len(new_password) < 8:
                messages.error(request, 'Пароль должен быть не менее 8 символов')
            else:
                user.set_password(new_password)
                user.save()
                messages.success(request, 'Пароль успешно изменён')
            return redirect('cabinet:user_detail', pk=pk)
    else:
        form = UserProfileForm(instance=profile)

    return render(request, 'cabinet/user_detail.html', {
        'title': f'Пользователь: {user.email}',
        'user_obj': user,
        'profile': profile,
        'form': form,
        'user_goods': user_goods,
        'user_products': user_products,
        'goods_list': Goods.objects.all()[:200],
        'products_list': Product.objects.all()[:200],
        'user_sections': user_sections,
        'CabinetPermission': CabinetPermission,
        'role_choices': UserProfile.ROLES,
    })


@login_required(login_url='/cabinet/login/')
def user_add_goods(request, pk):
    user = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        goods_id = request.POST.get('goods_id')
        if goods_id:
            goods = get_object_or_404(Goods, pk=goods_id)
            ug, created = UserGoods.objects.get_or_create(
                user=user, goods=goods,
                defaults={'is_active': True},
            )
            if not created:
                ug.is_active = True
                ug.save()
    return redirect('cabinet:user_detail', pk=pk)


@login_required(login_url='/cabinet/login/')
def user_remove_goods(request, user_pk, goods_pk):
    ug = get_object_or_404(UserGoods, user_id=user_pk, goods_id=goods_pk)
    ug.is_active = False
    ug.save()
    return redirect('cabinet:user_detail', pk=user_pk)


@login_required(login_url='/cabinet/login/')
def user_delete(request, pk):
    user = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        user.delete()
        return redirect('cabinet:user_list')
    return render(request, 'cabinet/confirm_delete.html', {
        'title': f'Удаление пользователя {user.email}',
        'obj': user,
        'model_name': 'user',
    })


@login_required(login_url='/cabinet/login/')
def user_create(request):
    if request.method == 'POST':
        form = UserCreateForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, f'Пользователь {user.email} создан')
            return redirect('cabinet:user_detail', pk=user.pk)
    else:
        form = UserCreateForm()
    return render(request, 'cabinet/form.html', {
        'title': 'Новый пользователь',
        'form': form,
        'model_name': 'user',
        'is_edit': False,
    })


@login_required(login_url='/cabinet/login/')
@require_POST
def user_toggle_staff(request, pk):
    user = get_object_or_404(User, pk=pk)
    user.is_staff = not user.is_staff
    user.save()
    messages.success(request, f'Права администратора {"выданы" if user.is_staff else "отозваны"} для {user.email}')
    return redirect('cabinet:user_detail', pk=pk)


@login_required(login_url='/cabinet/login/')
def user_add_product(request, pk):
    user = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        if product_id:
            product = get_object_or_404(Product, pk=product_id)
            up, created = UserProduct.objects.get_or_create(
                user=user, product=product,
                defaults={'is_active': True},
            )
            if not created:
                up.is_active = True
                up.save()
    return redirect('cabinet:user_detail', pk=pk)


@login_required(login_url='/cabinet/login/')
def user_remove_product(request, user_pk, product_pk):
    up = get_object_or_404(UserProduct, user_id=user_pk, product_id=product_pk)
    up.is_active = False
    up.save()
    return redirect('cabinet:user_detail', pk=user_pk)


# ─── UserSettings CRUD ─────────────────────────────────────────

from django import forms as django_forms

class UserSettingForm(django_forms.ModelForm):
    class Meta:
        model = UserSetting
        fields = ['name', 'value', 'is_active']
        widgets = {
            'value': django_forms.Textarea(attrs={'rows': 4}),
        }

@login_required(login_url='/cabinet/login/')
def usersetting_list(request):
    return _list_view(request, UserSetting, 'usersetting', 'Настройки кабинета пользователей',
                      ['name', 'is_active', 'updated_at'])


@login_required(login_url='/cabinet/login/')
def usersetting_form(request, pk=None):
    return _form_view(request, UserSetting, UserSettingForm, 'usersetting',
                      'Редактировать настройку' if pk else 'Новая настройка', pk)


@login_required(login_url='/cabinet/login/')
def usersetting_delete(request, pk):
    return _delete_view(request, UserSetting, 'usersetting', pk)


# ─── Projects CRUD ─────────────────────────────────────────────

@login_required(login_url='/cabinet/login/')
def project_list(request):
    return _list_view(request, Project, 'project', 'Проекты',
                      ['title', 'status', 'order', 'created_at'])


@login_required(login_url='/cabinet/login/')
def project_form(request, pk=None):
    return _form_view(request, Project, ProjectForm, 'project',
                      'Редактировать проект' if pk else 'Новый проект', pk)


@login_required(login_url='/cabinet/login/')
def project_delete(request, pk):
    return _delete_view(request, Project, 'project', pk)


# ─── Blog CRUD ─────────────────────────────────────────────────

@login_required(login_url='/cabinet/login/')
def blog_list(request):
    return _list_view(request, BlogPost, 'blog', 'Блог',
                      ['title', 'category', 'date', 'author', 'created_at'])


@login_required(login_url='/cabinet/login/')
def blog_form(request, pk=None):
    return _form_view(request, BlogPost, BlogPostForm, 'blog',
                      'Редактировать запись' if pk else 'Новая запись', pk)


@login_required(login_url='/cabinet/login/')
def blog_delete(request, pk):
    return _delete_view(request, BlogPost, 'blog', pk)


# ─── Contact Requests ──────────────────────────────────────────

@login_required(login_url='/cabinet/login/')
def contact_list(request):
    items = ContactRequest.objects.all().order_by('-created_at')
    return render(request, 'cabinet/list.html', {
        'title': 'Заявки',
        'items': items,
        'fields': [
            ('name', 'Имя'), ('email', 'Email'),
            ('created_at', 'Дата'), ('is_read', 'Прочитано'),
        ],
        'model_name': 'contact',
        'can_add': False,
        'create_url': None,
        'edit_url': None,
        'detail_url': '/cabinet/contact/',
    })


@login_required(login_url='/cabinet/login/')
def contact_detail(request, pk):
    obj = get_object_or_404(ContactRequest, pk=pk)
    if not obj.is_read:
        obj.is_read = True
        obj.save()
    return render(request, 'cabinet/contact_detail.html', {
        'title': 'Заявка',
        'obj': obj,
    })


# ─── Page Views Stats ──────────────────────────────────────────

@login_required(login_url='/cabinet/login/')
def pageviews_list(request):
    items = PageView.objects.all().order_by('-timestamp')[:100]
    return render(request, 'cabinet/list.html', {
        'title': 'Просмотры страниц',
        'items': items,
        'fields': [
            ('url', 'URL'), ('timestamp', 'Время'), ('ip_address', 'IP'),
        ],
        'model_name': 'pageviews',
        'can_add': False,
        'create_url': None,
        'edit_url': None,
    })


@login_required(login_url='/cabinet/login/')
def navlink_list(request):
    return _list_view(request, NavLink, 'navlink', 'Навигация',
                      ['title', 'url', 'order', 'is_visible'])

@login_required(login_url='/cabinet/login/')
def navlink_form(request, pk=None):
    return _form_view(request, NavLink, NavLinkForm, 'navlink',
                      'Редактировать ссылку' if pk else 'Новая ссылка', pk)

@login_required(login_url='/cabinet/login/')
def navlink_delete(request, pk):
    return _delete_view(request, NavLink, 'navlink', pk)


@login_required(login_url='/cabinet/login/')
def principle_list(request):
    return _list_view(request, Principle, 'principle', 'Принципы',
                      ['title', 'order'])

@login_required(login_url='/cabinet/login/')
def principle_form(request, pk=None):
    return _form_view(request, Principle, PrincipleForm, 'principle',
                      'Редактировать принцип' if pk else 'Новый принцип', pk)

@login_required(login_url='/cabinet/login/')
def principle_delete(request, pk):
    return _delete_view(request, Principle, 'principle', pk)


SITESETTING_LABELS = {
    'hero': 'Hero-блок (шапка главной)',
    'header': 'Шапка сайта',
    'services': 'Секция услуг',
    'projects': 'Секция проектов',
    'products': 'Секция продуктов',
    'about': 'Секция «О нас»',
    'blog': 'Секция блога',
    'ecosystem': 'Секция «Как мы работаем»',
    'cta': 'CTA-блок (форма заявки)',
    'contact_form': 'Форма связи',
    'footer': 'Футер',
    'footer_ip': 'Футер — Данные ИП',
    'privacy': 'Политика конфиденциальности',
    'seo': 'SEO / Мета-теги',
}


@login_required(login_url='/cabinet/login/')
def sitesetting_edit(request):
    from main.forms import SITESETTING_FIELDS
    instance, _ = SiteSetting.objects.get_or_create(pk=1)
    if request.method == 'POST':
        form = SiteSettingForm(request.POST, instance=instance)
        if form.is_valid():
            form.save()
            return redirect('cabinet:sitesetting_edit')
    else:
        form = SiteSettingForm(instance=instance)
    site_groups = [
        {'key': k, 'label': SITESETTING_LABELS.get(k, k), 'fields': v}
        for k, v in SITESETTING_FIELDS.items()
    ]
    return render(request, 'cabinet/form.html', {
        'title': 'Настройки сайта',
        'form': form,
        'model_name': 'sitesetting',
        'is_edit': True,
        'site_groups': site_groups,
    })


@login_required(login_url='/cabinet/login/')
def herosection_edit(request):
    instance = HeroSection.get_active()
    if request.method == 'POST':
        form = HeroSectionForm(request.POST, instance=instance)
        if form.is_valid():
            form.save()
            return redirect('cabinet:dashboard')
    else:
        form = HeroSectionForm(instance=instance)
    return render(request, 'cabinet/form.html', {
        'title': 'Настройки Hero-блока',
        'form': form,
        'model_name': 'herosection',
        'is_edit': True,
    })


@login_required(login_url='/cabinet/login/')
def contact_delete(request, pk):
    return _delete_view(request, ContactRequest, 'contact', pk)


@login_required(login_url='/cabinet/login/')
def profile(request):
    if request.method == 'POST':
        from django.contrib import messages
        old_password = request.POST.get('old_password', '')
        new_password = request.POST.get('new_password', '')
        new_password2 = request.POST.get('new_password2', '')
        if not request.user.check_password(old_password):
            messages.error(request, 'Неверный текущий пароль')
        elif new_password != new_password2:
            messages.error(request, 'Пароли не совпадают')
        elif len(new_password) < 8:
            messages.error(request, 'Пароль должен быть не менее 8 символов')
        else:
            request.user.set_password(new_password)
            request.user.save()
            from django.contrib.auth import login
            login(request, request.user)
            messages.success(request, 'Пароль успешно изменён')
    return render(request, 'cabinet/profile.html', {'title': 'Профиль'})


@login_required(login_url='/cabinet/login/')
@require_POST
def upload_image(request):
    file = request.FILES.get('file')
    if not file:
        return JsonResponse({'error': 'Файл не передан'}, status=400)
    ext = os.path.splitext(file.name)[1].lower()
    if ext not in ('.jpg', '.jpeg', '.png', '.gif', '.webp', '.svg', '.bmp'):
        return JsonResponse({'error': 'Недопустимый формат'}, status=400)
    filename = f'{uuid.uuid4().hex}{ext}'
    rel_path = os.path.join('editor_uploads', filename)
    full_path = os.path.join(settings.MEDIA_ROOT, rel_path)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, 'wb') as dest:
        for chunk in file.chunks():
            dest.write(chunk)
    url = f'{settings.MEDIA_URL}{rel_path}'
    return JsonResponse({'ok': True, 'url': url})


# ─── Social Links CRUD ─────────────────────────────────────

@login_required(login_url='/cabinet/login/')
def sociallink_list(request):
    return _list_view(request, SocialLink, 'sociallink', 'Социальные сети',
                      ['name', 'url', 'order', 'is_visible'])


@login_required(login_url='/cabinet/login/')
def sociallink_form(request, pk=None):
    return _form_view(request, SocialLink, SocialLinkForm, 'sociallink',
                      'Редактировать ссылку' if pk else 'Новая ссылка', pk)


@login_required(login_url='/cabinet/login/')
def sociallink_delete(request, pk):
    return _delete_view(request, SocialLink, 'sociallink', pk)


# ─── Admin CRM Dashboard ─────────────────────────────────────

@login_required(login_url='/cabinet/login/')
def manager_dashboard(request):
    today = timezone.now().date()
    week_ago = today - timedelta(days=7)
    month_ago = today - timedelta(days=30)
    status_labels = dict(CALL_STATUSES)

    # ── General stats ──
    total_clients = Client.objects.filter(is_deleted=False).count()
    called = Client.objects.filter(calls__isnull=False, is_archived=False, is_deleted=False).distinct().count()
    uncalled = Client.objects.filter(~Q(calls__isnull=False), is_archived=False, is_deleted=False).count()
    in_progress = Call.objects.exclude(status__in=['refusal', 'completed']).count()
    archived = Client.objects.filter(is_archived=True, is_deleted=False).count()

    qs_status_counts = list(Call.objects.values('status').annotate(count=Count('id')).order_by('status'))
    count_by_status = {s['status']: s['count'] for s in qs_status_counts}
    status_counts = [
        {'status': code, 'count': count_by_status.get(code, 0)}
        for code, _ in CALL_STATUSES
    ]
    total_calls = sum(s['count'] for s in status_counts) or 1

    # ── Managers ──
    managers = User.objects.filter(profile__role='manager').order_by('last_name', 'first_name')
    manager_ids = list(managers.values_list('pk', flat=True))

    # Batch-load call stats per manager
    from django.db.models import Q as DQ
    call_stats = {
        mgr: (total, today, week, month, non_refusal)
        for mgr, total, today, week, month, non_refusal in
        Call.objects.filter(manager_id__in=manager_ids)
        .values('manager_id')
        .annotate(
            total=Count('id'),
            today=Count('id', filter=DQ(created_at__date=today)),
            week=Count('id', filter=DQ(created_at__gte=week_ago)),
            month=Count('id', filter=DQ(created_at__gte=month_ago)),
            non_refusal=Count('id', filter=~DQ(status='refusal')),
        )
        .values_list('manager_id', 'total', 'today', 'week', 'month', 'non_refusal')
    }
    # Normalize: {manager_id: {...}}
    call_data = {}
    for row in Call.objects.filter(manager_id__in=manager_ids).values('manager_id', 'status').annotate(cnt=Count('id')):
        mid = row['manager_id']
        if mid not in call_data:
            call_data[mid] = {}
        call_data[mid][row['status']] = row['cnt']

    # Batch-load client stats per manager
    assigned_stats = {
        mgr: (assigned, active)
        for mgr, assigned, active in
        Client.objects.filter(assigned_manager_id__in=manager_ids, is_deleted=False)
        .values('assigned_manager_id')
        .annotate(
            assigned=Count('id'),
            active=Count('id', filter=DQ(calls__isnull=False, is_archived=False) & ~DQ(calls__status__in=['refusal', 'completed'])),
        )
        .values_list('assigned_manager_id', 'assigned', 'active')
    }

    # Batch-load last activity per manager
    last_activities = dict(
        ClientActivity.objects.filter(user_id__in=manager_ids)
        .values('user_id')
        .annotate(last_created=Max('created_at'))
        .values_list('user_id', 'last_created')
    )

    manager_rows = []
    for m in managers:
        stats = call_stats.get(m.pk, (0, 0, 0, 0, 0))
        mgr_total = stats[0]
        calls_today = stats[1]
        calls_week = stats[2]
        calls_month = stats[3]
        non_refusal = stats[4]
        conversion = round(non_refusal / mgr_total * 100, 1) if mgr_total else 0

        assigned_total = assigned_stats.get(m.pk, (0, 0))[0]
        active_clients = assigned_stats.get(m.pk, (0, 0))[1]

        mgr_status_counts = call_data.get(m.pk, {})
        total_mgr_calls = sum(mgr_status_counts.values()) or 1
        status_breakdown = []
        for code, label in CALL_STATUSES:
            cnt = mgr_status_counts.get(code, 0)
            status_breakdown.append({
                'status': code,
                'label': label,
                'count': cnt,
                'pct': round(cnt / total_mgr_calls * 100, 1),
            })

        last_activity = last_activities.get(m.pk)

        manager_rows.append({
            'manager': m,
            'name': m.first_name or m.email.split('@')[0] if m.email else m.username,
            'calls_today': calls_today,
            'calls_week': calls_week,
            'calls_month': calls_month,
            'total_calls': mgr_total,
            'conversion': conversion,
            'active_clients': active_clients,
            'assigned_total': assigned_total,
            'status_breakdown': status_breakdown,
            'last_login': m.last_login,
            'last_activity': last_activity,
        })

    # ── Donut chart data ──
    status_colors = {
        'negotiation': '#c2410c', 'tz_creation': '#3b82f6', 'tz_approval': '#8b5cf6',
        'contract_signing': '#f59e0b', 'in_progress': '#22c55e', 'completed': '#16a34a',
        'refusal': '#ef4444',
    }
    def build_segments(counts, labels, total):
        segs = []
        for item in counts:
            pct = item['count'] / total if total else 0
            deg = pct * 360
            segs.append({
                'label': labels.get(item['status'], item['status']),
                'count': item['count'],
                'color': status_colors.get(item['status'], '#6b7280'),
                'degrees': deg,
                'pct': round(pct * 100, 1),
            })
        return sorted(segs, key=lambda s: -s['degrees'])

    status_segments = build_segments(status_counts, status_labels, total_calls)

    stats_items = [
        {'label': 'Прозвоненные', 'count': called, 'color': '#22c55e'},
        {'label': 'Непрозвоненные', 'count': uncalled, 'color': '#f59e0b'},
        {'label': 'В работе', 'count': in_progress, 'color': '#3b82f6'},
        {'label': 'В архиве', 'count': archived, 'color': '#6b7280'},
    ]
    total_stats = sum(s['count'] for s in stats_items) or 1
    stats_total_display = total_clients
    stats_segments = sorted(stats_items, key=lambda s: -s['count'])

    for seg in stats_segments:
        seg['pct'] = round(seg['count'] / total_stats * 100, 1)
        seg['degrees'] = seg['pct'] / 100 * 360

    def conic_gradient(segs):
        cumul = 0
        stops = []
        for s in segs:
            end = cumul + s['degrees']
            stops.append(f"{s['color']} {cumul}deg {end}deg")
            cumul = end
        return f"conic-gradient({', '.join(stops)})"

    status_conic = conic_gradient(status_segments)
    stats_conic = conic_gradient(stats_segments)

    # Today's activity feed
    activities_today = ClientActivity.objects.filter(created_at__date=today).select_related('user', 'client').order_by('-created_at')[:20]

    sidebar_counts = {
        'called': _last_status_clients('call_back', 'unavailable').filter(is_archived=False, is_deleted=False).count(),
        'in_progress': _last_status_clients('negotiation', 'tz_creation', 'tz_approval', 'contract_signing', 'in_progress').filter(is_archived=False, is_deleted=False).count(),
        'completed': _last_status_clients('completed').filter(is_archived=False, is_deleted=False).count(),
        'archive': Client.objects.filter(is_archived=True, is_deleted=False).count(),
        'deleted': Client.objects.filter(is_deleted=True).count(),
        'suggestions_unread': SuggestionMessage.objects.filter(
            author__is_superuser=False,
            is_read=False,
        ).count(),
        'info_unread': InfoTopic.objects.count() - InfoTopicRead.objects.filter(user=request.user).values('topic').distinct().count(),
    }

    return render(request, 'cabinet/admin_dashboard.html', {
        'title': 'Дашборд продаж',
        'total_clients': total_clients,
        'status_segments': status_segments,
        'status_conic': status_conic,
        'status_total': total_calls,
        'stats_segments': stats_segments,
        'stats_conic': stats_conic,
        'stats_total': total_stats,
        'stats_total_display': stats_total_display,
        'manager_rows': manager_rows,
        'activities_today': activities_today,
        'sidebar_counts': sidebar_counts,
    })


@login_required(login_url='/cabinet/login/')
def admin_suggestion_list(request):
    if not request.user.is_superuser:
        messages.error(request, 'Доступ запрещён')
        return redirect('cabinet:dashboard')

    open_pk = ''

    # Handle reply
    if request.method == 'POST':
        pk = request.POST.get('pk', '')
        action = request.POST.get('action', '')
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'

        if action == 'reply' and pk:
            sug = get_object_or_404(ManagerSuggestion, pk=pk)
            if not sug.is_closed:
                text = request.POST.get('message', '').strip()
                if text:
                    msg = SuggestionMessage.objects.create(
                        suggestion=sug, author=request.user, message=text
                    )
                    if sug.status == 'unread':
                        sug.status = 'read'
                        sug.save(update_fields=['status'])
                    from main.notification import broadcast_suggestion_message
                    broadcast_suggestion_message(msg)
                    if is_ajax:
                        from django.utils import timezone
                        t = timezone.localtime(msg.created_at)
                        return JsonResponse({
                            'ok': True,
                            'message': msg.message,
                            'author': msg.author.get_full_name() or msg.author.email,
                            'is_superuser': msg.author.is_superuser,
                            'time': t.strftime('%H:%M'),
                            'pk': msg.pk,
                        })
            open_pk = pk
        elif action == 'close' and pk:
            sug = get_object_or_404(ManagerSuggestion, pk=pk)
            sug.is_closed = True
            sug.save(update_fields=['is_closed'])
            from main.notification import broadcast_status_change
            broadcast_status_change(sug)
            messages.success(request, 'Топик закрыт')
            open_pk = pk
        elif action == 'reopen' and pk:
            sug = get_object_or_404(ManagerSuggestion, pk=pk)
            sug.is_closed = False
            sug.save(update_fields=['is_closed'])
            from main.notification import broadcast_status_change
            broadcast_status_change(sug)
            messages.success(request, 'Топик открыт')
            open_pk = pk
        elif action == 'delete' and pk:
            sug = get_object_or_404(ManagerSuggestion, pk=pk)
            from main.notification import broadcast_suggestion_delete
            broadcast_suggestion_delete(sug)
            sug.delete()
            if is_ajax:
                return JsonResponse({'ok': True})
            messages.success(request, 'Топик удалён')
            url = reverse('cabinet:admin_suggestion_list')
            return redirect(url)

        if is_ajax:
            return JsonResponse({'ok': False}, status=400)
        url = reverse('cabinet:admin_suggestion_list')
        if open_pk:
            url += f'?open={open_pk}'
        return redirect(url)

    qs = ManagerSuggestion.objects.select_related('manager', 'admin').prefetch_related('messages', 'messages__author').all()
    search = request.GET.get('q', '').strip()
    if search:
        qs = qs.filter(
            Q(message__icontains=search) |
            Q(admin_comment__icontains=search) |
            Q(manager__email__icontains=search) |
            Q(manager__first_name__icontains=search) |
            Q(manager__last_name__icontains=search)
        )
    paginator = Paginator(qs, 15)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    suggestions = list(page_obj.object_list)
    for s in suggestions:
        s.has_unread = any(
            not m.is_read and not m.author.is_superuser
            for m in s.messages.all()
        ) or s.status == 'unread'
    return render(request, 'cabinet/suggestion_list.html', {
        'title': 'Обратная связь — Предложения менеджеров',
        'suggestions': suggestions,
        'page_obj': page_obj,
        'search': search,
    })


@login_required(login_url='/cabinet/login/')
def suggestion_mark_read(request):
    if request.method != 'POST':
        return JsonResponse({'ok': False}, status=405)
    pk = request.POST.get('pk', '')
    if not pk:
        return JsonResponse({'ok': False}, status=400)
    try:
        sug = ManagerSuggestion.objects.get(pk=pk)
        if request.user.is_superuser or sug.manager == request.user:
            SuggestionMessage.objects.filter(
                suggestion=sug,
                is_read=False
            ).exclude(author=request.user).update(is_read=True)
            from main.notification import _clear_sidebar_cache
            _clear_sidebar_cache(request.user.pk)
            if request.user.is_superuser and sug.status == 'unread':
                sug.status = 'read'
                sug.save(update_fields=['status'])
                from main.notification import broadcast_status_change
                broadcast_status_change(sug)
            if request.user.is_superuser:
                unread_count = SuggestionMessage.objects.filter(author__is_superuser=False, is_read=False).count()
            else:
                unread_count = SuggestionMessage.objects.filter(suggestion__manager=request.user, author__is_superuser=True, is_read=False).count()
            return JsonResponse({'ok': True, 'unread_count': unread_count})
    except ManagerSuggestion.DoesNotExist:
        pass
    return JsonResponse({'ok': False}, status=404)


@login_required(login_url='/cabinet/login/')
def admin_suggestion_action(request, pk):
    if request.method != 'POST':
        return redirect('cabinet:admin_suggestion_list')
    if not request.user.is_superuser:
        messages.error(request, 'Доступ запрещён')
        return redirect('cabinet:dashboard')
    suggestion = get_object_or_404(ManagerSuggestion, pk=pk)
    status = request.POST.get('status', '')
    comment = request.POST.get('admin_comment', '').strip()
    reply_text = request.POST.get('message', '').strip()
    if status in dict(ManagerSuggestion.STATUS_CHOICES):
        suggestion.status = status
    suggestion.admin = request.user
    if comment:
        suggestion.admin_comment = comment
    suggestion.save()
    # Mark all manager messages as read
    SuggestionMessage.objects.filter(
        suggestion=suggestion,
        author__is_superuser=False,
        is_read=False
    ).update(is_read=True)
    from main.notification import broadcast_status_change
    broadcast_status_change(suggestion)
    if reply_text:
        msg = SuggestionMessage.objects.create(
            suggestion=suggestion, author=request.user, message=reply_text
        )
        from main.notification import broadcast_suggestion_message
        broadcast_suggestion_message(msg)
    messages.success(request, 'Статус предложения обновлён')
    return redirect('cabinet:admin_suggestion_list')



