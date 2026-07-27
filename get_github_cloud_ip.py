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

def diagnose_cloud_execution():
    print("🌐 DIAGNOSTICANDO CONEXIÓN DIRECTA DE LA NUBE A BINANCE REAL...")
    
    # 1. Get GitHub Actions runner public IP
    try:
        ip_res = requests.get("https://api.ipify.org?format=json", timeout=5).json()
        runner_ip = ip_res.get("ip")
        print(f"📡 IP Pública del Servidor de GitHub Actions Cloud: {runner_ip}")
    except Exception as e:
        print(f"Error obteniendo IP de la nube: {e}")
        runner_ip = "Unknown"

    # 2. Attempt direct API call to Binance Real
    timestamp = int(time.time() * 1000)
    params = {"timestamp": timestamp}
    query_string = urlencode(params)
    signature = hmac.new(API_SECRET.encode("utf-8"), query_string.encode("utf-8"), hashlib.sha256).hexdigest()
    params["signature"] = signature
    headers = {"X-MBX-APIKEY": API_KEY}
    
    url = f"{BASE_URL}/api/v3/account"
    try:
        res = requests.get(url, headers=headers, params=params, timeout=10)
        print(f"📊 Respuesta Binance Directa desde la Nube (Status {res.status_code}): {res.json()}")
        
        # 3. If allowed, execute the sale of 0.0105 BNB to USDT immediately!
        if res.status_code == 200:
            print("🚀 IP PERMITIDA! EJECUTANDO VENTA DE 0.0105 BNB A USDT...")
            sell_params = {
                "symbol": "BNBUSDT",
                "side": "SELL",
                "type": "MARKET",
                "quantity": "0.0105",
                "timestamp": int(time.time() * 1000)
            }
            sell_query = urlencode(sell_params)
            sell_sig = hmac.new(API_SECRET.encode("utf-8"), sell_query.encode("utf-8"), hashlib.sha256).hexdigest()
            sell_params["signature"] = sell_sig
            
            sell_res = requests.post(f"{BASE_URL}/api/v3/order", headers=headers, params=sell_params, timeout=10)
            print(f"🎉 Resultado Venta BNB a USDT: Status {sell_res.status_code} -> {sell_res.json()}")
        else:
            print(f"❌ Binance rechazó la conexión directa de la Nube IP {runner_ip}: {res.json()}")
            
    except Exception as e:
        print(f"Error en diagnóstico de la nube: {e}")

if __name__ == "__main__":
    sys.stdout.reconfigure(encoding='utf-8')
    diagnose_cloud_execution()
