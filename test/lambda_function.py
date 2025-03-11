import boto3
import json
import logging
import custom_encoder from CustomEncoder

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
product = '/product'
products = 'products'

def lambda_handler(event, context):
  logger.info(event)
  httpMethod = event['httpdMethod']
  path = event['path']
  if httpdMethod == getMethod and path == healthPath : 
    response = buildResponse(200)
    
def buildresponse(statusCode, body=Nome) :
  response = {
    'statusCode': statusCode,
    'headers': {
      'Content-Type': 'application/json',
      'Access-Control-Allow-Origin': '*'
    }
  }
  if body is not None :
    response['body'] = json.dumps(body)
  return response