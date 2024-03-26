import base64
import hashlib
import hmac
import json
import os
import time

import boto3

ddb = None
secretmanager = None

project_name = os.getenv("PROJECT_NAME")
env = os.getenv("ENV")


def handler(event, context):
    global ddb
    global secretmanager

    if not ddb:
        ddb = boto3.client("dynamodb")
    if not secretmanager:
        secretmanager = boto3.client(
            service_name="secretsmanager",
            region_name="ap-northeast-2",
        )

    user_id = 0
    access = event.get("queryStringParameters") and event["queryStringParameters"].get(
        "access"
    )
    if access:
        response = secretmanager.get_secret_value(
            SecretId=f"{project_name}/{env}/django"
        )
        secret = json.loads(response["SecretString"])
        payload = jwt_decode(access, secret["key"])
        user_id = payload["user_id"]
        if time.time() > payload["exp"]:
            raise Exception("expired access token.")
    ddb.put_item(
        TableName=os.getenv("TABLE_NAME"),
        Item={
            "connection_id": {"S": event["requestContext"]["connectionId"]},
            "user_id": {"N": str(user_id)},
        },
    )

    return {}


def jwt_decode(access, key):
    token_parts = access.split(".")
    header = token_parts[0]
    payload = token_parts[1]
    signature = token_parts[2]

    decoded_payload = base64.urlsafe_b64decode(payload + "=" * (4 - len(payload) % 4))

    expected_signature = hmac.new(
        key.encode("utf-8"),
        (header + "." + payload).encode("utf-8"),
        digestmod=hashlib.sha256,
    ).digest()
    signature = base64.urlsafe_b64decode(signature + "=" * (4 - len(signature) % 4))

    if not hmac.compare_digest(expected_signature, signature):
        raise ValueError("Invalid JWT signature")

    payload_data = json.loads(decoded_payload)

    return payload_data
