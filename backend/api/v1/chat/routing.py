from django.urls import path

from api.v1.chat.consumers import ChatConsumer

websocket_urlpatterns = [
    path("ws", ChatConsumer.as_asgi()),
]
