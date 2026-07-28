import requests
import time
import hmac
import hashlib
from urllib.parse import urlencode
import real_money_trader

def force_sync():
    print("Iniciando sincronización forzada de balance real con Fixie...")
    
    timestamp = int(time.time() * 1000)
    params = {"timestamp": timestamp}
    query_string = urlencode(params)
    signature = hmac.new(real_money_trader.API_SECRET.encode("utf-8"), query_string.encode("utf-8"), hashlib.sha256).hexdigest()
    params["signature"] = signature
    headers = {"X-MBX-APIKEY": real_money_trader.API_KEY}
    
    spot_url = f"{real_money_trader.BASE_URL}/api/v3/account"
    futures_url = "https://fapi.binance.com/fapi/v2/account"
    
    total_balance = 0.0
    
    try:
        # Fetch Spot using Proxy
        res_spot = requests.get(spot_url, headers=headers, params=params, proxies=real_money_trader.PROXIES, timeout=10)
        if res_spot.status_code == 200:
            balances = res_spot.json().get("balances", [])
            spot_usdt = sum([float(b["free"]) for b in balances if b["asset"] in ["USDT", "USDC"]])
            total_balance += spot_usdt
    except Exception as e:
        print(f"Error fetching spot: {e}")
        
    try:
        # Fetch Futures using Proxy
        res_fut = requests.get(futures_url, headers=headers, params=params, proxies=real_money_trader.PROXIES, timeout=10)
        if res_fut.status_code == 200:
            assets = res_fut.json().get("assets", [])
            fut_usdt = sum([float(a["availableBalance"]) for a in assets if a["asset"] in ["USDT", "USDC"]])
            total_balance += fut_usdt
    except Exception as e:
        print(f"Error fetching futures: {e}")
        
    if total_balance > 0:
        st = real_money_trader.load_real_account_state()
        st['current_balance_usd'] = round(total_balance, 2)
        st['net_pnl_usd'] = round(total_balance - 20.07, 2)
        real_money_trader.save_real_account_state(st)
        print(f"✅ Sincronización exitosa. Nuevo Balance: ${total_balance:,.2f} USD")
    else:
        print("❌ Falló la sincronización. Balance devuelto fue 0.")

if __name__ == "__main__":
    force_sync()
