import json

import boto3
from django.conf import settings
from django.core.management import BaseCommand

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

        scheduler_client = boto3.client("scheduler", region_name="ap-northeast-2")

        schedules_response = scheduler_client.list_schedules(NamePrefix=self.prefix)["Schedules"]
        for schedule in schedules_response:
            scheduler_client.delete_schedule(Name=schedule["Name"])

        for name, entry in schedules.items():
            if not entry.cron_expression:
                continue
            scheduler_client.create_schedule(
                Name=f"{self.prefix}cron-{name}",
                ScheduleExpression=f"cron({entry.cron_expression})",
                ScheduleExpressionTimezone="Asia/Seoul",
                FlexibleTimeWindow={"Mode": "OFF"},
                Target={
                    "Arn": f"arn:aws:events:ap-northeast-2:{settings.AWS_ACCOUNT_ID}:event-bus/default",
                    "RoleArn": f"arn:aws:iam::{settings.AWS_ACCOUNT_ID}:role/{settings.PROJECT_NAME}-{settings.APP_ENV}-EventBridgeSchedulerRole",
                    "EventBridgeParameters": {
                        "DetailType": "Scheduled Event",
                        "Source": f"{settings.PROJECT_NAME}-{settings.APP_ENV}.scheduler",
                    },
                    "Input": json.dumps({"path": f"schedule/{entry.path}"}),
                    "RetryPolicy": {"MaximumRetryAttempts": 0},
                },
            )
