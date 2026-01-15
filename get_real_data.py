import pandas as pd
import pandas_datareader as pdr
from datetime import datetime

print("attempting to download 10 years of SPY data...")

# try multiple sources
sources_to_try = [
    ('stooq', 'downloading from stooq (polish stock market data provider)...'),
    ('yahoo', 'trying yahoo finance directly...'),
]

df = None

for source, msg in sources_to_try:
    print(f"\n{msg}")
    try:
        df = pdr.DataReader('SPY', source, start='2014-01-01', end='2024-12-31')
        if df is not None and len(df) > 1000:
            print(f"✓ success! downloaded {len(df)} rows from {source}")
            break
    except Exception as e:
        print(f"✗ failed: {e}")

if df is None or len(df) < 1000:
    print("\n✗ all sources failed")
    print("\nalternative: download manually from:")
    print("https://query1.finance.yahoo.com/v7/finance/download/SPY?period1=1388534400&period2=1735689600&interval=1d&events=history")
    exit(1)

# process and save
df.reset_index(inplace=True)

# standardize column names
if 'Date' not in df.columns and 'index' in df.columns:
    df.rename(columns={'index': 'Date'}, inplace=True)

df = df[['Date', 'Open', 'High', 'Low', 'Close', 'Volume']]
df = df.sort_values('Date')

df.to_csv('backend/data/SPY_raw.csv', index=False)

print(f"\n✓ saved {len(df)} rows to backend/data/SPY_raw.csv")
print(f"date range: {df['Date'].min()} to {df['Date'].max()}")
