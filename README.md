# volatility trading simulator

automated daily spy volatility prediction using xgboost deployed on aws lambda. runs every day at 5pm et, predicts if volatility will go up or down tomorrow.

## what it does

predicts spy volatility changes using machine learning
- binary classification: will volatility increase or decrease tomorrow
- confidence scoring: low/medium/high based on model probability
- automated: github actions triggers lambda daily
- stores predictions in dynamodb with timestamp

## model performance

trained on 2,768 days of spy data from 2014-2024
- cv accuracy: 61.4% (5-fold time series cross validation)
- features: 31 technical indicators
- top 3 features: volatility_20d (8.8%), momentum_10 (5.8%), returns_5d (5.0%)
- model size: 61kb
- hyperparameters: bayesian optimization, 40 iterations

## tech stack

ml: xgboost, pandas, numpy, scikit-learn
cloud: aws lambda (containerized), s3, dynamodb
automation: github actions
data: alpha vantage api (free tier, 100 days)

cost: about $0.03/month (mostly free tier)

## how to run locally

```bash
# get spy data
python get_real_data.py

# train model
python backend/src/feature_engineering.py

# test predictions
python test_model_predictions.py
```

## architecture

lambda container loads xgboost model from s3, engineers 31 features from ohlcv data, makes prediction, saves to dynamodb. github actions fetches spy data via alpha vantage api and invokes lambda daily.

## example output

```
date: 2026-01-15
prediction: decrease
confidence: medium (55.17%)
```

## features used

returns (1d, 5d, 10d, 20d), volatility (5d, 10d, 20d, 60d), sma (5, 10, 20, 50), ema (12, 26), rsi, atr, volume indicators, momentum, roc, bollinger bands, macd
