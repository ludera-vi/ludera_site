import json
from channels.generic.websocket import AsyncWebsocketConsumer
from django.utils import timezone


class SuggestionConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope['user']
        if not self.user.is_authenticated:
            await self.close()
            return
        self.admin_group = 'suggestions_admin'
        self.manager_group = f'suggestions_manager_{self.user.id}'
        if self.user.is_superuser:
            await self.channel_layer.group_add(self.admin_group, self.channel_name)
        else:
            await self.channel_layer.group_add(self.manager_group, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        if not hasattr(self, 'admin_group') or not hasattr(self, 'manager_group'):
            return
        if self.user.is_superuser:
            await self.channel_layer.group_discard(self.admin_group, self.channel_name)
        else:
            await self.channel_layer.group_discard(self.manager_group, self.channel_name)

    async def send_message(self, event):
        await self.send(text_data=json.dumps(event['data'], ensure_ascii=False))


class KanbanConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope['user']
        if not self.user.is_authenticated:
            await self.close()
            return
        await self.channel_layer.group_add('kanban', self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard('kanban', self.channel_name)

    async def send_message(self, event):
        await self.send(text_data=json.dumps(event['data'], ensure_ascii=False))


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope['user']
        if not self.user.is_authenticated:
            await self.close()
            return
        self.user_group = f'chats_user_{self.user.id}'
        await self.channel_layer.group_add(self.user_group, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.user_group, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        if data.get('action') == 'mark_read':
            chat_id = data.get('chat_id')
            if chat_id:
                from sales.models import ChatMember
                ChatMember.objects.filter(chat_id=chat_id, user=self.user).update(
                    last_read_at=timezone.now()
                )
                from main.notification import broadcast_chat_unread_update
                from asgiref.sync import sync_to_async
                await sync_to_async(broadcast_chat_unread_update)(self.user)

    async def send_message(self, event):
        await self.send(text_data=json.dumps(event['data'], ensure_ascii=False))


class InfoConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope['user']
        if not self.user.is_authenticated:
            await self.close()
            return
        self.user_group = f'info_user_{self.user.id}'
        await self.channel_layer.group_add(self.user_group, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.user_group, self.channel_name)

    async def send_message(self, event):
        await self.send(text_data=json.dumps(event['data'], ensure_ascii=False))
