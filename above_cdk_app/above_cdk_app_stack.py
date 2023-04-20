from constructs import Construct
from aws_cdk import (
    Stack,
    aws_dynamodb as dynamodb_cdk,
    aws_lambda as lambda_cdk,
    aws_apigateway as apigateway_cdk,
    aws_s3 as s3_cdk,
)


class AboveCdkAppStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Create Shoes DynamoDB Table with default RemvalPolicy of Retain
        shoes_table_cdk = dynamodb_cdk.Table(self, "Shoes",
            partition_key=dynamodb_cdk.Attribute(name="ShoeId", type=dynamodb_cdk.AttributeType.STRING))

        # Create Orders DynamoDB Table with default RemvalPolicy of Retain
        orders_table_cdk = dynamodb_cdk.Table(self, "Orders",
            partition_key=dynamodb_cdk.Attribute(name="OrderId", type=dynamodb_cdk.AttributeType.STRING))
        
        # Create AboveOrders Bucket
        above_orders_bucket_cdk = s3_cdk.Bucket(self, "above-orders", bucket_name="above-orders")

        # Create Shared Lambda Layer to be used by the Lambda Functions
        above_lambda_layer_cdk = lambda_cdk.LayerVersion(self, id="above_lambda_layer",
                code=lambda_cdk.Code.from_asset("./lambda/layers"),
                compatible_runtimes=[lambda_cdk.Runtime.PYTHON_3_9])

        # Create ListShoes Lambda function
        list_shoes_lambda_cdk = lambda_cdk.Function(self, "list_shoes",
                code = lambda_cdk.Code.from_asset("./lambda/shoes/listShoes"),
                handler="list_shoes.lambda_handler",
                runtime=lambda_cdk.Runtime.PYTHON_3_9,
                layers=[above_lambda_layer_cdk])
        list_shoes_lambda_cdk.add_environment("SHOES_TABLE", shoes_table_cdk.table_name)
        list_shoes_lambda_cdk.add_environment("ORDERS_TABLE", orders_table_cdk.table_name)

        # Create CreateOrder Lambda function
        create_order_lambda_cdk = lambda_cdk.Function(self, "create_order",
                code = lambda_cdk.Code.from_asset("./lambda/orders/createOrder"),
                handler="create_order.lambda_handler",
                runtime=lambda_cdk.Runtime.PYTHON_3_9,
                layers=[above_lambda_layer_cdk])
        create_order_lambda_cdk.add_environment("SHOES_TABLE", shoes_table_cdk.table_name)
        create_order_lambda_cdk.add_environment("ORDERS_TABLE", orders_table_cdk.table_name)
        create_order_lambda_cdk.add_environment("ORDERS_BUCKET", above_orders_bucket_cdk.bucket_name)

        # Grant CreateOrder Lambda Permission to S3 Bucket
        above_orders_bucket_cdk.grant_write(create_order_lambda_cdk)

        # Grant Lambdas Permission to DynamoDB
        shoes_table_cdk.grant_read_write_data(list_shoes_lambda_cdk)
        shoes_table_cdk.grant_read_data(create_order_lambda_cdk)
        orders_table_cdk.grant_write_data(list_shoes_lambda_cdk)
        orders_table_cdk.grant_write_data(create_order_lambda_cdk)

        # Create a dev deployment for the ApiGateway
        dev_deployment = apigateway_cdk.StageOptions(stage_name="dev")

        # Create ApiGateway
        above_api = apigateway_cdk.RestApi(self, "above_api", deploy_options=dev_deployment)

        # Deploy for prod (COMMENT OUT TO TURN OFF/ON) OR USE CI/CD (CodePipeline)
        
        # Create a prod deployment
        # prod_deployment = apigateway_cdk.Deployment(
        #     self,
        #     "ProdDeployment1",
        #     api=above_api,
        #     retain_deployments=True,
        #     description="Live Production API deployment"
        # )

        # git Create a prod stage
        # prodStage = apigateway_cdk.Stage(
        #     self,
        #     "ProdStage",
        #     deployment=prod_deployment,
        #     stage_name="prod"
        # )

        # above_api.deployment_stage = prodStage

        # Create Path for ListShoe
        listShoesLambdaPath = above_api.root.add_resource("shoes")
        listShoesLambdaPath.add_method("GET", apigateway_cdk.LambdaIntegration(list_shoes_lambda_cdk))

        # Create Path for CreateOrder
        createOrderLambdaPath = above_api.root.add_resource("orders")
        createOrderLambdaPath.add_method("POST", apigateway_cdk.LambdaIntegration(create_order_lambda_cdk))
