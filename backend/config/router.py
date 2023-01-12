from django.conf import settings
from django.db import transaction


class Router:
    databases: list = list(settings.DATABASES.keys())
    default_app_labels: set = {}

    def db_for_read(self, model, **hints):
        if "reader" in self.databases:
            return "reader"
        return "default"

    @staticmethod
    def db_for_write(model, **hints):
        return "default"

    @staticmethod
    def allow_relation(obj1, obj2, **hints):
        return True

    @staticmethod
    def allow_migrate(db, app_label, model_name=None, **hints):
        return True

    def _check_default_app_label(self, app_label):
        if app_label in self.default_app_labels:
            return True

    @staticmethod
    def _check_in_atomic_block():
        transaction.get_autocommit()
        if transaction.get_connection("default").in_atomic_block:
            return True
