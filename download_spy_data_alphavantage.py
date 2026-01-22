import requests
import pandas as pd
import time

# you need to set this - get it from alphavantage.co
API_KEY = input("Enter your Alpha Vantage API key: ").strip()

print("downloading SPY data from alpha vantage...")
print("note: this will take a while due to API rate limits (5 calls/min)")

all_data = []

# alpha vantage free tier: compact gives 100 days
# for full history, we need to use different approach or just use the 100 days
url = "https://www.alphavantage.co/query"

# try to get as much as possible with free tier
params = {
    'function': 'TIME_SERIES_DAILY',
    'symbol': 'SPY',
    'outputsize': 'compact',  # 100 days
    'apikey': API_KEY,
    'datatype': 'csv'
}

print("fetching data...")
response = requests.get(url, params=params)

if response.status_code == 200:
    # save raw csv
    with open('backend/data/SPY_raw.csv', 'w') as f:
        f.write(response.text)

    # read it back to check
    df = pd.read_csv('backend/data/SPY_raw.csv')
    print(f"downloaded {len(df)} rows")
    print(f"date range: {df['timestamp'].min()} to {df['timestamp'].max()}")

    # rename columns to match expected format
    df = df.rename(columns={
        'timestamp': 'Date',
        'open': 'Open',
        'high': 'High',
        'low': 'Low',
        'close': 'Close',
        'volume': 'Volume'
    })

    # sort by date ascending
    df = df.sort_values('Date')

    df.to_csv('backend/data/SPY_raw.csv', index=False)
    print(f"saved {len(df)} rows to backend/data/SPY_raw.csv")
else:
    print(f"error: {response.status_code}")
    print(response.text)
