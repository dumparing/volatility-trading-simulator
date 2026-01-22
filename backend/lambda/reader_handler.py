import json
import os
from datetime import datetime, timedelta
from decimal import Decimal
import boto3
from boto3.dynamodb.conditions import Key

# dynamodb client
dynamodb = boto3.resource('dynamodb')
table_name = os.environ.get('DYNAMODB_TABLE', 'VolatilityPredictions')
table = dynamodb.Table(table_name)

def decimal_to_float(obj):
    if isinstance(obj, list):
        return [decimal_to_float(i) for i in obj]
    elif isinstance(obj, dict):
        return {k: decimal_to_float(v) for k, v in obj.items()}
    elif isinstance(obj, Decimal):
        return float(obj)
    else:
        return obj

def transform_prediction(item):
    confidence = float(item.get('confidence', 0))
    prediction = int(item.get('prediction', 0))

    if confidence > 0.7:
        confidence_level = 'high'
    elif confidence > 0.5:
        confidence_level = 'medium'
    else:
        confidence_level = 'low'

    prediction_text = 'INCREASE' if prediction == 1 else 'DECREASE'

    transformed = dict(item)
    transformed['confidence_score'] = confidence
    transformed['confidence_level'] = confidence_level
    transformed['prediction_text'] = prediction_text

    return transformed

def lambda_handler(event, context):
    http_method = event.get('httpMethod', '')
    path = event.get('path', '')
    query_params = event.get('queryStringParameters') or {}

    headers = {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type,X-Api-Key',
        'Access-Control-Allow-Methods': 'GET,OPTIONS'
    }

    if http_method == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': headers,
            'body': ''
        }

    try:
        if path.endswith('/predictions/latest'):
            result = get_latest_prediction()
        elif path.endswith('/predictions/range'):
            start_date = query_params.get('start')
            end_date = query_params.get('end')
            if not start_date or not end_date:
                return error_response('missing start or end date', 400, headers)
            result = get_predictions_range(start_date, end_date)
        elif path.endswith('/predictions/all'):
            limit = int(query_params.get('limit', 90))
            result = get_all_predictions(limit)
        elif path.endswith('/analytics/accuracy'):
            result = get_accuracy_metrics()
        else:
            return error_response('not found', 404, headers)

        return {
            'statusCode': 200,
            'headers': headers,
            'body': json.dumps(decimal_to_float(result))
        }

    except Exception as e:
        print(f"error: {str(e)}")
        return error_response(str(e), 500, headers)

def get_latest_prediction():
    response = table.scan()
    items = response.get('Items', [])

    if not items:
        raise Exception('no predictions found')

    items.sort(key=lambda x: x['date'], reverse=True)
    return transform_prediction(items[0])

def get_predictions_range(start_date, end_date):
    response = table.scan(
        FilterExpression=Key('date').between(start_date, end_date)
    )

    items = response.get('Items', [])
    items.sort(key=lambda x: x['date'])

    return [transform_prediction(item) for item in items]

def get_all_predictions(limit=90):
    response = table.scan()
    items = response.get('Items', [])

    items.sort(key=lambda x: x['date'], reverse=True)

    return [transform_prediction(item) for item in items[:limit]]

def get_accuracy_metrics():
    response = table.scan()
    items = response.get('Items', [])

    verified = [item for item in items if 'is_correct' in item]

    if not verified:
        return {
            'total_predictions': 0,
            'correct_predictions': 0,
            'accuracy_rate': 0.0,
            'by_confidence': {
                'high': {'total': 0, 'correct': 0, 'rate': 0.0},
                'medium': {'total': 0, 'correct': 0, 'rate': 0.0},
                'low': {'total': 0, 'correct': 0, 'rate': 0.0}
            },
            'recent_30d_accuracy': 0.0,
            'current_streak': 0
        }

    total = len(verified)
    correct = sum(1 for item in verified if item['is_correct'])
    accuracy_rate = correct / total if total > 0 else 0.0

    by_confidence = {}
    for level in ['high', 'medium', 'low']:
        level_items = [item for item in verified if item.get('confidence_level') == level]
        level_correct = sum(1 for item in level_items if item['is_correct'])
        level_total = len(level_items)
        by_confidence[level] = {
            'total': level_total,
            'correct': level_correct,
            'rate': level_correct / level_total if level_total > 0 else 0.0
        }

    thirty_days_ago = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
    recent = [item for item in verified if item['date'] >= thirty_days_ago]
    recent_correct = sum(1 for item in recent if item['is_correct'])
    recent_total = len(recent)
    recent_accuracy = recent_correct / recent_total if recent_total > 0 else 0.0

    sorted_items = sorted(verified, key=lambda x: x['date'], reverse=True)
    current_streak = 0
    for item in sorted_items:
        if item['is_correct']:
            current_streak += 1
        else:
            break

    return {
        'total_predictions': total,
        'correct_predictions': correct,
        'accuracy_rate': accuracy_rate,
        'by_confidence': by_confidence,
        'recent_30d_accuracy': recent_accuracy,
        'current_streak': current_streak
    }

def error_response(message, status_code, headers):
    return {
        'statusCode': status_code,
        'headers': headers,
        'body': json.dumps({'error': message})
    }
