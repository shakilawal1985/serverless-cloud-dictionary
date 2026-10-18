import json
import boto3

dynamodb = boto3.client('dynamodb')
table_name = 'CloudDefinitions'

# [NEW] Shared CORS headers (was repeated inline in each return)
HEADERS = {
    'Content-Type': 'application/json',
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'OPTIONS,GET',
    'Access-Control-Allow-Headers': 'Content-Type',
}

# [NEW] trim, collapse repeated spaces, lowercase
def normalize(text):
    return ' '.join(text.split()).lower()

# [NEW] Scan the table and return the item whose term matches, ignoring case
def find_term(search):
    target = normalize(search)
    paginator = dynamodb.get_paginator('scan')
    for page in paginator.paginate(TableName=table_name):
        for item in page['Items']:
            if normalize(item['term']['S']) == target:
                return item
    return None

def lambda_handler(event, context):
    # [CHANGED] was: term = event['queryStringParameters']['term']
    params = event.get('queryStringParameters') or {}
    term = params.get('term', '')

    # [NEW] Return 400 if no term was provided
    if not term.strip():
        return {
            'statusCode': 400,
            'headers': HEADERS,
            'body': json.dumps({'message': 'term is required'})
        }

    # [CHANGED] was: response = dynamodb.get_item(TableName=table_name, Key={'term': {'S': term}})
    item = find_term(term)

    # [CHANGED] was: if 'Item' in response:
    if item:
        return {
            'statusCode': 200,
            'headers': HEADERS,  # [CHANGED] was: inline headers dict
            'body': json.dumps({
                'term': item['term']['S'],  # [CHANGED] was: 'term': term  (now returns stored spelling, e.g. "AWS KMS")
                'definition': item['definition']['S']  # [CHANGED] was: response['Item']['definition']['S']
            })
        }
    # [CHANGED] was: else: block with inline headers dict
    return {
        'statusCode': 404,
        'headers': HEADERS,
        'body': json.dumps({'message': 'Term not found'})
    }
