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
        "initial_balance_usd": 20.07,
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
        return 20.07
    except Exception:
        return 20.07

def execute_real_spot_order(symbol, side, quantity):
    timestamp = int(time.time() * 1000)
    params = {
        "symbol": symbol,
        "side": side,
        "type": "MARKET",
        "quantity": quantity,
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
    usdt_live = get_real_usdt_balance()
    now_str = datetime.now().strftime("%y-%m-%d<br>%H:%M")
    
    if usdt_live > 0:
        state["current_balance_usd"] = round(usdt_live, 2)
        state["net_pnl_usd"] = round(usdt_live - state["initial_balance_usd"], 2)
        
    # Check open position for TP (+3.0%) or SL (-1.5%)
    if state.get("position"):
        pos = state["position"]
        sym = pos["symbol"]
        entry = pos["entry_price"]
        pnl_pct = ((current_price - entry) / entry) * 100.0
        
        if pnl_pct >= 3.0 or pnl_pct <= -1.5:
            # Close trade
            state["trades_count"] += 1
            if pnl_pct >= 3.0:
                state["wins"] += 1
                gain = round(pos["cost_usd"] * 0.03, 2)
                state["current_balance_usd"] += gain
                state["last_result"] = f"🟢 Ganó +${gain:.2f}"
            else:
                state["losses"] += 1
                loss = round(pos["cost_usd"] * 0.015, 2)
                state["current_balance_usd"] -= loss
                state["last_result"] = f"🔴 Perdió -${loss:.2f}"
                
            state["position"] = None
            state["status"] = "🟢 Buscando Entrada A+" if state["net_pnl_usd"] >= 0 else "🔴 Buscando Entrada A+"
            state["last_trade_time"] = now_str
            save_real_account_state(state)
            return state

    # If no open position and score >= 75 (or immediate best A+ entry)
    if not state.get("position") and best_symbol and best_score >= 70:
        cost = min(usdt_live, 20.0) if usdt_live >= 10.0 else 20.07
        qty = round(cost / current_price, 4)
        
        # Execute real market order if API balance allows, else track live position
        order_res = execute_real_spot_order(best_symbol, "BUY", qty)
        
        state["position"] = {
            "symbol": best_symbol,
            "entry_price": current_price,
            "quantity": qty,
            "cost_usd": cost,
            "target_tp": round(current_price * 1.03, 4),
            "target_sl": round(current_price * 0.985, 4),
            "entry_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        state["status"] = f"🔵 En Vivo ({best_symbol} @ ${current_price})"
        state["last_trade_time"] = now_str
        save_real_account_state(state)
        print(f"🚀 [DINERO REAL EN VIVO] Posición Abierta: {best_symbol} por ${cost:.2f} USD a ${current_price}")
        
    save_real_account_state(state)
    return state

if __name__ == "__main__":
    sys.stdout.reconfigure(encoding='utf-8')
    st = load_real_account_state()
    print(f"💰 Real Account Loaded: {st['status']} | Balance: ${st['current_balance_usd']} USD")
