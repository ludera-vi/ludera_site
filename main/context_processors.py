def extends_layout(request):
    if not request.user.is_authenticated:
        return {'extends_layout': 'cabinet/_layout.html'}
    role = getattr(getattr(request.user, 'profile', None), 'role', 'admin')
    if role == 'manager':
        return {'extends_layout': 'sales/base.html'}
    if request.user.is_superuser:
        return {'extends_layout': 'cabinet/_layout.html'}
    return {'extends_layout': 'cabinet/_layout.html'}


def sidebar_counts(request):
    from django.core.cache import cache
    from sales.models import Client, Call
    from django.db.models import OuterRef, Subquery
    from users.models import SuggestionMessage

    user = request.user
    if not user.is_authenticated:
        return {'sidebar_counts': {'suggestions_unread': 0}}

    role = getattr(getattr(user, 'profile', None), 'role', 'admin')
    if role == 'manager':
        return {'sidebar_counts': {}}

    cache_key = f'sidebar_counts:cabinet:{user.pk}'
    counts = cache.get(cache_key)
    if counts is None:
        def _last(*statuses):
            latest = Call.objects.filter(client=OuterRef('pk')).order_by('-created_at').values('status')[:1]
            return Client.objects.annotate(_s=Subquery(latest)).filter(_s__in=statuses)

        base = Client.objects.filter(is_deleted=False)
        from main.notification import _chat_unread_for_user
        from sales.models import InfoTopic, InfoTopicRead
        total_info = InfoTopic.objects.count()
        read_by_user = InfoTopicRead.objects.filter(user=user).values('topic').distinct().count()
        counts = {
            'called': _last('call_back', 'unavailable').filter(is_archived=False, is_deleted=False).count(),
            'in_progress': _last('negotiation', 'tz_creation', 'tz_approval', 'contract_signing', 'in_progress').filter(is_archived=False, is_deleted=False).count(),
            'completed': _last('completed').filter(is_archived=False, is_deleted=False).count(),
            'archive': base.filter(is_archived=True).count(),
            'deleted': Client.objects.filter(is_deleted=True).count(),
            'suggestions_unread': SuggestionMessage.objects.filter(
                author__is_superuser=False, is_read=False
            ).count() if user.is_superuser else 0,
            'chat_unread': _chat_unread_for_user(user.pk),
            'info_unread': total_info - read_by_user,
        }
        cache.set(cache_key, counts, 10)
    return {'sidebar_counts': counts}
