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

def diagnose_and_sell_bnb_static():
    log_lines = []
    log_lines.append("🚀 EJECUTANDO VENTA EN LA NUBE CON STATIC IP DE GACTS...")
    
    # 1. Get GitHub Actions runner public IP
    try:
        ip_res = requests.get("https://api.ipify.org?format=json", timeout=5).json()
        runner_ip = ip_res.get("ip")
        log_lines.append(f"📡 IP Pública de la Nube con Static IP: {runner_ip}")
    except Exception as e:
        runner_ip = "Unknown"
        log_lines.append(f"Error obteniendo IP: {e}")

    # 2. Attempt account status check
    timestamp = int(time.time() * 1000)
    params = {"timestamp": timestamp}
    query_string = urlencode(params)
    signature = hmac.new(API_SECRET.encode("utf-8"), query_string.encode("utf-8"), hashlib.sha256).hexdigest()
    params["signature"] = signature
    headers = {"X-MBX-APIKEY": API_KEY}
    
    url = f"{BASE_URL}/api/v3/account"
    try:
        res = requests.get(url, headers=headers, params=params, timeout=10)
        res_json = res.json()
        log_lines.append(f"📊 Binance Response Status Code: {res.status_code}")
        
        # 3. Always attempt market sell order of 0.0105 BNB to USDT
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
        sell_json = sell_res.json()
        log_lines.append(f"🎉 Resultado Venta BNB a USDT: Status {sell_res.status_code} -> {sell_json}")
        
    except Exception as e:
        log_lines.append(f"Exception ejecutando orden en la nube: {e}")

    full_log = "\n".join(log_lines)
    print(full_log)
    with open("static_ip_execution_result.txt", "w", encoding="utf-8") as f:
        f.write(full_log)

if __name__ == "__main__":
    sys.stdout.reconfigure(encoding='utf-8')
    diagnose_and_sell_bnb_static()
