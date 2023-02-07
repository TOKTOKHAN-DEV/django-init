from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.v1.user.views import UserViewSet

router = DefaultRouter()
router.register("user", UserViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
