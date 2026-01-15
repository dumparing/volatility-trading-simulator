import boto3
import os
from datetime import datetime
from decimal import Decimal

dynamodb = None

def get_dynamodb_client():
    global dynamodb
    if dynamodb is None:
        dynamodb = boto3.resource('dynamodb')
    return dynamodb

def save_prediction_to_dynamodb(date_str, prediction, prediction_text, confidence_score, confidence_level, key_features):
    table_name = os.environ.get('DYNAMODB_TABLE', 'VolatilityPredictions')

    dynamodb = get_dynamodb_client()
    table = dynamodb.Table(table_name)

    # dynamodb needs Decimal not float
    key_features_decimal = {k: Decimal(str(v)) for k, v in key_features.items()}

    item = {
        'date': date_str,
        'prediction': prediction,
        'prediction_text': prediction_text,
        'confidence_score': Decimal(str(confidence_score)),
        'confidence_level': confidence_level,
        'timestamp': datetime.utcnow().isoformat(),
        **key_features_decimal
    }

    table.put_item(Item=item)
    print(f"saved prediction to dynamodb: {date_str}")

    return item
