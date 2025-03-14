import boto3
import json
import logging
import uuid
from custom_encoder import CustomEncoder
from decimal import Decimal

logger = logging.getLogger()
logger.setLevel(logging.INFO)

dynamodbTableName = 'car-inventory'
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(dynamodbTableName)

getMethod = 'GET'
postMethod = 'POST'
patchMethod = 'PATCH'
putMethod = 'PUT'
deleteMethod = 'DELETE'
healthPath = '/health'
carPath = '/car'
carsPath = '/cars'

def lambda_handler(event, context):
  logger.info(json.dumps(event))
  
  httpMethod = event['httpMethod']
  path = event['path']
  if httpMethod == getMethod and path == healthPath : 
    response = buildresponse(200)
  elif httpMethod == getMethod and path == carPath :
    response = getCar(event['queryStringParameters']['carId'])
  elif httpMethod == getMethod and path == carsPath :
    response = getCars()
  elif httpMethod == postMethod and path == carPath :
    response = saveCar(json.loads(event['body']))
  elif httpMethod == putMethod and path == carPath :
    requestBody = json.loads(event['body'])
    response = replaceCar(requestBody['carId'], requestBody)
  elif httpMethod == patchMethod and path == carPath :
    requestBody = json.loads(event['body'])
    response = modifyCar(requestBody['carId'], requestBody['updateKey'], requestBody['updateValue'])
  elif httpMethod == deleteMethod and path == carPath :
    requestBody = json.loads(event['body'])
    response = deleteCar(requestBody['carId'])
  else :
    response = buildresponse(404, {'message': 'Not Found'})
    
  return response

def getCar(carId) :
  try :
    response = table.get_item(
      Key={
        'carId': carId
      }
    )
    if 'Item' in response :
      return buildresponse(200, response['Item'])
    else :
      return buildresponse(404, {'message': 'Car not found' % carId})
  except Exception as e:  
    logger.exception('Unexpected error getting a car: %s', str(e))
    return buildresponse(500, {'message': 'Internal Server Error'})
    
def getCars() : 
  try :
    response = table.scan()
    result = response['Items']
    
    while 'lastEvaluatedKey' in response :
      response = table.sacan(ExclusiveStartKey=response['lastEvaluatedKey'])
      result.extend(response['Items'])
      
    body = {
      'cars': result
    }
    return buildresponse(200, body)
  except Exception as e:  
    logger.exception('Unexpected error getting cars: %s', str(e))
    return buildresponse(500, {'message': 'Internal Server Error'})
    
def saveCar(requestBody) :
  try :
    requestBody['carId'] = str(uuid.uuid4())
    
    if not isinstance(requestBody.get("car"), str):
      return buildresponse(400, {'message': 'Car should be a String.'})
    if not isinstance(requestBody.get("bran"), str):
      return buildresponse(400, {'message': 'Bran should be a String'})
    if not isinstance(requestBody.get("serial"), int):
      return buildresponse(400, {'message': 'Serial should be an integer'})
    if not isinstance(requestBody.get("price"), float):
      return buildresponse(400, {'message': 'Price should be a Double'})
    
    requestBody['price'] = Decimal(str(requestBody['price']))
    table.put_item(Item=requestBody)
    body = {
      'Operation': 'SAVE',
      'Message': 'SUCCESS' ,
      'Item': requestBody
    }
    return buildresponse(200, {'message': "Car created", "body": body})
  except Exception as e:  
    logger.exception('Unexpected error saving car: %s', str(e))
    return buildresponse(500, {'message': 'Internal Server Error'})
    
def replaceCar(carId, newCarData):
  try:
    newCarData['carId'] = carId
    response = table.put_item(Item=newCarData)
    body = {
        'Operation': 'REPLACE',
        'Message': 'SUCCESS',
        'NewCarData': newCarData
    }
    return buildresponse(200, body)

  except Exception as e:  
    logger.exception('Unexpected error replacing car: %s', str(e))
    return buildresponse(500, {'message': 'Internal Server Error'})

def modifyCar(carId, updateKey, updateValue) :
  try :
    response = table.update_item(
      Key={
        'carId': carId
      },
      UpdateExpression='set %s = :value' % updateKey,
      ExpressionAttributeValues={
        ':value': updateValue
      },
      ReturnValues='UPDATED_NEW'
    )
    body = {
      'Operation': 'UPDATE',
      'Message': 'SUCCESS',
      'UpdatedAttributes': response
    }
    return buildresponse(200, body)
  except Exception as e:  
    logger.exception('Unexpected error modifying a car: %s', str(e))
    return buildresponse(500, {'message': 'Internal Server Error'})
    
def deleteCar(carId) :
  try :
    response = table.delete_item(
      Key={
        'carId': carId
      },
      ReturnValues='ALL_OLD'
    )
    body = {
      'Operation': 'DELETE',
      'Message': 'SUCCESS',
      'Item': response
    }
    return buildresponse(200, body)
  except Exception as e:  
    logger.exception('Unexpected error deleting a car: %s', str(e))
    return buildresponse(500, {'message': 'Internal Server Error'})
    
def buildresponse(statusCode, body=None):
    response = {
        'statusCode': statusCode,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        },
        'body': json.dumps(body, default=str) if body is not None else json.dumps({"message": "No content"})
    }
    return response