from django.utils import timezone
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from users.models import SuggestionMessage


def _msg_data(msg):
    sug = msg.suggestion
    t = timezone.localtime(msg.created_at)
    data = {
        'type': 'new_message',
        'suggestion_pk': sug.pk,
        'pk': msg.pk,
        'message': msg.message,
        'author': msg.author.get_full_name() or msg.author.email,
        'is_superuser': msg.author.is_superuser,
        'time': t.strftime('%H:%M'),
    }
    if msg.author.is_superuser:
        data['sug_is_closed'] = sug.is_closed
    else:
        data['sug_manager_name'] = sug.manager.get_full_name() or sug.manager.email
        data['sug_created'] = timezone.localtime(sug.created_at).strftime('%d.%m.%Y %H:%M')
        data['sug_status'] = sug.status
        data['sug_is_closed'] = sug.is_closed
        data['sug_preview'] = sug.message[:70]
    return data


def broadcast_suggestion_message(msg):
    sug = msg.suggestion
    channel_layer = get_channel_layer()
    data = _msg_data(msg)

    if msg.author.is_superuser:
        data['unread_count'] = SuggestionMessage.objects.filter(
            suggestion__manager=sug.manager,
            author__is_superuser=True,
            is_read=False,
        ).count()
        async_to_sync(channel_layer.group_send)(
            f'suggestions_manager_{sug.manager_id}',
            {'type': 'send_message', 'data': data},
        )
    else:
        data['unread_count'] = SuggestionMessage.objects.filter(
            author__is_superuser=False,
            is_read=False,
        ).count()
        async_to_sync(channel_layer.group_send)(
            'suggestions_admin',
            {'type': 'send_message', 'data': data},
        )


def broadcast_status_change(suggestion):
    channel_layer = get_channel_layer()
    data = {
        'type': 'status_changed',
        'suggestion_pk': suggestion.pk,
        'status': suggestion.status,
        'is_closed': suggestion.is_closed,
    }
    if suggestion.manager_id:
        data['unread_count'] = SuggestionMessage.objects.filter(
            suggestion__manager=suggestion.manager,
            author__is_superuser=True,
            is_read=False,
        ).count()
        async_to_sync(channel_layer.group_send)(
            f'suggestions_manager_{suggestion.manager_id}',
            {'type': 'send_message', 'data': data},
        )
