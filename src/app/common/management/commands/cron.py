import json

import boto3
from django.conf import settings
from django.core.management import BaseCommand

from app.common.schedule_client import ScheduleClient
from app.common.schedule_registry import autodiscover, registry


class Command(BaseCommand):
    help = "cron을 등록합니다."
    prefix = f"{settings.PROJECT_NAME}-{settings.APP_ENV}-"

    def handle(self, *args, **options):
        autodiscover()
        schedules = registry.all()

        event_client = boto3.client("events", region_name="ap-northeast-2")
        event_client.update_api_destination(
            Name=f"{self.prefix}api-destination",
            InvocationEndpoint=f"{settings.API_URL}/*",
        )

        client = ScheduleClient()
        for schedule in client.list():
            client.delete(name=schedule["name"])

        for name, entry in schedules.items():
            if not entry.cron_expression:
                continue

            client.create(
                f"{self.prefix}cron-{name}",
                f"cron({entry.cron_expression})",
                path=entry.path,
            )
