from rest_framework import serializers

from app.celery_logs.models import CeleryLogs


class CeleryLogsSerializer(serializers.ModelSerializer):
    class Meta:
        model = CeleryLogs
        fields = [
            "id",
        ]

    def validate(self, attrs):
        attrs = super().validate(attrs)
        return attrs

    def create(self, validated_data):
        instance = super().create(validated_data)
        return instance

    def update(self, instance, validated_data):
        instance = super().update(instance, validated_data)
        return instance
