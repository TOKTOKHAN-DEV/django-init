from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import mixins
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from app.websocket_connection.models import WebsocketConnection
from app.websocket_connection.v1.serializers import WebsocketConnectionSerializer


@extend_schema_view(
    create=extend_schema(summary="WebsocketConnection 등록"),
    destroy=extend_schema(summary="WebsocketConnection 삭제"),
)
class WebsocketConnectionViewSet(
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    GenericViewSet,
):
    queryset = WebsocketConnection.objects.all()
    serializer_class = WebsocketConnectionSerializer
    permission_classes = []

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset

    @action(methods=["POST"], detail=False)
    def connect(self, request, *args, **kwargs):
        print(request.data)
        return Response(status=200)

    @action(methods=["POST"], detail=False)
    def disconnect(self, request, *args, **kwargs):
        print(request.data)
        return Response()
