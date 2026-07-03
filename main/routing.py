from django.urls import re_path

from . import consumers

websocket_urlpatterns = [
    re_path(r'^ws/suggestions/$', consumers.SuggestionConsumer.as_asgi()),
    re_path(r'^ws/kanban/$', consumers.KanbanConsumer.as_asgi()),
    re_path(r'^ws/chats/$', consumers.ChatConsumer.as_asgi()),
    re_path(r'^ws/info/$', consumers.InfoConsumer.as_asgi()),
]
