def handler(event, context):
    response = event
    print(response)
    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
        },
        "body": "",
        "isBase64Encoded": False,
    }
