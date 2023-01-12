from django.db import models

from app.common.models import BaseModel


class LogStatus(models.TextChoices):
    SUCCESS = "S", "성공"
    FAILED = "F", "실패"


class EmailLog(BaseModel):
    to = models.EmailField(verbose_name="수신자")
    title = models.CharField(verbose_name="제목", max_length=256)
    body = models.TextField(verbose_name="내용")
    status = models.CharField(
        verbose_name="상태",
        editable=False,
        max_length=1,
        choices=LogStatus.choices,
        null=True,
        blank=True,
    )

    class Meta:
        db_table = "email_log"
        verbose_name = "이메일 로그"
        verbose_name_plural = verbose_name
        ordering = ["-created"]

    def __str__(self):
        return self.body


class PhoneLog(BaseModel):
    to = models.CharField(verbose_name="수신자", max_length=11)
    title = models.CharField(verbose_name="제목", max_length=64)
    body = models.TextField(verbose_name="내용")
    status = models.CharField(
        verbose_name="상태",
        editable=False,
        max_length=1,
        choices=LogStatus.choices,
        null=True,
        blank=True,
    )
    fail_reason = models.TextField(verbose_name="실패사유", null=True, blank=True)

    class Meta:
        db_table = "phone_log"
        verbose_name = "휴대폰 로그"
        verbose_name_plural = verbose_name
        ordering = ["-created"]

    def __str__(self):
        return self.body


class AlarmTalkLog(BaseModel):
    to = models.CharField(verbose_name="수신자", max_length=11)
    template_code = models.CharField(verbose_name="템플릿 코드", max_length=16)
    body = models.TextField(verbose_name="내용")
    status = models.CharField(
        verbose_name="상태",
        editable=False,
        max_length=1,
        choices=LogStatus.choices,
        null=True,
        blank=True,
    )
    fail_reason = models.TextField(verbose_name="실패사유", null=True, blank=True)

    class Meta:
        db_table = "alarm_talk_log"
        verbose_name = "알림톡 로그"
        verbose_name_plural = verbose_name
        ordering = ["-created"]


class PushLog(BaseModel):
    to = models.ForeignKey("user.User", verbose_name="수신자", on_delete=models.CASCADE)
    title = models.CharField(verbose_name="제목", max_length=64)
    body = models.TextField(verbose_name="내용")
    status = models.CharField(
        verbose_name="상태",
        editable=False,
        max_length=1,
        choices=LogStatus.choices,
        null=True,
        blank=True,
    )
    # keyword = models.CharField(verbose_name='키워드', max_length=64, null=True, blank=True)
    is_read = models.BooleanField(verbose_name="읽음", default=False)

    class Meta:
        db_table = "push_log"
        verbose_name = "푸시 로그"
        verbose_name_plural = verbose_name
        ordering = ["-created"]

    def __str__(self):
        return self.body


class TaskLog(BaseModel):
    class StatusChoices(models.TextChoices):
        SUCCESS = "S", "성공"
        FAIL = "F", "실패"

    title = models.CharField(verbose_name="제목", max_length=128, null=True, blank=True)
    body = models.TextField(verbose_name="내용", null=True, blank=True)
    status = models.TextField(verbose_name="상태", max_length=1, choices=StatusChoices.choices)

    class Meta:
        db_table = "task_log"
        verbose_name = "테스크 로그"
        verbose_name_plural = verbose_name
        ordering = ["-created"]

    def __str__(self):
        return self.title
