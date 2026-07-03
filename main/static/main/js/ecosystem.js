(function () {
    'use strict';

    /* ─── Scroll-reveal ─── */
    var revealEls = document.querySelectorAll('.ecosystem__grid > *');
    revealEls.forEach(function (el) {
        new IntersectionObserver(function (entries) {
            entries.forEach(function (e) {
                if (e.isIntersecting) { e.target.classList.add('ecosystem--visible'); this.unobserve(e.target); }
            });
        }, { threshold: 0.15 }).observe(el);
    });

    /* ─── 10 scripts (10 lines each = 20 items) ─── */
    var SCRIPTS = [
        [
            ['$', 'git push origin main'],
            ['>', 'Enumerating objects: 34, done.'],
            ['>', 'Writing objects: 100% (34/34), 8.2 MiB'],
            ['>', 'remote: Resolving deltas: 100% (12/12)'],
            ['✓', 'Branch main updated — commit f3a8e2d'],
            ['$', 'npm run build'],
            ['>', 'Building frontend for production...'],
            ['>', 'Assets: main.a7b3c9.css, vendor.d4e5f6.js'],
            ['✓', 'Build complete — 3.2s'],
            ['$', 'docker compose up -d --build'],
        ],
        [
            ['$', 'ludera init project --name crm-lite'],
            ['>', 'Scaffolding project structure...'],
            ['>', 'Creating Django project: crm_lite'],
            ['>', 'Configuring PostgreSQL database...'],
            ['✓', 'Project initialized in ./crm_lite'],
            ['$', 'ludera add module --name contacts'],
            ['>', 'Generating model: Contact, Company, Deal'],
            ['>', 'Creating REST endpoints...'],
            ['>', 'Setting up permissions...'],
            ['✓', 'Module contacts installed'],
        ],
        [
            ['$', 'ludera db backup'],
            ['>', 'Dumping PostgreSQL: ludera_prod (12 tables)'],
            ['>', 'Compressing: 248 MB — 67 MB'],
            ['>', 'Uploading to S3: backup-2026-06-18.gz'],
            ['✓', 'Backup complete — 4.8s'],
            ['$', 'ludera db migrate --name add_analytics'],
            ['>', 'Applying 0003_analytics... OK'],
            ['>', 'Applying 0004_analytics_indexes... OK'],
            ['>', 'Running data migration... 12,450 rows'],
            ['✓', 'Migration applied successfully'],
        ],
        [
            ['$', 'ludera ci run'],
            ['>', 'Pipeline: commit a7d3f9b (main)'],
            ['>', 'Stage 1/4: Linting — ESLint, flake8'],
            ['>', '134 files checked — 0 warnings'],
            ['✓', 'Linting passed — 12s'],
            ['$', 'ludera ci test'],
            ['>', 'Stage 2/4: Running test suite'],
            ['>', 'Unit tests: 248/248 passed'],
            ['>', 'Integration: 56/56 passed'],
            ['✓', 'Coverage: 94.2% — 45s'],
        ],
        [
            ['$', 'ludera infra setup'],
            ['>', 'Creating VPC: ludera-prod (10.0.0.0/16)'],
            ['>', 'Provisioning RDS, Redis, S3 bucket'],
            ['✓', 'Infrastructure ready — 2m 14s'],
            ['$', 'ludera ssl issue --domain ludera.ru'],
            ['>', 'Certificate issued: ludera.ru, *.ludera.ru'],
            ['>', 'Auto-renewal configured — 30 days'],
            ['✓', 'SSL/TLS active — grade A+'],
            ['$', 'curl https://status.ludera.ru/api/health'],
            ['>', 'crm: ok · chat: ok · web: ok'],
        ],
        [
            ['$', 'ludera generate module analytics'],
            ['>', 'Creating files: models, views, urls, tests'],
            ['>', 'Model: Event, Metric, Dashboard'],
            ['>', 'API: /api/v1/analytics/* (RESTful)'],
            ['✓', 'Module scaffolded — 8 files'],
            ['$', 'ludera generate report --name sales'],
            ['>', 'Building query: revenue by month, top clients'],
            ['>', 'Charts: bar, line, pie — Chart.js'],
            ['>', 'PDF export configured'],
            ['✓', 'Report sales ready — /reports/sales/'],
        ],
        [
            ['$', 'docker ps --format "table {{.Name}}\t{{.Status}}"'],
            ['>', 'ludera-crm       Up 14 days (healthy)'],
            ['>', 'ludera-chat      Up 14 days (healthy)'],
            ['>', 'ludera-web       Up 14 days (healthy)'],
            ['>', 'ludera-nginx     Up 14 days (healthy)'],
            ['✓', 'All 4 containers running'],
            ['$', 'docker compose logs api --tail 20'],
            ['>', 'api — 10:23:41 GET /api/v1/health 200'],
            ['>', 'api — 10:23:42 POST /api/v1/deals 201'],
            ['>', 'api — 10:23:44 GET /api/v1/contacts 200'],
            ['✓', 'Avg response: 24ms · p99: 86ms'],
        ],
        [
            ['$', 'ludera monitor setup'],
            ['>', 'Configuring Prometheus targets...'],
            ['>', 'Endpoints: api, worker, db, cache'],
            ['>', 'Scrape interval: 15s'],
            ['✓', 'Metrics collection active'],
            ['$', 'ludera alert add --rule high_latency'],
            ['>', 'Threshold: p99 latency > 500ms for 5m'],
            ['>', 'Channel: Telegram, Email'],
            ['>', 'Cooldown: 30m'],
            ['✓', 'Alert created — high_latency'],
            ['$', 'ludera dashboard --name overview'],
        ],
        [
            ['$', 'ludera api create --path /api/v2/leads'],
            ['>', 'Serializer: LeadSerializer (fields: 8)'],
            ['>', 'ViewSet: LeadViewSet (CRUD + search)'],
            ['>', 'Permissions: IsAuthenticated, IsStaff'],
            ['✓', 'Endpoint /api/v2/leads created'],
            ['$', 'ludera api docs --generate'],
            ['>', 'OpenAPI 3.0 spec generated'],
            ['>', 'Endpoints documented: 24'],
            ['>', 'Swagger UI: /api/docs/'],
            ['✓', 'API documentation ready'],
        ],
        [
            ['$', 'ludera perf profile --endpoint /api/v1/deals'],
            ['>', 'Analyzing query performance...'],
            ['>', 'N+1 queries detected: pipeline__stage'],
            ['>', 'Missing index: deals.created_at'],
            ['✓', 'Profile complete — 3 optimizations found'],
            ['$', 'ludera perf optimize --apply'],
            ['>', 'Adding index: deals_created_at_idx... OK'],
            ['>', 'Eager loading: pipeline + stage'],
            ['>', 'Query time: 340ms to 12ms'],
            ['✓', 'Performance improved 28x'],
            ['$', 'ludera perf benchmark --suite full'],
        ],
    ];

    var MESSAGES = [
        'Код написан, собран и запущен — всё, что вы видели в терминале, Ludera делает сама. Вам остаётся только пользоваться готовым решением.',
        'Пока выполняются миграции и настройки, Ludera уже подготовила ваш продукт к работе. Просто начните.',
        'Создание модулей, генерация эндпоинтов, настройка прав — Ludera берёт на себя всю рутину. Вы управляете бизнесом, а не кодом.',
        'Тесты пройдены, сборка готова, проект развёрнут — Ludera делает это за минуты. Вам не нужно думать о pipeline.',
        'Базы данных, API, сертификаты — всё настраивается автоматически. Ludera даёт готовый продукт, а не головную боль.',
        'Новый модуль одной командой — и всё готово. Ludera генерирует код, пока вы занимаетесь своими задачами.',
        'Контейнеры, логи, масштабирование — терминал показывает всю работу, которую Ludera делает за вас. Просто работайте.',
        'Метрики, алерты, дашборды — Ludera следит за проектом, чтобы вы могли сосредоточиться на бизнесе, а не на мониторинге.',
        'Документация API генерируется сама. Интеграции подключаются за минуты. Ludera убирает всё лишнее.',
        'Профилирование, оптимизация, бенчмарки — Ludera настраивает производительность. Вы просто получаете результат.',
    ];

    var termLines = [];
    for (var i = 0; i <= 11; i++) {
        var el = document.getElementById('termLine' + i);
        if (el) termLines.push(el);
    }
    var dividerEl = document.getElementById('termDivider');

    var scriptIdx = 0;

    function cls(p) {
        if (p === '✓') return 'terminal__line--success';
        return 'terminal__line--dim';
    }

    function setLine(num, prompt, text, visible) {
        var el = termLines[num];
        if (!el) return;
        el.className = 'terminal__line ' + cls(prompt) + (visible ? ' terminal__line--visible' : '');
        var pEl = el.querySelector('.terminal__prompt');
        var tEl = el.querySelector('.terminal__text');
        if (pEl) pEl.textContent = prompt || '';
        if (tEl) tEl.textContent = text || '';
    }

    function clearAll() {
        for (var i = 0; i < termLines.length; i++) setLine(i, '', '', false);
        if (dividerEl) dividerEl.className = 'terminal__divider-line';
    }

    function typeLine(num, prompt, text, done) {
        setLine(num, prompt, '', true);
        var tEl = termLines[num].querySelector('.terminal__text');
        if (!tEl) { if (done) done(); return; }

        var chars = text.split('');
        var pos = 0;
        tEl.textContent = '';

        function tick() {
            if (pos >= chars.length) {
                if (done) setTimeout(done, 150);
                return;
            }
            tEl.textContent += chars[pos];
            pos++;
            setTimeout(tick, 12 + Math.random() * 18);
        }
        tick();
    }

    function showDivider(done) {
        if (!dividerEl) { if (done) done(); return; }
        dividerEl.className = 'terminal__divider-line terminal__divider-line--show';
        if (done) setTimeout(done, 1200);
    }

    function typeMessage(msg, done) {
        showDivider(function () {
            setLine(10, '▸', '', true);
            termLines[10].classList.add('terminal__line--msg');
            var tEl = termLines[10].querySelector('.terminal__text');
            if (!tEl) { clearAll(); if (done) done(); return; }

            var chars = msg.split('');
            var pos = 0;
            tEl.textContent = '';

            function tick() {
                if (pos >= chars.length) {
                    setTimeout(function () {
                        clearAll();
                        if (done) done();
                    }, 4000);
                    return;
                }
                tEl.textContent += chars[pos];
                pos++;
                setTimeout(tick, 16 + Math.random() * 24);
            }
            tick();
        });
    }

    function runScript() {
        clearAll();
        var script = SCRIPTS[scriptIdx];
        var idx = 0;

        function next() {
            if (idx >= script.length) {
                typeMessage(MESSAGES[scriptIdx], function () {
                    scriptIdx = (scriptIdx + 1) % SCRIPTS.length;
                    runScript();
                });
                return;
            }
            var parts = script[idx];
            idx++;
            typeLine(idx - 1, parts[0], parts[1], next);
        }

        setTimeout(next, 400);
    }

    setTimeout(runScript, 600);
})();

/* ─── Flow Connectors ─── */
(function () {
    'use strict';

    var flowBody = document.querySelector('.flow__body');
    var flowSvg = document.querySelector('.flow__svg');
    if (!flowBody || !flowSvg) return;

    var NS = 'http://www.w3.org/2000/svg';
    var arrowId = 'flow-arrow';

    (function setupMarker() {
        var defs = document.createElementNS(NS, 'defs');
        var marker = document.createElementNS(NS, 'marker');
        marker.setAttribute('id', arrowId);
        marker.setAttribute('markerWidth', '7');
        marker.setAttribute('markerHeight', '5');
        marker.setAttribute('refX', '7');
        marker.setAttribute('refY', '2.5');
        marker.setAttribute('orient', 'auto');
        var poly = document.createElementNS(NS, 'polygon');
        poly.setAttribute('points', '0 0, 7 2.5, 0 5');
        poly.setAttribute('fill', '#5a7f74');
        marker.appendChild(poly);
        defs.appendChild(marker);
        flowSvg.appendChild(defs);
    })();

    function getRel(el) {
        var er = el.getBoundingClientRect();
        var cr = flowBody.getBoundingClientRect();
        var st = flowBody.scrollTop;
        return {
            t: er.top - cr.top + st,
            b: er.bottom - cr.top + st,
            l: er.left - cr.left,
            r: er.right - cr.left,
            cx: er.left + er.width / 2 - cr.left,
        };
    }

    function makePath(d, arrow, animate) {
        var p = document.createElementNS(NS, 'path');
        p.setAttribute('d', d);
        p.classList.add('flow__path');
        if (arrow) p.setAttribute('marker-end', 'url(#' + arrowId + ')');
        flowSvg.appendChild(p);
        if (animate) {
            var len = p.getTotalLength();
            p.style.strokeDasharray = len;
            p.style.strokeDashoffset = len;
        }
        return p;
    }

    function clearPaths() {
        var paths = flowSvg.querySelectorAll('.flow__path');
        for (var i = paths.length - 1; i >= 0; i--) paths[i].remove();
    }

    function animatePaths() {
        var paths = flowSvg.querySelectorAll('.flow__path');
        paths.forEach(function (p) {
            var len = p.getTotalLength();
            p.style.strokeDasharray = len;
            p.style.strokeDashoffset = len;
            p.getBoundingClientRect();
            p.style.strokeDashoffset = '0';
        });
    }

    function cubicBezier(x1, y1, x2, y2, x3, y3) {
        return ' C ' + x1 + ' ' + y1 + ', ' + x2 + ' ' + y2 + ', ' + x3 + ' ' + y3;
    }

    function smoothCurve(ax, ay, bx, by, arrow, animate) {
        var dx = bx - ax;
        var dy = by - ay;
        var cx1 = ax + dx * 0.4;
        var cy1 = ay + dy * 0.35;
        var cx2 = bx - dx * 0.4;
        var cy2 = by - dy * 0.35;
        makePath('M ' + ax + ' ' + ay + cubicBezier(cx1, cy1, cx2, cy2, bx, by), arrow, animate);
    }

    function draw(animate) {
        clearPaths();

        var client = document.querySelector('.flow__card--client');
        var analysis = document.querySelector('.flow__card--analysis');
        var custom = document.querySelector('.flow__card--custom');
        var ready = document.querySelector('.flow__card--ready');
        var support = document.querySelector('.flow__card--support');
        if (!client || !analysis || !custom || !ready || !support) return;

        var c = getRel(client);
        var a = getRel(analysis);
        var cu = getRel(custom);
        var r = getRel(ready);
        var s = getRel(support);

        var split = document.querySelector('.flow__split');
        var cols = split && window.getComputedStyle(split).gridTemplateColumns;
        var isStacked = split && cols.split(' ').length === 1;

        /* ─── Connector 1: Client → Analysis (прямая вертикальная) ─── */
        var gap1 = a.t - c.b;
        makePath(
            'M ' + c.cx + ' ' + c.b +
            ' C ' + c.cx + ' ' + (c.b + gap1 * 0.5) +
            ', ' + a.cx + ' ' + (a.t - gap1 * 0.5) +
            ', ' + a.cx + ' ' + a.t,
            true, animate
        );

        if (isStacked) {
            /* ─── Mobile: последовательные вертикальные линии ─── */
            smoothCurve(a.cx, a.b, cu.cx, cu.t, true, animate);
            smoothCurve(cu.cx, cu.b, r.cx, r.t, true, animate);
            smoothCurve(r.cx, r.b, s.cx, s.t, true, animate);
        } else {
            /* ─── Desktop: Branching (Analysis → Custom & Ready) ─── */
            smoothCurve(a.cx, a.b, cu.cx, cu.t, true, animate);
            smoothCurve(a.cx, a.b, r.cx, r.t, true, animate);

            /* ─── Desktop: Merging (Custom & Ready → Support) ─── */
            var lx2 = cu.cx, ly2 = cu.b;
            var rx2 = r.cx, ry2 = r.b;
            var sx = s.cx, sy = s.t;

            var maxBottom = Math.max(ly2, ry2);
            var mpY = sy - (sy - maxBottom) * 0.45;

            smoothCurve(lx2, ly2, sx, mpY, false, animate);
            smoothCurve(rx2, ry2, sx, mpY, false, animate);

            var stemGap = sy - mpY;
            makePath(
                'M ' + sx + ' ' + mpY +
                ' C ' + sx + ' ' + (mpY + stemGap * 0.5) +
                ', ' + sx + ' ' + (sy - stemGap * 0.5) +
                ', ' + sx + ' ' + sy,
                true, animate
            );
        }

        if (animate) {
            requestAnimationFrame(function () {
                requestAnimationFrame(animatePaths);
            });
        }
    }

    function tryDraw(animate) {
        if (document.fonts && document.fonts.ready) {
            document.fonts.ready.then(function () {
                draw(animate);
            });
        } else {
            draw(animate);
        }
    }

    /* ─── Observe visibility ─── */
    var diagram = document.querySelector('.ecosystem__diagram');
    if (diagram) {
        var revealObs = new MutationObserver(function () {
            if (diagram.classList.contains('ecosystem--visible')) {
                tryDraw(true);
                revealObs.disconnect();
            }
        });
        revealObs.observe(diagram, { attributes: true, attributeFilter: ['class'] });
        if (diagram.classList.contains('ecosystem--visible')) tryDraw(true);
    }

    /* ─── Redraw on resize/orientation/scroll ─── */
    var redrawTimer;
    function scheduleRedraw() {
        clearTimeout(redrawTimer);
        redrawTimer = setTimeout(function () { draw(false); }, 80);
    }

    var resizeObs = new ResizeObserver(function () {
        scheduleRedraw();
    });
    resizeObs.observe(flowBody);

    flowBody.addEventListener('scroll', scheduleRedraw, { passive: true });
})();
