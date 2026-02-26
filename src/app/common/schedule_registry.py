import importlib
from dataclasses import dataclass

from django.apps import apps


@dataclass
class ScheduleEntry:
    name: str
    path: str
    view_class: type
    cron_expression: str | None = None


class ScheduleRegistry:
    def __init__(self):
        self._registry: dict[str, ScheduleEntry] = {}

    def register(self, name: str, path: str, cron_expression: str | None = None):
        def decorator(cls):
            self._registry[name] = ScheduleEntry(
                name=name,
                cron_expression=cron_expression,
                path=path,
                view_class=cls,
            )
            return cls

        return decorator

    def all(self) -> dict[str, ScheduleEntry]:
        return self._registry


registry = ScheduleRegistry()
schedule = registry.register


def autodiscover():
    for app_config in apps.get_app_configs():
        try:
            importlib.import_module(f"{app_config.name}.schedule")
        except ModuleNotFoundError:
            pass
