from io import StringIO
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponse, HttpResponseRedirect
from django.utils.xmlutils import SimplerXMLGenerator
from django.views.decorators.http import require_POST
from django.core.cache import cache
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string

from .models import (
    SiteSetting, HeroSection, NavLink, Service, Project,
    Product, Principle, BlogPost, PageView,
    ContactRequest, SocialLink,
)


def index(request):
    hero = HeroSection.get_active()
    nav_links = NavLink.objects.filter(is_visible=True)
    services = Service.objects.all()
    projects = Project.objects.filter(is_visible=True)
    products = Product.objects.filter(is_visible=True)
    principles = Principle.objects.all()
    blog_posts = BlogPost.objects.filter(is_visible=True)
    settings = SiteSetting.objects.first()
    social_links = SocialLink.objects.filter(is_visible=True).order_by('order')

    context = {
        'hero': hero,
        'nav_links': nav_links,
        'services': services,
        'projects': projects,
        'products': products,
        'principles': principles,
        'footer_products': products,
        'blog_posts': blog_posts,
        'settings': settings,
        'social_links': social_links,
    }

    return render(request, 'main/index.html', context)


def _common_context(request):
    return {
        'nav_links': NavLink.objects.filter(is_visible=True),
        'footer_products': Product.objects.filter(is_visible=True),
        'settings': SiteSetting.objects.first(),
        'social_links': SocialLink.objects.filter(is_visible=True).order_by('order'),
    }


def _get_prev_next(qs, obj):
    if not qs:
        return None, None
    idx = None
    for i, o in enumerate(qs):
        if o.pk == obj.pk:
            idx = i
            break
    if idx is None:
        return None, None
    prev = qs[idx - 1] if idx > 0 else None
    next_obj = qs[idx + 1] if idx < len(qs) - 1 else None
    return prev, next_obj


def blog_detail(request, slug):
    obj = get_object_or_404(BlogPost, slug=slug)
    qs = list(BlogPost.objects.filter(is_visible=True))
    prev, next_obj = _get_prev_next(qs, obj)
    ctx = {'obj': obj, 'prev': prev, 'next': next_obj, 'detail_type': 'blog'}
    ctx.update(_common_context(request))
    return render(request, 'main/detail.html', ctx)


def project_detail(request, slug):
    obj = get_object_or_404(Project, slug=slug)
    qs = list(Project.objects.filter(is_visible=True))
    prev, next_obj = _get_prev_next(qs, obj)
    ctx = {'obj': obj, 'prev': prev, 'next': next_obj, 'detail_type': 'project'}
    ctx.update(_common_context(request))
    return render(request, 'main/detail.html', ctx)


def service_detail(request, slug):
    obj = get_object_or_404(Service, slug=slug)
    qs = list(Service.objects.all())
    prev, next_obj = _get_prev_next(qs, obj)
    ctx = {'obj': obj, 'prev': prev, 'next': next_obj, 'detail_type': 'service'}
    ctx.update(_common_context(request))
    return render(request, 'main/detail.html', ctx)


def product_detail(request, slug):
    obj = get_object_or_404(Product, slug=slug)
    qs = list(Product.objects.filter(is_visible=True))
    prev, next_obj = _get_prev_next(qs, obj)
    ctx = {'obj': obj, 'prev': prev, 'next': next_obj, 'detail_type': 'product'}
    ctx.update(_common_context(request))
    return render(request, 'main/detail.html', ctx)


def contact_submit(request):
    if request.method == 'GET':
        return redirect('/#contact')
    ip = request.META.get('REMOTE_ADDR', '')
    rate_key = f'contact_rate:{ip}'
    count = cache.get(rate_key, 0)
    if count > 5:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'status': 'error', 'message': 'Слишком много запросов'}, status=429)
        return render(request, 'main/contact_rate_limit.html', _common_context(request), status=429)
    cache.set(rate_key, count + 1, 3600)

    name = request.POST.get('name', '').strip()
    email = request.POST.get('email', '').strip()
    message = request.POST.get('message', '').strip()
    if email:
        ContactRequest.objects.create(name=name, email=email, message=message)

        subject = f'Новая заявка с Ludera — {name}'
        html_message = render_to_string('main/email/contact_notification.html', {
            'name': name,
            'email': email,
            'message': message,
        })
        try:
            send_mail(
                subject,
                f'Имя: {name}\nEmail: {email}\n\n{message}',
                settings.DEFAULT_FROM_EMAIL,
                [settings.OWNER_EMAIL],
                html_message=html_message,
                fail_silently=False,
            )
        except Exception:
            pass

        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'status': 'ok'})
        return render(request, 'main/contact_success.html', _common_context(request))
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'status': 'error'}, status=400)
    return redirect('/#contact')


def sitemap_xml(request):
    base_url = f'{request.scheme}://{request.get_host()}'

    stream = StringIO()
    xml = SimplerXMLGenerator(stream, 'utf-8')
    xml.startDocument()
    xml.startElement('urlset', {'xmlns': 'http://www.sitemaps.org/schemas/sitemap/0.9'})

    xml.startElement('url', {})
    xml.addQuickElement('loc', base_url + '/')
    xml.addQuickElement('changefreq', 'weekly')
    xml.addQuickElement('priority', '1.0')
    xml.endElement('url')

    for service in Service.objects.all():
        xml.startElement('url', {})
        xml.addQuickElement('loc', f'{base_url}{service.get_absolute_url()}')
        xml.addQuickElement('changefreq', 'monthly')
        xml.addQuickElement('priority', '0.8')
        xml.endElement('url')

    for project in Project.objects.filter(is_visible=True):
        xml.startElement('url', {})
        xml.addQuickElement('loc', f'{base_url}{project.get_absolute_url()}')
        xml.addQuickElement('changefreq', 'monthly')
        xml.addQuickElement('priority', '0.7')
        xml.endElement('url')

    for product in Product.objects.filter(is_visible=True):
        xml.startElement('url', {})
        xml.addQuickElement('loc', f'{base_url}{product.get_absolute_url()}')
        xml.addQuickElement('changefreq', 'monthly')
        xml.addQuickElement('priority', '0.8')
        xml.endElement('url')

    for post in BlogPost.objects.filter(is_visible=True):
        xml.startElement('url', {})
        xml.addQuickElement('loc', f'{base_url}{post.get_absolute_url()}')
        xml.addQuickElement('lastmod', post.updated_at.strftime('%Y-%m-%d'))
        xml.addQuickElement('changefreq', 'weekly')
        xml.addQuickElement('priority', '0.6')
        xml.endElement('url')

    xml.endElement('urlset')

    return HttpResponse(stream.getvalue(), content_type='application/xml')


def ecosystem_test(request):
    return render(request, 'main/ecosystem_test.html')


def privacy_policy(request):
    ctx = _common_context(request)
    return render(request, 'main/privacy.html', ctx)


def robots_txt(request):
    lines = [
        'User-agent: *',
        'Allow: /',
        'Disallow: /cabinet/',
        'Disallow: /account/',
        'Disallow: /admin/',
        'Disallow: /accounts/',
        'Disallow: /ecosystem-test/',
        '',
        '# Яндекс.Вебмастер',
        'User-agent: Yandex',
        'Allow: /',
        'Disallow: /cabinet/',
        'Disallow: /account/',
        'Disallow: /admin/',
        'Disallow: /accounts/',
        '',
        'Sitemap: {}://{}/sitemap.xml'.format(request.scheme, request.get_host),
    ]
    return HttpResponse('\n'.join(lines), content_type='text/plain')


def handler404(request, exception):
    ctx = _common_context(request)
    return render(request, 'main/404.html', ctx, status=404)


def favicon_ico(request):
    return HttpResponseRedirect('/static/images/favicon.svg')
