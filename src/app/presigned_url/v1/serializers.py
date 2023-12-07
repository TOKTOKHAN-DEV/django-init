import uuid

import boto3
from botocore.config import Config
from botocore.exceptions import ClientError
from django.apps import apps
from django.conf import settings
from rest_framework import serializers
from rest_framework.exceptions import ValidationError


class PresignedUrlSerializer(serializers.Serializer):
    name = serializers.CharField(write_only=True)
    category = serializers.ChoiceField(
        choices=[model.__name__.lower() for model in apps.get_models() if model.__module__.startswith("app.")],
        write_only=True,
    )
    url = serializers.URLField(read_only=True)

    def validate(self, attrs):
        attrs["url"] = self.create_presigned_url(attrs["name"], attrs["category"])

        return attrs

    def create(self, validated_data):
        return validated_data

    @staticmethod
    def create_presigned_url(name, category):
        s3_config = Config(
            region_name="ap-northeast-2",
            signature_version="s3v4",
        )
        s3_client = boto3.client("s3", config=s3_config)
        ext = name.split(".")[-1]

        object_key = "/".join(["_media/category", f"{uuid.uuid4()}.{ext}"])
        try:
            url = s3_client.generate_presigned_url(
                "put_object",
                Params={
                    "Bucket": settings.AWS_STORAGE_BUCKET_NAME,
                    "Key": object_key,
                },
                ExpiresIn=300,
            )
        except ClientError as e:
            raise ValidationError({"s3": ["S3 Client Error"]})
        return url
