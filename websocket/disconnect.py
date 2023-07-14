import boto3
import os

db = boto3.client("dynamodb")


def lambda_handler(event, context):
    print(event)
    print(context)

    db.delete_item(
        TableName=os.getenv("TABLE_NAME"),
        Key={"connection_id": {"S": event["requestContext"]["connectionId"]}},
    )

    return {}