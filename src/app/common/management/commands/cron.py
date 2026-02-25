import json

import boto3
from django.conf import settings
from django.core.management import BaseCommand

from app.common.schedule_registry import autodiscover, registry


class Command(BaseCommand):
    help = "cron을 등록합니다."
    prefix = f"{settings.PROJECT_NAME}-{settings.APP_ENV}-cron-"

    def handle(self, *args, **options):
        autodiscover()
        schedules = registry.all()
        scheduler = boto3.client("scheduler", region_name="ap-northeast-2")

        for name in schedules:
            try:
                scheduler.delete_schedule(Name=f"{self.prefix}{name}")
            except scheduler.exceptions.ResourceNotFoundException:
                pass

        for name, entry in schedules.items():
            if not entry.cron_expression:
                continue
            scheduler.create_schedule(
                Name=f"{self.prefix}{name}",
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
