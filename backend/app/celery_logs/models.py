from django.db import models

from app.common.models import BaseModel


class CeleryLogs(BaseModel):
    class TaskStatus(models.TextChoices):
        PENDING = "PENDING", "대기"
        SUCCESS = "SUCCESS", "성공"
        FAIL = "FAIL", "실패"

    task_name = models.CharField(max_length=500, verbose_name="태스크 명")
    task_id = models.CharField(max_length=500, verbose_name="태스크 ID")
    status = models.CharField(max_length=10, verbose_name="태스크 상태", default=TaskStatus.choices)
    process_time = models.FloatField(verbose_name="실행 시간", blank=True, null=True)
    message = models.TextField(verbose_name="메세지", blank=True, null=True)

    class Meta:
        db_table = "celery_logs"
        verbose_name = "셀러리 로그"
        verbose_name_plural = verbose_name
        ordering = ["-created_at"]
