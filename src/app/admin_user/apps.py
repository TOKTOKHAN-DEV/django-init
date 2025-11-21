from django.apps import AppConfig


class AdminUserConfig(AppConfig):
    name = "app.admin_user"
    verbose_name = '01.관리자'

    def ready(self):
        import app.admin_user.signals
