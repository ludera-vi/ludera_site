import json

from channels.generic.websocket import AsyncWebsocketConsumer


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
        if self.user.is_superuser and hasattr(self, 'admin_group'):
            await self.channel_layer.group_discard(self.admin_group, self.channel_name)
        elif hasattr(self, 'manager_group'):
            await self.channel_layer.group_discard(self.manager_group, self.channel_name)

    async def send_message(self, event):
        await self.send(text_data=json.dumps(event['data'], ensure_ascii=False))
