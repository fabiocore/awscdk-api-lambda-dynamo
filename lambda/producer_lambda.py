import json
import uuid
import os
import boto3

# get the service resource.
dynamodb = boto3.resource("dynamodb")

# set ddb environment variable
TABLE_NAME = os.environ["DYNAMODB_TABLE"]
table = dynamodb.Table(TABLE_NAME)


def lambda_handler(event, context):
    # prepare data
    pk_id = str(uuid.uuid4())
    json_data = json.loads(event["body"])
    json_data.update({"id": pk_id})
    print("Data to be added to table: ", json_data)

    # put item in table
    response = table.put_item(Item=json_data)
    print("PutItem succeeded:", response)

    message = f"New item added to table, with id: {pk_id}"
    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
        },
        "body": message,
        "isBase64Encoded": False,
    }
