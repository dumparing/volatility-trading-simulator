import json
import pickle
import pandas as pd
import boto3
import os
from io import BytesIO
from feature_utils import engineer_features, get_feature_columns
from dynamodb_helper import save_prediction_to_dynamodb

# cache model in memory for container reuse
model = None
s3_client = None

def load_model_from_s3(bucket_name, model_key):
    global model, s3_client

    if model is not None:
        return model

    if s3_client is None:
        s3_client = boto3.client('s3')

    print(f"loading model from s3://{bucket_name}/{model_key}")

    response = s3_client.get_object(Bucket=bucket_name, Key=model_key)
    model_bytes = response['Body'].read()
    model = pickle.loads(model_bytes)

    print("model loaded")
    return model

def load_model_from_local(model_path):
    global model

    if model is not None:
        return model

    print(f"loading model from {model_path}")
    with open(model_path, 'rb') as f:
        model = pickle.load(f)

    print("model loaded")
    return model

def lambda_handler(event, context):
    try:
        if isinstance(event, str):
            event = json.loads(event)

        data = event.get('data')
        if not data:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'missing data field'})
            }

        # load model from s3 or local
        if 'local_model_path' in event:
            model = load_model_from_local(event['local_model_path'])
        else:
            bucket = event.get('s3_bucket')
            model_key = event.get('s3_model_key')
            if not bucket or not model_key:
                return {
                    'statusCode': 400,
                    'body': json.dumps({'error': 'missing s3_bucket or s3_model_key'})
                }
            model = load_model_from_s3(bucket, model_key)

        df = pd.DataFrame(data)
        if 'Date' in df.columns:
            df['Date'] = pd.to_datetime(df['Date'])
            df = df.set_index('Date')

        print("engineering features...")
        df_features = engineer_features(df)

        latest = df_features.iloc[-1]
        feature_cols = get_feature_columns()
        X = latest[feature_cols].values.reshape(1, -1)

        # make sure no nans in the data
        if pd.isna(X).any():
            return {
                'statusCode': 400,
                'body': json.dumps({
                    'error': 'nan values in features - need more historical data',
                    'nan_features': [feature_cols[i] for i in range(len(feature_cols)) if pd.isna(X[0, i])]
                })
            }

        print("making prediction...")
        prediction = int(model.predict(X)[0])

        probabilities = model.predict_proba(X)[0]
        confidence_score = float(max(probabilities))

        # map to low/medium/high
        if confidence_score >= 0.70:
            confidence_level = "high"
        elif confidence_score >= 0.55:
            confidence_level = "medium"
        else:
            confidence_level = "low"

        prediction_text = "volatility will increase" if prediction == 1 else "volatility will decrease"

        # pull out key features for output
        key_feature_names = ['volatility_20d', 'rsi', 'bb_width', 'macd', 'volume_ratio']
        key_features = {}
        for feat in key_feature_names:
            if feat in feature_cols:
                idx = feature_cols.index(feat)
                key_features[feat] = float(X[0, idx])

        date_str = df_features.index[-1].strftime('%Y-%m-%d') if hasattr(df_features.index[-1], 'strftime') else str(df_features.index[-1])

        if os.environ.get('DYNAMODB_TABLE'):
            save_prediction_to_dynamodb(date_str, prediction, prediction_text, confidence_score, confidence_level, key_features)

        # build response
        response = {
            'statusCode': 200,
            'body': json.dumps({
                'prediction': prediction,
                'prediction_text': prediction_text,
                'confidence_score': confidence_score,
                'confidence_level': confidence_level,
                'date': date_str,
                'key_features': key_features
            })
        }

        print(f"prediction successful!")
        print(f"date: {date_str}")
        print(f"prediction: {prediction_text}")
        print(f"confidence: {confidence_level} ({confidence_score:.2%})")
        return response

    except Exception as e:
        print(f"error: {str(e)}")
        import traceback
        traceback.print_exc()

        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': str(e),
                'type': type(e).__name__
            })
        }

if __name__ == "__main__":
    test_event = {
        "local_model_path": "../models/xgboost_final.pkl",
        "data": [
            {"Date": "2024-01-01", "Open": 100, "High": 102, "Low": 99, "Close": 101, "Volume": 1000000}
        ]
    }

    result = lambda_handler(test_event, None)
    print(json.dumps(result, indent=2))
