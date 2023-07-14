import json

import boto3
import os

db = boto3.client("dynamodb")


def lambda_handler(event, context):
    print(event)
    print(context)

    message = json.loads(event["body"])["message"]

    items = db.query(
        TableName=os.getenv("TABLE_NAME"),
        IndexName="UserIdIndex",
        KeyConditionExpression="user_id = :user_id",
        ExpressionAttributeValues={
            ":user_id": {"N": str(event["body"]["user_id"])},
        },
    )

    api = boto3.client(
        "apigatewaymanagementapi",
        endpoint_url=f"https://{event['requestContext']['domainName']}/{event['requestContext']['stage']}",
    )
    for item in items:
        api.post_to_connection(
            ConnectionId=item["connectionId"],
            Data=message,
        )

    return {}
