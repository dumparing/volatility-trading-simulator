import yfinance as yf
import pandas as pd
import time

print("downloading SPY data from yahoo finance...")

# try with session and retry
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

session = requests.Session()
retry = Retry(connect=3, backoff_factor=0.5)
adapter = HTTPAdapter(max_retries=retry)
session.mount('http://', adapter)
session.mount('https://', adapter)

# download with retry
for attempt in range(3):
    try:
        spy = yf.download('SPY', start='2014-01-01', end='2024-12-31', session=session, progress=False)
        if len(spy) > 0:
            break
        print(f"attempt {attempt + 1} got 0 rows, retrying...")
        time.sleep(2)
    except Exception as e:
        print(f"attempt {attempt + 1} failed: {e}")
        if attempt < 2:
            time.sleep(2)

if len(spy) == 0:
    print("ERROR: failed to download data after 3 attempts")
    print("trying alternative method...")

    # fallback: use Ticker object
    spy_ticker = yf.Ticker("SPY")
    spy = spy_ticker.history(start='2014-01-01', end='2024-12-31')

print(f"downloaded {len(spy)} rows")

spy.reset_index(inplace=True)
spy.to_csv('backend/data/SPY_raw.csv', index=False)

print(f"saved to backend/data/SPY_raw.csv")
print(f"date range: {spy['Date'].min()} to {spy['Date'].max()}")
