from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import mixins
from rest_framework.viewsets import GenericViewSet

from app.celery_log.models import CeleryLogs
from app.celery_log.v1.filters import CeleryLogsFilter
from app.celery_log.v1.permissions import CeleryLogsPermission
from app.celery_log.v1.serializers import CeleryLogsSerializer
from app.common.pagination import CursorPagination


@extend_schema_view(
    list=extend_schema(summary="CeleryLogs 목록 조회"),
    create=extend_schema(summary="CeleryLogs 등록"),
    retrieve=extend_schema(summary="CeleryLogs 상세 조회"),
    update=extend_schema(summary="CeleryLogs 수정"),
    partial_update=extend_schema(exclude=True),
    destroy=extend_schema(summary="CeleryLogs 삭제"),
)
class CeleryLogsViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    GenericViewSet,
):
    queryset = CeleryLogs.objects.all()
    serializer_class = CeleryLogsSerializer
    permission_classes = [CeleryLogsPermission]
    pagination_class = CursorPagination
    filter_class = CeleryLogsFilter

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset
