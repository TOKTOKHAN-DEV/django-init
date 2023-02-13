from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import mixins
from rest_framework.viewsets import GenericViewSet

from api.common.pagination import CursorPagination
from api.v1.post.filters import PostFilter
from api.v1.post.permissions import PostPermission
from api.v1.post.serializers import PostSerializer
from app.post.models import Post


@extend_schema_view(
    list=extend_schema(summary="Post 목록 조회"),
    create=extend_schema(summary="Post 등록"),
    retrieve=extend_schema(summary="Post 상세 조회"),
    update=extend_schema(summary="Post 수정"),
    partial_update=extend_schema(exclude=True),
    destroy=extend_schema(summary="Post 삭제"),
)
class PostViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    GenericViewSet,
):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [PostPermission]
    pagination_class = CursorPagination
    filter_class = PostFilter

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset
