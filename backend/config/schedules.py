from celery.schedules import crontab

CELERY_BEAT_SCHEDULE = dict(
    task_delete_withdrawal_user={
        "task": "app.withdrawal_user.tasks.task_delete_withdrawal_user",
        "schedule": crontab(hour="0"),
    },
)
