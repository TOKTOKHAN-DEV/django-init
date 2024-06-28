from django.urls import include, path
from rest_framework.routers import DefaultRouter

from app.websocket_connection.v1.views import WebsocketConnectionViewSet

router = DefaultRouter()
router.register("websocket_connection", WebsocketConnectionViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
