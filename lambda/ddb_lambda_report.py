import boto3
import os

# defining dynamodb resource
dynamodb = boto3.resource("dynamodb")
TABLE_NAME = os.environ["DYNAMODB_TABLE"]

# defining s3 resource
s3 = boto3.client("s3")
S3_BUCKET = os.environ["S3_BUCKET"]


def lambda_handler(event, context):
    # Not a table scan, low cost
    # table = dynamodb.Table(TABLE_NAME)
    # print(table.item_count)

    # Performs a table scan, high cost
    table = dynamodb.Table(TABLE_NAME)

    response = table.scan()
    item_count = len(response["Items"])
    message = f"Total number of items for DynamoDB table {TABLE_NAME}: {item_count}"
    print(message)

    # Writing the total number of items to the s3 bucket
    with open(r"/tmp/report.txt", "w") as report:
        report.write(message)

    s3.upload_file("/tmp/report.txt", S3_BUCKET, "reports/dynamodb_total_items.txt")

    return {"statusCode": 200}
