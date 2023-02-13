from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.v1.post.views import PostViewSet

router = DefaultRouter()
router.register("post", PostViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
