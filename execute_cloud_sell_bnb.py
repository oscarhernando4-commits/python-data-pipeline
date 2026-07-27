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

def sell_bnb_from_cloud_with_auth_proxy(qty_bnb=0.0105):
    print(f"🚀 EJECUTANDO EN LA NUBE: VENTA DE {qty_bnb} BNB A USDT VIA FIXIE EU PROXY (54.195.3.54)...")
    
    proxy_url = "http://fixie:yqYN8TxTpLkrqC0@ventoux.usefixie.com:80"
    proxies = {"http": proxy_url, "https": proxy_url}
    timestamp = int(time.time() * 1000)
    
    params = {
        "symbol": "BNBUSDT",
        "side": "SELL",
        "type": "MARKET",
        "quantity": "0.011",
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
        
        output_str = f"Status {res.status_code}: {res_json}"
        with open("last_cloud_sell_result.txt", "w", encoding="utf-8") as f:
            f.write(output_str)
            
        if res.status_code == 200 and "orderId" in res_json:
            print(f"🎉 ¡VENTA REAL EN LA NUBE EJECUTADA CON ÉXITO!")
            print(f"  - ID de Orden: {res_json.get('orderId')}")
            print(f"  - Monto USDT Recibido: ${res_json.get('cummulativeQuoteQty')} USDT")
            print(f"  - Cantidad BNB Vendida: {res_json.get('executedQty')} BNB")
            return True
        else:
            print(f"❌ Error en Venta desde la Nube: {res_json}")
            return False
    except Exception as e:
        print(f"Exception ejecutando orden en la nube: {e}")
        with open("last_cloud_sell_result.txt", "w", encoding="utf-8") as f:
            f.write(f"Exception: {e}")
        return False

if __name__ == "__main__":
    sys.stdout.reconfigure(encoding='utf-8')
    sell_bnb_from_cloud_with_auth_proxy(0.0105)
