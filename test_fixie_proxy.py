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

def test_fixie_static_ip():
    print("📡 Probando conexión directa a Binance Real a través de la IP Estática de la Nube (52.2.146.126)...")
    
    # Try connecting using Fixie URL or direct Cloud IP
    proxy_url = os.getenv("FIXIE_URL", "")
    proxies = {"http": proxy_url, "https": proxy_url} if proxy_url else None
    
    timestamp = int(time.time() * 1000)
    params = {"timestamp": timestamp}
    query_string = urlencode(params)
    signature = hmac.new(API_SECRET.encode("utf-8"), query_string.encode("utf-8"), hashlib.sha256).hexdigest()
    params["signature"] = signature
    headers = {"X-MBX-APIKEY": API_KEY}
    
    url = f"{BASE_URL}/api/v3/account"
    try:
        res = requests.get(url, headers=headers, params=params, proxies=proxies, timeout=10)
        print(f"📊 Respuesta Binance Real Status Code: {res.status_code}")
        print(f"  - Body: {res.json()}")
        return res.status_code == 200
    except Exception as e:
        print(f"Error en prueba: {e}")
        return False

if __name__ == "__main__":
    sys.stdout.reconfigure(encoding='utf-8')
    test_fixie_static_ip()
