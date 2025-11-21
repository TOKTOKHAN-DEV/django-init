from django.apps import AppConfig


class UserConfig(AppConfig):
    name = "app.user"
    verbose_name = '02.유저'

    def ready(self):
        import app.user.signals
