import os
import boto3
import uuid
import json
from decimalencoder.decimal_encoder import DecimalEncoder

def createResponse(statusCode, body):
  return {
    "statusCode": statusCode,
    "body": json.dumps(body),
    "headers":{
      "Content-Type": "application/json",
      "Access-Control-Allow-Origin": "*",
      "Access-Control-Allow-Methods": "OPTIONS,POST"
    },
    "isBase64Encoded": False,
  }

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
    return createResponse(400, {"error": "No ShoeId was provided"})
  
  # Retrieve the shoe data from DynamoDB Shoes table
  try:
    shoe = shoes_table.get_item(
      Key={
        "ShoeId": shoeId
      }
    )
    
    shoe = shoe.get("Item")
  
    if not shoe:
      return createResponse(400, {"error": "No Shoe exists for the given ShoeId"})

  except Exception as e:
    print(f"Exception - {e} occured")
  
  # Check that all needed fields are provided in payload
  client = data.get("client")
  size = data.get("size")
  shippingInfo = data.get("shippingInfo")
  
  if not client or not size or not shippingInfo:
    return createResponse(400, {"error": "Please make sure you provide values for these fields: client, size and shippingInfo"})

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
    return createResponse(500, {"error": f"Could not save the order. Error {ordersResponseHttpStatusCode}"})
  
  # Save the order as a JSON object in S3
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

  return createResponse(200, { "message": "Order was created successfully"})
