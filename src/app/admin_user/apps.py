from django.apps import AppConfig


class AdminUserConfig(AppConfig):
    name = "app.admin_user"

    def ready(self):
        import app.admin_user.signals
