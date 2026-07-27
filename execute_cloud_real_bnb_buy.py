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

def execute_real_bnb_buy_from_cloud():
    output_lines = []
    output_lines.append("🚀 EJECUTANDO ORDEN REAL: COMPRA DE $5.00 USD EN BNB EN BINANCE SPOT REAL VIA PROXY ESPAÑA...")
    
    proxy_url = "http://64.137.96.74:6641"
    proxies = {"http": proxy_url, "https": proxy_url}
    timestamp = int(time.time() * 1000)
    
    params = {
        "symbol": "BNBUSDT",
        "side": "BUY",
        "type": "MARKET",
        "quoteOrderQty": "5.00",
        "timestamp": timestamp
    }
    query_string = urlencode(params)
    signature = hmac.new(API_SECRET.encode("utf-8"), query_string.encode("utf-8"), hashlib.sha256).hexdigest()
    params["signature"] = signature
    headers = {"X-MBX-APIKEY": API_KEY}
    
    url = f"{BASE_URL}/api/v3/order"
    try:
        res = requests.post(url, headers=headers, params=params, proxies=proxies, timeout=10)
        res_json = res.json()
        output_lines.append(f"📊 Respuesta Binance Real (Status {res.status_code}): {res_json}")
        
        if res.status_code == 200 and "orderId" in res_json:
            output_lines.append(f"🎉 ¡ORDEN REAL EN LA NUBE EJECUTADA CON ÉXITO!")
            output_lines.append(f"  - ID de Orden: {res_json.get('orderId')}")
            output_lines.append(f"  - Monto USD Ejecutado: ${res_json.get('cummulativeQuoteQty')} USD")
        else:
            output_lines.append(f"❌ Error en Orden Real: {res_json}")
    except Exception as e:
        output_lines.append(f"Exception ejecutando orden real: {e}")
        
    full_output = "\n".join(output_lines)
    print(full_output)
    
    with open("last_bnb_buy_log.txt", "w", encoding="utf-8") as f:
        f.write(full_output)

if __name__ == "__main__":
    sys.stdout.reconfigure(encoding='utf-8')
    execute_real_bnb_buy_from_cloud()
