from django.urls import include, path
from rest_framework.routers import DefaultRouter

from app.admin_user.v1.views import AdminUserViewSet

router = DefaultRouter()
router.register("admin_user", AdminUserViewSet, basename="admin_user")

urlpatterns = [
    path("", include(router.urls)),
]
