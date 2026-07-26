import os
import sys
import time
import json
import hmac
import hashlib
import requests
from urllib.parse import urlencode
from datetime import datetime

API_KEY = os.getenv("BINANCE_REAL_API_KEY", "2nfL1p3pIXWmPLpBC9d0MtQzOBzlBBKu5xkKQPJ46QxbqxxqbTrC7tW0ltjJJpka")
API_SECRET = os.getenv("BINANCE_REAL_API_SECRET", "9g2cBC6SgWlgywcJDqxsLELxZnrNV5dYjD5bqxEbjbKEjbZ5qD8f0ldrXfJpbfnN")
BASE_URL = "https://api.binance.com"

REAL_STATE_FILE = os.path.join(os.path.dirname(__file__), "real_money_account.json")

def load_real_account_state():
    if os.path.exists(REAL_STATE_FILE):
        try:
            with open(REAL_STATE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {
        "initial_deposit_usdt": 15.47,
        "initial_total_usd": 20.07,
        "current_balance_usd": 20.07,
        "net_pnl_usd": 0.0,
        "wins": 0,
        "losses": 0,
        "trades_count": 0,
        "position": None,
        "last_trade_time": datetime.now().strftime("%y-%m-%d<br>%H:%M"),
        "status": "🟦 Buscando Entrada A+"
    }

def save_real_account_state(state):
    with open(REAL_STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2, ensure_ascii=False)

def get_real_balances():
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
            return res.json().get("balances", [])
        return []
    except Exception:
        return []

def execute_real_spot_market_buy(symbol, usdt_amount):
    timestamp = int(time.time() * 1000)
    params = {
        "symbol": symbol,
        "side": "BUY",
        "type": "MARKET",
        "quoteOrderQty": f"{usdt_amount:.2f}",
        "timestamp": timestamp
    }
    query_string = urlencode(params)
    signature = hmac.new(API_SECRET.encode("utf-8"), query_string.encode("utf-8"), hashlib.sha256).hexdigest()
    params["signature"] = signature
    headers = {"X-MBX-APIKEY": API_KEY}
    
    url = f"{BASE_URL}/api/v3/order"
    try:
        res = requests.post(url, headers=headers, params=params, timeout=10)
        return res.json()
    except Exception as e:
        return {"error": str(e)}

def evaluate_and_trade_real_money(best_symbol, best_score, current_price):
    state = load_real_account_state()
    balances = get_real_balances()
    
    usdt_free = sum([float(b["free"]) for b in balances if b["asset"] == "USDT"])
    bnb_free = sum([float(b["free"]) for b in balances if b["asset"] == "BNB"])
    
    # Calculate BNB USD value
    bnb_usd = bnb_free * 576.0 # Approx BNB price
    total_val = usdt_free + bnb_usd
    
    # Check if there is an active non-USDT crypto position on Binance Spot
    crypto_balances = [b for b in balances if b["asset"] not in ["USDT", "USDC", "BNB"] and float(b["free"]) > 0]
    
    now_str = datetime.now().strftime("%y-%m-%d<br>%H:%M")
    
    if crypto_balances:
        active_asset = crypto_balances[0]["asset"]
        active_qty = float(crypto_balances[0]["free"])
        state["position"] = {
            "symbol": f"{active_asset}USDT",
            "quantity": active_qty,
            "entry_price": current_price,
            "cost_usd": round(active_qty * current_price, 2)
        }
        state["status"] = f"🔵 En Vivo ({active_asset}USDT @ ${current_price})"
    else:
        state["position"] = None
        state["status"] = "🟦 Buscando Entrada A+"

    state["current_balance_usd"] = round(total_val if total_val > 0 else 20.07, 2)
    state["net_pnl_usd"] = round(state["current_balance_usd"] - 20.07, 2)
    save_real_account_state(state)
    return state

if __name__ == "__main__":
    sys.stdout.reconfigure(encoding='utf-8')
    st = load_real_account_state()
    print(f"💰 Real Account State: {st['status']} | Balance: ${st['current_balance_usd']} USD")
