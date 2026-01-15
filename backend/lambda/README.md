# lambda function

daily SPY volatility predictions using xgboost

## files

- lambda_handler.py - main handler
- feature_utils.py - feature engineering (36 indicators)
- dynamodb_helper.py - save predictions to dynamodb
- invoke_lambda.py - invoke from github actions
- test_lambda_with_csv.py - local testing
- Dockerfile - container build
- requirements.txt - dependencies

## local test

```bash
python test_lambda_with_csv.py
```

## deployment

build:
```bash
docker buildx build --platform linux/amd64 --provenance=false --sbom=false -t volatility-predictor .
```

push to ecr:
```bash
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 231222198828.dkr.ecr.us-east-1.amazonaws.com
docker tag volatility-predictor:latest 231222198828.dkr.ecr.us-east-1.amazonaws.com/volatility-predictor:latest
docker push 231222198828.dkr.ecr.us-east-1.amazonaws.com/volatility-predictor:latest
```

update lambda:
```bash
aws lambda update-function-code \
  --function-name VolatilityPredictor \
  --image-uri 231222198828.dkr.ecr.us-east-1.amazonaws.com/volatility-predictor:latest
```

## env vars

- S3_BUCKET - bucket with model
- S3_MODEL_KEY - model path in s3
- DYNAMODB_TABLE - predictions table

## confidence levels

- high: ≥70% probability
- medium: 55-70%
- low: <55%
