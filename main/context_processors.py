def extends_layout(request):
    if not request.user.is_authenticated:
        return {'extends_layout': 'cabinet/_layout.html'}
    role = getattr(getattr(request.user, 'profile', None), 'role', 'admin')
    if role == 'manager':
        return {'extends_layout': 'sales/base.html'}
    return {'extends_layout': 'cabinet/_layout.html'}


def sidebar_counts(request):
    from sales.models import Client
    from django.db.models import Q

    base = Client.objects.filter(is_archived=False)
    counts = {
        'sidebar_counts': {
            'clients': base.count(),
            'in_progress': base.filter(
                calls__isnull=False
            ).exclude(calls__status__in=['refusal', 'completed']).distinct().count(),
            'completed': base.filter(calls__status='completed').distinct().count(),
        }
    }
    if getattr(getattr(request.user, 'profile', None), 'role', 'admin') == 'manager' or request.user.is_superuser:
        counts['sidebar_counts']['called'] = base.filter(calls__isnull=False).distinct().count()
    return counts
