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

**backend:**
- ml: xgboost, pandas, numpy, scikit-learn
- cloud: aws lambda (containerized), s3, dynamodb, api gateway
- automation: github actions
- data: alpha vantage api (free tier, 100 days)

**frontend:**
- react 18 + typescript
- vite, tailwind css, recharts
- tanstack query, axios
- deployed on vercel

cost: about $0.08/month (mostly free tier)

## frontend dashboard

live demo: [your-vercel-url.vercel.app](https://your-vercel-url.vercel.app) (deploy to add url)

features:
- latest prediction card with confidence visualization
- historical prediction chart (last 90 days)
- accuracy metrics by confidence level
- technical indicators chart (rsi, volatility, macd, bollinger bands, volume ratio)

see [frontend/README.md](frontend/README.md) for setup instructions.

## how to run locally

**backend:**
```bash
# get spy data
python get_real_data.py

# train model
python backend/src/feature_engineering.py

# test predictions
python test_model_predictions.py
```

**frontend:**
```bash
cd frontend
npm install
npm run dev
# open http://localhost:5173
```

## architecture

```
React Dashboard (Vercel)
    ↓ HTTPS
API Gateway (REST)
    ↓ Lambda Proxy
Read Lambda (128MB)
    ↓ Query
DynamoDB (predictions)
    ↑ Write
Prediction Lambda (1024MB)
    ↑ Trigger Daily
GitHub Actions (5pm ET)
```

**prediction flow:** github actions fetches spy data from alpha vantage → invokes prediction lambda → lambda loads xgboost model from s3 → engineers 31 features → makes prediction → saves to dynamodb with confidence scores

**dashboard flow:** react app calls api gateway → read lambda queries dynamodb → returns predictions, accuracy metrics, and historical data → visualized with recharts

## example output

```
date: 2026-01-15
prediction: decrease
confidence: medium (55.17%)
```

## features used

returns (1d, 5d, 10d, 20d), volatility (5d, 10d, 20d, 60d), sma (5, 10, 20, 50), ema (12, 26), rsi, atr, volume indicators, momentum, roc, bollinger bands, macd
