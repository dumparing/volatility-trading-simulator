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

def get_prediction(date_str):
    table_name = os.environ.get('DYNAMODB_TABLE', 'VolatilityPredictions')

    dynamodb = get_dynamodb_client()
    table = dynamodb.Table(table_name)

    try:
        response = table.get_item(Key={'date': date_str})
        return response.get('Item')
    except Exception as e:
        print(f"error getting prediction for {date_str}: {str(e)}")
        return None

def update_prediction_accuracy(date_str, actual_volatility, actual_change, is_correct):
    table_name = os.environ.get('DYNAMODB_TABLE', 'VolatilityPredictions')

    dynamodb = get_dynamodb_client()
    table = dynamodb.Table(table_name)

    try:
        table.update_item(
            Key={'date': date_str},
            UpdateExpression='SET actual_volatility_20d = :vol, actual_change = :change, is_correct = :correct, verified_at = :verified',
            ExpressionAttributeValues={
                ':vol': Decimal(str(actual_volatility)),
                ':change': actual_change,
                ':correct': is_correct,
                ':verified': datetime.utcnow().isoformat()
            }
        )
        print(f"updated accuracy for {date_str}: correct={is_correct}")
        return True
    except Exception as e:
        print(f"error updating accuracy for {date_str}: {str(e)}")
        return False
