from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages


def cabinet_section_required(section):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('/cabinet/login/')
            if not request.user.is_staff:
                messages.error(request, 'У вас нет доступа к панели управления')
                return redirect('/account/login/')
            if not request.user.is_superuser:
                if not request.user.cabinet_permissions.filter(section=section).exists():
                    messages.error(request, 'У вас нет доступа к этому разделу')
                    return redirect('cabinet:dashboard')
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator
