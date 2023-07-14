import os

import boto3

db = boto3.client("dynamodb")


def lambda_handler(event, context):
    db.delete_item(
        TableName=os.getenv("TABLE_NAME"),
        Key={"connection_id": {"S": event["requestContext"]["connectionId"]}},
    )

    return {}
