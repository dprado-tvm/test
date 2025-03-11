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
product = '/product'
products = 'products'

def lambda_handler(event, context):
  logger.info(event)
  httpMethod = event['httpdMethod']
  path = event['path']
  if httpMethod == getMethod and path == healthPath : 
    response = buildresponse(200)
    
def buildresponse(statusCode, body=None) :
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