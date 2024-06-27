import json

import boto3
from boto3.dynamodb.conditions import Key
from botocore.exceptions import ClientError
from django.conf import settings


class WebSocketManager:
    def __init__(self):
        self.dynamodb = boto3.resource("dynamodb")
        self.table_name = f"{settings.PROJECT_NAME}-{settings.APP_ENV}-connection"
        self.table = self.dynamodb.Table(self.table_name)
        self.apigw = boto3.client(
            "apigatewaymanagementapi",
            endpoint_url=settings.WEBSOCKET_URL,
        )

    def send(self, user_id, event, data):
        response = self.table.query(IndexName="UserIdIndex", KeyConditionExpression=Key("user_id").eq(user_id))
        delete_connection_ids = []
        for item in response["Items"]:
            try:
                self.apigw.post_to_connection(
                    ConnectionId=item["connection_id"],
                    Data=json.dumps(
                        {
                            "event": event,
                            "data": data,
                        }
                    ),
                )
            except ClientError as e:
                if e.response["Error"]["Code"] == "GoneException":
                    delete_connection_ids.append(item["connection_id"])
        if delete_connection_ids:
            with self.table.batch_writer() as batch:
                for connection_id in delete_connection_ids:
                    batch.delete_item(Key={"connection_id": connection_id})
