# SEO.md — Что сделано и почему

Документ описывает все изменения, внесённые для SEO-оптимизации сайта Ludera и исправления превью карточек в социальных сетях.

---

## 1. Исправление превью-карточек в соцсетях (VK, Telegram, Odnoklassniki)

### Проблема
При вставке ссылки на сайт в социальные сети (ВКонтакте, Telegram и др.) карточка превью не отображалась или была пустой.

### Причина
- Тег `og:image` выводился **условно** — только когда в админке был загружен `og_image` в `SiteSetting`
- Не было fallback-изображения на случай, если админ не загрузил картинку
- Отсутствовали VK-специфичные мета-теги (`vk:title`, `vk:description`, `vk:image`)

### Что сделано

**Файл:** `main/templates/main/base.html`
- `og:image` теперь выводится **всегда** — с fallback на статическое изображение `/static/images/og-preview.svg`
- Добавлены VK-теги: `vk:title`, `vk:description`, `vk:image`
- Добавлен `og:image:type` для корректного определения формата
- Блоки `og_title`, `og_description`, `vk_title`, `vk_description` вынесены в `{% block %}` для переопределения на страницах

**Файл:** `main/templates/main/detail.html`
- Добавлен блок `og_image` для отображения per-page изображения (из модели `obj.image`) или fallback
- Добавлены блоки `vk_title` и `vk_description` для VK-превью
- Удалены дублирующие inline OG-теги (теперь используются блоки)

**Файл:** `static/images/og-preview.svg` (НОВЫЙ)
- Создано OG-изображение 1200×630 для fallback превью
- Стиль: тёмный фон с логотипом, названием компании и описанием услуг
- Формат SVG — поддерживается большинством платформ

### Как проверить
1. После деплоя откройте [VK debugger](https://vk.com/dev.php?method=widgets.check) — вставьте URL сайта
2. Или откройте [Telegram debugger](https://t.me/urlinfo) — отправьте ссылку боту @urlinfo
3. Проверьте HTML-код страницы: `og:image` должен быть всегда, с абсолютным URL

---

## 2. Улучшение Open Graph и Twitter Cards

### Что сделано

**Файл:** `main/templates/main/base.html`
- Добавлен блок `{% block og_image %}` для переопределения OG-изображения на страницах
- Twitter Cards теперь тоже используют fallback изображение
- `og:image:alt` всегда выводится (для доступности и SEO)

**Файл:** `main/templates/main/index.html`
- Добавлены блоки: `og_title`, `og_description`, `twitter_title`, `twitter_description`, `vk_title`, `vk_description`
- Главная страница теперь корректно отдаёт мета-теги из `SiteSetting`

---

## 3. Улучшение JSON-LD структурированных данных

### Что сделано

**Файл:** `main/templates/main/base.html`
- Обновлён `Organization` schema:
  - `areaServed` теперь объект `Country` (Россия) вместо строки
  - Добавлено `knowsLanguage: ["ru", "en"]`
  - Добавлен `hasOfferCatalog` с тремя основными услугами (чат-боты, сайты, CRM)
  - `contactType` изменён на `customer service`
- Обновлён `WebSite` schema:
  - Добавлен `potentialAction` с `SearchAction` (для интеграции с поисковиками)

**Файл:** `main/templates/main/detail.html`
- Добавлены типизированные schema для каждого типа контента:
  - `BlogPosting` — с `publisher` и `image`
  - `Service` — для страниц услуг
  - `SoftwareApplication` — для страниц продуктов
  - `CreativeWork` — для страниц проектов

---

## 4. Улучшение robots.txt

### Что сделано

**Файл:** `main/views.py`
- Добавлен отдельный блок `User-agent: Yandex` для Яндекс.Вебмастера
- Добавлен `Disallow: /ecosystem-test/` (служебная страница)
- Исправлен формат вывода (f-string → format)

---

## 5. SEO Meta-теги

### Что сделано

**Файл:** `main/templates/main/base.html`
- Добавлен тег `<meta name="robots" content="index, follow, max-image-preview:large, max-snippet:-1, max-video-preview:-1">` — явное разрешение индексации и большого превью изображений
- Добавлен тег `<meta name="author" content="Ludera">`
- Добавлены `hreflang` теги: `ru` и `x-default`
- Блок `meta_keywords` вынесен в `{% block %}` для переопределения
- Блок `canonical` вынесен в `{% block %}` для переопределения

---

## 6. Favicon redirect

### Что сделано

**Файл:** `main/views.py`
- Добавлена view `favicon_ico` — редирект `/favicon.ico` → `/static/images/favicon.svg`
- Некоторые браузеры и краулеры запрашивают `/favicon.ico` — теперь они получают правильный ответ

**Файл:** `main/urls.py`
- Добавлен маршрут `favicon.ico`

---

## 7. Созданные файлы

| Файл | Описание |
|---|---|
| `static/images/og-preview.svg` | Fallback OG-изображение 1200×630 для превью в соцсетях |
| `SEO.md` | Этот документ |

---

## 8. Рекомендации (требуют ручных действий)

### Загрузите OG-изображение в админке
1. Зайдите в `/admin/main/sitesetting/`
2. Загрузите изображение 1200×630px (PNG/JPG) в поле `og_image`
3. Это заменит fallback SVG на полноценное растровое изображение для соцсетей

> **Важно:** VK и некоторые другие платформы лучше работают с PNG/JPG, чем SVG. Рекомендуем загрузить растровое изображение.

### Яндекс.Вебмастер
- Добавьте сайт в Яндекс.Вебмастер: https://webmaster.yandex.ru/
- Вставьте код верификации в поле `Yandex Webmaster` в админке (`SiteSetting`)

### Google Search Console
- Добавьте сайт в Google Search Console: https://search.google.com/search-console
- Вставьте код верификации в поле `Google Search Console` в админке

### Контрольный список
- [ ] Загрузить OG-изображение (1200×630 PNG/JPG) в админку
- [ ] Добавить сайт в Яндекс.Вебмастер
- [ ] Добавить сайт в Google Search Console
- [ ] Проверить превью в VK через https://vk.com/dev.php?method=widgets.check
- [ ] Проверить превью в Telegram через бота @urlinfo
- [ ] Проверить structured data через https://search.google.com/test/rich-results
