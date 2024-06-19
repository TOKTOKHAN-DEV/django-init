import boto3
from django.conf import settings
from django.core.management import BaseCommand
from drf_spectacular.generators import EndpointEnumerator

from app.common.utils import color_string


class Command(BaseCommand):
    help = "cron을 등록합니다."

    def handle(self, *args, **options):
        project_name = settings.PROJECT_NAME
        app_env = settings.APP_ENV
        enumerator = EndpointEnumerator(urlconf="config.urls.cron")
        api_endpoints = [
            api_endpoint[0] for api_endpoint in enumerator.get_api_endpoints() if api_endpoint[2] == "POST"
        ]
        for i, path in enumerate(api_endpoints):
            print(color_string("cyan", f"{i}. {path}"))
        endpoint_index = int(input(color_string("red", "엔드포인트를 선택하세요: ")))
        endpoint = api_endpoints[endpoint_index]

        minute = input(color_string("red", "분(0-59, default: *)")) or "*"
        hour = input(color_string("red", "시(0-24, default: *)")) or "*"
        day = input(color_string("red", "일(0-31, default: *)")) or "*"
        month = input(color_string("red", "월(1-12, default: *)")) or "*"
        weekday = "?"
        year = input(color_string("red", "년(yyyy, default: *)")) or "*"

        schedule_expression = f"cron({minute} {hour} {day} {month} {weekday} {year})"

        iam_client = boto3.client("iam")
        event_client = boto3.client("events")
        prefix = f"{project_name}-{app_env}-"
        rule_name = prefix + endpoint[1:-1].replace("/", "_")

        rule = event_client.put_rule(
            Name=rule_name,
            ScheduleExpression=schedule_expression,
            State="ENABLED",
        )

        api_destination_name = f"{project_name}-{app_env}-api-destination"
        api_destination_arn = event_client.describe_api_destination(Name=api_destination_name)["ApiDestinationArn"]
        event_client.update_api_destination(
            Name=api_destination_name,
            InvocationEndpoint=f"https://api.{settings.DOMAIN}/*",
        )

        role = iam_client.get_role(RoleName=f"{project_name}-{app_env}-InvokeApiDestinationRole")["Role"]

        event_client.put_targets(
            Rule=rule["RuleArn"].split("/", 1)[-1],
            Targets=[
                {
                    "Id": rule_name,
                    "Arn": api_destination_arn,
                    "RoleArn": role["Arn"],
                    "HttpParameters": {
                        "PathParameterValues": [endpoint[1:]],
                    },
                }
            ],
        )
