import boto3
from django.conf import settings
from django.core.management import BaseCommand
from drf_spectacular.generators import EndpointEnumerator


class ConsoleColors:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"


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
            print(f"{i}.", path)
        endpoint_index = int(input(self.get_log_color(ConsoleColors.RED, "엔드포인트를 선택하세요: ")))
        endpoint = api_endpoints[endpoint_index]

        minute = input(self.get_log_color(ConsoleColors.RED, "분(default: *)")) or "*"
        hour = input(self.get_log_color(ConsoleColors.RED, "시(default: *)")) or "*"
        day = input(self.get_log_color(ConsoleColors.RED, "일(default: *)")) or "*"
        month = input(self.get_log_color(ConsoleColors.RED, "월(default: *)")) or "*"
        weekday = "?"
        year = input(self.get_log_color(ConsoleColors.RED, "년(default: *)")) or "*"

        schedule_expression = f"cron({minute} {hour} {day} {month} {weekday} {year})"

        event_client = boto3.client("events")
        rule_name = endpoint[0][1:-1].replace("/", "-")
        rule = event_client.put_rule(
            Name=rule_name,
            ScheduleExpression=schedule_expression,
            State="ENABLED",
        )
        api_destination_arn = event_client.describe_api_destination(Name=f"{project_name}-{app_env}-api-destination")[
            "ApiDestinationArn"
        ]
        iam_client = boto3.client("iam")
        role = iam_client.get_role(RoleName=f"{project_name}-{app_env}-InvokeApiDestinationRole")["Role"]
        event_client.put_targets(
            Rule=rule["RuleArn"].split("/", 1)[-1],
            Targets=[
                {
                    "Id": rule_name,
                    "Arn": api_destination_arn,
                    "RoleArn": role["Arn"],
                    "HttpParameters": {
                        "PathParameterValues": [endpoint[0].replace("/cron/")],
                    },
                }
            ],
        )

    @staticmethod
    def get_log_color(color, text):
        return color + str(text) + ConsoleColors.RESET
