import boto3
from django.conf import settings
from django.core.management import BaseCommand, CommandError
from drf_spectacular.generators import EndpointEnumerator

from app.common.utils import color_string


class Command(BaseCommand):
    help = "cron을 등록합니다."

    def handle(self, *args, **options):
        project_name = settings.PROJECT_NAME
        app_env = settings.APP_ENV

        event_client = boto3.client("events")
        prefix = f"{project_name}-{app_env}-"
        rules = event_client.list_rules(NamePrefix=prefix, Limit=100)["Rules"]
        if not rules:
            raise CommandError("크론이 존재하지 않습니다.")
        for i, rule in enumerate(rules):
            print(color_string("cyan", f"{i}.{rule['Name']}"))
        rule_index = int(input(color_string("red", "크론을 선택하세요: ")))
        remove_rule = rules[rule_index]
        event_client.remove_targets(
            Rule=remove_rule["Arn"].split("/", 1)[-1],
            Ids=[remove_rule["Name"]],
        )
        event_client.delete_rule(Name=remove_rule["Name"])
