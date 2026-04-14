import yfinance as yf
import requests
import time
import logging

logging.basicConfig(level=logging.INFO)

def test_fetch():
    symbols = ["AAPL", "MSFT", "AMZN", "NVDA", "GOOGL"]
    
    # Test 1: Bare yf
    print("--- Test 1: Bare yfinance (No custom session) ---")
    for sym in symbols:
        try:
            df = yf.Ticker(sym).history(period="1y")
            print(f"{sym}: {'SUCCESS' if not df.empty else 'EMPTY'}")
        except Exception as e:
            print(f"{sym}: ERROR - {e}")
        time.sleep(1)
        
    print("\n--- Test 2: With custom session ---")
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
    })
    for sym in symbols:
        try:
            df = yf.Ticker(sym, session=session).history(period="1y")
            print(f"{sym}: {'SUCCESS' if not df.empty else 'EMPTY'}")
        except Exception as e:
            print(f"{sym}: ERROR - {e}")
        time.sleep(1)

    print("\n--- Test 3: Download method ---")
    for sym in symbols:
        try:
            df = yf.download(sym, period="1y", progress=False)
            print(f"{sym}: {'SUCCESS' if not df.empty else 'EMPTY'}")
        except Exception as e:
            print(f"{sym}: ERROR - {e}")
        time.sleep(1)

if __name__ == "__main__":
    test_fetch()
