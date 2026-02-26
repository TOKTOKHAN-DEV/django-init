import json

import boto3
from django.conf import settings


class ScheduleClient:
    client = boto3.client("scheduler", region_name="ap-northeast-2")
    prefix = f"{settings.PROJECT_NAME}-{settings.APP_ENV}"

    def list(self):
        response = self.client.list_schedules(NamePrefix=self.prefix)
        return response["Schedules"]

    def create(self, name, expression, path):
        self.client.create_schedule(
            Name=name,
            ScheduleExpression=expression,
            ScheduleExpressionTimezone="Asia/Seoul",
            ActionAfterCompletion="DELETE",
            FlexibleTimeWindow={"Mode": "OFF"},
            Target={
                "Arn": f"arn:aws:events:ap-northeast-2:{settings.AWS_ACCOUNT_ID}:event-bus/default",
                "RoleArn": f"arn:aws:iam::{settings.AWS_ACCOUNT_ID}:role/{self.prefix}-EventBridgeSchedulerRole",
                "EventBridgeParameters": {
                    "DetailType": "Scheduled Event",
                    "Source": f"{self.prefix}.scheduler",
                },
                "Input": json.dumps({"path": f"schedule/{path}"}),
                "RetryPolicy": {"MaximumRetryAttempts": 0},
            },
        )

    def delete(self, name):
        self.client.delete_schedule(Name=name)
