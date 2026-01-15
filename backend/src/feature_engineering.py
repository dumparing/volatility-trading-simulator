import pandas as pd
import numpy as np
import pickle
from skopt import BayesSearchCV
from skopt.space import Real, Integer
from xgboost import XGBClassifier
from sklearn.model_selection import TimeSeriesSplit

import sys
sys.path.append('../lambda')
from feature_utils import engineer_features, get_feature_columns


def create_target_variable(df, horizon=20):
    df = df.copy()

    df['future_volatility'] = df['volatility_20d'].shift(-horizon)
    df['target'] = (df['future_volatility'] > df['volatility_20d']).astype(int)
    df = df.dropna(subset=['target'])

    return df


def train_model_with_tuning(X, y, n_iter=40):
    print(f"Training XGBoost with Bayesian optimization ({n_iter} iterations)...")

    search_spaces = {
        'n_estimators': Integer(50, 200),
        'max_depth': Integer(3, 10),
        'learning_rate': Real(0.01, 0.3, prior='log-uniform'),
        'subsample': Real(0.6, 1.0),
        'colsample_bytree': Real(0.6, 1.0),
    }

    xgb = XGBClassifier(
        objective='binary:logistic',
        random_state=42,
        use_label_encoder=False,
        eval_metric='logloss'
    )

    tscv = TimeSeriesSplit(n_splits=5)

    opt = BayesSearchCV(
        xgb,
        search_spaces,
        n_iter=n_iter,
        cv=tscv,
        scoring='accuracy',
        n_jobs=-1,
        random_state=42,
        verbose=1
    )

    opt.fit(X, y)

    print(f"\nBest CV score: {opt.best_score_:.4f}")
    print("Best parameters:")
    for param, value in opt.best_params_.items():
        print(f"  {param}: {value}")

    return opt.best_estimator_, opt.best_params_, opt.best_score_


def save_feature_importance(model, feature_names, output_path='../models/feature_importance.csv'):
    importances = pd.DataFrame({
        'feature': feature_names,
        'importance': model.feature_importances_
    }).sort_values('importance', ascending=False)

    importances.to_csv(output_path, index=False)
    print(f"\nFeature importances saved to {output_path}")
    print("\nTop 10 features:")
    print(importances.head(10).to_string(index=False))


def main():
    print("Loading SPY data...")
    df = pd.read_csv('../data/SPY_raw.csv')
    df['Date'] = pd.to_datetime(df['Date'])
    df = df.set_index('Date')

    print(f"Loaded {len(df)} rows from {df.index[0]} to {df.index[-1]}")

    print("\nEngineering features...")
    df_features = engineer_features(df)

    print("Creating target variable...")
    df_features = create_target_variable(df_features, horizon=20)

    feature_cols = get_feature_columns()
    df_features = df_features.dropna(subset=feature_cols)

    print(f"\nFinal dataset: {len(df_features)} rows with {len(feature_cols)} features")

    output_csv = '../data/SPY_features.csv'
    df_features.to_csv(output_csv)
    print(f"Saved features to {output_csv}")

    X = df_features[feature_cols].values
    y = df_features['target'].values

    print(f"\nTarget distribution:")
    print(f"  Volatility will increase: {y.sum()} ({y.mean():.1%})")
    print(f"  Volatility will decrease: {len(y) - y.sum()} ({(1-y.mean()):.1%})")

    model, best_params, cv_score = train_model_with_tuning(X, y, n_iter=40)

    model_path = '../models/xgboost_tuned.pkl'
    with open(model_path, 'wb') as f:
        pickle.dump(model, f)
    print(f"\nModel saved to {model_path}")

    save_feature_importance(model, feature_cols)

    params_path = '../models/best_hyperparameters.json'
    import json
    with open(params_path, 'w') as f:
        json.dump(best_params, f, indent=2)
    print(f"Best parameters saved to {params_path}")

    print("\n✓ Training complete!")
    print(f"  CV Accuracy: {cv_score:.1%}")
    print(f"  Model: {model_path}")
    print(f"  Features: {output_csv}")


if __name__ == "__main__":
    main()
