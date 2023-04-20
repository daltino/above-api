import os
import boto3
import uuid
import json
from decimalencoder.decimal_encoder import DecimalEncoder

def lambda_handler(event, context):
  dynamodb = boto3.resource("dynamodb")
  SHOES_TABLE = os.environ["SHOES_TABLE"]
  shoes_table = dynamodb.Table(SHOES_TABLE)
  ORDERS_TABLE = os.environ["ORDERS_TABLE"]
  orders_table = dynamodb.Table(ORDERS_TABLE)
  ORDERS_BUCKET = os.environ["ORDERS_BUCKET"]

  data = event.get("body")
  
  if data and isinstance(data, str):
    data = json.loads(data)

  # Check if shoeID was provided
  shoeId = data.get("shoeId")
  
  if not shoeId:
    return {
      "statusCode":400,
      "body": json.dumps({"error": "No ShoeId was provided"}),
      "headers":{
        "Content-Type": "application/json",
      },
      "isBase64Encoded": False,
    }
  
  # Retrieve the shoe data from DynamoDB Shoes table
  try:
    shoe = shoes_table.get_item(
      Key={
        "ShoeId": shoeId
      }
    )
    
    shoe = shoe.get("Item")
  
    if not shoe:
      return {
        "statusCode":400,
        "body": json.dumps({"error": "No Shoe exists for the given ShoeId"}),
        "headers":{
          "Content-Type": "application/json",
        },
        "isBase64Encoded": False,
      }
  except Exception as e:
    print(f"Exception - {e} occured")
  
  # Check that all needed fields are provided in payload
  client = data.get("client")
  size = data.get("size")
  shippingInfo = data.get("shippingInfo")
  
  if not client or not size or not shippingInfo:
    return {
      "statusCode":400,
      "body": json.dumps({"error": "Please make sure you provide values for these fields: client, size and shippingInfo"}),
      "headers":{
        "Content-Type": "application/json",
      },
      "isBase64Encoded": False,
    }
  
  # Create the order from the POST request
  orderId = str(uuid.uuid4())
  order = {
    "OrderId": orderId,
    "Client": client,
    "Size": size,
    "ShippingInformation": shippingInfo,
  }

  try:
    response = orders_table.put_item(
      Item = {
        **order,
        "ShoeId": shoeId,
      }
    )
  except Exception as e:
    print(f"Exception - {e} occured")
  
  ordersResponseHttpStatusCode = response.get("ResponseMetadata").get("HTTPStatusCode")
  if ordersResponseHttpStatusCode != 200:
    return {
      "statusCode":500,
      "body": json.dumps({"error": f"Could not save the order. Error {ordersResponseHttpStatusCode}"}),
      "headers":{
        "Content-Type": "application/json",
      },
      "isBase64Encoded": False,
    }
  
  orderJson = {
    **order,
    "Shoe": shoe
  }

  s3 = boto3.client("s3")
  try:
    s3.put_object(
      Body = json.dumps(orderJson, cls=DecimalEncoder),
      Bucket = ORDERS_BUCKET,
      Key = orderId
    )
  except Exception as e:
    print(f"Exception - {e} occured")

  return {
    'statusCode': 200,
    'body': json.dumps({ "message": "Order was created successfully"}),
    "isBase64Encoded": False,
    "headers": {
        "Content-Type": "application/json",
    }
  }
