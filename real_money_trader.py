
import os
import sys
import time
import json
import hmac
import hashlib
import requests
from urllib.parse import urlencode
from datetime import datetime

# Static Proxy Configuration for 24/7 Cloud Execution (Fixie EU West IPs: 54.195.3.54 & 54.217.142.99)
PROXY_URL = os.getenv("FIXIE_URL", "http://fixie:yqYN8TxTpLkrqC0@ventoux.usefixie.com:80")
PROXIES = {"http": PROXY_URL, "https": PROXY_URL} if PROXY_URL else None

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
        res = requests.get(url, headers=headers, params=params, proxies=PROXIES, timeout=10)
        if res.status_code == 200:
            return res.json().get("balances", [])
        return []
    except Exception:
        return []

def get_real_usdt_balance():
    balances = get_real_balances()
    return sum([float(b["free"]) for b in balances if b["asset"] in ["USDT", "USDC"]])

def execute_real_spot_market_buy(symbol, usdt_amount):
    timestamp = int(time.time() * 1000)
    # Round down to nearest clean integer (e.g. 15.00 USD) for 100% precision safety
    clean_usd = int(usdt_amount) if usdt_amount >= 10.0 else usdt_amount
    params = {
        "symbol": symbol,
        "side": "BUY",
        "type": "MARKET",
        "quoteOrderQty": f"{clean_usd:.2f}",
        "timestamp": timestamp
    }
    query_string = urlencode(params)
    signature = hmac.new(API_SECRET.encode("utf-8"), query_string.encode("utf-8"), hashlib.sha256).hexdigest()
    params["signature"] = signature
    headers = {"X-MBX-APIKEY": API_KEY}
    
    url = f"{BASE_URL}/api/v3/order"
    try:
        res = requests.post(url, headers=headers, params=params, proxies=PROXIES, timeout=10)
        return res.json()
    except Exception as e:
        return {"error": str(e)}

def execute_real_futures_market_short(symbol, usdt_amount):
    timestamp = int(time.time() * 1000)
    clean_usd = int(usdt_amount) if usdt_amount >= 10.0 else usdt_amount
    
    # Futures endpoint uses fapi.binance.com
    fapi_url = "https://fapi.binance.com"
    params = {
        "symbol": symbol,
        "side": "SELL",
        "type": "MARKET",
        "quantity": "0.001",  # Precision quantity calculated per symbol
        "timestamp": timestamp
    }
    # For USDT-M futures market orders with USD value, use quoteOrderQty if supported or calculate qty
    # Fetch live price via futures
    try:
        price_res = requests.get(f"{fapi_url}/fapi/v1/ticker/price?symbol={symbol}", proxies=PROXIES, timeout=5).json()
        price = float(price_res.get("price", 1.0))
        qty = round(clean_usd / price, 3)
        params["quantity"] = f"{qty:.3f}"
    except Exception:
        pass
        
    query_string = urlencode(params)
    signature = hmac.new(API_SECRET.encode("utf-8"), query_string.encode("utf-8"), hashlib.sha256).hexdigest()
    params["signature"] = signature
    headers = {"X-MBX-APIKEY": API_KEY}
    
    try:
        res = requests.post(f"{fapi_url}/fapi/v1/order", headers=headers, params=params, proxies=PROXIES, timeout=10)
        return res.json()
    except Exception as e:
        return {"error": str(e)}

def evaluate_and_trade_real_money(best_symbol, best_score, current_price, is_bearish=False):
    state = load_real_account_state()
    balances = get_real_balances()
    
    usdt_free = sum([float(b["free"]) for b in balances if b["asset"] == "USDT"])
    bnb_free = sum([float(b["free"]) for b in balances if b["asset"] == "BNB"])
    
    # Calculate BNB USD value
    bnb_usd = bnb_free * 575.0  # Approx BNB price
    total_val = usdt_free + bnb_usd
    
    # Check for active non-USDT crypto position on Binance Spot Real
    crypto_balances = [b for b in balances if b["asset"] not in ["USDT", "USDC", "BNB"] and float(b["free"]) > 0]
    
    now_str = datetime.now().strftime("%y-%m-%d<br>%H:%M")
    
    if crypto_balances:
        active_asset = crypto_balances[0]["asset"]
        active_qty = float(crypto_balances[0]["free"])
        active_symbol = f"{active_asset}USDT"
        est_val = active_qty * current_price if current_price > 0 else 17.0
        
        state["position"] = {
            "symbol": active_symbol,
            "quantity": active_qty,
            "entry_price": state.get("position", {}).get("entry_price", current_price),
            "cost_usd": round(est_val, 2),
            "side": "LONG"
        }
        state["status"] = f"🔵 En Vivo LONG ({active_asset}USDT @ ${current_price:.4f})"
        
        # Check for exit condition (Take Profit +3.0% or Stop Loss -1.5%)
        entry = state["position"].get("entry_price", current_price)
        if entry > 0:
            pnl_pct = ((current_price - entry) / entry) * 100.0
            if pnl_pct >= 3.0 or pnl_pct <= -1.5:
                print(f"🎯 ALERTA REAL: Salida LONG por PnL {pnl_pct:.2f}% en {active_symbol}. Vendiendo...")
                sell_params = {
                    "symbol": active_symbol,
                    "side": "SELL",
                    "type": "MARKET",
                    "quantity": f"{active_qty:.3f}",
                    "timestamp": int(time.time() * 1000)
                }
                query_string = urlencode(sell_params)
                signature = hmac.new(API_SECRET.encode("utf-8"), query_string.encode("utf-8"), hashlib.sha256).hexdigest()
                sell_params["signature"] = signature
                headers = {"X-MBX-APIKEY": API_KEY}
                try:
                    res = requests.post(f"{BASE_URL}/api/v3/order", headers=headers, params=sell_params, proxies=PROXIES, timeout=10)
                    if res.status_code == 200:
                        state["trades_count"] += 1
                        if pnl_pct >= 3.0:
                            state["wins"] += 1
                        else:
                            state["losses"] += 1
                        state["position"] = None
                        state["status"] = "🟦 Buscando Entrada A+"
                except Exception as e:
                    print(f"Error ejecutando venta real: {e}")
    else:
        state["position"] = None
        state["status"] = "🟦 Buscando Entrada A+"
        
        # 1. LONG Entry Signal (Score >= 85 Pts)
        if best_symbol and not is_bearish and best_score >= 85 and usdt_free >= 15.0:
            print(f"🚀 SEÑAL A+ ALCISTA (LONG) DETECTADA ({best_symbol} @ {best_score} Pts). Comprando en Binance Spot...")
            buy_res = execute_real_spot_market_buy(best_symbol, usdt_free)
            if "orderId" in buy_res:
                state["position"] = {
                    "symbol": best_symbol,
                    "entry_price": current_price,
                    "cost_usd": round(usdt_free, 2),
                    "side": "LONG"
                }
                state["status"] = f"🔵 En Vivo LONG ({best_symbol})"
                
        # 2. SHORT Entry Signal (Bearish Score <= 15 Pts / High Bearish Confluence)
        elif best_symbol and is_bearish and best_score <= 15 and usdt_free >= 15.0:
            print(f"📉 SEÑAL A+ BAJISTA (SHORT) DETECTADA ({best_symbol} @ Score {best_score}). Abriendo Short en Binance Futuros...")
            short_res = execute_real_futures_market_short(best_symbol, usdt_free)
            if "orderId" in short_res:
                state["position"] = {
                    "symbol": best_symbol,
                    "entry_price": current_price,
                    "cost_usd": round(usdt_free, 2),
                    "side": "SHORT"
                }
                state["status"] = f"🔻 En Vivo SHORT ({best_symbol})"

    state["current_balance_usd"] = round(total_val if total_val > 0 else 20.08, 2)
    state["net_pnl_usd"] = round(state["current_balance_usd"] - 20.07, 2)
    save_real_account_state(state)
    return state

if __name__ == "__main__":
    sys.stdout.reconfigure(encoding='utf-8')
    st = load_real_account_state()
    print(f"💰 Real Account State: {st['status']} | Balance: ${st['current_balance_usd']} USD")
