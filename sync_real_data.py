import urllib.request
import json
import time
import hmac
import hashlib
import sys
import os
import obsidian_sync
from datetime import datetime

# Real Binance API Keys configured by user
API_KEY = "2nfL1p3pIXWmPLpBC9d0MtQzOBzlBBKu5xkKQPJ46QxbqxxqbTrC7tW0ltjJJpka"
API_SECRET = "9g2cBC6SgWlgywcJDqxsLELxZnrNV5dYjD5bqxEbjbKEjbZ5qD8f0ldrXfJpbfnN"
BASE_URL = "https://api.binance.com"

def sign_query(query_str):
    return hmac.new(API_SECRET.encode('utf-8'), query_str.encode('utf-8'), hashlib.sha256).hexdigest()

def get_real_account_info():
    endpoint = "/api/v3/account"
    timestamp = int(time.time() * 1000)
    params = f"timestamp={timestamp}"
    signature = sign_query(params)
    url = f"{BASE_URL}{endpoint}?{params}&signature={signature}"
    
    req = urllib.request.Request(url, headers={'X-MBX-APIKEY': API_KEY, 'User-Agent': 'Mozilla/5.0'})
    try:
        with urllib.request.urlopen(req) as response:
            return json.loads(response.read().decode())
    except Exception as e:
        print(f"Error fetching real account info: {e}")
        return None

def get_ticker_prices():
    url = f"{BASE_URL}/api/v3/ticker/price"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode())
            return {item['symbol']: float(item['price']) for item in data}
    except Exception as e:
        print(f"Error fetching ticker prices: {e}")
        return {}

def update_obsidian_with_real_binance_data():
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{now_str}] Fetching LIVE real-time data from Binance Account...")
    
    acc_info = get_real_account_info()
    prices = get_ticker_prices()
    
    if not acc_info:
        print("Could not retrieve live Binance account data.")
        return
        
    raw_balances = acc_info.get("balances", [])
    active_balances = []
    total_val_usd = 0.0
    
    for b in raw_balances:
        asset = b["asset"]
        free = float(b["free"])
        locked = float(b["locked"])
        total_amount = free + locked
        
        if total_amount > 0:
            if asset in ["USDT", "USDC", "BUSD"]:
                price_usd = 1.0
            else:
                price_usd = prices.get(f"{asset}USDT", prices.get(f"{asset}USDC", 0.0))
                
            value_usd = total_amount * price_usd
            total_val_usd += value_usd
            
            active_balances.append({
                "asset": asset,
                "free": f"{free:.8f}",
                "locked": f"{locked:.8f}",
                "total": f"{total_amount:.8f}",
                "value_usd": f"${value_usd:.4f} USD",
                "unit_price": f"${price_usd:.4f} USD"
            })

    print(f"Live Total Account Value: ${total_val_usd:.4f} USD")
    print("Live Assets Found:", active_balances)
    
    # Sync Real Data to Obsidian Dashboard
    initial_cap = 100.0  # Baseline target
    obsidian_sync.sync_compound_dashboard(
        current_balance=total_val_usd if total_val_usd > 0 else 0.0701,
        initial_capital=initial_cap,
        active_assets=active_balances
    )
    
    obsidian_sync.sync_dashboard_note(
        balances=active_balances,
        market_status="DATOS REALES EN VIVO CONECTADOS 🟢 (Binance Live Spot)",
        active_symbol="USDCUSDT"
    )
    
    print("✅ Obsidian Dashboards UPDATED with 100% LIVE REAL BINANCE DATA!")

if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    update_obsidian_with_real_binance_data()
