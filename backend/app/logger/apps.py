from django.apps import AppConfig


class LoggerConfig(AppConfig):
    name = "app.logger"

    def ready(self):
        import app.logger.signals
