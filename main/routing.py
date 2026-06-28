from django.urls import re_path

from . import consumers

websocket_urlpatterns = [
    re_path(r'^ws/suggestions/$', consumers.SuggestionConsumer.as_asgi()),
]
