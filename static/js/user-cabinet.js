(function () {
    var sidebar = document.getElementById('userSidebar');
    var overlay = document.getElementById('userSidebarOverlay');
    var toggle = document.getElementById('userSidebarToggle');

    if (!sidebar || !overlay || !toggle) return;

    function openSidebar() {
        sidebar.classList.add('user-sidebar--open');
        overlay.classList.add('open');
        toggle.setAttribute('aria-label', 'Закрыть меню');
        document.body.style.overflow = 'hidden';
    }

    function closeSidebar() {
        sidebar.classList.remove('user-sidebar--open');
        overlay.classList.remove('open');
        toggle.setAttribute('aria-label', 'Открыть меню');
        document.body.style.overflow = '';
    }

    toggle.addEventListener('click', function () {
        if (sidebar.classList.contains('user-sidebar--open')) {
            closeSidebar();
        } else {
            openSidebar();
        }
    });

    overlay.addEventListener('click', closeSidebar);

    document.addEventListener('keydown', function (e) {
        if (e.key === 'Escape' && sidebar.classList.contains('user-sidebar--open')) {
            closeSidebar();
        }
    });

    var navLinks = sidebar.querySelectorAll('.user-nav__link');
    for (var i = 0; i < navLinks.length; i++) {
        navLinks[i].addEventListener('click', function () {
            if (window.innerWidth <= 768) {
                closeSidebar();
            }
        });
    }
})();
