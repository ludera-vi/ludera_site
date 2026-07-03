from django.utils import timezone
from django.core.cache import cache
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.contrib.auth.models import User
from users.models import SuggestionMessage


def _clear_sidebar_cache(user_id):
    cache.delete(f'sidebar_counts:sales:{user_id}')
    cache.delete(f'sidebar_counts:cabinet:{user_id}')


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


def _sug_unread_for_admin():
    return SuggestionMessage.objects.filter(author__is_superuser=False, is_read=False).count()


def _sug_unread_for_manager(manager_id):
    return SuggestionMessage.objects.filter(suggestion__manager_id=manager_id, author__is_superuser=True, is_read=False).count()


def _chat_unread_for_user(user_id):
    from django.db import connection
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT COUNT(*) FROM (
                SELECT DISTINCT c.id FROM sales_chat c
                INNER JOIN sales_chatmember cm ON cm.chat_id = c.id AND cm.user_id = %s AND cm.is_active = TRUE
                WHERE c.is_deleted = FALSE
                AND EXISTS (
                    SELECT 1 FROM sales_chatmessage msg
                    WHERE msg.chat_id = c.id
                    AND msg.author_id != %s
                    AND msg.created_at > COALESCE(cm.last_read_at, '2000-01-01 00:00:00')
                )
            ) sub
        """, [user_id, user_id])
        return cursor.fetchone()[0]


def _info_unread_for_user(user_id):
    from sales.models import InfoTopic
    return InfoTopic.objects.exclude(reads__user_id=user_id).count()


def broadcast_suggestion_message(msg):
    sug = msg.suggestion
    channel_layer = get_channel_layer()
    data = _msg_data(msg)
    if msg.author.is_superuser:
        data['unread_count'] = _sug_unread_for_manager(sug.manager_id)
        _clear_sidebar_cache(sug.manager_id)
        async_to_sync(channel_layer.group_send)(
            f'suggestions_manager_{sug.manager_id}',
            {'type': 'send_message', 'data': data},
        )
    else:
        data['unread_count'] = _sug_unread_for_admin()
        for uid in User.objects.filter(is_superuser=True).values_list('pk', flat=True):
            _clear_sidebar_cache(uid)
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
        data['unread_count'] = _sug_unread_for_manager(suggestion.manager_id)
        _clear_sidebar_cache(suggestion.manager_id)
        async_to_sync(channel_layer.group_send)(
            f'suggestions_manager_{suggestion.manager_id}',
            {'type': 'send_message', 'data': data},
        )


def broadcast_suggestion_delete(suggestion):
    channel_layer = get_channel_layer()
    data = {'type': 'deleted', 'suggestion_pk': suggestion.pk}
    for uid in User.objects.filter(is_superuser=True).values_list('pk', flat=True):
        _clear_sidebar_cache(uid)
    async_to_sync(channel_layer.group_send)(
        'suggestions_admin',
        {'type': 'send_message', 'data': data},
    )
    if suggestion.manager_id:
        _clear_sidebar_cache(suggestion.manager_id)
        async_to_sync(channel_layer.group_send)(
            f'suggestions_manager_{suggestion.manager_id}',
            {'type': 'send_message', 'data': data},
        )


def broadcast_chat_message(msg):
    from sales.models import ChatMember
    channel_layer = get_channel_layer()
    ts = timezone.localtime(msg.created_at).strftime('%H:%M')
    aname = msg.author.get_full_name() or msg.author.email if msg.author else '—'
    members = list(ChatMember.objects.filter(chat=msg.chat, is_active=True).values_list('user_id', flat=True))
    for uid in members:
        _clear_sidebar_cache(uid)
    unreads = {uid: _chat_unread_for_user(uid) for uid in members}
    for uid in members:
        async_to_sync(channel_layer.group_send)(
            f'chats_user_{uid}',
            {
                'type': 'send_message',
                'data': {
                    'type': 'chat_message',
                    'chat_id': msg.chat_id,
                    'pk': msg.pk,
                    'message': msg.message,
                    'author_id': msg.author_id,
                    'author_name': aname,
                    'created_at': ts,
                    'unread_count': unreads[uid],
                },
            },
        )


def broadcast_chat_unread_update(user, chat_id=None):
    _clear_sidebar_cache(user.pk)
    channel_layer = get_channel_layer()
    data = {'type': 'chat_unread', 'unread_count': _chat_unread_for_user(user.pk)}
    if chat_id:
        data['chat_id'] = chat_id
    async_to_sync(channel_layer.group_send)(
        f'chats_user_{user.pk}',
        {'type': 'send_message', 'data': data},
    )


def broadcast_chat_member_update(chat, action, user, added_by=None):
    from sales.models import ChatMember
    channel_layer = get_channel_layer()
    members = list(ChatMember.objects.filter(chat=chat, is_active=True).values_list('user_id', flat=True))
    for uid in members:
        _clear_sidebar_cache(uid)
    unreads = {uid: _chat_unread_for_user(uid) for uid in members}
    for uid in members:
        data = {
            'type': 'chat_member_' + action,
            'chat_id': chat.pk,
            'user_id': user.pk,
            'user_name': user.get_full_name() or user.email,
            'unread_count': unreads[uid],
        }
        if added_by:
            data['added_by_id'] = added_by.pk
        async_to_sync(channel_layer.group_send)(
            f'chats_user_{uid}',
            {'type': 'send_message', 'data': data},
        )


def broadcast_info_topic(topic, action='created'):
    channel_layer = get_channel_layer()
    for user_id in User.objects.filter(is_active=True).values_list('pk', flat=True):
        _clear_sidebar_cache(user_id)
        async_to_sync(channel_layer.group_send)(
            f'info_user_{user_id}',
            {
                'type': 'send_message',
                'data': {
                    'type': 'info_' + action,
                    'topic_id': topic.pk,
                    'title': topic.title,
                    'unread_count': _info_unread_for_user(user_id),
                },
            },
        )


def broadcast_info_unread_update(user):
    _clear_sidebar_cache(user.pk)
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f'info_user_{user.pk}',
        {
            'type': 'send_message',
            'data': {
                'type': 'info_unread',
                'unread_count': _info_unread_for_user(user.pk),
            },
        },
    )


def broadcast_kanban_card(card, action, old_col_id=None):
    from sales.models import Column
    channel_layer = get_channel_layer()
    data = {
        'type': 'kanban_' + action,
        'card_pk': card.pk,
        'card_title': card.title,
        'column_id': card.column_id,
        'board_id': card.column.board_id,
        'position': card.position,
        'client_name': str(card.client) if card.client else '',
        'client_id': card.client_id,
        'responsible_name': card.responsible.get_full_name() or card.responsible.email if card.responsible else '',
        'responsible_id': card.responsible_id,
    }
    if old_col_id is not None:
        data['old_column_id'] = old_col_id
    async_to_sync(channel_layer.group_send)(
        'kanban',
        {'type': 'send_message', 'data': data},
    )
