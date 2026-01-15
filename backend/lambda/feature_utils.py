import pandas as pd
import numpy as np

def calculate_returns(df):
    df['returns'] = df['Close'].pct_change()
    df['returns_5d'] = df['Close'].pct_change(5)
    df['returns_10d'] = df['Close'].pct_change(10)
    df['returns_20d'] = df['Close'].pct_change(20)
    return df

def calculate_volatility(df):
    # rolling volatility
    df['volatility_5d'] = df['returns'].rolling(window=5).std()
    df['volatility_10d'] = df['returns'].rolling(window=10).std()
    df['volatility_20d'] = df['returns'].rolling(window=20).std()
    df['volatility_60d'] = df['returns'].rolling(window=60).std()
    return df

def calculate_moving_averages(df):
    # sma and ema
    df['sma_5'] = df['Close'].rolling(window=5).mean()
    df['sma_10'] = df['Close'].rolling(window=10).mean()
    df['sma_20'] = df['Close'].rolling(window=20).mean()
    df['sma_50'] = df['Close'].rolling(window=50).mean()
    df['ema_12'] = df['Close'].ewm(span=12, adjust=False).mean()
    df['ema_26'] = df['Close'].ewm(span=26, adjust=False).mean()
    return df

def calculate_rsi(df, period=14):
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    df['rsi'] = 100 - (100 / (1 + rs))
    return df

def calculate_atr(df, period=14):
    high_low = df['High'] - df['Low']
    high_close = np.abs(df['High'] - df['Close'].shift())
    low_close = np.abs(df['Low'] - df['Close'].shift())
    ranges = pd.concat([high_low, high_close, low_close], axis=1)
    true_range = np.max(ranges, axis=1)
    df['atr'] = true_range.rolling(period).mean()
    return df

def calculate_volume_indicators(df):
    df['volume_sma_20'] = df['Volume'].rolling(window=20).mean()
    df['volume_ratio'] = df['Volume'] / df['volume_sma_20']
    df['volume_change'] = df['Volume'].pct_change()
    return df

def calculate_price_momentum(df):
    df['momentum_5'] = df['Close'] - df['Close'].shift(5)
    df['momentum_10'] = df['Close'] - df['Close'].shift(10)
    df['momentum_20'] = df['Close'] - df['Close'].shift(20)
    df['roc_5'] = ((df['Close'] - df['Close'].shift(5)) / df['Close'].shift(5)) * 100
    df['roc_10'] = ((df['Close'] - df['Close'].shift(10)) / df['Close'].shift(10)) * 100
    return df

def calculate_bollinger_bands(df, period=20, std=2):
    df['bb_middle'] = df['Close'].rolling(window=period).mean()
    bb_std = df['Close'].rolling(window=period).std()
    df['bb_upper'] = df['bb_middle'] + (bb_std * std)
    df['bb_lower'] = df['bb_middle'] - (bb_std * std)
    df['bb_width'] = (df['bb_upper'] - df['bb_lower']) / df['bb_middle']
    return df

def calculate_macd(df):
    exp1 = df['Close'].ewm(span=12, adjust=False).mean()
    exp2 = df['Close'].ewm(span=26, adjust=False).mean()
    df['macd'] = exp1 - exp2
    df['macd_signal'] = df['macd'].ewm(span=9, adjust=False).mean()
    df['macd_histogram'] = df['macd'] - df['macd_signal']
    return df

def engineer_features(df):
    df = df.copy()
    df = calculate_returns(df)
    df = calculate_volatility(df)
    df = calculate_moving_averages(df)
    df = calculate_rsi(df)
    df = calculate_atr(df)
    df = calculate_volume_indicators(df)
    df = calculate_price_momentum(df)
    df = calculate_bollinger_bands(df)
    df = calculate_macd(df)
    return df

def get_feature_columns():
    all_features = [
        'returns', 'returns_5d', 'returns_10d', 'returns_20d',
        'volatility_5d', 'volatility_10d', 'volatility_20d', 'volatility_60d',
        'sma_5', 'sma_10', 'sma_20', 'sma_50',
        'ema_12', 'ema_26',
        'rsi', 'atr',
        'volume_sma_20', 'volume_ratio', 'volume_change',
        'momentum_5', 'momentum_10', 'momentum_20',
        'roc_5', 'roc_10',
        'bb_middle', 'bb_upper', 'bb_lower', 'bb_width',
        'macd', 'macd_signal', 'macd_histogram'
    ]
    return all_features
