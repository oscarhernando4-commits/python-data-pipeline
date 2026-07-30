import time
import requests
import hmac
import hashlib
from urllib.parse import urlencode
import os
import random

API_KEY = os.getenv("BINANCE_REAL_API_KEY", "")
API_SECRET = os.getenv("BINANCE_REAL_API_SECRET", "")

# Use shared proxy rotator (6 fresh accounts)
from real_money_trader import FIXIE_POOL
PROXY_URL = random.choice(FIXIE_POOL[:6])
PROXIES = {
    "http": PROXY_URL,
    "https": PROXY_URL
}
BASE_URL = "https://api.binance.com"

def verify():
    print("====================================================")
    print("🚀 INICIANDO VERIFICACIÓN AUTÓNOMA DESDE LA NUBE 🚀")
    print("====================================================")
    
    if not API_KEY or not API_SECRET:
        print("❌ ERROR: Credenciales de Binance no encontradas en el entorno de la Nube.")
        return
        
    print("1️⃣ Probando Ping a Binance a través del Proxy Fixie...")
    try:
        requests.get(f"{BASE_URL}/api/v3/ping", proxies=PROXIES, timeout=10)
        print("✅ Ping exitoso. El servidor de la Nube puede comunicarse con Binance.")
    except Exception as e:
        print("❌ Error de Ping:", str(e))
        return

    timestamp = int(time.time() * 1000)
    print("\n2️⃣ Leyendo Balance de Dinero Real...")
    q_str = urlencode({"timestamp": timestamp})
    sig = hmac.new(API_SECRET.encode("utf-8"), q_str.encode("utf-8"), hashlib.sha256).hexdigest()
    res = requests.get(f"{BASE_URL}/api/v3/account", headers={"X-MBX-APIKEY": API_KEY}, params={"timestamp": timestamp, "signature": sig}, proxies=PROXIES)
    
    if res.status_code != 200:
        print("❌ Error de API:", res.text)
        return
        
    usdt = next((b for b in res.json().get("balances", []) if b["asset"] == "USDT"), None)
    if not usdt:
        print("❌ No se encontró USDT en la cuenta.")
        return
    print(f"✅ Balance Real Verificado: ${usdt['free']} USDT disponibles.")
    
    print("\n3️⃣ Simulando Operación de Compra Real (LIMIT BUY $10.00 a precio súper bajo)...")
    # Placing a buy limit order for BTC at $10,000 USD for a total of $10 USD.
    timestamp = int(time.time() * 1000)
    params = {
        "symbol": "BTCUSDT",
        "side": "BUY",
        "type": "LIMIT",
        "timeInForce": "GTC",
        "quantity": "0.001",
        "price": "10000.00",
        "timestamp": timestamp
    }
    query_string = urlencode(params)
    signature = hmac.new(API_SECRET.encode("utf-8"), query_string.encode("utf-8"), hashlib.sha256).hexdigest()
    params["signature"] = signature
    
    order_res = requests.post(f"{BASE_URL}/api/v3/order", headers={"X-MBX-APIKEY": API_KEY}, params=params, proxies=PROXIES)
    
    if order_res.status_code == 200:
        order_data = order_res.json()
        order_id = order_data["orderId"]
        print(f"✅ ¡ÉXITO ROTUNDO! La Nube ha ejecutado una orden real de forma autónoma. Order ID: {order_id}")
        
        print("\n4️⃣ Cancelando la orden para proteger los fondos...")
        timestamp = int(time.time() * 1000)
        c_params = {"symbol": "BTCUSDT", "orderId": order_id, "timestamp": timestamp}
        c_sig = hmac.new(API_SECRET.encode("utf-8"), urlencode(c_params).encode("utf-8"), hashlib.sha256).hexdigest()
        c_params["signature"] = c_sig
        
        can_res = requests.delete(f"{BASE_URL}/api/v3/order", headers={"X-MBX-APIKEY": API_KEY}, params=c_params, proxies=PROXIES)
        if can_res.status_code == 200:
            print("✅ ORDEN CANCELADA CORRECTAMENTE.")
            print("\n====================================================")
            print("🏆 VERIFICACIÓN FINALIZADA. EL SISTEMA ES 100% CAPAZ DE OPERAR EN LA NUBE. 🏆")
            print("====================================================")
        else:
            print("❌ Error al cancelar:", can_res.text)
    else:
        print("❌ Falla al crear la orden real en la Nube:", order_res.text)

if __name__ == "__main__":
    verify()
