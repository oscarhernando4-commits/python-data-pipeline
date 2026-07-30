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

def run_cloud_bnb_buy_test():
    timestamp = int(time.time() * 1000)
    
    # Check current balances
    params = {"timestamp": timestamp}
    query_string = urlencode(params)
    signature = hmac.new(API_SECRET.encode("utf-8"), query_string.encode("utf-8"), hashlib.sha256).hexdigest()
    params["signature"] = signature
    headers = {"X-MBX-APIKEY": API_KEY}
    
    try:
        res = requests.get(f"{BASE_URL}/api/v3/account", headers=headers, params=params, timeout=10)
        print(f"📊 Cloud Balance Status Code: {res.status_code}")
        if res.status_code == 200:
            balances = res.json().get("balances", [])
            usdt_bal = sum([float(b["free"]) for b in balances if b["asset"] == "USDT"])
            bnb_bal = sum([float(b["free"]) for b in balances if b["asset"] == "BNB"])
            print(f"  - USDT Libre en la Nube: ${usdt_bal:.2f} USDT")
            print(f"  - BNB Libre en la Nube: {bnb_bal:.6f} BNB")
            
            # Execute Market Order for minimum spot $5.00 USD to buy BNB if USDT >= 15.0
            if usdt_bal >= 15.0:
                print("🚀 Ejecutando Orden Compradora de BNB en la Nube desde IP Estática de GitHub...")
                timestamp_order = int(time.time() * 1000)
                order_params = {
                    "symbol": "BNBUSDT",
                    "side": "BUY",
                    "type": "MARKET",
                    "quoteOrderQty": "5.00",
                    "timestamp": timestamp_order
                }
                query_order = urlencode(order_params)
                sig_order = hmac.new(API_SECRET.encode("utf-8"), query_order.encode("utf-8"), hashlib.sha256).hexdigest()
                order_params["signature"] = sig_order
                
                order_res = requests.post(f"{BASE_URL}/api/v3/order", headers=headers, params=order_params, timeout=10)
                print(f"🎉 Orden Nube Binance (Status {order_res.status_code}): {order_res.json()}")
        else:
            print(f"❌ Nube Error ({res.status_code}): {res.json()}")
    except Exception as e:
        print(f"Error en prueba nube BNB: {e}")

if __name__ == "__main__":
    sys.stdout.reconfigure(encoding='utf-8')
    run_cloud_bnb_buy_test()
