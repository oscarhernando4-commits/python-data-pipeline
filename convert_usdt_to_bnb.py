import os
import sys
import time
import hmac
import hashlib
import requests
from urllib.parse import urlencode

API_KEY = os.getenv("BINANCE_REAL_API_KEY", "")
API_SECRET = os.getenv("BINANCE_REAL_API_SECRET", "")

BASE_URL = "https://api.binance.com"

def convert_usdt_to_bnb(amount_usdt=0.20):
    timestamp = int(time.time() * 1000)
    
    # 1. Try Binance Convert API
    url = f"{BASE_URL}/sapi/v1/convert/getQuote"
    params = {
        "fromAsset": "USDT",
        "toAsset": "BNB",
        "fromAmount": amount_usdt,
        "validTime": "10s",
        "timestamp": timestamp
    }
    query_string = urlencode(params)
    signature = hmac.new(API_SECRET.encode("utf-8"), query_string.encode("utf-8"), hashlib.sha256).hexdigest()
    params["signature"] = signature
    headers = {"X-MBX-APIKEY": API_KEY}
    
    try:
        res = requests.post(url, headers=headers, params=params, timeout=10)
        res_data = res.json()
        print(f"Convert Quote Response: {res_data}")
        
        if "quoteId" in res_data:
            quote_id = res_data["quoteId"]
            # Accept quote
            timestamp_accept = int(time.time() * 1000)
            params_accept = {
                "quoteId": quote_id,
                "timestamp": timestamp_accept
            }
            query_accept = urlencode(params_accept)
            sig_accept = hmac.new(API_SECRET.encode("utf-8"), query_accept.encode("utf-8"), hashlib.sha256).hexdigest()
            params_accept["signature"] = sig_accept
            
            url_accept = f"{BASE_URL}/sapi/v1/convert/acceptQuote"
            res_acc = requests.post(url_accept, headers=headers, params=params_accept, timeout=10)
            acc_data = res_acc.json()
            print(f"🎉 Convert Accept Response: {acc_data}")
            return True
        else:
            print(f"ℹ️ Convert API notice: {res_data}")
    except Exception as e:
        print(f"Error during convert: {e}")

    # Fallback: check current BNB balance
    bal_res = requests.get(f"{BASE_URL}/api/v3/account", headers=headers, params={"timestamp": int(time.time() * 1000), "signature": hmac.new(API_SECRET.encode("utf-8"), f"timestamp={int(time.time() * 1000)}".encode("utf-8"), hashlib.sha256).hexdigest()}, timeout=10)
    if bal_res.status_code == 200:
        balances = bal_res.json().get("balances", [])
        bnb_bal = sum([float(b["free"]) for b in balances if b["asset"] == "BNB"])
        usdt_bal = sum([float(b["free"]) for b in balances if b["asset"] == "USDT"])
        print(f"📊 Balances Actuales Spot Real:")
        print(f"  - BNB Libre: {bnb_bal:.6f} BNB (~${bnb_bal * 576.0:.2f} USD)")
        print(f"  - USDT Libre: ${usdt_bal:.2f} USDT")
    return False

if __name__ == "__main__":
    sys.stdout.reconfigure(encoding='utf-8')
    convert_usdt_to_bnb(0.20)
