import json
import os
import boto3
from aws_lambda_powertools import Logger
from pydantic import BaseModel, EmailStr, ValidationError

logger = Logger()


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

        logger.info(f"Walidacja udana dla auta: {request_data.auto}")

        return {
            "statusCode": 200,
            "body": json.dumps({"message": "Dane są poprawne!", "auto": request_data.auto})
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
