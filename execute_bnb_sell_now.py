import os
import sys
import time
import hmac
import hashlib
import requests
from urllib.parse import urlencode

API_KEY = os.getenv("BINANCE_REAL_API_KEY", "2nfL1p3pIXWmPLpBC9d0MtQzOBzlBBKu5xkKQPJ46QxbqxxqbTrC7tW0ltjJJpka")
API_SECRET = os.getenv("BINANCE_REAL_API_SECRET", "9g2cBC6SgWlgywcJDqxsLELxZnrNV5dYjD5bqxEbjbKEjbZ5qD8f0ldrXfJpbfnN")
BASE_URL = "https://api.binance.com"

def execute_bnb_sell_now():
    print("🚀 EJECUTANDO ORDEN REAL VENDEDORA DE 0.0105 BNB A USDT...")
    
    # Try direct first, then proxy fallback
    timestamp = int(time.time() * 1000)
    params = {
        "symbol": "BNBUSDT",
        "side": "SELL",
        "type": "MARKET",
        "quantity": "0.0105",
        "timestamp": timestamp
    }
    query_string = urlencode(params)
    signature = hmac.new(API_SECRET.encode("utf-8"), query_string.encode("utf-8"), hashlib.sha256).hexdigest()
    params["signature"] = signature
    headers = {"X-MBX-APIKEY": API_KEY}
    
    url = f"{BASE_URL}/api/v3/order"
    
    # 1. Direct attempt
    try:
        res = requests.post(url, headers=headers, params=params, timeout=5)
        print(f"📊 Intento Directo Status: {res.status_code} -> {res.json()}")
        if res.status_code == 200:
            print(f"🎉 ¡VENTA DE BNB A USDT EJECUTADA CON ÉXITO!")
            return True
    except Exception as e:
        print(f"Direct error: {e}")

    # 2. Proxy attempt with auth
    proxy_url = "http://mjkcggfj:f1tlwlv0tmgy@64.137.96.74:6641"
    proxies = {"http": proxy_url, "https": proxy_url}
    try:
        res_proxy = requests.post(url, headers=headers, params=params, proxies=proxies, timeout=10)
        print(f"📊 Intento Proxy España Status: {res_proxy.status_code} -> {res_proxy.json()}")
        if res_proxy.status_code == 200:
            print(f"🎉 ¡VENTA VIA PROXY ESPAÑA EJECUTADA CON ÉXITO!")
            return True
    except Exception as e:
        print(f"Proxy error: {e}")

    return False

if __name__ == "__main__":
    sys.stdout.reconfigure(encoding='utf-8')
    execute_bnb_sell_now()
