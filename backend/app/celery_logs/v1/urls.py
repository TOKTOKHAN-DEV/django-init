from django.urls import path, include
from rest_framework.routers import DefaultRouter

from app.celery_logs.v1.views import CeleryLogsViewSet

router = DefaultRouter()
router.register("celery_logs", CeleryLogsViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
