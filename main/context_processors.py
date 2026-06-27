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
    from users.models import ManagerSuggestion, SuggestionMessage

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
    user = request.user
    if user.is_authenticated:
        role = getattr(getattr(user, 'profile', None), 'role', 'admin')
        if role == 'manager':
            counts['sidebar_counts']['suggestions_unread'] = SuggestionMessage.objects.filter(
                suggestion__manager=user,
                author__is_superuser=True,
                is_read=False
            ).count()
        elif user.is_superuser:
            counts['sidebar_counts']['suggestions_unread'] = ManagerSuggestion.objects.filter(
                status='unread'
            ).count() + SuggestionMessage.objects.filter(
                author__is_superuser=False,
                is_read=False
            ).count()
        else:
            counts['sidebar_counts']['suggestions_unread'] = 0
        if role == 'manager' or user.is_superuser:
            counts['sidebar_counts']['called'] = base.filter(calls__isnull=False).distinct().count()
    else:
        counts['sidebar_counts']['suggestions_unread'] = 0
    return counts
