import json
import subprocess

import boto3
from botocore.exceptions import ClientError
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "AWS session manager를 시작합니다."

    def add_arguments(self, parser):
        parser.add_argument("--port", "-p", default=str(settings.DATABASES["default"]["PORT"]), type=str, help="로컬 포트")

    def handle(self, *args, **options):
        settings_option = options.get("settings")
        port = options.get("port")
        if settings_option != "config.settings.prod":
            raise CommandError("The --settings option can't be used not 'config.settings.prod'.")

        instance_id = self.get_instance_id()
        try:
            self.control_instance(instance_id, "start")
            self.start_session(instance_id, port)
        except Exception:
            # TODO
            self.control_instance(instance_id, "stop")

    @staticmethod
    def get_instance_id():
        ec2_client = boto3.client("ec2")
        response = ec2_client.describe_instances(
            Filters=[
                {
                    "Name": "tag:aws:cloudformation:stack-name",
                    "Values": [f"{settings.PROJECT_NAME}-{settings.ENV}-vpc"],
                },
                {"Name": "tag:aws:cloudformation:logical-id", "Values": ["BastionHost"]},
            ]
        )
        instance_id = response["Reservations"][0]["Instances"][0]["InstanceId"]
        return instance_id

    def control_instance(self, instance_id, action):
        ec2_client = boto3.client("ec2")
        if action == "start":
            print(f"Starting EC2 instance {instance_id}...")
            try:
                ec2_client.start_instances(InstanceIds=[instance_id])
            except ClientError:
                print("잠시후 다시 시도해주세요.")  # TODO
            print("Waiting for the instance to be in 'running' state...")
            waiter = ec2_client.get_waiter("instance_running")
            try:
                waiter.wait(InstanceIds=[instance_id], WaiterConfig={"Delay": 15, "MaxAttempts": 12})
                print("Instance is now running.")
            except Exception as e:
                print("Waiting for instance to run failed: ", e)
                raise
        elif action == "stop":
            print(f"Stopping EC2 instance {instance_id}...")
            ec2_client.stop_instances(InstanceIds=[instance_id])

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
        try:
            print("Starting session. Press Ctrl+C to exit.")
            subprocess.call(command, shell=True)
        except KeyboardInterrupt:
            self.control_instance(instance_id, "stop")
            print("Session terminated.")
