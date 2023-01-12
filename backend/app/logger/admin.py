from django.contrib import admin

from app.logger.models import EmailLog, PhoneLog, PushLog, TaskLog


@admin.register(EmailLog)
class EmailLogAdmin(admin.ModelAdmin):
    pass


@admin.register(PhoneLog)
class PhoneLogAdmin(admin.ModelAdmin):
    pass


@admin.register(PushLog)
class PushLogAdmin(admin.ModelAdmin):
    pass


@admin.register(TaskLog)
class TaskLogAdmin(admin.ModelAdmin):
    pass
