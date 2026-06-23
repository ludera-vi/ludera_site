import re

from django.utils.deprecation import MiddlewareMixin
from django.shortcuts import redirect
from .models import PageView


URL_SECTION_MAP = [
    (r'^/cabinet/$', None),  # dashboard доступен всем staff
    (r'^/cabinet/service/', 'services'),
    (r'^/cabinet/product/', 'products'),
    (r'^/cabinet/goods/', 'goods'),
    (r'^/cabinet/project/', 'projects'),
    (r'^/cabinet/blog/', 'blog'),
    (r'^/cabinet/contact/', 'contacts'),
    (r'^/cabinet/pageviews/', 'pageviews'),
    (r'^/cabinet/navlink/', 'structure'),
    (r'^/cabinet/principle/', 'structure'),
    (r'^/cabinet/user/', 'users'),
    (r'^/cabinet/users/', 'users'),
    (r'^/cabinet/usersetting/', 'users'),
    (r'^/cabinet/sitesetting/', 'settings'),
    (r'^/cabinet/herosection/', 'settings'),
    (r'^/cabinet/profile/', None),
    (r'^/cabinet/upload-image/', None),
]


class CabinetAccessMiddleware(MiddlewareMixin):
    def process_request(self, request):
        path = request.path
        if path.startswith('/cabinet/') and not path.startswith('/cabinet/login/') and not path.startswith('/cabinet/logout/'):
            if not request.user.is_authenticated:
                return redirect('/cabinet/login/')
            if not request.user.is_staff:
                return redirect('/account/login/')
            if not request.user.is_superuser:
                for pattern, section in URL_SECTION_MAP:
                    if re.match(pattern, path):
                        if section is None:
                            break
                        if not request.user.cabinet_permissions.filter(section=section).exists():
                            return redirect('cabinet:dashboard')
                        break


class PageViewMiddleware(MiddlewareMixin):
    def process_response(self, request, response):
        if not request.path.startswith('/admin') and not request.path.startswith('/static'):
            if response.status_code == 200:
                ip = request.META.get('REMOTE_ADDR', '')
                ua = request.META.get('HTTP_USER_AGENT', '')
                session = request.session.session_key or ''
                url = request.get_full_path()
                PageView.objects.create(
                    url=url,
                    user_agent=ua,
                    ip_address=ip or None,
                    session_key=session,
                )
        return response
