import os

import boto3

ddb = None


def handler(event, context):
    global ddb

    if not ddb:
        ddb = boto3.resource("dynamodb")
    table_name = os.getenv("TABLE_NAME")
    table = ddb.Table(table_name)
    table.delete_item(Key={"connection_id": event["requestContext"]["connectionId"]})

    return {}
