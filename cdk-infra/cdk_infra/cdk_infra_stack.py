from aws_cdk import (
    Stack,
    aws_lambda as _lambda,
    aws_dynamodb as dynamodb,
    RemovalPolicy,
    aws_s3 as s3,
    aws_s3_deployment as s3deploy,
    CfnOutput,
    aws_sns as sns,
    aws_sns_subscriptions as subs
)
from constructs import Construct
import aws_cdk.aws_apigatewayv2_alpha as apigw
import aws_cdk.aws_apigatewayv2_integrations_alpha as integrations


class CdkInfraStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # DynamoDb
        table = dynamodb.Table(
            self, 'RepairsTableCDK',
            partition_key=dynamodb.Attribute(name='Id', type=dynamodb.AttributeType.STRING),
            removal_policy=RemovalPolicy.DESTROY
        )

        #SNS
        topic = sns.Topic(self, "RepairStatusTopicCDK",topic_name="RepairStatusAlertCDK")

        topic.add_subscription(subs.EmailSubscription("werulik.krzysztof@gmail.com"))

        # Leyers
        layer = _lambda.LayerVersion(
            self, "AppDependencies",
            code=_lambda.Code.from_asset("../lambda_layer"),
            compatible_runtimes=[_lambda.Runtime.PYTHON_3_12],
            description="Warstwa z Pydantic i Powertools"
        )

        # Lambda
        my_lambda = _lambda.Function(
            self, "RepairHandlerCdk",
            runtime=_lambda.Runtime.PYTHON_3_12,
            handler="lambda_cdk.lambda_handler",
            code=_lambda.Code.from_asset("../src"),
            layers=[layer],
            environment={
                "TABLE_NAME": table.table_name,
                "POWERTOOLS_SERVICE_NAME": "CarRepairService",
                "SNS_TOPIC_ARN": topic.topic_arn,
            }
        )

        topic.grant_publish(my_lambda)
        # IAM
        table.grant_read_write_data(my_lambda)


        # API Gateway
        api = apigw.HttpApi(self, "RepairApiCdk",
            cors_preflight=apigw.CorsPreflightOptions( 
                allow_methods=[apigw.CorsHttpMethod.POST,apigw.CorsHttpMethod.OPTIONS],
                allow_origins=["*"],
                allow_headers=["Content-Type"]
            )
        )

        api.add_routes(
            path='/AddRepair',
            methods=[apigw.HttpMethod.POST],
            integration=integrations.HttpLambdaIntegration(
                "LambdaIntegration", my_lambda)
        )

        # Bucket S3 dla frontendu

        frontend_bucket = s3.Bucket(
            self, "FrontendBucketCDK",
            website_index_document="index.html",
            public_read_access=True,
            block_public_access=s3.BlockPublicAccess(
                block_public_acls=False,
                block_public_policy=False,
                ignore_public_acls=False,
                restrict_public_buckets=False
            ),
            removal_policy=RemovalPolicy.DESTROY,  
            auto_delete_objects=True
        )

        # Deployment index.html
        s3deploy.BucketDeployment(
            self, "DeployFrontendCDK",
            sources=[s3deploy.Source.asset("../cdk-frontend")],
            destination_bucket=frontend_bucket
        )

        # Wyświetlanie URL w terminalu
        CfnOutput(self, "FrontendURL", value=frontend_bucket.bucket_website_url)
        CfnOutput(self, "NewApiUrl", value=api.api_endpoint)
