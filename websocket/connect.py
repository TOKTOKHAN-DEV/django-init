import boto3
import os

db = boto3.client("dynamodb")


def lambda_handler(event, context):
    print(event)
    print(context)

    db.put_item(
        TableName=os.getenv("TABLE_NAME"),
        Item={
            "connection_id": {"S": event["requestContext"]["connectionId"]},
            # "user_id": {"N": event['body']}
        },
    )

    return {}
