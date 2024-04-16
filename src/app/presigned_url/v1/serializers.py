import random
import string

import boto3
from botocore.config import Config
from botocore.exceptions import ClientError
from django.conf import settings
from rest_framework import serializers


class PresignedSerializer(serializers.Serializer):
    file_name = serializers.CharField(write_only=True)
    url = serializers.URLField(read_only=True)
    fields = serializers.JSONField(read_only=True)

    def validate(self, attrs):
        response = self.create_presigned_post(attrs["file_name"])
        attrs.update(response)

        return attrs

    def create(self, validated_data):
        return validated_data

    def create_presigned_post(self, file_name):
        s3_config = Config(
            region_name="ap-northeast-2",
            signature_version="s3v4",
        )
        s3_client = boto3.client("s3", config=s3_config)
        basename = "/".join(["_media", self.context["view"].basename])
        object_key = self.get_object_key(s3_client, basename, file_name)

        response = s3_client.generate_presigned_post(
            settings.AWS_STORAGE_BUCKET_NAME,
            object_key,
            Fields={"x-amz-tagging": "status=editing"},
            Conditions=[
                {"x-amz-tagging": "status=editing"},
                ["content-length-range", 0, 20971520],  # 20MB
                ["starts-with", "$Content-Type", f"image/"],
            ],
            ExpiresIn=360,
        )
        return response

    def get_object_key(self, s3_client, basename, file_name):
        object_key = f"{basename}/{file_name}"
        try:
            s3_client.head_object(
                Bucket=settings.AWS_STORAGE_BUCKET_NAME,
                Key=object_key,
            )
            name, ext = file_name.split(".")
            characters = string.ascii_lowercase + string.digits
            random_string = "".join(random.choices(characters, k=7))
            file_name = ".".join([f"{name}_{random_string}", ext])
            return self.get_object_key(s3_client, basename, file_name)
        except ClientError:
            return object_key
