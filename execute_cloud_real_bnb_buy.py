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
    print("🚀 EJECUTANDO ORDEN REAL EN LA NUBE: COMPRA DE $5.00 USD EN BNB EN BINANCE SPOT REAL...")
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
        res = requests.post(url, headers=headers, params=params, timeout=10)
        res_json = res.json()
        print(f"📊 Respuesta Binance Real (Status {res.status_code}): {res_json}")
        
        if res.status_code == 200 and "orderId" in res_json:
            print(f"🎉 ¡ORDEN REAL EN LA NUBE EJECUTADA CON ÉXITO!")
            print(f"  - ID de Orden: {res_json.get('orderId')}")
            print(f"  - Cripto Comprada: {res_json.get('symbol')}")
            print(f"  - Monto USD Ejecutado: ${res_json.get('cummulativeQuoteQty')} USD")
            print(f"  - Cantidad BNB Recibida: {res_json.get('executedQty')} BNB")
            return True
        else:
            print(f"❌ Error en Orden Real: {res_json}")
            return False
    except Exception as e:
        print(f"Exception ejecutando orden real: {e}")
        return False

if __name__ == "__main__":
    sys.stdout.reconfigure(encoding='utf-8')
    execute_real_bnb_buy_from_cloud()
