import json
import os
import boto3
import uuid
from aws_lambda_powertools import Logger
from pydantic import BaseModel, EmailStr, ValidationError

logger = Logger()
dynamodb = boto3.resource('dynamodb')
TABLE_NAME = os.environ.get('TABLE_NAME')
table = dynamodb.Table(TABLE_NAME)
sns = boto3.client('sns')
topic_arn = os.environ.get('SNS_TOPIC_ARN')

class RepairRequest(BaseModel):
    auto: str
    opis: str
    email: EmailStr = "brak@email.com"


def lambda_handler(event, context):
    logger.info("Otrzymano nowe zdarzenie", extra={"raw_event": event})

    try:
        body_str = event.get('body', '{}')
        body_json = json.loads(body_str)
        request_data = RepairRequest(**body_json)

        repair_id = str(uuid.uuid4())
        item = {
            'Id': repair_id,
            'auto': request_data.auto,
            'opis': request_data.opis,
            'email': request_data.email
        }

        table.put_item(Item=item)
        logger.info(f"Zapisano zgłoszenie {repair_id} do tabeli {TABLE_NAME}")


        sns.publish(
            TopicArn=topic_arn,
            Message=f"Nowe zgłoszenie naprawy!\nAuto: {request_data.auto}\nOpis: {request_data.opis}",
            Subject="Nowa Naprawa - System CDK"
        )
        logger.info("Wysłano powiadomienie SNS")

        return {
            "statusCode": 200,
            "headers": {
                "Access-Control-Allow-Origin": "*", 
                "Content-Type": "application/json"
            },
            "body": json.dumps({"message": "Zgłoszenie zapisane!", "id": repair_id})
        }

    except ValidationError as e:
        logger.error(f"Błąd walidacji danych: {e.json()}")
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "Niepoprawne dane wejściowe", "details": e.errors()})
        }
    except Exception as e:
        logger.exception("Wystąpił nieoczekiwany błąd")
        return {"statusCode": 500, "body": "Błąd serwera"}
