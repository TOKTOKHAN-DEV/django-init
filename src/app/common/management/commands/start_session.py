import json
import subprocess
import time

import boto3
from botocore.exceptions import ClientError
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "AWS session manager를 시작합니다."

    def add_arguments(self, parser):
        parser.add_argument(
            "--port", "-p", default=str(settings.DATABASES["default"]["PORT"]), type=str, help="로컬 포트"
        )

    def handle(self, *args, **options):
        settings_option = options.get("settings")
        if settings_option != "config.settings.prod":
            raise CommandError("The --settings option can't be used not 'config.settings.prod'.")
        port = options.get("port")
        instance_id = self.get_bastion_host_instance_id()
        self.start_session(instance_id, port)

    @staticmethod
    def get_bastion_host_instance_id():
        ec2_client = boto3.client("ec2")
        response = ec2_client.describe_instances(
            Filters=[
                {
                    "Name": "tag:aws:cloudformation:stack-name",
                    "Values": [f"{settings.PROJECT_NAME}-{settings.APP_ENV}-vpc"],
                },
                {"Name": "tag:aws:cloudformation:logical-id", "Values": ["NatInstance"]},
            ]
        )
        instance_id = response["Reservations"][-1]["Instances"][0]["InstanceId"]
        return instance_id

    def start_session(self, instance_id, port):
        parameters = {
            "localPortNumber": [port],
            "portNumber": [str(settings.DATABASES["default"]["PORT"])],
            "host": [settings.DATABASES["default"]["HOST"]],
        }

        command = (
            f"aws ssm start-session --target {instance_id} "
            f"--document-name AWS-StartPortForwardingSessionToRemoteHost "
            f"--parameters '{json.dumps(parameters)}'"
        )
        response = subprocess.call(command, shell=True)
        if response == 254:
            raise KeyboardInterrupt()
