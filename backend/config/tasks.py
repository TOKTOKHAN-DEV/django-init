import os

from celery import Celery

from config.schedules import CELERY_BEAT_SCHEDULE

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.local")

app = Celery("config")

app.config_from_object("django.conf:settings", namespace="CELERY")
app.conf.beat_schedule = CELERY_BEAT_SCHEDULE

app.autodiscover_tasks()
