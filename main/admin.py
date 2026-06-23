from django import forms
from django.contrib import admin
from django.db.models import Count
from django.template.response import TemplateResponse
from django.urls import path
from django.utils import timezone
from django.utils.safestring import mark_safe
from datetime import timedelta

from .models import (
    SiteSetting, HeroSection, NavLink, Service, Project,
    Product, ProductMetric, ProductDetail, Principle,
    BlogPost, PageView, ContactRequest,
)


from .forms import ColorInput, DatalistInput

ColorInputWidget = ColorInput
DatalistWidget = DatalistInput


class HideOnCreateMixin:
    def get_form(self, request, obj=None, **kwargs):
        if obj is None:
            exclude = list(kwargs.get('exclude', []))
            exclude += list(getattr(self, 'hide_on_create', []))
            kwargs['exclude'] = exclude
        return super().get_form(request, obj, **kwargs)

admin.site.site_header = 'Ludera — Панель управления'
admin.site.site_title = 'Ludera Admin'
admin.site.index_title = 'Добро пожаловать в панель управления Ludera'


# ─── Статистика в главную админку ─────────────────────────────

original_index = admin.site.index


def stats_index(request, extra_context=None):
    extra_context = extra_context or {}
    today = timezone.now().date()
    week_ago = today - timedelta(days=7)
    extra_context['total_views'] = PageView.objects.count()
    extra_context['today_views'] = PageView.objects.filter(timestamp__date=today).count()
    extra_context['week_views'] = PageView.objects.filter(timestamp__date__gte=week_ago).count()
    extra_context['unread_contacts'] = ContactRequest.objects.filter(is_read=False).count()
    extra_context['total_projects'] = Project.objects.count()
    extra_context['total_blog'] = BlogPost.objects.count()
    return original_index(request, extra_context)


admin.site.index = stats_index


# ─── Дашборд ──────────────────────────────────────────────────

original_get_urls = admin.site.get_urls


def dashboard_urls(self):
    urls = original_get_urls()
    custom = [
        path('dashboard/', self.admin_view(self.dashboard_view), name='dashboard'),
    ]
    return custom + urls


def dashboard_view(request):
    today = timezone.now().date()
    week_ago = today - timedelta(days=7)
    total_views = PageView.objects.count()
    today_views = PageView.objects.filter(timestamp__date=today).count()
    week_views = PageView.objects.filter(timestamp__date__gte=week_ago).count()
    top_pages = (
        PageView.objects
        .values('url')
        .annotate(count=Count('id'))
        .order_by('-count')[:10]
    )
    recent_contacts = ContactRequest.objects.order_by('-created_at')[:5]
    unread_contacts = ContactRequest.objects.filter(is_read=False).count()
    return TemplateResponse(request, 'admin/dashboard.html', {
        'total_views': total_views,
        'today_views': today_views,
        'week_views': week_views,
        'top_pages': top_pages,
        'recent_contacts': recent_contacts,
        'unread_contacts': unread_contacts,
        'title': 'Дашборд',
    })


admin.site.get_urls = dashboard_urls.__get__(admin.site, type(admin.site))
admin.site.dashboard_view = dashboard_view


# ─── Регистрация моделей ──────────────────────────────────────

@admin.register(SiteSetting)
class SiteSettingAdmin(admin.ModelAdmin):
    list_display = ['email', 'meta_title']
    fieldsets = [
        ('Контакты', {'fields': ['email']}),
        ('Футер', {'fields': ['footer_description', 'copyright_text']}),
        ('CTA-блок', {'fields': ['cta_title', 'cta_description', 'cta_button_text']}),
        ('SEO', {'fields': ['meta_title', 'meta_description']}),
    ]

    def has_add_permission(self, request):
        return SiteSetting.objects.count() == 0


@admin.register(HeroSection)
class HeroSectionAdmin(admin.ModelAdmin):
    list_display = ['tagline', 'title', 'is_active']
    list_editable = ['is_active']


@admin.register(NavLink)
class NavLinkAdmin(admin.ModelAdmin):
    list_display = ['title', 'url', 'order', 'is_visible']
    list_editable = ['order', 'is_visible']


@admin.register(Service)
class ServiceAdmin(HideOnCreateMixin, admin.ModelAdmin):
    hide_on_create = ['created_at']
    list_display = ['title', 'pill_number', 'pill_label', 'order', 'created_at']
    list_editable = ['order']
    fieldsets = [
        ('Основное', {'fields': ['title', 'slug', 'description', 'content']}),
        ('Пилл', {'fields': ['pill_number', 'pill_label']}),
        ('Панель', {'fields': ['panel_config']}),
        ('Порядок', {'fields': ['order']}),
        ('Даты', {'fields': ['created_at']}),
    ]


@admin.register(Project)
class ProjectAdmin(HideOnCreateMixin, admin.ModelAdmin):
    hide_on_create = ['created_at']
    list_display = ['title', 'status', 'accent_color', 'order', 'is_visible', 'created_at']
    list_editable = ['order', 'is_visible']
    list_filter = ['is_visible']
    search_fields = ['title', 'description']
    fieldsets = [
        ('Основное', {'fields': ['title', 'slug', 'description', 'content', 'image']}),
        ('Статус', {'fields': ['status']}),
        ('Теги', {'fields': ['tag1', 'tag2']}),
        ('Цвет', {'fields': ['accent_color']}),
        ('Порядок', {'fields': ['order', 'is_visible']}),
        ('Даты', {'fields': ['created_at']}),
    ]

    def formfield_for_dbfield(self, db_field, **kwargs):
        if db_field.name == 'accent_color':
            kwargs['widget'] = ColorInputWidget
        return super().formfield_for_dbfield(db_field, **kwargs)


class ProductMetricInline(admin.TabularInline):
    model = ProductMetric
    extra = 1


class ProductDetailInline(admin.TabularInline):
    model = ProductDetail
    extra = 1


@admin.register(Product)
class ProductAdmin(HideOnCreateMixin, admin.ModelAdmin):
    hide_on_create = ['created_at']
    list_display = ['title', 'order', 'is_visible', 'created_at']
    list_editable = ['order', 'is_visible']
    inlines = [ProductMetricInline, ProductDetailInline]
    search_fields = ['title', 'description']
    fieldsets = [
        ('Основное', {'fields': ['title', 'slug', 'subtitle', 'description', 'content']}),
        ('Цвета', {'fields': ['accent', 'accent_rgb']}),
        ('Бейдж', {'fields': ['badge_text']}),
        ('Порядок', {'fields': ['order', 'is_visible']}),
        ('Даты', {'fields': ['created_at']}),
    ]

    def formfield_for_dbfield(self, db_field, **kwargs):
        if db_field.name == 'accent':
            kwargs['widget'] = ColorInputWidget
        return super().formfield_for_dbfield(db_field, **kwargs)


@admin.register(Principle)
class PrincipleAdmin(admin.ModelAdmin):
    list_display = ['title', 'order']
    list_editable = ['order']


@admin.register(BlogPost)
class BlogPostAdmin(HideOnCreateMixin, admin.ModelAdmin):
    hide_on_create = ['created_at', 'date']
    list_display = ['title', 'category', 'date', 'author', 'is_visible']
    list_editable = ['is_visible']
    list_filter = ['category', 'is_visible']
    search_fields = ['title', 'description']
    readonly_fields = ['author_initials']
    fieldsets = [
        ('Основное', {'fields': ['title', 'slug', 'description', 'content', 'image']}),
        ('Мета', {'fields': ['category', 'category_color', 'date', 'reading_time']}),
        ('Автор', {'fields': ['author', 'author_initials']}),
        ('Дизайн', {'fields': ['gradient_start', 'gradient_end']}),
        ('Публикация', {'fields': ['is_visible']}),
        ('Даты', {'fields': ['created_at']}),
    ]

    def formfield_for_dbfield(self, db_field, **kwargs):
        if db_field.name in ('category_color', 'gradient_start', 'gradient_end'):
            kwargs['widget'] = ColorInputWidget
        if db_field.name == 'category':
            existing = list(BlogPost.objects.values_list('category', flat=True).distinct())
            kwargs['widget'] = DatalistWidget(existing)
        return super().formfield_for_dbfield(db_field, **kwargs)


@admin.register(PageView)
class PageViewAdmin(admin.ModelAdmin):
    list_display = ['url', 'timestamp', 'ip_address']
    list_filter = ['timestamp']
    readonly_fields = ['url', 'user_agent', 'ip_address', 'session_key', 'timestamp']
    date_hierarchy = 'timestamp'

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False


@admin.register(ContactRequest)
class ContactRequestAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'created_at', 'is_read']
    list_editable = ['is_read']
    list_filter = ['is_read', 'created_at']
    readonly_fields = ['name', 'email', 'message', 'created_at']
    date_hierarchy = 'created_at'

    def has_add_permission(self, request):
        return False
