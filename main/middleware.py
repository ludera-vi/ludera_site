import re
from datetime import timedelta

from django.utils.deprecation import MiddlewareMixin
from django.shortcuts import redirect
from django.utils import timezone
from django.conf import settings
from .models import PageView


URL_SECTION_MAP = [
    (r'^/cabinet/$', None),
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
    (r'^/cabinet/sociallink/', 'settings'),
    (r'^/cabinet/profile/', None),
    (r'^/cabinet/upload-image/', None),
]


class CabinetAccessMiddleware(MiddlewareMixin):
    def process_request(self, request):
        path = request.path
        if not path.startswith('/cabinet/'):
            return
        if path.startswith('/cabinet/login/') or path.startswith('/cabinet/logout/'):
            return
        if not request.user.is_authenticated:
            return redirect('/cabinet/login/')
        role = getattr(getattr(request.user, 'profile', None), 'role', 'admin')
        if path.startswith('/cabinet/manager-panel/'):
            if role == 'manager' or request.user.is_superuser:
                return
            return redirect('/cabinet/')
        if role == 'manager':
            for pattern, section in URL_SECTION_MAP:
                if re.match(pattern, path):
                    if section and request.user.cabinet_permissions.filter(section=section).exists():
                        return
                    break
            return redirect('/cabinet/manager-panel/')
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
        if settings.DEBUG:
            return response
        if request.path.startswith('/admin') or request.path.startswith('/static'):
            return response
        if response.status_code != 200:
            return response
        session = request.session.session_key or ''
        if not session:
            return response
        url = request.get_full_path()
        today = timezone.now().date()
        exists = PageView.objects.filter(
            session_key=session, url=url, timestamp__date=today,
        ).exists()
        if not exists:
            PageView.objects.create(
                url=url,
                user_agent=request.META.get('HTTP_USER_AGENT', ''),
                ip_address=request.META.get('REMOTE_ADDR', None),
                session_key=session,
            )
        return response
