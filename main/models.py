from django.db import models
from django.utils.text import slugify
from django.utils import timezone
from django.urls import reverse
from django.core.exceptions import ValidationError

CYRILLIC_TO_LATIN = {
    'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd', 'е': 'e', 'ё': 'e',
    'ж': 'zh', 'з': 'z', 'и': 'i', 'й': 'y', 'к': 'k', 'л': 'l', 'м': 'm',
    'н': 'n', 'о': 'o', 'п': 'p', 'р': 'r', 'с': 's', 'т': 't', 'у': 'u',
    'ф': 'f', 'х': 'kh', 'ц': 'ts', 'ч': 'ch', 'ш': 'sh', 'щ': 'shch',
    'ъ': '', 'ы': 'y', 'ь': '', 'э': 'e', 'ю': 'yu', 'я': 'ya',
}


def transliterate(value):
    result = []
    for char in value.lower():
        result.append(CYRILLIC_TO_LATIN.get(char, char))
    return ''.join(result)


def make_slug(value, max_length=200):
    transliterated = transliterate(value)
    slug = slugify(transliterated)[:max_length]
    return slug


class SlugMixin:
    slug_max_length = 200
    fallback_slug = 'object'

    def _generate_slug(self):
        slug = make_slug(getattr(self, 'title', '') or '', self.slug_max_length) or self.fallback_slug
        base = slug
        counter = 1
        model_class = self.__class__
        while model_class.objects.filter(slug=slug).exclude(pk=self.pk).exists():
            counter += 1
            slug = f'{base}-{counter}'
        return slug

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = self._generate_slug()
        super().save(*args, **kwargs)


class SiteSetting(models.Model):
    email = models.EmailField('Email', default='hello@ludera.ru')
    footer_description = models.TextField('Описание в футере', default='Создаём современные цифровые решения для малого и среднего бизнеса.')
    copyright_text = models.CharField('Копирайт', max_length=300, default='© 2024 Ludera. Все права защищены.')
    cta_title = models.CharField('Заголовок CTA', max_length=300, default='Готовы обсудить ваш проект?')
    cta_description = models.TextField('Описание CTA', default='Расскажите о вашей задаче — мы подберём оптимальное решение.')
    meta_title = models.CharField('Meta title', max_length=300, default='Ludera — CRM, чат-боты и веб-разработка для бизнеса')
    meta_description = models.TextField('Meta description', default='Ludera — разработка CRM, чат-ботов и сайтов для бизнеса.')
    meta_keywords = models.CharField('Meta keywords', max_length=500, blank=True, default='создание сайтов, разработка CRM, чат-боты, заказать сайт, разработка программ, веб-студия, автоматизация бизнеса')
    og_image = models.ImageField('Open Graph изображение', upload_to='settings/', blank=True, help_text='Рекомендуемый размер: 1200x630px')
    yandex_verification = models.CharField('Yandex Webmaster', max_length=100, blank=True, default='', help_text='Код верификации Яндекс.Вебмастер')
    google_verification = models.CharField('Google Search Console', max_length=100, blank=True, default='', help_text='Код верификации Google Search Console')

    # Navigation titles
    nav_services_title = models.CharField('Название пункта «Услуги»', max_length=100, default='Услуги')
    nav_products_title = models.CharField('Название пункта «Продукты»', max_length=100, default='Продукты')
    nav_projects_title = models.CharField('Название пункта «Проекты»', max_length=100, default='Проекты')
    nav_blog_title = models.CharField('Название пункта «Блог»', max_length=100, default='Блог')

    # Header
    header_cta_text = models.CharField('Текст кнопки в хедере', max_length=100, default='Заказать демо')
    header_login_text = models.CharField('Текст «Войти»', max_length=100, default='Войти')
    header_account_text = models.CharField('Текст «Личный кабинет»', max_length=100, default='Личный кабинет')

    # Services section
    services_section_title = models.CharField('Заголовок секции услуг', max_length=300, default='Современные инструменты для роста вашего бизнеса')
    services_detail_text = models.CharField('Текст «Подробнее» в услугах', max_length=100, default='Подробнее')

    # Projects section
    projects_section_title = models.CharField('Заголовок секции проектов', max_length=300, default='Наши проекты')
    projects_section_subtitle = models.CharField('Подзаголовок секции проектов', max_length=500, default='Реальные кейсы и решения для бизнеса')

    # Products section
    products_section_title = models.CharField('Заголовок секции продуктов', max_length=300, default='Наши продукты')
    products_section_subtitle = models.CharField('Подзаголовок секции продуктов', max_length=500, default='Интегрированная платформа для управления IT-продуктами')
    products_detail_text = models.CharField('Текст «Подробнее» в продуктах', max_length=100, default='Подробнее')

    # About section
    about_section_title = models.CharField('Заголовок секции «О нас»', max_length=300, default='Почему Ludera')
    about_section_subtitle = models.CharField('Подзаголовок секции «О нас»', max_length=500, default='Четыре принципа, на которых построена наша работа')

    # Blog section
    blog_section_title = models.CharField('Заголовок секции блога', max_length=300, default='Блог')
    blog_section_subtitle = models.CharField('Подзаголовок секции блога', max_length=500, default='Полезные статьи, новости и кейсы от команды Ludera')
    blog_read_text = models.CharField('Текст «Читать»', max_length=100, default='Читать')
    blog_filter_all = models.CharField('Текст фильтра «Все»', max_length=100, default='Все')
    blog_empty_text = models.CharField('Текст «нет статей»', max_length=300, default='Статьи скоро появятся')

    # Footer / Contact form
    footer_cta_label = models.CharField('Лейбл CTA в футере', max_length=100, default='Начните сегодня')
    footer_company_title = models.CharField('Заголовок колонки «Компания»', max_length=100, default='Компания')
    footer_products_title = models.CharField('Заголовок колонки «Продукты»', max_length=100, default='Продукты')
    contact_name_placeholder = models.CharField('Placeholder «Имя»', max_length=100, default='Ваше имя')
    contact_email_placeholder = models.CharField('Placeholder «Email»', max_length=100, default='Email')
    contact_message_placeholder = models.CharField('Placeholder «Сообщение»', max_length=300, default='Расскажите о вашем проекте...')
    contact_submit_text = models.CharField('Текст кнопки отправки', max_length=100, default='Отправить заявку')
    contact_success_text = models.CharField('Текст об успешной отправке', max_length=300, default='Заявка отправлена! Мы свяжемся с вами в ближайшее время.')

    # Ecosystem section
    ecosystem_badge = models.CharField('Бейдж ecosystem', max_length=50, default='Pipeline')
    ecosystem_title = models.CharField('Заголовок ecosystem', max_length=300, default='Как мы работаем')
    ecosystem_subtitle = models.CharField('Подзаголовок ecosystem', max_length=500, default='От задачи до запуска — два пути, один результат')
    ecosystem_terminal_title = models.CharField('Заголовок терминала', max_length=100, default='ludera-cli — interactive')
    ecosystem_flow_title = models.CharField('Заголовок диаграммы', max_length=100, default='Client Journey')
    ecosystem_client_label = models.CharField('Метка «Клиент»', max_length=100, default='Клиент')
    ecosystem_client_badge = models.CharField('Бейдж клиента', max_length=50, default='B2B / B2C')
    ecosystem_analysis_label = models.CharField('Метка «Анализ»', max_length=100, default='Анализ потребностей')
    ecosystem_custom_label = models.CharField('Метка «Инд. разработка»', max_length=100, default='Индивидуальная разработка')
    ecosystem_ready_label = models.CharField('Метка «Готовый продукт»', max_length=100, default='Готовый продукт')
    ecosystem_support_label = models.CharField('Метка «Поддержка»', max_length=100, default='Поддержка и развитие')

    # Hero section
    hero_tagline = models.CharField('Теглайн Hero', max_length=200, default='Ваш цифровой партнёр')
    hero_title = models.CharField('Заголовок Hero', max_length=500, default='Создаём CRM, чат-ботов и сайты, которые работают на вас')
    hero_description = models.TextField('Описание Hero', default='Помогаем малому и среднему бизнесу автоматизировать продажи.')
    hero_cta_text = models.CharField('Текст кнопки Hero', max_length=100, default='Обсудить проект')
    hero_cta_link = models.CharField('Ссылка кнопки Hero', max_length=200, default='#contact')

    # Footer ИП
    footer_ip_name = models.CharField('Наименование ИП', max_length=300, blank=True, default='')
    footer_ip_inn = models.CharField('ИНН', max_length=20, blank=True, default='')
    footer_ip_ogrnip = models.CharField('ОГРНИП', max_length=20, blank=True, default='')
    footer_ip_address = models.CharField('Адрес ИП', max_length=500, blank=True, default='')

    updated_at = models.DateTimeField('Обновлено', auto_now=True)

    class Meta:
        verbose_name = 'Настройка сайта'
        verbose_name_plural = 'Настройки сайта'

    def __str__(self):
        return 'Настройки сайта'

    def save(self, *args, **kwargs):
        if not self.pk and SiteSetting.objects.exists():
            raise ValidationError('Может существовать только один экземпляр SiteSetting')
        super().save(*args, **kwargs)

    def get_social_links(self):
        return self.social_links.filter(is_visible=True).order_by('order')

    @property
    def ecosystem_custom_steps_list(self):
        return ['Проектирование', 'Дизайн', 'Разработка', 'Тестирование', 'Запуск']

    @property
    def ecosystem_ready_steps_list(self):
        return ['Выбор решения', 'Подключение', 'Интеграция', 'Адаптация', 'Запуск']


class SocialLink(models.Model):
    site_setting = models.ForeignKey(SiteSetting, on_delete=models.CASCADE, related_name='social_links', verbose_name='Настройки сайта', null=True, blank=True)
    name = models.CharField('Название', max_length=100, help_text='Напр. Telegram, VK, Instagram')
    icon = models.TextField('Иконка (SVG)', help_text='Вставьте SVG-код иконки')
    url = models.URLField('Ссылка')
    order = models.IntegerField('Порядок', default=0)
    is_visible = models.BooleanField('Показывать', default=True)

    class Meta:
        ordering = ['order']
        verbose_name = 'Ссылка соцсети'
        verbose_name_plural = 'Социальные сети'

    def __str__(self):
        return self.name


class HeroSection(models.Model):
    tagline = models.CharField('Теглайн', max_length=200, default='Ваш цифровой партнёр')
    title = models.CharField('Заголовок', max_length=500, default='Создаём CRM, чат-ботов и сайты, которые работают на вас')
    description = models.TextField('Описание', default='Помогаем малому и среднему бизнесу автоматизировать продажи.')
    cta_text = models.CharField('Текст кнопки', max_length=100, default='Обсудить проект')
    cta_link = models.CharField('Ссылка кнопки', max_length=200, default='#contact')
    is_active = models.BooleanField('Активно', default=True)

    class Meta:
        verbose_name = 'Hero-блок'
        verbose_name_plural = 'Hero-блоки'

    def __str__(self):
        return self.title or 'Hero-блок'

    def save(self, *args, **kwargs):
        if self.is_active:
            HeroSection.objects.exclude(pk=self.pk).update(is_active=False)
        super().save(*args, **kwargs)

    @classmethod
    def get_active(cls):
        obj = cls.objects.filter(is_active=True).first()
        if not obj:
            obj = cls.objects.create()
        return obj


class NavLink(models.Model):
    title = models.CharField('Название', max_length=100)
    url = models.CharField('Ссылка', max_length=200, help_text='Напр. #services, /blog/')
    order = models.IntegerField('Порядок', default=0)
    is_visible = models.BooleanField('Видимая', default=True)

    class Meta:
        ordering = ['order']
        verbose_name = 'Ссылка в навигации'
        verbose_name_plural = 'Навигация'

    def __str__(self):
        return self.title


class Service(SlugMixin, models.Model):
    slug_max_length = 220
    fallback_slug = 'usluga'
    title = models.CharField('Название', max_length=200)
    slug = models.SlugField('Слаг', max_length=220, unique=True, blank=True, editable=False)
    description = models.TextField('Описание')
    content = models.TextField('Контент (HTML)', blank=True, help_text='Полный текст с форматированием')
    pill_number = models.CharField('Номер пилла', max_length=10, default='01', help_text='Напр. 01, 02, 03')
    pill_label = models.CharField('Лейбл пилла', max_length=100, default='Ludera CRM')
    panel_config = models.JSONField('Настройки панели', blank=True, null=True,
        help_text='JSON: {"badge": "...", "chart": [50,60,...], "chart_label": "...", "metric1_label": "...", "metric1_value": 68, "metric1_suffix": "%", "metric1_change": "...", "metric2_...", "timeline_label": "...", "timeline_progress": 75, "timeline_total": 8, "timeline_done": 6, "timeline_badge": "...", "lead_label": "...", "lead_channels": 5, "lead_pills": ["green","teal",...], "footer_text": "...", "footer_dots": ["green",...]}')
    order = models.IntegerField('Порядок', default=0)
    created_at = models.DateTimeField('Создано', default=timezone.now)
    updated_at = models.DateTimeField('Обновлено', auto_now=True)

    class Meta:
        ordering = ['order']
        verbose_name = 'Услуга'
        verbose_name_plural = 'Услуги'

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('main:service_detail', kwargs={'slug': self.slug})

    @property
    def panel(self):
        if self.panel_config:
            return self.panel_config
        return {
            'badge': '—',
            'chart': [50, 60, 70, 80, 60, 90],
            'chart_label': 'Показатели',
            'metric1_label': 'Метрика', 'metric1_value': 50, 'metric1_suffix': '%', 'metric1_change': '',
            'metric2_label': 'Метрика', 'metric2_value': 50, 'metric2_suffix': '%', 'metric2_change': '',
            'timeline_label': 'Прогресс', 'timeline_progress': 50, 'timeline_total': 8, 'timeline_done': 4, 'timeline_badge': '—',
            'lead_label': 'Каналы', 'lead_channels': 0,
            'lead_pills': ['green', 'green', 'green', 'green', 'green'],
            'footer_text': '',
            'footer_dots': ['green', 'green', 'green'],
        }


class Project(SlugMixin, models.Model):
    slug_max_length = 320
    fallback_slug = 'proekt'
    title = models.CharField('Название', max_length=300)
    slug = models.SlugField('Слаг', max_length=320, unique=True, blank=True, editable=False)
    status = models.CharField('Статус', max_length=100, default='', blank=True)
    description = models.TextField('Описание')
    content = models.TextField('Контент (HTML)', blank=True, help_text='Полный текст с форматированием')
    image = models.ImageField('Изображение', upload_to='projects/', blank=True)
    tag1 = models.CharField('Тег 1', max_length=100, blank=True)
    tag2 = models.CharField('Тег 2', max_length=100, blank=True)
    accent_color = models.CharField('Цвет акцента', max_length=20, default='#e86969')
    order = models.IntegerField('Порядок', default=0)
    is_visible = models.BooleanField('Показывать', default=True)
    created_at = models.DateTimeField('Создано', default=timezone.now)
    updated_at = models.DateTimeField('Обновлено', auto_now=True)

    class Meta:
        ordering = ['order']
        verbose_name = 'Проект'
        verbose_name_plural = 'Проекты'

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('main:project_detail', kwargs={'slug': self.slug})


class Product(SlugMixin, models.Model):
    slug_max_length = 220
    fallback_slug = 'produkt'
    title = models.CharField('Название', max_length=200)
    slug = models.SlugField('Слаг', max_length=220, unique=True, blank=True, editable=False)
    subtitle = models.CharField('Подзаголовок', max_length=300, blank=True)
    description = models.TextField('Описание')
    content = models.TextField('Контент (HTML)', blank=True, help_text='Полный текст с форматированием')
    accent = models.CharField('Цвет акцента', max_length=20, default='#a7d5b8')
    accent_rgb = models.CharField('RGB акцента', max_length=30, default='167,213,184')
    badge_text = models.CharField('Текст бейджа', max_length=20, default='CRM')
    order = models.IntegerField('Порядок', default=0)
    is_visible = models.BooleanField('Показывать', default=True)
    created_at = models.DateTimeField('Создано', default=timezone.now)
    updated_at = models.DateTimeField('Обновлено', auto_now=True)

    class Meta:
        ordering = ['order']
        verbose_name = 'Продукт'
        verbose_name_plural = 'Продукты'

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('main:product_detail', kwargs={'slug': self.slug})


class ProductMetric(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='metrics')
    label = models.CharField('Название', max_length=100)
    value = models.IntegerField('Значение (проценты)', help_text='Значение от 0 до 100')

    class Meta:
        verbose_name = 'Метрика продукта'
        verbose_name_plural = 'Метрики продуктов'

    def __str__(self):
        return f'{self.product.title} — {self.label}'


class ProductDetail(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='details')
    text = models.CharField('Текст', max_length=300)

    class Meta:
        verbose_name = 'Возможность продукта'
        verbose_name_plural = 'Возможности продуктов'

    def __str__(self):
        return self.text


class Principle(models.Model):
    title = models.CharField('Название', max_length=200)
    description = models.TextField('Описание')
    order = models.IntegerField('Порядок', default=0)

    class Meta:
        ordering = ['order']
        verbose_name = 'Принцип'
        verbose_name_plural = 'Принципы'

    def __str__(self):
        return self.title


class FooterLink(models.Model):
    COLUMN_CHOICES = [
        ('company', 'Компания'),
        ('products', 'Продукты'),
    ]
    column = models.CharField('Колонка', max_length=20, choices=COLUMN_CHOICES, default='company')
    title = models.CharField('Название', max_length=200)
    url = models.CharField('Ссылка', max_length=200)
    order = models.IntegerField('Порядок', default=0)

    class Meta:
        ordering = ['column', 'order']
        verbose_name = 'Ссылка в футере'
        verbose_name_plural = 'Ссылки в футере'

    def __str__(self):
        return self.title


class BlogPost(SlugMixin, models.Model):
    slug_max_length = 320
    fallback_slug = 'statya'
    title = models.CharField('Заголовок', max_length=300)
    slug = models.SlugField('Слаг', max_length=320, unique=True, blank=True, editable=False)
    description = models.TextField('Описание')
    content = models.TextField('Контент (HTML)', blank=True, help_text='Полный текст статьи с форматированием')
    image = models.ImageField('Обложка', upload_to='blog/', blank=True)
    category = models.CharField('Категория', max_length=100)
    category_color = models.CharField('Цвет категории', max_length=20, default='#a7d5b8')
    date = models.DateField('Дата', default=timezone.now)
    reading_time = models.CharField('Время чтения', max_length=50, default='5 мин чтения')
    author = models.CharField('Автор', max_length=200)
    gradient_start = models.CharField('Начальный цвет градиента', max_length=20, default='#0a2e33')
    gradient_end = models.CharField('Конечный цвет градиента', max_length=20, default='#1a4a50')
    is_visible = models.BooleanField('Показывать', default=True)
    created_at = models.DateTimeField('Создано', default=timezone.now)
    updated_at = models.DateTimeField('Обновлено', auto_now=True)

    class Meta:
        ordering = ['-date']
        verbose_name = 'Запись блога'
        verbose_name_plural = 'Блог'

    def __str__(self):
        return self.title

    @property
    def author_initials(self):
        parts = self.author.strip().split()
        if len(parts) >= 2:
            return (parts[0][0] + parts[1][0]).upper()
        if parts:
            return parts[0][0].upper()
        return '?'

    def get_absolute_url(self):
        return reverse('main:blog_detail', kwargs={'slug': self.slug})


class PageView(models.Model):
    url = models.CharField('URL', max_length=500)
    user_agent = models.TextField('User-Agent', blank=True)
    ip_address = models.GenericIPAddressField('IP', blank=True, null=True)
    session_key = models.CharField('Сессия', max_length=100, blank=True)
    timestamp = models.DateTimeField('Время', auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']
        verbose_name = 'Просмотр страницы'
        verbose_name_plural = 'Статистика просмотров'

    def __str__(self):
        return f'{self.url} — {self.timestamp.strftime("%d.%m.%Y %H:%M")}'

    @property
    def page_name(self):
        from django.urls import resolve, Resolver404
        path = self.url.split('?')[0]
        try:
            match = resolve(path)
            mapping = {
                'index': 'Главная',
                'blog_detail': 'Запись блога',
                'project_detail': 'Проект',
                'service_detail': 'Услуга',
                'product_detail': 'Продукт',
                'contact_submit': 'Контакты',
                'sitemap': 'Sitemap',
            }
            return mapping.get(match.url_name, self.url)
        except Resolver404:
            return path or 'Главная'


class ContactRequest(models.Model):
    name = models.CharField('Имя', max_length=200, blank=True)
    email = models.EmailField('Email')
    message = models.TextField('Сообщение', blank=True)
    created_at = models.DateTimeField('Дата', auto_now_add=True)
    is_read = models.BooleanField('Прочитано', default=False)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Заявка'
        verbose_name_plural = 'Заявки с сайта'

    def __str__(self):
        return f'{self.email} — {self.created_at.strftime("%d.%m.%Y")}'
