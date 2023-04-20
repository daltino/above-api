import os
import boto3
import uuid
import json
from decimalencoder.decimal_encoder import DecimalEncoder

dynamodb = boto3.resource('dynamodb')
SHOES_TABLE = os.environ['SHOES_TABLE']
shoes_table = dynamodb.Table(SHOES_TABLE)
ORDERS_TABLE = os.environ['ORDERS_TABLE']
orders_table = dynamodb.Table(ORDERS_TABLE)

def lambda_handler(event, context):
  
  # Possible Improvement is to add Pagination due to the 1MB LIMIT per scan
  
  if event and event.get('queryStringParameters'):
    brand = event.get('queryStringParameters').get('brand')

    if brand:
      response = shoes_table.scan(
        FilterExpression="Brand = :brand",
        ExpressionAttributeValues={
            ":brand": brand,
        },
      )
  else:
      response = shoes_table.scan()

  items = response["Items"]

  if not items:
    # Initial Data: HardCode the creation of Shoes / Orders
    createInitialData()
    response = shoes_table.scan()
  
  
  
  return {
    "statusCode": 200,
    "body": json.dumps({ "shoes": response["Items"] }, cls=DecimalEncoder),
    "isBase64Encoded": False,
    "headers": {
      "Content-Type": "application/json",
      "Access-Control-Allow-Origin": "*",
      "Access-Control-Allow-Methods": "OPTIONS,GET"
    }
  }

def createInitialData():
  shoeId1 = str(uuid.uuid4())
  shoeId2 = str(uuid.uuid4())
  shoeId3 = str(uuid.uuid4())
  shoeId4 = str(uuid.uuid4())

  try:
    with shoes_table.batch_writer() as batch:
      batch.put_item(Item={"ShoeId": shoeId1, "Brand": "Nike",
          "AvailableSizes": [42,43,44,45,46,47], "Price": 99 })
      batch.put_item(Item={"ShoeId": shoeId2, "Brand": "Adidas",
          "AvailableSizes": [40,43,44,45,46,47], "Price": 99 })
      batch.put_item(Item={"ShoeId": shoeId3, "Brand": "New Balance",
          "AvailableSizes": [41,43,44,45,46,47], "Price": 99 })
      batch.put_item(Item={"ShoeId": shoeId4, "Brand": "Vans",
          "AvailableSizes": [42,43,44,45,46,48], "Price": 99 })
      
    with orders_table.batch_writer() as batch:
      batch.put_item(Item={"OrderId": str(uuid.uuid4()), "Client": "James Bond",
          "Size": 42, "ShoeId": shoeId1,
          "ShippingInformation": {"Destination": " XYZ Street, XYZ 1234","DeliveryDate": "2023-04-10 11:00:00"} })
      batch.put_item(Item={"OrderId": str(uuid.uuid4()), "Client": "John Doe",
          "Size": 40, "ShoeId": shoeId2,
          "ShippingInformation": {"Destination": " XYZ Street, XYZ 1234", "DeliveryDate": "2023-04-10 11:00:00"} })
      batch.put_item(Item={"OrderId": str(uuid.uuid4()),"Client": "Jane Doe",
          "Size": 41, "ShoeId": shoeId3,
          "ShippingInformation": {"Destination": " XYZ Street, XYZ 1234", "DeliveryDate": "2023-04-10 11:00:00"} })
      batch.put_item(Item={"OrderId": str(uuid.uuid4()), "Client": "Helen Williams",
          "Size": 48, "ShoeId": shoeId4,
          "ShippingInformation": {"Destination": " XYZ Street, XYZ 1234", "DeliveryDate": "2023-04-10 11:00:00"} })
  except Exception as e:
    print(f"Exception - {e} occured")