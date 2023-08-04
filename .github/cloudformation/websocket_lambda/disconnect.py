import os

import boto3

ddb = None


def handler(event, context):
    global ddb

    if not ddb:
        ddb = boto3.client("dynamodb")

    ddb.delete_item(
        TableName=os.getenv("TABLE_NAME"),
        Key={"connection_id": {"S": event["requestContext"]["connectionId"]}},
    )

    return {}
