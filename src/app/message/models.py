import json

import boto3
from django.conf import settings
from django.db import models

from app.common.models import BaseModel


class Message(BaseModel):
    chat = models.ForeignKey("chat.Chat", verbose_name="채팅", on_delete=models.CASCADE)
    user = models.ForeignKey("user.User", verbose_name="유저", on_delete=models.CASCADE)
    text = models.TextField(verbose_name="텍스트", null=True, blank=True)
    image = models.URLField(verbose_name="이미지", null=True, blank=True)

    class Meta:
        db_table = "message"
        verbose_name = "메세지"
        verbose_name_plural = verbose_name
        ordering = ["-created_at"]

    def __str__(self):
        return self.text

    def send(self, receiver_user_id):
        db = boto3.client("dynamodb")
        response = db.query(
            TableName=f"{settings.PROJECT_NAME}-{settings.APP_ENV}-connection",
            IndexName="UserIdIndex",
            KeyConditionExpression="user_id = :user_id",
            ExpressionAttributeValues={
                ":user_id": {"N": str(receiver_user_id)},
            },
        )
        apigw = boto3.client(
            "apigatewaymanagementapi",
            endpoint_url=f"https://ws.{settings.DOMAIN}",
        )
        for item in response["Items"]:
            try:
                apigw.post_to_connection(
                    ConnectionId=item["connection_id"]["S"],
                    Data=json.dumps(
                        {
                            "chat_id": self.chat_id,
                            "user_id": self.user_id,
                            "text": self.text,
                            "image": self.image,
                        }
                    ),
                )
            except Exception:
                db.delete_item(
                    TableName=f"{settings.PROJECT_NAME}-{settings.APP_ENV}-connection",
                    Key={"connection_id": {"S": item["connection_id"]["S"]}},
                )
