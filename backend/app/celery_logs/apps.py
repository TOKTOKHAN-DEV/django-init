from django.apps import AppConfig


class CeleryLogsConfig(AppConfig):
    name = "app.celery_logs"

    def ready(self):
        import app.celery_logs.signals
