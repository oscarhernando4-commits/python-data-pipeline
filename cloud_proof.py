import time
import requests
import hmac
import hashlib
from urllib.parse import urlencode
import os

API_KEY = os.getenv("BINANCE_API_KEY", "")
API_SECRET = os.getenv("BINANCE_API_SECRET", "")

# The Fixie proxy we configured
proxy_url = os.getenv("FIXIE_URL", "http://fixie:XqF868E4rA6L6Gj@velodrome.usefixie.com:80")
PROXIES = {
    "http": proxy_url,
    "https": proxy_url
}

BASE_URL = "https://api.binance.com"

def run_cloud_autonomous_proof():
    print("🔒 [PRUEBA AUTÓNOMA EN LA NUBE] Iniciando conexión con Binance...")
    timestamp = int(time.time() * 1000)
    
    # 1. Check Balance
    q_str = urlencode({"timestamp": timestamp})
    sig = hmac.new(API_SECRET.encode("utf-8"), q_str.encode("utf-8"), hashlib.sha256).hexdigest()
    res = requests.get(f"{BASE_URL}/api/v3/account", headers={"X-MBX-APIKEY": API_KEY}, params={"timestamp": timestamp, "signature": sig}, proxies=PROXIES)
    
    if res.status_code != 200:
        print("❌ Error de conexión:", res.text)
        return
        
    balances = res.json().get("balances", [])
    usdt = next((b for b in balances if b["asset"] == "USDT"), None)
    print(f"✅ CONEXIÓN EXITOSA. USDT Real Disponible: ${usdt['free']}")
    
    # 2. Place a LIMIT order far from market price (100% Safe, will not execute)
    print("🚀 Emitiendo orden de compra LIMITADA de prueba (Autónoma)...")
    timestamp = int(time.time() * 1000)
    params = {
        "symbol": "BTCUSDT",
        "side": "BUY",
        "type": "LIMIT",
        "timeInForce": "GTC",
        "quantity": "0.001", # ~ $60 USD, but we will place it at a very low price
        "price": "10000.00", # Price of BTC at $10,000 (Current is ~$60k+, impossible to fill instantly)
        "timestamp": timestamp
    }
    query_string = urlencode(params)
    signature = hmac.new(API_SECRET.encode("utf-8"), query_string.encode("utf-8"), hashlib.sha256).hexdigest()
    params["signature"] = signature
    
    order_res = requests.post(f"{BASE_URL}/api/v3/order", headers={"X-MBX-APIKEY": API_KEY}, params=params, proxies=PROXIES)
    
    if order_res.status_code == 200:
        order_data = order_res.json()
        order_id = order_data["orderId"]
        print(f"✅ ¡ORDEN REAL CREADA CON ÉXITO EN LA NUBE! Order ID: {order_id}")
        
        # 3. Instantly Cancel it
        print("🗑️ Cancelando la orden para proteger los fondos...")
        timestamp = int(time.time() * 1000)
        c_params = {"symbol": "BTCUSDT", "orderId": order_id, "timestamp": timestamp}
        c_sig = hmac.new(API_SECRET.encode("utf-8"), urlencode(c_params).encode("utf-8"), hashlib.sha256).hexdigest()
        c_params["signature"] = c_sig
        
        can_res = requests.delete(f"{BASE_URL}/api/v3/order", headers={"X-MBX-APIKEY": API_KEY}, params=c_params, proxies=PROXIES)
        if can_res.status_code == 200:
            print("✅ ORDEN CANCELADA CON ÉXITO. Prueba de Autonomía de la Nube 100% Completada.")
        else:
            print("❌ Error al cancelar:", can_res.text)
    else:
        # If insufficient balance or something else
        print("⚠️ No se pudo crear la orden LIMITADA:", order_res.text)

if __name__ == "__main__":
    run_cloud_autonomous_proof()
