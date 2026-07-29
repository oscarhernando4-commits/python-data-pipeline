import json
import real_money_trader
import sys
import time
import hmac
import hashlib
import requests
from urllib.parse import urlencode

sys.stdout.reconfigure(encoding='utf-8')

print("=== INICIANDO OPERACIÓN KAMIKAZE SHORT EN FUTUROS (XRP) ===")

try:
    # Use XRPUSDT because its step size allows for <$10 trades without needing leverage adjustments
    best_symbol = "XRPUSDT"
    
    balances = real_money_trader.get_real_futures_balances()
    usdt_free = sum([float(b["availableBalance"]) for b in balances if b["asset"] in ["USDT", "USDC"]])
    if usdt_free == 0.0:
        usdt_free = 8.5
        
    print(f"Forzando SHORT en {best_symbol} con {usdt_free} USDT...")
    
    # 1. Fetch live price
    fapi_url = "https://fapi.binance.com"
    price_res = requests.get(f"{fapi_url}/fapi/v1/ticker/price?symbol={best_symbol}", proxies=real_money_trader.PROXIES, timeout=5).json()
    price = float(price_res.get("price", 1.0))
    
    # 2. Calculate quantity
    clean_usd = int(usdt_free * 0.98 * 100) / 100.0
    # XRP step size is 1.0 (no decimals needed for qty)
    qty = int(clean_usd / price) 
    
    timestamp = int(time.time() * 1000)
    
    # 3. Place Market SHORT order using the single order endpoint (bypassing batch restrictions)
    params = {
        "symbol": best_symbol,
        "side": "SELL",
        "type": "MARKET",
        "quantity": str(qty),
        "timestamp": timestamp
    }
    
    query_string = urlencode(params)
    signature = hmac.new(real_money_trader.API_SECRET.encode("utf-8"), query_string.encode("utf-8"), hashlib.sha256).hexdigest()
    params["signature"] = signature
    headers = {"X-MBX-APIKEY": real_money_trader.API_KEY}
    
    print(f"Enviando MARKET SELL de {qty} {best_symbol}...")
    res = requests.post(f"{fapi_url}/fapi/v1/order", headers=headers, params=params, proxies=real_money_trader.PROXIES, timeout=10)
    
    print("\n✅ RESPUESTA RAW DE BINANCE (FUTUROS SHORT):")
    print(json.dumps(res.json(), indent=4, ensure_ascii=False))

except Exception as e:
    print(f"ERROR FORZANDO OPERACIÓN: {e}")
