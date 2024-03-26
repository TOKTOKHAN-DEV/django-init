from datetime import datetime

import boto3
from django.conf import settings
from django.core.management.base import BaseCommand


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
    help = "AWS CloudWatch 로그를 확인합니다."

    def add_arguments(self, parser):
        parser.add_argument("env", type=str, choices=["dev", "prod"], help="env")
        parser.add_argument("log_level", type=str, choices=["info", "error"], help="loglevel")

    def handle(self, *args, **options):
        env = options.get("env")
        log_level = options.get("log_level")
        self.get_log_tail(env, log_level)

    def get_log_tail(self, env, log_level):
        logs_client = boto3.client("logs")
        response = logs_client.describe_log_groups(logGroupNamePrefix=f"{settings.PROJECT_NAME}/{env}/{log_level}")
        response = logs_client.start_live_tail(logGroupIdentifiers=[response["logGroups"][0]["arn"][:-2]])
        try:
            for event in response["responseStream"]:
                if "sessionStart" in event:
                    session_start_event = event["sessionStart"]
                    print(session_start_event)
                elif "sessionUpdate" in event:
                    log_events = event["sessionUpdate"]["sessionResults"]
                    for log_event in log_events:
                        print(
                            "[{date}] {log}".format(
                                date=self.get_log_color(
                                    ConsoleColors.CYAN, datetime.fromtimestamp(log_event["timestamp"] / 1000)
                                ),
                                log=self.get_log_color(ConsoleColors.RED, log_event["message"]),
                            )
                        )
                else:
                    raise RuntimeError(str(event))
        except KeyboardInterrupt:
            print("로그 스트림을 종료합니다.")

    @staticmethod
    def get_log_color(color, text):
        return color + str(text) + ConsoleColors.RESET
