from aws_cdk import (
    aws_apigateway as apigw,
    aws_dynamodb,
    aws_lambda,
    aws_events as events,
    aws_events_targets as targets,
    aws_s3 as s3,
    Stack,
    RemovalPolicy,
)
from constructs import Construct


class AwscdkApiLambdaDynamoStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Deploy a DynamoDB table
        hub_table = aws_dynamodb.Table(
            self,
            "hub_table",
            partition_key=aws_dynamodb.Attribute(
                name="id", type=aws_dynamodb.AttributeType.STRING
            ),
            removal_policy=RemovalPolicy.DESTROY,
        )

        # Deploy a lambda funcion and add the DynamoDB table as a event source
        producer_lambda = aws_lambda.Function(
            self,
            "producer_lambda",
            runtime=aws_lambda.Runtime.PYTHON_3_9,
            handler="producer_lambda.lambda_handler",
            code=aws_lambda.Code.from_asset("lambda"),
            environment={"DYNAMODB_TABLE": hub_table.table_name},
        )

        # Grant the lambda function permission to write to the dynamodb table
        hub_table.grant_write_data(producer_lambda)

        # Deploy the API Gateway and routes
        api = apigw.RestApi(self, "ApiGW", rest_api_name="hub_api")

        endpoint = api.root.add_resource("add")
        endpoint.add_method("POST", apigw.LambdaIntegration(producer_lambda))

        # Reporting
        # Create a Lambda function that it will trigger every 2 hours interval
        # The Lambda function will scan the DynamoDB table to count all items and save the results to a S3 bucket

        # Create the S3 bucket
        bucket = s3.Bucket(self, "hubbucket")

        # Create a lambda function that will count the number of items in the DynamoDB table and save it in a S3 bucket
        ddb_lambda_report = aws_lambda.Function(
            self,
            "ddb_lambda_report",
            runtime=aws_lambda.Runtime.PYTHON_3_9,
            handler="ddb_lambda_report.lambda_handler",
            code=aws_lambda.Code.from_asset("lambda"),
            environment={"DYNAMODB_TABLE": hub_table.table_name},
        )

        # Grant the lambda function permission to read from the dynamodb table
        hub_table.grant_read_data(ddb_lambda_report)
        # Grant the lambda function permission to write to the S3 bucket
        bucket.grant_write(ddb_lambda_report)

        # Create a events rule that will trigger the consumer lambda function every 2 hours
        rule = events.Rule(
            self,
            "Rule",
            schedule=events.Schedule.cron(
                minute="0", hour="*/2", month="*", week_day="MON-FRI", year="*"
            ),
        )
        rule.add_target(targets.LambdaFunction(ddb_lambda_report))
