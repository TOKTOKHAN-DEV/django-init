import boto3
import requests
import os

db = boto3.client("dynamodb")


def handler(event, context):
    user_id = 0
    # access = event["queryStringParameters"].get("access")
    # if access:
    #     requests.post(url=, headers={"Authorization": f"Bearer {access}"})

    db.put_item(
        TableName=os.getenv("TABLE_NAME"),
        Item={
            "connection_id": {"S": event["requestContext"]["connectionId"]},
            "user_id": {"N": str(user_id)}
        },
    )

    return {}