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

def sell_bnb_direct(qty_bnb=0.011):
    print(f"🚀 EJECUTANDO ORDEN VENDEDORA EN LA NUBE DE {qty_bnb} BNB A USDT EN BINANCE SPOT REAL VIA PROXY ESPAÑA...")
    
    proxy_url = "http://64.137.96.74:6641"
    proxies = {"http": proxy_url, "https": proxy_url}
    timestamp = int(time.time() * 1000)
    params = {
        "symbol": "BNBUSDT",
        "side": "SELL",
        "type": "MARKET",
        "quantity": f"{qty_bnb:.3f}",
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
        print(f"📊 Respuesta Binance Real (Status {res.status_code}): {res_json}")
        
        if res.status_code == 200 and "orderId" in res_json:
            print(f"🎉 ¡VENTA EN VIVO DE BNB A USDT EJECUTADA CON ÉXITO!")
            print(f"  - ID de Orden: {res_json.get('orderId')}")
            print(f"  - Monto USDT Recibido: ${res_json.get('cummulativeQuoteQty')} USDT")
            print(f"  - Cantidad BNB Vendida: {res_json.get('executedQty')} BNB")
            return True
        else:
            print(f"❌ Error en Venta: {res_json}")
            return False
    except Exception as e:
        print(f"Error procesando orden de venta BNB: {e}")
        return False

if __name__ == "__main__":
    sys.stdout.reconfigure(encoding='utf-8')
    sell_bnb_direct(0.011)
