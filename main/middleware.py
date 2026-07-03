import re
from collections import defaultdict
from datetime import timedelta

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


class CabinetAccessMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        path = request.path
        if not path.startswith('/cabinet/') and not path.startswith('/manager/'):
            return self.get_response(request)

        # Public auth-free paths
        if path.startswith('/cabinet/login/') or path.startswith('/cabinet/logout/'):
            return self.get_response(request)
        if path.startswith('/manager/login/') or path.startswith('/manager/logout/'):
            return self.get_response(request)

        if not request.user.is_authenticated:
            if path.startswith('/manager/'):
                return redirect('/manager/login/')
            return redirect('/cabinet/login/')

        role = getattr(getattr(request.user, 'profile', None), 'role', 'admin')

        if path.startswith('/manager/'):
            if role == 'manager':
                return self.get_response(request)
            return redirect('/cabinet/')

        if path.startswith('/cabinet/'):
            if role == 'admin' or request.user.is_superuser:
                return self.get_response(request)
            return redirect('/manager/login/')

        return self.get_response(request)


class PageViewMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
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
        if not PageView.objects.filter(
            session_key=session, url=url, timestamp__date=today,
        ).exists():
            PageView.objects.create(
                url=url,
                user_agent=request.META.get('HTTP_USER_AGENT', ''),
                ip_address=request.META.get('REMOTE_ADDR', None),
                session_key=session,
            )
        return response
