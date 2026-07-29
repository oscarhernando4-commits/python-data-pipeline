import os
import requests
import time
import hmac
import hashlib
from urllib.parse import urlencode
import json

API_KEY = os.getenv("BINANCE_REAL_API_KEY", "")
API_SECRET = os.getenv("BINANCE_REAL_API_SECRET", "")
PROXY_URL = os.getenv("FIXIE_URL", "http://fixie:yqYN8TxTpLkrqC0@ventoux.usefixie.com:80")
PROXIES = {"http": PROXY_URL, "https": PROXY_URL} if PROXY_URL else None
BASE_URL = "https://api.binance.com"
FAPI_URL = "https://fapi.binance.com"

report_lines = []

def log_report(msg):
    print(msg)
    report_lines.append(msg)

def sign(params):
    query_string = urlencode(params)
    signature = hmac.new(API_SECRET.encode("utf-8"), query_string.encode("utf-8"), hashlib.sha256).hexdigest()
    params["signature"] = signature
    return params

def test_spot_limit():
    log_report("1. Probando ejecución LONG real en Binance Spot...")
    headers = {"X-MBX-APIKEY": API_KEY}
    
    # Place Limit Order for BTCUSDT at $20,000 (Will never fill, 100% safe)
    params = {
        "symbol": "BTCUSDT",
        "side": "BUY",
        "type": "LIMIT",
        "timeInForce": "GTC",
        "quantity": "0.0003", # ~ $18 total
        "price": "20000.00",
        "timestamp": int(time.time() * 1000)
    }
    params = sign(params)
    res = requests.post(f"{BASE_URL}/api/v3/order", headers=headers, params=params, proxies=PROXIES)
    data = res.json()
    
    if "orderId" in data:
        order_id = data["orderId"]
        log_report(f"✅ ORDEN LONG CREADA EXITOSAMENTE EN LA NUBE. OrderID: {order_id}")
        
        # Cancel it
        c_params = sign({"symbol": "BTCUSDT", "orderId": order_id, "timestamp": int(time.time() * 1000)})
        c_res = requests.delete(f"{BASE_URL}/api/v3/order", headers=headers, params=c_params, proxies=PROXIES)
        if "orderId" in c_res.json():
            log_report(f"✅ ORDEN LONG CANCELADA EXITOSAMENTE. El dinero real está intacto.")
        else:
            log_report(f"❌ Error al cancelar LONG: {c_res.text}")
    else:
        log_report(f"❌ Error al crear LONG en Spot: {res.text}")

def test_futures_limit():
    log_report("\n2. Probando ejecución SHORT real en Binance Futuros...")
    headers = {"X-MBX-APIKEY": API_KEY}
    
    # Place Limit Order for BTCUSDT SHORT at $120,000 (Will never fill)
    params = {
        "symbol": "BTCUSDT",
        "side": "SELL", # Sell short
        "type": "LIMIT",
        "timeInForce": "GTC",
        "quantity": "0.002",
        "price": "120000.00",
        "timestamp": int(time.time() * 1000)
    }
    params = sign(params)
    res = requests.post(f"{FAPI_URL}/fapi/v1/order", headers=headers, params=params, proxies=PROXIES)
    data = res.json()
    
    if "orderId" in data:
        order_id = data["orderId"]
        log_report(f"✅ ORDEN SHORT CREADA EXITOSAMENTE EN LA NUBE. OrderID: {order_id}")
        
        # Cancel it
        c_params = sign({"symbol": "BTCUSDT", "orderId": order_id, "timestamp": int(time.time() * 1000)})
        c_res = requests.delete(f"{FAPI_URL}/fapi/v1/order", headers=headers, params=c_params, proxies=PROXIES)
        if "orderId" in c_res.json():
            log_report(f"✅ ORDEN SHORT CANCELADA EXITOSAMENTE. El dinero real está intacto.")
        else:
            log_report(f"❌ Error al cancelar SHORT: {c_res.text}")
    else:
        log_report(f"❌ Error al crear SHORT en Futuros: {res.text}")

test_spot_limit()
test_futures_limit()

# Save report
with open("TEST_EJECUCION_REAL.md", "w", encoding="utf-8") as f:
    f.write("\n".join(report_lines))
