# Сервер ludera.ru

## Подключение

```bash
ssh root@159.194.214.14
# Пароль: bNyoG6Ir%Alf
```

## Проект

- **Путь:** `/home/django/ludera_site/`
- **Пользователь:** `django` (группа `django`)
- **Виртуальное окружение:** `/home/django/ludera_site/.venv/`
- **Настройки:** `ludera/settings.py` + `ludera/.env` → `~/ludera_site/.env`
- **Статика:** `~/ludera_site/staticfiles/`
- **Медиа:** `~/ludera_site/media/`

## ASGI-сервер (Daphne)

- **Сервис:** `ludera.service` (Daphne)
- **Порт:** 127.0.0.1:8001
- **Команда:** `daphne -b 127.0.0.1 -p 8001 ludera.asgi:application`
- **Restart:** systemd, `Restart=always`

```bash
systemctl status ludera.service
journalctl -u ludera.service -n 50 -f
sudo systemctl restart ludera.service
```

Daphne обслуживает и HTTP, и WebSocket на одном порту.

## Nginx

- **Конфиг:** `/etc/nginx/sites-enabled/ludera` (только этот сервер)
- **SSL:** Let's Encrypt, сертификат для `ludera.ru`
- **Статика:** отдаётся Nginx напрямую (`/static/`, `/media/`)
- **WebSocket:** `location /ws/` → `proxy_pass` с Upgrade-заголовками
- **Основной трафик:** `location /` → `proxy_pass http://127.0.0.1:8001`

```bash
nginx -t
systemctl reload nginx
```

## Redis

- **Сервис:** `redis-server.service`
- **Порт:** 127.0.0.1:6379
- **Используется:** Django Channels — channel layer для WebSocket

```bash
redis-cli ping  # → PONG
```

## База данных

- **СУБД:** PostgreSQL
- **БД:** `ludera`
- **Пользователь:** `ludera`
- **Пароль:** в `~/ludera_site/.env` (`DB_PASSWORD`)

## Полезные команды

```bash
# Django (manage.py)
sudo -u django bash -c 'cd ~/ludera_site && .venv/bin/python manage.py shell'

# Сбор статики
sudo -u django bash -c 'cd ~/ludera_site && .venv/bin/python manage.py collectstatic --noinput'

# Миграции
sudo -u django bash -c 'cd ~/ludera_site && .venv/bin/python manage.py migrate'

# Перезапуск всего
systemctl restart ludera.service && systemctl reload nginx
```

## Примечания

- `CSRF_USE_SESSIONS = True` — CSRF-токен в сессии, не куке. JS использует `'{{ csrf_token }}'`.
- DEBUG=False в production
- `ALLOWED_HOSTS` и `CSRF_TRUSTED_ORIGINS` в `.env`
- Полная замена Gunicorn → Daphne (WSGI → ASGI) для поддержки WebSocket
