from aws_cdk import (
    aws_apigateway as apigw,
    aws_dynamodb,
    aws_lambda,
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
            handler="producer_lambda.handler",
            code=aws_lambda.Code.from_asset("lambda"),
            environment={"DYNAMODB_TABLE": hub_table.table_name},
        )

        # Grant the lambda function permission to write to the dynamodb table
        hub_table.grant_write_data(producer_lambda)

        # Deploy the API Gateway and routes
        api = apigw.RestApi(self, "ApiGW", rest_api_name="hub_api")

        endpoint = api.root.add_resource("add")
        endpoint.add_method("POST", apigw.LambdaIntegration(producer_lambda))
