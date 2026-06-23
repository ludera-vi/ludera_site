/* ================================================================
   main.js — Главный JavaScript-файл сайта Ludera.
   ================================================================
   
   СОДЕРЖАНИЕ:
    1. IntersectionObserver — анимация элементов при скролле
    2. Хедер — изменение прозрачности при скролле
    3. Дополнительные микро-анимации (при наведении и т.д.)
   
   Все анимации сделаны на ванильном JS без библиотек.
   ================================================================ */


/* ================================================================
   1. INTERSECTION OBSERVER — АНИМАЦИЯ ПРИ СКРОЛЛЕ
   ================================================================
   
   IntersectionObserver — встроенный браузерный API, который позволяет
   отслеживать, когда элемент появляется в области видимости окна.
   
   Мы используем его, чтобы:
   - Добавлять класс .visible элементам, когда они появляются на экране
   - Повторно запускать анимации, если пользователь скроллит туда-сюда
   
   Как это работает:
   1. Создаём наблюдатель (IntersectionObserver) с настройками.
   2. Наблюдаем за каждым элементом с классом .scroll-animate.
   3. Когда элемент пересекает порог видимости (threshold), срабатывает
      колбэк, который добавляет/убирает класс .visible.
   ================================================================ */

(function() {
    'use strict';  // Строгий режим — помогает избежать ошибок

    // ─── Проверяем, поддерживает ли браузер IntersectionObserver ──
    if (!('IntersectionObserver' in window)) {
        // Если не поддерживается (старые браузеры), просто показываем всё
        document.querySelectorAll('.scroll-animate').forEach(function(el) {
            el.classList.add('visible');
        });
        return;  // Выходим, ничего больше не делаем
    }

    // ─── Настройки наблюдателя ────────────────────────────────────
    const observerOptions = {
        // root: null — используем viewport браузера как область наблюдения
        root: null,
        // rootMargin — отступы от границ области видимости.
        // '0px 0px -50px 0px' — сработает, когда элемент войдёт на 50px
        // в видимую область (чтобы анимация начиналась чуть раньше,
        // можно сделать 0px 0px -50px 0px)
        rootMargin: '0px 0px -50px 0px',
        // threshold — порог видимости (0 = любой пиксель, 1 = весь элемент).
        // 0.1 означает "когда видно хотя бы 10% элемента".
        threshold: 0.1
    };

    // ─── Создаём наблюдатель ──────────────────────────────────────
    const observer = new IntersectionObserver(function(entries) {
        // entries — массив всех наблюдаемых элементов, которые изменили
        // своё состояние (появились/исчезли).
        entries.forEach(function(entry) {
            // entry.isIntersecting — true, если элемент виден на экране
            if (entry.isIntersecting) {
                // ─── Элемент появился в области видимости ──────────
                // Добавляем класс .visible для запуска CSS-анимации
                entry.target.classList.add('visible');
            } else {
                // ─── Элемент скрылся из области видимости ──────────
                // Убираем класс .visible, чтобы при повторном появлении
                // анимация запустилась снова.
                entry.target.classList.remove('visible');
            }
        });
    }, observerOptions);

    // ─── Начинаем наблюдение за всеми .scroll-animate элементами ──
    // querySelectorAll возвращает статический NodeList всех элементов,
    // соответствующих селектору.
    document.querySelectorAll('.scroll-animate').forEach(function(element) {
        // Для каждого элемента вызываем observe(), чтобы наблюдатель
        // начал отслеживать его видимость.
        observer.observe(element);

        // data-delay больше не используем — ховер должен работать мгновенно.
        // Если нужен будет stagger для entrance — добавим потом нормально.
    });

    // Теперь, когда пользователь скроллит, элементы будут анимированно
    // появляться. А если проскроллить назад, они снова скроются, и при
    // повторном скролле анимация запустится заново. Это удовлетворяет
    // требованию "анимации должны повторяться".

})();


/* ================================================================
    2. ХЕДЕР — ПРОЗРАЧНОСТЬ ПРИ СКРОЛЛЕ
   ================================================================
   
   Когда пользователь скроллит вниз, хедер становится более непрозрачным
   и фон размывается сильнее. Это создаёт эффект "прилипания".
   ================================================================ */

(function() {
    'use strict';

    const header = document.querySelector('.header');

    // Если хедера нет на странице — ничего не делаем
    if (!header) return;

    // Функция-обработчик скролла
    function handleScroll() {
        // window.scrollY — количество пикселей, прокрученных сверху
        if (window.scrollY > 50) {
            // Если прокрутили больше 50px — делаем хедер плотнее
            header.style.backgroundColor = 'rgba(3, 33, 38, 0.95)';
            header.style.borderBottomColor = 'rgba(255, 255, 255, 0.1)';
        } else {
            // Вернулись наверх — возвращаем исходную прозрачность
            header.style.backgroundColor = 'rgba(3, 33, 38, 0.9)';
            header.style.borderBottomColor = 'rgba(255, 255, 255, 0.05)';
        }
    }

    // Подписываемся на событие scroll
    window.addEventListener('scroll', handleScroll, { passive: true });
    // { passive: true } — оптимизация: сообщаем браузеру, что мы не будем
    // вызывать preventDefault(), что улучшает производительность скролла.

    // Вызываем сразу, чтобы задать правильное состояние при загрузке
    handleScroll();

})();





/* ================================================================
    3. FEATURES — ИНТЕРАКТИВНЫЕ КАРТОЧКИ И ПИЛЛЫ
    ================================================================
    Переключение активной карточки и пилла в секции features.
    ================================================================ */

(function() {
    'use strict';

    var pills = document.querySelectorAll('.features__pill');
    var cards = document.querySelectorAll('.feature-card');
    var panels = document.querySelectorAll('.dashboard-panel');

    if (!pills.length || !cards.length) return;

    function setActive(index) {
        pills.forEach(function(p) {
            p.classList.toggle('features__pill--active', +p.dataset.index === index);
        });
        cards.forEach(function(c) {
            c.classList.toggle('feature-card--active', +c.dataset.index === index);
        });
        panels.forEach(function(p) {
            var isActive = +p.dataset.index === index;
            p.classList.toggle('dashboard-panel--active', isActive);
            if (isActive) {
                replayAnimations(p);
            }
        });
    }

    function replayAnimations(panel) {
        var bars = panel.querySelectorAll('.d-chart-bar');
        bars.forEach(function(bar) {
            bar.style.animation = 'none';
        });
        var fills = panel.querySelectorAll('.d-card__progress-fill, .d-card__track-fill');
        fills.forEach(function(fill) {
            fill.style.animation = 'none';
        });
        void panel.offsetWidth;
        bars.forEach(function(bar) {
            bar.style.animation = '';
        });
        fills.forEach(function(fill) {
            fill.style.animation = '';
        });
    }

    pills.forEach(function(pill) {
        pill.addEventListener('click', function() {
            setActive(+this.dataset.index);
        });
    });

    cards.forEach(function(card) {
        card.addEventListener('click', function() {
            setActive(+this.dataset.index);
        });
    });

})();


/* ================================================================
    4. PRODUCT CARDS — 3D TILT + МЕТРИКИ
    ================================================================
    3D-эффект наклона карточек продуктов при движении мыши
    и анимация заполнения метрик-баров при появлении в viewport.
    ================================================================ */

(function() {
    'use strict';

    /* ─── 4.1 Анимация метрик при появлении карточки ────────────── */
    var metricObserver = new MutationObserver(function() {
        document.querySelectorAll('.product-card.visible .product-card__metric-fill').forEach(function(fill) {
            if (fill.dataset.animated) return;
            var target = parseInt(fill.dataset.target, 10);
            if (!isNaN(target)) {
                fill.style.width = target + '%';
                fill.dataset.animated = 'true';
            }
        });
    });

    metricObserver.observe(document.body, {
        childList: true,
        subtree: true,
        attributes: true,
        attributeFilter: ['class']
    });

    // Однократный проход для уже видимых элементов
    document.querySelectorAll('.product-card.visible .product-card__metric-fill').forEach(function(fill) {
        if (fill.dataset.animated) return;
        var target = parseInt(fill.dataset.target, 10);
        if (!isNaN(target)) {
            fill.style.width = target + '%';
            fill.dataset.animated = 'true';
        }
    });

    /* ─── 4.3 ─ Сглаженный скролл к якорям (если браузер не поддерживает scroll-behavior) ── */
    if (!('scrollBehavior' in document.documentElement.style)) {
        document.querySelectorAll('a[href^="#"]').forEach(function(anchor) {
            anchor.addEventListener('click', function(e) {
                e.preventDefault();
                var targetId = this.getAttribute('href');
                if (targetId === '#') return;

                var targetElement = document.querySelector(targetId);
                if (targetElement) {
                    targetElement.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                }
            });
        });
    }

})();


/* ================================================================
    5. BURGER MENU — MOBILE NAVIGATION
    ================================================================ */

(function() {
    'use strict';

    var burger = document.getElementById('headerBurger');
    var backdrop = document.getElementById('mobileBackdrop');
    var menu = document.getElementById('mobileMenu');
    var closeBtn = document.getElementById('menuClose');
    if (!burger || !menu) return;

    function openMenu() {
        burger.classList.add('active');
        if (backdrop) backdrop.classList.add('open');
        menu.classList.add('open');
        document.body.style.overflow = 'hidden';
    }

    function closeMenu() {
        burger.classList.remove('active');
        if (backdrop) backdrop.classList.remove('open');
        menu.classList.remove('open');
        document.body.style.overflow = '';
    }

    burger.addEventListener('click', function() {
        if (menu.classList.contains('open')) {
            closeMenu();
        } else {
            openMenu();
        }
    });

    if (closeBtn) {
        closeBtn.addEventListener('click', closeMenu);
    }

    menu.querySelectorAll('.mobile-menu__link').forEach(function(link) {
        link.addEventListener('click', closeMenu);
    });

    if (backdrop) {
        backdrop.addEventListener('click', closeMenu);
    }

})();


/* ================================================================
    6. SECTION PAGINATION — CLIENT-SIDE FILTER + PAGINATION
    ================================================================ */

(function() {
    'use strict';

    var PER_PAGE = 6;

    function scrollToSection(section) {
        if (!section) return;
        var headerHeight = 80;
        var top = section.getBoundingClientRect().top + window.scrollY - headerHeight;
        window.scrollTo({ top: top, behavior: 'smooth' });
    }

    function initSectionPagination(config) {
        var section = document.querySelector(config.sectionSelector);
        if (!section) return;

        var filterBar = section.querySelector('.filter-bar');
        var grid = section.querySelector(config.gridSelector);
        var paginationEl = section.querySelector(config.paginationSelector);
        if (!grid) return;

        var allItems = Array.prototype.slice.call(grid.children);
        var currentPage = 1;
        var currentFilter = 'all';

        if (config.dynamicFilters && filterBar) {
            var cats = {};
            allItems.forEach(function(item) {
                var vals = item.dataset[config.filterAttr] || '';
                if (config.filterMode === 'contains') {
                    vals.split(/\s+/).forEach(function(v) { if (v) cats[v] = true; });
                } else if (vals && !cats[vals]) {
                    cats[vals] = true;
                }
            });
            Object.keys(cats).sort().forEach(function(cat) {
                var btn = document.createElement('button');
                btn.className = 'filter-btn';
                btn.dataset.filter = cat;
                btn.textContent = cat;
                filterBar.appendChild(btn);
            });
        }

        function getFiltered() {
            if (currentFilter === 'all') return allItems;
            return allItems.filter(function(item) {
                var val = item.dataset[config.filterAttr] || '';
                if (config.filterMode === 'contains') {
                    return val.split(/\s+/).indexOf(currentFilter) !== -1;
                }
                return val === currentFilter;
            });
        }

        function render() {
            var filteredItems = getFiltered();
            var totalPages = Math.ceil(filteredItems.length / PER_PAGE);
            if (currentPage > totalPages) currentPage = totalPages || 1;

            var start = (currentPage - 1) * PER_PAGE;
            var end = start + PER_PAGE;

            allItems.forEach(function(item) {
                item.style.display = 'none';
            });

            filteredItems.forEach(function(item, i) {
                if (i >= start && i < end) {
                    item.style.display = '';
                }
            });

            if (paginationEl) {
                paginationEl.innerHTML = '';
                if (totalPages <= 1) return;

                var wrapper = document.createElement('div');
                wrapper.className = 'pagination';

                var prev = document.createElement('button');
                prev.className = 'pagination__btn pagination__btn--prev';
                prev.innerHTML = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="15 18 9 12 15 6"/></svg>';
                prev.disabled = currentPage === 1;
                prev.addEventListener('click', function() { currentPage--; render(); scrollToSection(section); });
                wrapper.appendChild(prev);

                var pages = document.createElement('div');
                pages.className = 'pagination__pages';
                for (var p = 1; p <= totalPages; p++) {
                    var btn = document.createElement('button');
                    btn.className = 'pagination__page' + (p === currentPage ? ' pagination__page--active' : '');
                    btn.textContent = p;
                    btn.dataset.page = p;
                    btn.addEventListener('click', function() {
                        currentPage = parseInt(this.dataset.page);
                        render();
                        scrollToSection(section);
                    });
                    pages.appendChild(btn);
                }
                wrapper.appendChild(pages);

                var next = document.createElement('button');
                next.className = 'pagination__btn pagination__btn--next';
                next.innerHTML = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="9 18 15 12 9 6"/></svg>';
                next.disabled = currentPage === totalPages;
                next.addEventListener('click', function() { currentPage++; render(); scrollToSection(section); });
                wrapper.appendChild(next);

                paginationEl.appendChild(wrapper);
            }
        }

        if (filterBar) {
            filterBar.querySelectorAll('.filter-btn').forEach(function(btn) {
                btn.addEventListener('click', function() {
                    filterBar.querySelectorAll('.filter-btn').forEach(function(b) { b.classList.remove('active'); });
                    this.classList.add('active');
                    currentFilter = this.dataset.filter;
                    currentPage = 1;
                    render();
                });
            });
        }

        render();
    }

    initSectionPagination({
        sectionSelector: '#projects',
        gridSelector: '#projectsGrid',
        paginationSelector: '#projectPagination',
        filterAttr: 'tags',
        dynamicFilters: true,
        filterMode: 'contains'
    });

    initSectionPagination({
        sectionSelector: '#blog',
        gridSelector: '#blogGrid',
        paginationSelector: '#blogPagination',
        filterAttr: 'category',
        dynamicFilters: true
    });

})();


/* ================================================================
    7. CONTACT FORM — AJAX SUBMISSION
    ================================================================ */

(function() {
    'use strict';

    var form = document.getElementById('contactForm');
    if (!form) return;

    form.addEventListener('submit', function(e) {
        e.preventDefault();

        var submitBtn = form.querySelector('.contact-form__submit');
        var originalText = submitBtn.textContent;
        submitBtn.textContent = 'Отправка...';
        submitBtn.disabled = true;

        var formData = new FormData(form);

        var xhr = new XMLHttpRequest();
        xhr.open('POST', form.action, true);
        xhr.setRequestHeader('X-Requested-With', 'XMLHttpRequest');

        xhr.onload = function() {
            if (xhr.status === 200) {
                form.style.display = 'none';
                var success = document.getElementById('contactSuccess');
                if (success) success.style.display = 'flex';
            } else {
                submitBtn.textContent = originalText;
                submitBtn.disabled = false;
                alert('Ошибка отправки. Попробуйте ещё раз.');
            }
        };

        xhr.onerror = function() {
            submitBtn.textContent = originalText;
            submitBtn.disabled = false;
            alert('Ошибка сети. Проверьте подключение.');
        };

        xhr.send(formData);
    });

})();


/* ================================================================
    8. SCROLL TO TOP BUTTON
    ================================================================ */

(function() {
    'use strict';

    var btn = document.getElementById('scrollTop');
    if (!btn) return;

    window.addEventListener('scroll', function() {
        if (window.scrollY > 400) {
            btn.classList.add('visible');
        } else {
            btn.classList.remove('visible');
        }
    }, { passive: true });

    btn.addEventListener('click', function() {
        window.scrollTo({ top: 0, behavior: 'smooth' });
    });

})();

