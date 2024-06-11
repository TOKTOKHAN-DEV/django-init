import json

import boto3
from boto3.dynamodb.conditions import Key
from botocore.exceptions import ClientError
from django.conf import settings


def send(user_id, event, data):
    dynamodb = boto3.resource("dynamodb")
    table_name = f"{settings.PROJECT_NAME}-{settings.APP_ENV}-connection"
    table = dynamodb.Table(table_name)
    response = table.query(IndexName="UserIdIndex", KeyConditionExpression=Key("user_id").eq(user_id))
    apigw = boto3.client(
        "apigatewaymanagementapi",
        endpoint_url=f"https://ws.{settings.DOMAIN}",
    )
    for item in response["Items"]:
        try:
            apigw.post_to_connection(
                ConnectionId=item["connection_id"],
                Data=json.dumps(
                    {
                        "event": event,
                        "data": data,
                    }
                ),
            )
        except ClientError as e:
            if e.response["Error"]["Code"] == "BadRequestException":
                table.delete_item(Key={"connection_id": item["connection_id"]})
