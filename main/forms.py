from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.utils.safestring import mark_safe

from .models import (
    Service, Project, Product, ProductMetric, ProductDetail,
    BlogPost, SiteSetting, HeroSection, NavLink, Principle,
    ContactRequest, SocialLink,
)
from users.models import Goods, GoodsFile


class ColorInput(forms.TextInput):
    input_type = 'color'

    def __init__(self, attrs=None):
        default_attrs = {'style': 'width: 60px; height: 40px; cursor: pointer; padding: 2px;'}
        if attrs:
            default_attrs.update(attrs)
        super().__init__(default_attrs)


class DatalistInput(forms.TextInput):
    def __init__(self, choices_list, attrs=None):
        self.choices_list = choices_list
        super().__init__(attrs)

    def render(self, name, value, attrs=None, renderer=None):
        if attrs is None:
            attrs = {}
        list_id = f'{name}_datalist'
        attrs['list'] = list_id
        attrs.setdefault('placeholder', 'Выберите или введите новую')
        html = super().render(name, value, attrs, renderer)
        options = ''.join(
            f'<option value="{c}">' for c in self.choices_list
        )
        html += f'<datalist id="{list_id}">{options}</datalist>'
        return mark_safe(html)


class LoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Логин'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Пароль'}))


PANEL_COLORS = [
    ('green', 'Зелёный'),
    ('teal', 'Бирюзовый'),
    ('amber', 'Янтарный'),
    ('red', 'Красный'),
]


class ServiceForm(forms.ModelForm):
    panel_fields = [
        'chart_badge', 'chart_label', 'chart_bars',
        'metric1_label', 'metric1_value', 'metric1_suffix', 'metric1_change', 'metric1_color',
        'metric2_label', 'metric2_value', 'metric2_suffix', 'metric2_change', 'metric2_color',
        'timeline_label', 'timeline_progress', 'timeline_total', 'timeline_done', 'timeline_badge',
        'lead_label', 'lead_channels', 'lead_pills',
        'footer_text', 'footer_dots',
    ]

    chart_badge = forms.CharField(label='Бейдж', required=False, max_length=50,
        widget=forms.TextInput(attrs={'placeholder': '↓ 12%'}))
    chart_label = forms.CharField(label='Заголовок графика', required=False, max_length=100,
        widget=forms.TextInput(attrs={'placeholder': 'Sales Pipeline'}))
    chart_bars = forms.CharField(label='Высота столбцов (через запятую)', required=False, max_length=50,
        widget=forms.TextInput(attrs={'placeholder': '45, 55, 70, 85, 65, 90'}))

    metric1_label = forms.CharField(label='Название метрики 1', required=False, max_length=50,
        widget=forms.TextInput(attrs={'placeholder': 'Конверсия'}))
    metric1_value = forms.IntegerField(label='Значение метрики 1', required=False, initial=0,
        widget=forms.NumberInput(attrs={'placeholder': '68'}))
    metric1_suffix = forms.CharField(label='Суффикс метрики 1', required=False, max_length=10,
        widget=forms.TextInput(attrs={'placeholder': '%'}))
    metric1_change = forms.CharField(label='Изменение метрики 1', required=False, max_length=100,
        widget=forms.TextInput(attrs={'placeholder': '+14% за месяц'}))
    metric1_color = forms.ChoiceField(label='Цвет метрики 1', choices=PANEL_COLORS, required=False, initial='green')

    metric2_label = forms.CharField(label='Название метрики 2', required=False, max_length=50,
        widget=forms.TextInput(attrs={'placeholder': 'Активные клиенты'}))
    metric2_value = forms.IntegerField(label='Значение метрики 2', required=False, initial=0,
        widget=forms.NumberInput(attrs={'placeholder': '128'}))
    metric2_suffix = forms.CharField(label='Суффикс метрики 2', required=False, max_length=10,
        widget=forms.TextInput(attrs={'placeholder': ''}))
    metric2_change = forms.CharField(label='Изменение метрики 2', required=False, max_length=100,
        widget=forms.TextInput(attrs={'placeholder': '92% retention'}))
    metric2_color = forms.ChoiceField(label='Цвет метрики 2', choices=PANEL_COLORS, required=False, initial='green')

    timeline_label = forms.CharField(label='Заголовок таймлайна', required=False, max_length=100,
        widget=forms.TextInput(attrs={'placeholder': 'Воронка продаж'}))
    timeline_progress = forms.IntegerField(label='Прогресс таймлайна %', required=False, initial=0,
        widget=forms.NumberInput(attrs={'placeholder': '75'}))
    timeline_total = forms.IntegerField(label='Всего этапов', required=False, initial=8,
        widget=forms.NumberInput(attrs={'placeholder': '8'}))
    timeline_done = forms.IntegerField(label='Завершено этапов', required=False, initial=0,
        widget=forms.NumberInput(attrs={'placeholder': '6'}))
    timeline_badge = forms.CharField(label='Бейдж таймлайна', required=False, max_length=50,
        widget=forms.TextInput(attrs={'placeholder': '6/8 этапов'}))

    lead_label = forms.CharField(label='Заголовок источников', required=False, max_length=100,
        widget=forms.TextInput(attrs={'placeholder': 'Источники лидов'}))
    lead_channels = forms.IntegerField(label='Количество каналов', required=False, initial=0,
        widget=forms.NumberInput(attrs={'placeholder': '5'}))
    lead_pills = forms.CharField(label='Цвета пилл (через запятую)', required=False, max_length=200,
        widget=forms.TextInput(attrs={'placeholder': 'green, teal, green, amber, green'}))

    footer_text = forms.CharField(label='Текст в футере панели', required=False, max_length=200,
        widget=forms.TextInput(attrs={'placeholder': 'Средний чек: 45 000 ₽'}))
    footer_dots = forms.CharField(label='Цвета точек (через запятую)', required=False, max_length=200,
        widget=forms.TextInput(attrs={'placeholder': 'green, green, green, amber, green'}))

    class Meta:
        model = Service
        fields = ['title', 'description', 'content', 'pill_number', 'pill_label',
                  'order', 'created_at']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'content': forms.Textarea(attrs={'class': 'rich-editor', 'rows': 10}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        instance = kwargs.get('instance')
        if not instance or not instance.pk:
            self.fields.pop('created_at', None)
        if self.instance and self.instance.panel_config:
            cfg = self.instance.panel_config
            self.fields['chart_badge'].initial = cfg.get('badge', '')
            self.fields['chart_label'].initial = cfg.get('chart_label', '')
            self.fields['chart_bars'].initial = ', '.join(str(v) for v in cfg.get('chart', []))
            self.fields['metric1_label'].initial = cfg.get('metric1_label', '')
            self.fields['metric1_value'].initial = cfg.get('metric1_value', 0)
            self.fields['metric1_suffix'].initial = cfg.get('metric1_suffix', '')
            self.fields['metric1_change'].initial = cfg.get('metric1_change', '')
            self.fields['metric1_color'].initial = cfg.get('metric1_color', 'green')
            self.fields['metric2_label'].initial = cfg.get('metric2_label', '')
            self.fields['metric2_value'].initial = cfg.get('metric2_value', 0)
            self.fields['metric2_suffix'].initial = cfg.get('metric2_suffix', '')
            self.fields['metric2_change'].initial = cfg.get('metric2_change', '')
            self.fields['metric2_color'].initial = cfg.get('metric2_color', 'green')
            self.fields['timeline_label'].initial = cfg.get('timeline_label', '')
            self.fields['timeline_progress'].initial = cfg.get('timeline_progress', 0)
            self.fields['timeline_total'].initial = cfg.get('timeline_total', 8)
            self.fields['timeline_done'].initial = cfg.get('timeline_done', 0)
            self.fields['timeline_badge'].initial = cfg.get('timeline_badge', '')
            self.fields['lead_label'].initial = cfg.get('lead_label', '')
            self.fields['lead_channels'].initial = cfg.get('lead_channels', 0)
            self.fields['lead_pills'].initial = ', '.join(cfg.get('lead_pills', []))
            self.fields['footer_text'].initial = cfg.get('footer_text', '')
            self.fields['footer_dots'].initial = ', '.join(cfg.get('footer_dots', []))

    def clean_chart_bars(self):
        val = self.cleaned_data.get('chart_bars', '')
        if val:
            parts = [p.strip() for p in val.split(',') if p.strip()]
            return [min(max(int(p), 0), 100) for p in parts if p.isdigit()]
        return []

    def clean_lead_pills(self):
        val = self.cleaned_data.get('lead_pills', '')
        if val:
            colors = [c.strip() for c in val.split(',') if c.strip()]
            valid = {'green', 'teal', 'amber', 'red'}
            return [c for c in colors if c in valid]
        return []

    def clean_footer_dots(self):
        val = self.cleaned_data.get('footer_dots', '')
        if val:
            colors = [c.strip() for c in val.split(',') if c.strip()]
            valid = {'green', 'teal', 'amber', 'red'}
            return [c for c in colors if c in valid]
        return []

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.panel_config = {
            'badge': self.cleaned_data.get('chart_badge', ''),
            'chart_label': self.cleaned_data.get('chart_label', ''),
            'chart': self.cleaned_data.get('chart_bars', []),
            'metric1_label': self.cleaned_data.get('metric1_label', ''),
            'metric1_value': self.cleaned_data.get('metric1_value', 0) or 0,
            'metric1_suffix': self.cleaned_data.get('metric1_suffix', ''),
            'metric1_change': self.cleaned_data.get('metric1_change', ''),
            'metric1_color': self.cleaned_data.get('metric1_color', 'green'),
            'metric2_label': self.cleaned_data.get('metric2_label', ''),
            'metric2_value': self.cleaned_data.get('metric2_value', 0) or 0,
            'metric2_suffix': self.cleaned_data.get('metric2_suffix', ''),
            'metric2_change': self.cleaned_data.get('metric2_change', ''),
            'metric2_color': self.cleaned_data.get('metric2_color', 'green'),
            'timeline_label': self.cleaned_data.get('timeline_label', ''),
            'timeline_progress': self.cleaned_data.get('timeline_progress', 0) or 0,
            'timeline_total': self.cleaned_data.get('timeline_total', 8) or 8,
            'timeline_done': self.cleaned_data.get('timeline_done', 0) or 0,
            'timeline_badge': self.cleaned_data.get('timeline_badge', ''),
            'lead_label': self.cleaned_data.get('lead_label', ''),
            'lead_channels': self.cleaned_data.get('lead_channels', 0) or 0,
            'lead_pills': self.cleaned_data.get('lead_pills', []),
            'footer_text': self.cleaned_data.get('footer_text', ''),
            'footer_dots': self.cleaned_data.get('footer_dots', []),
        }
        if commit:
            instance.save()
        return instance


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['title', 'status', 'description', 'content', 'image',
                  'tag1', 'tag2', 'accent_color', 'order', 'is_visible', 'created_at']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'content': forms.Textarea(attrs={'class': 'rich-editor', 'rows': 10}),
            'accent_color': ColorInput,
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        instance = kwargs.get('instance')
        if not instance or not instance.pk:
            self.fields.pop('created_at', None)
        existing = sorted(
            set(
                Project.objects.values_list('tag1', flat=True).distinct()
            ) |
            set(
                Project.objects.values_list('tag2', flat=True).distinct()
            )
        )
        existing = [t for t in existing if t]
        self.fields['tag1'].widget = DatalistInput(existing)
        self.fields['tag2'].widget = DatalistInput(existing)


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['title', 'subtitle', 'description', 'content',
                  'accent', 'accent_rgb', 'badge_text',
                  'order', 'is_visible', 'created_at']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'content': forms.Textarea(attrs={'class': 'rich-editor', 'rows': 10}),
            'accent': ColorInput,
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        instance = kwargs.get('instance')
        if not instance or not instance.pk:
            self.fields.pop('created_at', None)


class ProductMetricForm(forms.ModelForm):
    class Meta:
        model = ProductMetric
        fields = ['label', 'value']


class ProductDetailForm(forms.ModelForm):
    class Meta:
        model = ProductDetail
        fields = ['text']


class BlogPostForm(forms.ModelForm):
    class Meta:
        model = BlogPost
        fields = ['title', 'description', 'content', 'image', 'category', 'category_color',
                  'date', 'reading_time', 'author',
                  'gradient_start', 'gradient_end', 'created_at']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'content': forms.Textarea(attrs={'class': 'rich-editor', 'rows': 15}),
            'date': forms.DateInput(attrs={'type': 'date'}),
            'category_color': ColorInput,
            'gradient_start': ColorInput,
            'gradient_end': ColorInput,
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        instance = kwargs.get('instance')
        if not instance or not instance.pk:
            self.fields.pop('created_at', None)
            self.fields.pop('date', None)
        existing = list(BlogPost.objects.values_list('category', flat=True).distinct())
        self.fields['category'].widget = DatalistInput(existing)


SITESETTING_FIELDS = {
    'hero': ['hero_tagline', 'hero_title', 'hero_description', 'hero_cta_text', 'hero_cta_link'],
    'header': ['header_cta_text', 'header_login_text', 'header_account_text'],
    'services': ['services_section_title', 'services_detail_text'],
    'projects': ['projects_section_title', 'projects_section_subtitle'],
    'products': ['products_section_title', 'products_section_subtitle', 'products_detail_text'],
    'about': ['about_section_title', 'about_section_subtitle'],
    'blog': ['blog_section_title', 'blog_section_subtitle', 'blog_read_text', 'blog_filter_all', 'blog_empty_text'],
    'ecosystem': ['ecosystem_badge', 'ecosystem_title', 'ecosystem_subtitle',
                   'ecosystem_terminal_title', 'ecosystem_flow_title',
                   'ecosystem_client_label', 'ecosystem_client_badge',
                   'ecosystem_analysis_label',
                   'ecosystem_custom_label',
                   'ecosystem_ready_label',
                   'ecosystem_support_label'],
    'cta': ['cta_title', 'cta_description'],
    'contact_form': ['contact_name_placeholder', 'contact_email_placeholder',
                     'contact_message_placeholder', 'contact_submit_text', 'contact_success_text'],
    'footer': ['footer_cta_label', 'footer_company_title', 'footer_products_title',
               'footer_description', 'copyright_text', 'email'],
    'footer_ip': ['footer_ip_name', 'footer_ip_inn', 'footer_ip_ogrnip', 'footer_ip_address'],
    'seo': ['meta_title', 'meta_description', 'meta_keywords', 'og_image', 'yandex_verification', 'google_verification'],
}


class SiteSettingForm(forms.ModelForm):
    panel_fields = []

    class Meta:
        model = SiteSetting
        fields = sum(SITESETTING_FIELDS.values(), [])
        widgets = {
            'footer_description': forms.Textarea(attrs={'rows': 3}),
            'meta_description': forms.Textarea(attrs={'rows': 3}),
            'meta_keywords': forms.Textarea(attrs={'rows': 2}),
            'cta_description': forms.Textarea(attrs={'rows': 3}),
            'hero_description': forms.Textarea(attrs={'rows': 3}),
            'contact_success_text': forms.Textarea(attrs={'rows': 2}),
            'contact_message_placeholder': forms.Textarea(attrs={'rows': 2}),
            'footer_ip_address': forms.Textarea(attrs={'rows': 2}),
        }


class HeroSectionForm(forms.ModelForm):
    class Meta:
        model = HeroSection
        fields = ['tagline', 'title', 'description', 'cta_text', 'cta_link', 'is_active']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }


class NavLinkForm(forms.ModelForm):
    class Meta:
        model = NavLink
        fields = ['title', 'url', 'order', 'is_visible']


class PrincipleForm(forms.ModelForm):
    class Meta:
        model = Principle
        fields = ['title', 'description', 'order']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }


class ContactRequestForm(forms.ModelForm):
    class Meta:
        model = ContactRequest
        fields = ['name', 'email', 'message', 'is_read']
        widgets = {
            'message': forms.Textarea(attrs={'rows': 3}),
        }


class GoodsForm(forms.ModelForm):
    class Meta:
        model = Goods
        fields = ['title', 'subtitle', 'description', 'content',
                  'badge_text', 'accent_color', 'order', 'is_visible']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'content': forms.Textarea(attrs={'class': 'rich-editor', 'rows': 10}),
            'accent_color': ColorInput,
        }


class GoodsFileForm(forms.ModelForm):
    class Meta:
        model = GoodsFile
        fields = ['title', 'file', 'file_type', 'order']


class SocialLinkForm(forms.ModelForm):
    class Meta:
        model = SocialLink
        fields = ['name', 'icon', 'url', 'order', 'is_visible']
        widgets = {
            'icon': forms.Textarea(attrs={'rows': 4, 'placeholder': '<svg width="18" height="18" viewBox="..." fill="none">...</svg>'}),
        }
