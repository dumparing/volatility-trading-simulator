import json
import pandas as pd
from lambda_handler import lambda_handler

def test_lambda_with_csv(csv_path='../data/SPY_raw.csv', model_path='../models/xgboost_tuned.pkl'):
    print(f"Loading data from {csv_path}")

    df = pd.read_csv(csv_path)
    df = df.tail(100)
    data = df.to_dict('records')

    print(f"Testing with {len(data)} days of data")
    print(f"Date range: {data[0]['Date']} to {data[-1]['Date']}")

    event = {
        'local_model_path': model_path,
        'data': data
    }

    print("\nInvoking lambda handler...")
    result = lambda_handler(event, None)

    print("\n=== RESULT ===")
    print(f"Status: {result['statusCode']}")

    if result['statusCode'] == 200:
        body = json.loads(result['body'])
        print(f"Date: {body['date']}")
        print(f"Prediction: {body['prediction_text']}")
        print(f"Confidence: {body['confidence_level']} ({body['confidence_score']:.2%})")
        print(f"\nKey Features:")
        for feature, value in body['key_features'].items():
            print(f"  {feature}: {value:.6f}")
    else:
        body = json.loads(result['body'])
        print(f"Error: {body.get('error', 'Unknown error')}")
        if 'nan_features' in body:
            print(f"NaN features: {body['nan_features']}")

if __name__ == "__main__":
    test_lambda_with_csv()
