import os
import time
import hmac
import hashlib
import requests
from urllib.parse import urlencode
import json

API_KEY = os.getenv("BINANCE_REAL_API_KEY", "")
API_SECRET = os.getenv("BINANCE_REAL_API_SECRET", "")
BASE_URL = "https://api.binance.com"

def get_signature(query_string):
    return hmac.new(API_SECRET.encode("utf-8"), query_string.encode("utf-8"), hashlib.sha256).hexdigest()

def check_funding_wallet():
    timestamp = int(time.time() * 1000)
    params = {"timestamp": timestamp}
    query_string = urlencode(params)
    signature = get_signature(query_string)
    params["signature"] = signature
    headers = {"X-MBX-APIKEY": API_KEY}
    
    url = f"{BASE_URL}/sapi/v1/asset/get-funding-asset"
    try:
        res = requests.post(url, headers=headers, params=params)
        return res.json()
    except Exception as e:
        return {"error": str(e)}

def check_earn_wallet():
    timestamp = int(time.time() * 1000)
    params = {"timestamp": timestamp}
    query_string = urlencode(params)
    signature = get_signature(query_string)
    params["signature"] = signature
    headers = {"X-MBX-APIKEY": API_KEY}
    
    url = f"{BASE_URL}/sapi/v1/simple-earn/flexible/position"
    try:
        res = requests.get(url, headers=headers, params=params)
        return res.json()
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    print("=== BINANCE WALLET INVESTIGATION ===")
    
    funding = check_funding_wallet()
    print("\n--- FUNDING WALLET ---")
    print(json.dumps(funding, indent=2))
    
    earn = check_earn_wallet()
    print("\n--- EARN WALLET ---")
    print(json.dumps(earn, indent=2))
