from django.contrib import admin

from app.celery_logs.models import CeleryLogs


@admin.register(CeleryLogs)
class CeleryLogsAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "task_name",
        "task_id",
        "status",
        "created_at",
        "updated_at",
    )

    list_filter = (
        "status",
    )
