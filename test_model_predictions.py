import pickle
import pandas as pd
import sys
sys.path.append('backend/lambda')
from feature_utils import engineer_features, get_feature_columns

# load model
with open('backend/models/xgboost_tuned.pkl', 'rb') as f:
    model = pickle.load(f)

# load SPY data
df = pd.read_csv('backend/data/SPY_raw.csv')
df['Date'] = pd.to_datetime(df['Date'])
df = df.set_index('Date')

# engineer features
df_features = engineer_features(df)
feature_cols = get_feature_columns()

# test predictions on last 10 days
print("Testing model predictions on last 10 days:\n")
for i in range(-10, 0):
    row = df_features.iloc[i]
    X = row[feature_cols].values.reshape(1, -1)

    if pd.isna(X).any():
        print(f"{row.name.date()}: SKIP (has NaN)")
        continue

    pred = model.predict(X)[0]
    proba = model.predict_proba(X)[0]
    conf = max(proba)

    pred_text = "INCREASE" if pred == 1 else "DECREASE"
    level = "HIGH" if conf >= 0.70 else "MED" if conf >= 0.55 else "LOW"

    print(f"{row.name.date()}: {pred_text:8} confidence: {level:4} ({conf:.1%})")

print(f"\nModel has {len(feature_cols)} features")
print(f"Dataset has {len(df_features)} days of history")
