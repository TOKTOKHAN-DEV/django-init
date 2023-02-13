from celery.schedules import crontab

CELERY_BEAT_SCHEDULE = dict(
    task_korea_timezone={
        "task": "app.user.tasks.task_korea_timezone",
        "schedule": crontab(hour="18,19,20,21,22"),
    },
)
