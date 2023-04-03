from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application

import app.chat.v1.routing
from config.ws_middleware import TokenAuthMiddlewareStack

application = ProtocolTypeRouter(
    {
        "http": get_asgi_application(),
        "websocket": TokenAuthMiddlewareStack(
            URLRouter(
                [
                    *app.chat.v1.routing.websocket_urlpatterns,
                ]
            ),
        ),
    }
)
