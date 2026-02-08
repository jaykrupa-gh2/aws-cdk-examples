# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

from aws_xray_sdk.core import xray_recorder
from aws_xray_sdk.core import patch_all

patch_all()

import boto3
import os
import json
import logging
import uuid

logger = logging.getLogger()
logger.setLevel(logging.INFO)

dynamodb_client = boto3.client("dynamodb")


def handler(event, context):
    request_id = context.request_id
    table = os.environ.get("TABLE_NAME")
    
    # Structured logging with request context
    logger.info(json.dumps({
        "request_id": request_id,
        "event": "table_access",
        "table_name": table,
        "source_ip": event.get("requestContext", {}).get("identity", {}).get("sourceIp"),
        "user_agent": event.get("requestContext", {}).get("identity", {}).get("userAgent"),
    }))
    
    try:
        if event.get("body"):
            item = json.loads(event["body"])
            logger.info(json.dumps({
                "request_id": request_id,
                "event": "item_insert",
                "item_id": item.get("id"),
            }))
            year = str(item["year"])
            title = str(item["title"])
            id = str(item["id"])
            dynamodb_client.put_item(
                TableName=table,
                Item={"year": {"N": year}, "title": {"S": title}, "id": {"S": id}},
            )
            message = "Successfully inserted data!"
            return {
                "statusCode": 200,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({"message": message}),
            }
        else:
            logger.info(json.dumps({
                "request_id": request_id,
                "event": "default_item_insert",
            }))
            dynamodb_client.put_item(
                TableName=table,
                Item={
                    "year": {"N": "2012"},
                    "title": {"S": "The Amazing Spider-Man 2"},
                    "id": {"S": str(uuid.uuid4())},
                },
            )
            message = "Successfully inserted data!"
            return {
                "statusCode": 200,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({"message": message}),
            }
    except Exception as e:
        logger.error(json.dumps({
            "request_id": request_id,
            "event": "error",
            "error_type": type(e).__name__,
            "error_message": str(e),
        }))
        raise
