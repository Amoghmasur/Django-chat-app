from django.urls import path
from . import consumers_chat


websocket_urlpatterns = [
    path('chat/', consumers_chat.ChatConsumer.as_asgi()),
]
