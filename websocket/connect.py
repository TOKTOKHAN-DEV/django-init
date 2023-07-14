import json
import os

import boto3
import jwt

db = boto3.client("dynamodb")
secretmanager = boto3.client(
    service_name="secretsmanager",
    region_name="ap-northeast-2",
)
project_name = os.getenv("PROJECT_NAME")
env = os.getenv("ENV")


def handler(event, context):
    user_id = 0
    access = event["queryStringParameters"].get("access")
    if access:
        response = secretmanager.get_secret_value(SecretId=f"{project_name}/django/{env}")
        secret = json.loads(response["SecretString"])
        payload = jwt.decode(access, key=secret["key"], algorithms="HS256")
        user_id = payload["user_id"]

    db.put_item(
        TableName=os.getenv("TABLE_NAME"),
        Item={"connection_id": {"S": event["requestContext"]["connectionId"]}, "user_id": {"N": str(user_id)}},
    )

    return {}
