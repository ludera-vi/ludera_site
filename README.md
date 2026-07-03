# Ludera

Сайт-визитка компании Ludera — разработка чат-ботов, сайтов и CRM-систем для бизнеса.

## Стек

- **Backend:** Python 3.14 / Django 6.0
- **Frontend:** Vanilla JS, CSS custom properties, IntersectionObserver, Quill editor
- **База данных:** SQLite (dev) / PostgreSQL (prod)
- **Аутентификация:** django-allauth (email + Yandex/Google OAuth)
- **Аналитика:** встроенная (PageView middleware с дедупликацией)

## Быстрый старт

```bash
# 1. Клонировать и перейти в папку
cd ludera

# 2. Виртуальное окружение
python -m venv .venv && source .venv/bin/activate

# 3. Зависимости
pip install -r requirements.txt

# 4. Настройки окружения
cp .env.example .env
# Отредактировать .env под свои нужды

# 5. Миграции и данные
python manage.py migrate
python seed_data.py
python manage.py createsuperuser

# 6. Запуск
python manage.py runserver
```

## Переменные окружения (.env)

| Переменная | По умолчанию | Описание |
|---|---|---|
| `DEBUG` | `True` | Режим отладки (на VPS — `False`) |
| `SECRET_KEY` | — | Секретный ключ Django |
| `ALLOWED_HOSTS` | `127.0.0.1,localhost` | Разрешённые хосты |
| `DB_ENGINE` | `sqlite` | `sqlite` или `postgresql` |
| `EMAIL_BACKEND` | `console` | `console` или `smtp` |

### Переключение на PostgreSQL

```bash
# Установить PostgreSQL и создать БД
sudo -u postgres psql -c "CREATE USER ludera WITH PASSWORD 'password';"
sudo -u postgres psql -c "CREATE DATABASE ludera OWNER ludera;"

# В .env заменить:
# DB_ENGINE=postgresql
# DB_NAME=ludera
# DB_USER=ludera
# DB_PASSWORD=password
# DB_HOST=localhost

# Применить миграции
python manage.py migrate
```

## Продакшн (VPS)

```bash
# 1. Установить зависимости
pip install -r requirements.txt
pip install gunicorn

# 2. Настроить .env (DEBUG=False, PostgreSQL, SMTP)
# 3. Собрать статику
python manage.py collectstatic --noinput

# 4. Запуск через gunicorn
gunicorn ludera.wsgi:application -w 4 --bind 127.0.0.1:8000

# 5. Nginx → static/media → gunicorn
```

## Известный технический долг

- **Product / Goods** — две похожие сущности с почти идентичной структурой. `Product` — публичные предложения на сайте, `Goods` — цифровые товары в кабинете пользователя. При рефакторинге объединить в одну модель с полем-дискриминатором.
- **UserProduct / UserGoods** — аналогично, наследуют общую логику доступа.
- **Тесты** — покрыты только базовые шаблоны и фильтры; CRUD-операции не покрыты.

## Структура проекта

```
ludera/
├── ludera/              # Конфиг Django
│   ├── settings.py      # Настройки (env-driven)
│   ├── urls.py          # Корневые URL
│   └── wsgi.py          # WSGI-точка входа
├── main/                # Главное приложение (сайт)
│   ├── models.py        # Service, Product, Project, BlogPost, etc.
│   ├── views.py         # Главная, деталки, sitemap
│   ├── cabinet_views.py # Панель управления (CRUD)
│   ├── middleware.py     # CabinetAccess + PageView
│   └── templates/       # Шаблоны публичной части и кабинета
├── users/               # Приложение пользователей
│   ├── models.py        # UserProfile, File, Goods, CabinetPermission
│   ├── views.py         # Регистрация, логин, кабинет пользователя
│   └── templates/       # Шаблоны ЛК пользователя
├── static/              # CSS, JS
├── media/               # Загруженные файлы
├── scripts/             # Скрипты развёртывания
├── .env                 # Локальные настройки (в .gitignore)
└── seed_data.py         # Наполнение БД контентом
```
