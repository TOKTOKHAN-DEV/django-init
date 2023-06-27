from django.urls import include, path
from rest_framework.routers import DefaultRouter

from app.celery_log.v1.views import CeleryLogsViewSet

router = DefaultRouter()
router.register("celery_log", CeleryLogsViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
