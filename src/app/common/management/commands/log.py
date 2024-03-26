import time
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

    def handle(self, *args, **options):

        cloudwatch_client = boto3.client("logs")

        log_groups_response = cloudwatch_client.describe_log_groups(logGroupNamePrefix=settings.PROJECT_NAME)
        log_groups = log_groups_response["logGroups"]
        for i, group in enumerate(log_groups):
            print(self.get_log_color(ConsoleColors.RED, f"{i}: {group['logGroupName']}"))
        group_index = int(input(self.get_log_color(ConsoleColors.RED, "로그 그룹 번호를 선택하세요: ")))
        log_group_arn = log_groups[group_index]["arn"][:-1]
        self.get_last_log(log_group_arn)
        self.get_tail_log(log_group_arn)

    def get_last_log(self, log_group_arn):
        cloudwatch_client = boto3.client("logs")
        log_streams_response = cloudwatch_client.describe_log_streams(logGroupIdentifier=log_group_arn)
        log_stream_name = log_streams_response["logStreams"][-1]["logStreamName"]
        response = cloudwatch_client.get_log_events(
            logGroupIdentifier=log_group_arn,
            logStreamName=log_stream_name,
            limit=100,
        )
        for log_event in response["events"]:
            print(
                "{date} {log}".format(
                    date=self.get_log_color(
                        ConsoleColors.CYAN, f"[{datetime.fromtimestamp(log_event['timestamp'] / 1000)}]"
                    ),
                    log=self.get_log_color(ConsoleColors.WHITE, log_event["message"]),
                )
            )

    def get_tail_log(self, log_group_arn):
        cloudwatch_client = boto3.client("logs")
        response = cloudwatch_client.start_live_tail(logGroupIdentifiers=[log_group_arn])
        try:
            for event in response["responseStream"]:
                if "sessionStart" in event:
                    pass
                elif "sessionUpdate" in event:
                    log_events = event["sessionUpdate"]["sessionResults"]
                    for log_event in log_events:
                        print(
                            "{date} {log}".format(
                                date=self.get_log_color(
                                    ConsoleColors.CYAN, f"[{datetime.fromtimestamp(log_event['timestamp'] / 1000)}]"
                                ),
                                log=self.get_log_color(ConsoleColors.WHITE, log_event["message"]),
                            )
                        )
                else:
                    raise RuntimeError(str(event))
        except KeyboardInterrupt:
            print(self.get_log_color(ConsoleColors.RED, "로그 스트림을 종료합니다."))

    @staticmethod
    def get_log_color(color, text):
        return color + str(text) + ConsoleColors.RESET
