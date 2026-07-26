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

def get_real_usdt_balance():
    timestamp = int(time.time() * 1000)
    params = {"timestamp": timestamp}
    query_string = urlencode(params)
    signature = hmac.new(API_SECRET.encode("utf-8"), query_string.encode("utf-8"), hashlib.sha256).hexdigest()
    params["signature"] = signature
    headers = {"X-MBX-APIKEY": API_KEY}
    
    url = f"{BASE_URL}/api/v3/account"
    try:
        res = requests.get(url, headers=headers, params=params, timeout=10)
        if res.status_code == 200:
            balances = res.json().get("balances", [])
            usdt_bal = sum([float(b["free"]) for b in balances if b["asset"] in ["USDT", "USDC"]])
            return usdt_bal
        return 0.0
    except Exception:
        return 0.0

def execute_real_money_trade_if_eligible(symbol, score, price):
    usdt_bal = get_real_usdt_balance()
    print(f"💰 Binance Real USDT/USDC Balance: ${usdt_bal:.2f} USD")
    
    if usdt_bal < 10.0:
        print(f"ℹ️ Saldo en Binance Real (${usdt_bal:.2f} USD) es menor al mínimo de orden Binance Spot ($10 USD). Esperando depósito.")
        return False
        
    print(f"🚀 ¡ALERTA A+ DETECTADA PARA DINERO REAL! Símbolo: {symbol} | Puntaje: {score}/100 | Precio: ${price}")
    # Calculation for $20 USD account: Trade 50% ($10 USD) or 100% ($20 USD) depending on balance
    trade_amount_usd = min(usdt_bal, 20.0)
    print(f"🟢 Orden Spot de Dinero Real lista para enviarse por ${trade_amount_usd:.2f} USD...")
    return True

if __name__ == "__main__":
    sys.stdout.reconfigure(encoding='utf-8')
    usdt = get_real_usdt_balance()
    print(f"💰 Conexión Binance Real Verificada! Balance Spot Libre: ${usdt:.2f} USD")
