from django.db import migrations


def load_initial_data(apps, schema_editor):
    SiteSetting = apps.get_model('main', 'SiteSetting')
    HeroSection = apps.get_model('main', 'HeroSection')
    NavLink = apps.get_model('main', 'NavLink')
    Service = apps.get_model('main', 'Service')
    Project = apps.get_model('main', 'Project')
    Product = apps.get_model('main', 'Product')
    ProductMetric = apps.get_model('main', 'ProductMetric')
    ProductDetail = apps.get_model('main', 'ProductDetail')
    Principle = apps.get_model('main', 'Principle')
    FooterLink = apps.get_model('main', 'FooterLink')
    BlogPost = apps.get_model('main', 'BlogPost')

    SiteSetting.objects.create(
        email='hello@ludera.ru',
        footer_description=(
            'Создаём современные цифровые решения для малого и среднего бизнеса. '
            'CRM, чат-боты, сайты и веб-приложения — быстро, качественно и с '
            'индивидуальным подходом.'
        ),
        copyright_text='© 2024 Ludera. Все права защищены.',
        cta_title='Готовы обсудить ваш проект?',
        cta_description=(
            'Расскажите о вашей задаче — мы подберём оптимальное решение '
            'и предложим лучшие условия.'
        ),
        cta_button_text='hello@ludera.ru',
        meta_title='Ludera — CRM, чат-боты и веб-разработка для бизнеса',
        meta_description=(
            'Ludera — разработка CRM, чат-ботов и сайтов для малого и среднего '
            'бизнеса. Современные технологии, индивидуальный подход и быстрая разработка.'
        ),
    )

    HeroSection.objects.create(
        tagline='Ваш цифровой партнёр',
        title='Создаём CRM, чат-ботов и сайты,которые работают на вас',
        description=(
            'Помогаем малому и среднему бизнесу автоматизировать продажи, '
            'общаться с клиентами 24/7 и выделяться в цифровой среде. '
            'Современные технологии, быстрая разработка и индивидуальный подход.'
        ),
        cta_text='Обсудить проект',
        cta_link='#contact',
    )

    for title, url in [
        ('Услуги', '#services'),
        ('Продукты', '#products'),
        ('Проекты', '#projects'),
        ('О нас', '#about'),
        ('Контакты', '#contact'),
    ]:
        NavLink.objects.create(title=title, url=url)

    services_data = [
        {
            'title': 'CRM для малого бизнеса',
            'description': (
                'Управляйте клиентами, сделками и задачами в одном окне. '
                'Простая и понятная система, которая не требует обучения '
                'и внедряется за день.'
            ),
            'pill_number': '01',
            'pill_label': 'Ludera CRM',
        },
        {
            'title': 'Чат-боты для бизнеса',
            'description': (
                'Автоматизируйте общение с клиентами в Telegram, WhatsApp '
                'и на сайте. Быстрая настройка, интеграция с CRM и '
                'круглосуточная поддержка.'
            ),
            'pill_number': '02',
            'pill_label': 'Ludera Chat',
        },
        {
            'title': 'Сайты и веб-приложения',
            'description': (
                'Современные, быстрые и адаптивные сайты любой сложности. '
                'От лендинга до интернет-магазина с админ-панелью и '
                'SEO-оптимизацией.'
            ),
            'pill_number': '03',
            'pill_label': 'Ludera Web',
        },
    ]
    for i, s in enumerate(services_data):
        Service.objects.create(order=i, **s)

    projects_data = [
        {
            'number': 'P-001',
            'title': 'CRM для сети автосервисов',
            'status': 'active',
            'description': 'Автоматизация записи клиентов, учёт ремонтов и интеграция со складскими остатками.',
            'tag1': 'CRM',
            'tag2': 'Автосервис',
            'accent_color': '#e86969',
        },
        {
            'number': 'P-002',
            'title': 'Чат-бот для интернет-магазина',
            'status': 'active',
            'description': 'Мультиканальный бот для Telegram и WhatsApp с отслеживанием заказов и подбором товаров.',
            'tag1': 'Чат-бот',
            'tag2': 'E-Commerce',
            'accent_color': '#d4a853',
        },
        {
            'number': 'P-003',
            'title': 'Сайт для студии дизайна',
            'status': 'completed',
            'description': 'Современный сайт-портфолио с админ-панелью, интеграцией с CRM и SEO-оптимизацией.',
            'tag1': 'Веб-разработка',
            'tag2': 'Дизайн',
            'accent_color': '#5cc47c',
        },
        {
            'number': 'P-004',
            'title': 'CRM для агентства недвижимости',
            'status': 'active',
            'description': 'Учёт объектов, сделок и клиентов. Интеграция с сайтом и автоматические напоминания.',
            'tag1': 'CRM',
            'tag2': 'Недвижимость',
            'accent_color': '#5b8cbe',
        },
        {
            'number': 'P-005',
            'title': 'Чат-бот для службы поддержки',
            'status': 'pending',
            'description': 'Автоматизация типовых запросов, эскалация сложных вопросов и интеграция с CRM.',
            'tag1': 'Чат-бот',
            'tag2': 'Support',
            'accent_color': '#d4a853',
        },
        {
            'number': 'P-006',
            'title': 'Интернет-магазин для бренда одежды',
            'status': 'completed',
            'description': 'Полноценный интернет-магазин с каталогом, корзиной, оплатой и личным кабинетом.',
            'tag1': 'Веб-разработка',
            'tag2': 'E-Commerce',
            'accent_color': '#5cc47c',
        },
    ]
    for i, p in enumerate(projects_data):
        Project.objects.create(order=i, **p)

    products_data = [
        {
            'number': 'CRM',
            'title': 'Ludera CRM',
            'subtitle': 'Управление отношениями с клиентами',
            'description': 'Простая и мощная CRM для малого бизнеса. Ведение клиентской базы, учёт сделок, задач и аналитика продаж в одном окне.',
            'accent': '#a7d5b8',
            'accent_rgb': '167,213,184',
            'badge_text': 'CRM',
            'order': 0,
            'metrics': [('Клиенты', 95), ('Сделки', 88), ('Задачи', 92)],
            'details': [
                'Учёт клиентов и сделок',
                'Напоминания и задачи',
                'Отчёты и аналитика',
                'Интеграция с мессенджерами',
                'Импорт из Excel и Google Таблиц',
            ],
        },
        {
            'number': 'BOT',
            'title': 'Ludera Chat',
            'subtitle': 'Чат-боты для бизнеса',
            'description': 'Интеллектуальные чат-боты для Telegram, WhatsApp и сайта. Автоматизация поддержки, продаж и сбора заявок 24/7.',
            'accent': '#6b8cbe',
            'accent_rgb': '107,140,190',
            'badge_text': 'BOT',
            'order': 1,
            'metrics': [('Ответ 24/7', 99), ('Охват', 85), ('Удовлетворённость', 93)],
            'details': [
                'Telegram, WhatsApp, Web',
                'Интеграция с CRM',
                'Гибкая настройка сценариев',
                'Аналитика диалогов',
                'Эскалация на оператора',
            ],
        },
        {
            'number': 'WEB',
            'title': 'Ludera Web',
            'subtitle': 'Создание сайтов и веб-приложений',
            'description': 'Современные, быстрые и адаптивные сайты любой сложности. От лендинга до полноценного интернет-магазина с админ-панелью.',
            'accent': '#c9a84c',
            'accent_rgb': '201,168,76',
            'badge_text': 'WEB',
            'order': 2,
            'metrics': [('Скорость', 98), ('Адаптивность', 95), ('SEO', 90)],
            'details': [
                'Адаптивный дизайн',
                'SEO-оптимизация',
                'Админ-панель',
                'Высокая скорость загрузки',
                'Интеграция с любыми сервисами',
            ],
        },
    ]
    for pd in products_data:
        metrics = pd.pop('metrics')
        details = pd.pop('details')
        product = Product.objects.create(**pd)
        for label, value in metrics:
            ProductMetric.objects.create(product=product, label=label, value=value)
        for text in details:
            ProductDetail.objects.create(product=product, text=text)

    principles = [
        ('Доступность', 'Даём малому бизнесу современные цифровые инструменты, которые раньше были доступны только крупным корпорациям. Без сложного внедрения и скрытых платежей.'),
        ('Конфиденциальность', 'Ваши данные под надёжной защитой. Мы гарантируем безопасность информации и соответствие стандартам обработки персональных данных.'),
        ('Сотрудничество', 'Работаем в тесной связке с вами. Прозрачные процессы, понятная коммуникация и гибкость — мы всегда на вашей стороне.'),
        ('Инновации', 'Постоянно развиваем продукты, внедряем современные технологии и предлагаем новые решения, чтобы ваш бизнес оставался конкурентоспособным.'),
    ]
    for i, (title, desc) in enumerate(principles):
        Principle.objects.create(title=title, description=desc, order=i)

    footer_company = [
        ('Услуги', '#services'),
        ('Продукты', '#products'),
        ('Проекты', '#projects'),
        ('О нас', '#about'),
        ('Контакты', '#contact'),
    ]
    for i, (title, url) in enumerate(footer_company):
        FooterLink.objects.create(column='company', title=title, url=url, order=i)

    footer_products = [
        ('Ludera CRM', '#products'),
        ('Ludera Chat', '#products'),
        ('Ludera Web', '#products'),
    ]
    for i, (title, url) in enumerate(footer_products):
        FooterLink.objects.create(column='products', title=title, url=url, order=i)

    blog_posts = [
        {
            'title': 'Как выбрать CRM для малого бизнеса: 5 ключевых критериев',
            'description': 'Разбираемся, на что обратить внимание при выборе CRM-системы для небольшой компании. Функции, бюджет, интеграции и простота внедрения.',
            'category': 'CRM',
            'category_color': '#a7d5b8',
            'date': '2024-03-12',
            'reading_time': '5 мин чтения',
            'author': 'Алексей Кузнецов',
            'author_initials': 'АК',
            'gradient_start': '#0a2e33',
            'gradient_end': '#1a4a50',
        },
        {
            'title': 'Чат-боты в 2024: тренды и возможности для бизнеса',
            'description': 'Какие задачи решают современные чат-боты, где их применять и как не ошибиться с выбором платформы для автоматизации.',
            'category': 'Чат-боты',
            'category_color': '#6b8cbe',
            'date': '2024-02-28',
            'reading_time': '7 мин чтения',
            'author': 'Мария Соколова',
            'author_initials': 'МС',
            'gradient_start': '#1a2a4a',
            'gradient_end': '#2a4a6a',
        },
        {
            'title': 'Современный сайт за 14 дней: наш подход к разработке',
            'description': 'Как мы создаём сайты быстро без потери качества. Процесс, инструменты и почему скорость не означает «сырой результат».',
            'category': 'Веб-разработка',
            'category_color': '#5cc47c',
            'date': '2024-02-15',
            'reading_time': '4 мин чтения',
            'author': 'Дмитрий Ильин',
            'author_initials': 'ДИ',
            'gradient_start': '#2a3a1a',
            'gradient_end': '#4a6a2a',
        },
    ]
    for bp in blog_posts:
        BlogPost.objects.create(**bp)


def unload_initial_data(apps, schema_editor):
    for model in [
        'BlogPost', 'FooterLink', 'Principle', 'ProductDetail', 'ProductMetric',
        'Product', 'Project', 'Service', 'NavLink', 'HeroSection', 'SiteSetting',
    ]:
        apps.get_model('main', model).objects.all().delete()


class Migration(migrations.Migration):
    dependencies = [
        ('main', '0001_initial'),
    ]
    operations = [
        migrations.RunPython(load_initial_data, unload_initial_data),
    ]
