
# Static Proxy Configuration for 24/7 Cloud Execution
PROXY_URL = os.getenv("FIXIE_URL", os.getenv("QUOTAGUARDSTATIC_URL", ""))
PROXIES = {"http": PROXY_URL, "https": PROXY_URL} if PROXY_URL else None
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

def get_real_account_balances():
    timestamp = int(time.time() * 1000)
    params = {"timestamp": timestamp}
    query_string = urlencode(params)
    signature = hmac.new(API_SECRET.encode("utf-8"), query_string.encode("utf-8"), hashlib.sha256).hexdigest()
    params["signature"] = signature
    
    headers = {
        "X-MBX-APIKEY": API_KEY
    }
    
    url = f"{BASE_URL}/api/v3/account"
    try:
        response = requests.get(url, headers=headers, params=params, proxies=PROXIES, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            balances = data.get("balances", [])
            non_zero = [b for b in balances if float(b["free"]) > 0 or float(b["locked"]) > 0]
            print("✅ CONEXIÓN BINANCE REAL EXITOSA!")
            print("📊 Estado de Cuenta Spot Real:")
            if not non_zero:
                print("  - Saldo libre actual: 0.00 USD / Todos los activos en 0. (Listo para tu depósito de $100 USD)")
            for b in non_zero:
                print(f"  - {b['asset']}: Disponible={b['free']} | En Orden={b['locked']}")
            return non_zero
        else:
            print(f"❌ Respuesta Binance Real ({response.status_code}): {response.text}")
            return None
    except Exception as e:
        print(f"Error de conexión: {e}")
        return None

if __name__ == "__main__":
    sys.stdout.reconfigure(encoding='utf-8')
    get_real_account_balances()
