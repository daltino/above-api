import aws_cdk as core
import aws_cdk.assertions as assertions
from above_cdk_app.above_cdk_app_stack import AboveCdkAppStack


def test_shoes_dynamodb_tables_created():
    app = core.App()
    stack = AboveCdkAppStack(app, "above-cdk-app")
    template = assertions.Template.from_stack(stack)

    template.has_resource_properties("AWS::DynamoDB::Table", {
        "KeySchema": [
            {
                "AttributeName": "ShoeId",
                "KeyType": "HASH",
            },
            {
                "AttributeName": "Brand",
                "KeyType": "RANGE",
            }
        ]
    })


def test_orders_dynamodb_tables_created():
    app = core.App()
    stack = AboveCdkAppStack(app, "above-cdk-app")
    template = assertions.Template.from_stack(stack)

    template.has_resource_properties("AWS::DynamoDB::Table", {
        "KeySchema": [
            {
                "AttributeName": "OrderId",
                "KeyType": "HASH",
            },
            {
                "AttributeName": "ShoeId",
                "KeyType": "RANGE",
            }
        ]
    })

def test_list_shoes_lambda_function_created():
    app = core.App()
    stack = AboveCdkAppStack(app, "above-cdk-app")
    template = assertions.Template.from_stack(stack)

    template.has_resource_properties("AWS::Lambda::Function", {
        "Handler": "list_shoes.lambda_handler"
    })

def test_create_order_lambda_function_created():
    app = core.App()
    stack = AboveCdkAppStack(app, "above-cdk-app")
    template = assertions.Template.from_stack(stack)

    template.has_resource_properties("AWS::Lambda::Function", {
        "Handler": "create_order.lambda_handler"
    })

def test_above_api_gateway_created():
    app = core.App()
    stack = AboveCdkAppStack(app, "above-cdk-app")
    template = assertions.Template.from_stack(stack)

    template.has_resource_properties("AWS::ApiGateway::RestApi", {
        "Name": "above_api"
    })

def test_shoes_api_gateway_resource_created():
    app = core.App()
    stack = AboveCdkAppStack(app, "above-cdk-app")
    template = assertions.Template.from_stack(stack)

    template.has_resource_properties("AWS::ApiGateway::Resource", {
        "PathPart": "shoes",
    })


def test_orders_api_gateway_resource_created():
    app = core.App()
    stack = AboveCdkAppStack(app, "above-cdk-app")
    template = assertions.Template.from_stack(stack)

    template.has_resource_properties("AWS::ApiGateway::Resource", {
        "PathPart": "orders",
    })

def test_GET_list_shoes_api_gateway_method_created():
    app = core.App()
    stack = AboveCdkAppStack(app, "above-cdk-app")
    template = assertions.Template.from_stack(stack)

    template.has_resource_properties("AWS::ApiGateway::Resource", {
        "PathPart": "shoes",
    })


def test_orders_api_gateway_resource_created():
    app = core.App()
    stack = AboveCdkAppStack(app, "above-cdk-app")
    template = assertions.Template.from_stack(stack)

    template.has_resource_properties("AWS::ApiGateway::Resource", {
        "PathPart": "orders",
    })