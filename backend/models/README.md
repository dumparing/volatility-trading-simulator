# models

trained xgboost model goes here

model details:
- binary classifier (will volatility increase or decrease)
- 36 features from OHLCV data
- ~68% cv accuracy

upload to s3:
```bash
aws s3 cp xgboost_tuned.pkl s3://volatility-trading-models-1767821459/models/
```
