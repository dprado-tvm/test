import boto3
import json
import logging
from custom_encoder import CustomEncoder

logger = logging.getLogger()
logger.setLevel(logging.INFO)

dynamodbTableName = 'car-inventory'
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(dynamodbTableName)

getMethod = 'GET'
postMehod = 'POST'
patchMethod = 'PATCH'
deleteMethod = 'DELETE'
healthPath = '/health'
carPath = '/car'
carsPath = '/cars'

def lambda_handler(event, context):
  logger.info(event)
  httpMethod = event['httpdMethod']
  path = event['path']
  if httpMethod == getMethod and path == healthPath : 
    response = buildresponse(200)
  elif httpMethod == getMethod and path == carPath :
    response = getCar(event['queryStringParameters']['carId'])
  elif httpMethod == getMethod and path == carsPath :
    response = getCars()
  elif httpMethod == postMehod and path == carPath :
    response = saveCar(json.loads(event['body']))
  elif httpMethod == patchMethod and path == carPath :
    requestBody = json.loads(event['body'])
    response = modifyCar(requestBody['carId'], requestBody['updateKey'], requestBody['updateValue'])
  elif httpMethod == deleteMethod and path == carPath :
    requestBody == json.loads(event['body'])
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
  except :
    logger.exception('Do your custom error handling here. I am just gonna log it out here!!')
    
def getCars() : 
  try :
    response = table.scan()
    result = response['Item']
    
    while 'lastEvaluatedKey' in response :
      response = table.sacan(ExclusiveStartKey=response['lastEvaluatedKey'])
      result.extend(response['Item'])
      
    body = {
      'cars': response
    }
    return buildresponse(200, body)
  except :
    logger.exception('Do your custom error handling here. I am just gonna log it out here!!')
    
def saveCar(requestBody) :
  try :
    table.put_item(Item=requestBody)
    body = {
      'Operation': 'SAVE',
      'Message': 'SUCCESS' ,
      'Item': requestBody
    }
  except :
    logger.exception('Do your custom error handling here. I am just gonna log it out here!!')
    
def modifyCar(carId, updateKey, updateValue) :
  try :
    response = table.update_item(
      Key={
        'carId': carId
      },
      UpdateExpression='set %s = :val' % updateKey,
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
  except :  
    logger.exception('Do your custom error handling here. I am just gonna log it out here!!')
    
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
  except :
    logger.exception('Do your custom error handling here. I am just gonna log it out here!!')
    
def buildresponse(statusCode, body=None) :
  response = {
    'statusCode': statusCode,
    'headers': {
      'Content-Type': 'application/json',
      'Access-Control-Allow-Origin': '*'
    }
  }
  if body is not None :
    response['body'] = json.dumps(body, cls=CustomEncoder)
  return response