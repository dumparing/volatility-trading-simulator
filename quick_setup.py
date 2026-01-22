import requests
import pandas as pd
import numpy as np
import pickle
from xgboost import XGBClassifier
import sys
sys.path.append('backend/lambda')
from feature_utils import engineer_features, get_feature_columns

print("QUICK SETUP - Get data and train model")
print("=" * 50)

# get api key
API_KEY = input("enter your alpha vantage api key: ").strip()

# download data
print("\n1. downloading SPY data (100 days)...")
url = "https://www.alphavantage.co/query"
params = {
    'function': 'TIME_SERIES_DAILY',
    'symbol': 'SPY',
    'outputsize': 'compact',
    'apikey': API_KEY,
    'datatype': 'csv'
}

response = requests.get(url, params=params)

if response.status_code != 200:
    print(f"error downloading data: {response.status_code}")
    print(response.text)
    exit(1)

# save and process data
with open('backend/data/SPY_raw.csv', 'w') as f:
    f.write(response.text)

df = pd.read_csv('backend/data/SPY_raw.csv')
df = df.rename(columns={
    'timestamp': 'Date',
    'open': 'Open',
    'high': 'High',
    'low': 'Low',
    'close': 'Close',
    'volume': 'Volume'
})
df = df.sort_values('Date')
df.to_csv('backend/data/SPY_raw.csv', index=False)

print(f"   downloaded {len(df)} rows ({df['Date'].min()} to {df['Date'].max()})")

# engineer features
print("\n2. engineering features...")
df['Date'] = pd.to_datetime(df['Date'])
df = df.set_index('Date')
df_features = engineer_features(df)

# create target (simple: will volatility increase tomorrow?)
df_features['future_vol'] = df_features['volatility_20d'].shift(-1)
df_features['target'] = (df_features['future_vol'] > df_features['volatility_20d']).astype(int)

# drop nans
feature_cols = get_feature_columns()
df_features = df_features.dropna(subset=feature_cols + ['target'])

print(f"   created {len(df_features)} training samples with {len(feature_cols)} features")

# train model
print("\n3. training xgboost model...")
X = df_features[feature_cols].values
y = df_features['target'].values

model = XGBClassifier(
    n_estimators=100,
    max_depth=6,
    learning_rate=0.1,
    random_state=42
)
model.fit(X, y)

# save model
model_path = 'backend/models/xgboost_tuned.pkl'
with open(model_path, 'wb') as f:
    pickle.dump(model, f)

print(f"   model saved to {model_path}")

# upload to s3
print("\n4. uploading to s3...")
import boto3
s3 = boto3.client('s3')
try:
    s3.upload_file(
        model_path,
        'volatility-trading-models-1767821459',
        'models/xgboost_tuned.pkl'
    )
    print("   ✓ uploaded to s3://volatility-trading-models-1767821459/models/xgboost_tuned.pkl")
except Exception as e:
    print(f"   error uploading to s3: {e}")
    print("   you can upload manually with:")
    print("   aws s3 cp backend/models/xgboost_tuned.pkl s3://volatility-trading-models-1767821459/models/")

print("\n" + "=" * 50)
print("✓ SETUP COMPLETE!")
print("\nYour model is ready. Next time the workflow runs, it will make real predictions.")
print(f"Training data: {len(df_features)} samples")
print(f"Target distribution: {y.sum()}/{len(y)} will increase ({y.mean():.1%})")
