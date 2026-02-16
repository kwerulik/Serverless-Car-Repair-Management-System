import json
import boto3
import uuid
from datetime import datetime
import os

# Service init
SNS_TOPIC_ARN = os.environ.get('SNS_TOPIC_ARN')
dynamodb = boto3.resource('dynamodb')
sns = boto3.client('sns')
table = dynamodb.Table('Repairs')

def lambda_handler(event, context):
    print("Event:", event) # debug logging

    try:
        http_method = event.get('requestContext', {}).get('http', {}).get('method')
        if http_method == 'OPTIONS':
            return build_response(200, '')
    except:
        pass

    try:
        if 'body' not in event:
             return build_response(400, {'error': 'Brak danych w body'})
            
        if isinstance(event['body'], str):
            body = json.loads(event['body'])
        else:
            body = event['body']
        
        if 'auto' not in body or 'opis' not in body:
            return build_response(400, {'error': 'Brak pola auto lub opis!'})

        repair_id = str(uuid.uuid4())
        # saving to DB
        item = {
            'Id': repair_id,
            'auto': body['auto'],
            'opis': body['opis'],
            'klient_email': body.get('email', 'brak@email.com'),
            'status': 'PRZYJETY',
            'data_zgloszenia': str(datetime.now())
        }
        table.put_item(Item=item)

        # SNS notif
        sns.publish(
            TopicArn=SNS_TOPIC_ARN,
            Message=f"Nowe zgłoszenie!\nAuto: {body['auto']}\nOpis: {body['opis']}",
            Subject="Nowa Naprawa"
        )

        return build_response(200, {'message': 'Zgłoszenie przyjęte', 'id': repair_id})

    except Exception as e:
        print(f"ERROR: {str(e)}")
        return build_response(500, {'error': str(e)})

def build_response(status_code, body):
    return {
        'statusCode': status_code,
        'headers': {
            'content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
            'Access-Control-Allow-Methods': 'OPTIONS,POST'
        },
        'body': json.dumps(body) if body else ''
    }