import json
import boto3
import requests
import os
from datetime import datetime

def fetch_spy_data_alpha_vantage(api_key, days=100):
    url = f"https://www.alphavantage.co/query"
    params = {
        'function': 'TIME_SERIES_DAILY',
        'symbol': 'SPY',
        'outputsize': 'full',  # get full history
        'apikey': api_key
    }

    print(f"fetching {days} days of SPY data from Alpha Vantage...")
    response = requests.get(url, params=params)
    data = response.json()

    if 'Time Series (Daily)' not in data:
        print(f"API Response: {data}")
        error_msg = data.get('Note', data.get('Error Message', data.get('Information', str(data))))
        raise ValueError(f"Failed to fetch data: {error_msg}")

    time_series = data['Time Series (Daily)']

    spy_data = []
    for date_str, values in sorted(time_series.items(), reverse=True)[:days]:
        spy_data.append({
            'Date': date_str,
            'Open': float(values['1. open']),
            'High': float(values['2. high']),
            'Low': float(values['3. low']),
            'Close': float(values['4. close']),
            'Volume': float(values['5. volume'])
        })

    spy_data.reverse()

    print(f"fetched {len(spy_data)} days of data")
    print(f"date range: {spy_data[0]['Date']} to {spy_data[-1]['Date']}")

    return spy_data

def invoke_lambda_function(function_name, spy_data, s3_bucket, s3_model_key):
    lambda_client = boto3.client('lambda')

    payload = {
        'data': spy_data,
        's3_bucket': s3_bucket,
        's3_model_key': s3_model_key
    }

    print(f"invoking lambda function: {function_name}")
    response = lambda_client.invoke(
        FunctionName=function_name,
        InvocationType='RequestResponse',
        Payload=json.dumps(payload)
    )

    result = json.loads(response['Payload'].read())

    return result

def main():
    alpha_vantage_api_key = os.environ.get('ALPHA_VANTAGE_API_KEY')
    lambda_function_name = os.environ.get('LAMBDA_FUNCTION_NAME', 'VolatilityPredictor')
    s3_bucket = os.environ.get('S3_BUCKET', 'volatility-trading-models-1767821459')
    s3_model_key = os.environ.get('S3_MODEL_KEY', 'models/xgboost_tuned.pkl')

    if not alpha_vantage_api_key:
        raise ValueError("ALPHA_VANTAGE_API_KEY environment variable not set")

    spy_data = fetch_spy_data_alpha_vantage(alpha_vantage_api_key, days=100)
    result = invoke_lambda_function(lambda_function_name, spy_data, s3_bucket, s3_model_key)
    if result.get('statusCode') == 200:
        body = json.loads(result['body'])
        print("\n=== PREDICTION SUCCESSFUL ===")
        print(f"Date: {body['date']}")
        print(f"Prediction: {body['prediction_text']}")
        print(f"Confidence: {body['confidence_level']} ({body['confidence_score']:.2%})")
        print(f"\nKey Features:")
        for feature, value in body['key_features'].items():
            print(f"  {feature}: {value:.6f}")
    else:
        print(f"\n=== PREDICTION FAILED ===")
        print(f"Status: {result.get('statusCode')}")
        body = json.loads(result.get('body', '{}'))
        print(f"Error: {body.get('error', 'Unknown error')}")

if __name__ == "__main__":
    main()
