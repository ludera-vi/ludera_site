#!/usr/bin/env bash
set -euo pipefail

# ─── Установка PostgreSQL ──────────────────────────────────────────
echo ">>> Installing PostgreSQL..."
sudo pacman -S --noconfirm postgresql
sudo -u postgres initdb --locale ru_RU.UTF-8 -D /var/lib/postgres/data
sudo systemctl enable --now postgresql

# ─── Создание БД и пользователя ────────────────────────────────────
echo ">>> Creating database and user..."
sudo -u postgres psql -c "CREATE USER ludera WITH PASSWORD '/,.6Dq-wW.ajV3{n?,dL9kBim\"%k%*';"
sudo -u postgres psql -c "CREATE DATABASE ludera OWNER ludera;"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE ludera TO ludera;"

echo ">>> Database 'ludera' created successfully."

# ─── Настройка .env для продакшна ──────────────────────────────────
cat > /home/vi/ludera/.env << 'ENVEOF'
DEBUG=False
SECRET_KEY=change-me-to-a-real-random-secret
ALLOWED_HOSTS=ludera.ru,www.ludera.ru
CSRF_TRUSTED_ORIGINS=https://ludera.ru,https://www.ludera.ru

DB_ENGINE=postgresql
DB_NAME=ludera
DB_USER=ludera
DB_PASSWORD=/,.6Dq-wW.ajV3{n?,dL9kBim"%k%*
DB_HOST=localhost
DB_PORT=5432

EMAIL_BACKEND=smtp
EMAIL_HOST=smtp.yandex.ru
EMAIL_PORT=465
EMAIL_USE_SSL=True
EMAIL_HOST_USER=hello@ludera.ru
EMAIL_HOST_PASSWORD=your-password
DEFAULT_FROM_EMAIL=hello@ludera.ru

YANDEX_CLIENT_ID=
YANDEX_SECRET=
GOOGLE_CLIENT_ID=
GOOGLE_SECRET=

SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
SECURE_HSTS_SECONDS=31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS=True
SECURE_HSTS_PRELOAD=True
ENVEOF

echo ">>> .env file created. Edit SECRET_KEY, EMAIL and OAuth settings."
echo ""
echo ">>> Next steps:"
echo "  1. cd /home/vi/ludera"
echo "  2. python -m venv .venv && source .venv/bin/activate"
echo "  3. pip install -r requirements.txt"
echo "  4. python manage.py migrate"
echo "  5. python manage.py collectstatic --noinput"
echo "  6. python manage.py createsuperuser"
echo "  7. python seed_data.py"
echo "  8. Run with gunicorn: gunicorn ludera.wsgi -w 4 -b 127.0.0.1:8000"
