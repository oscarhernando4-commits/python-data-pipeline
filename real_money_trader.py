
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
PROXY_URL = os.getenv("FIXIE_URL", "")
if not PROXY_URL:
    PROXY_URL = "http://fixie:yqYN8TxTpLkrqC0@ventoux.usefixie.com:80"
PROXIES = {"http": PROXY_URL, "https": PROXY_URL}

API_KEY = os.getenv("BINANCE_REAL_API_KEY", "")
API_SECRET = os.getenv("BINANCE_REAL_API_SECRET", "")
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
        # NO proxy here - balance checks must NOT consume Fixie quota
        # Fixie is EXCLUSIVELY reserved for BUY/SELL order execution
        res = requests.get(url, headers=headers, params=params, timeout=10)
        if res.status_code == 200:
            return res.json().get("balances", [])
        return []
    except Exception:
        return []

def get_real_usdt_balance():
    balances = get_real_balances()
    return sum([float(b["free"]) for b in balances if b["asset"] in ["USDT", "USDC"]])

def get_real_futures_balances():
    timestamp = int(time.time() * 1000)
    params = {"timestamp": timestamp}
    query_string = urlencode(params)
    signature = hmac.new(API_SECRET.encode("utf-8"), query_string.encode("utf-8"), hashlib.sha256).hexdigest()
    params["signature"] = signature
    headers = {"X-MBX-APIKEY": API_KEY}
    
    url = "https://fapi.binance.com/fapi/v2/account"
    try:
        # NO proxy here - balance checks must NOT consume Fixie quota
        res = requests.get(url, headers=headers, params=params, timeout=10)
        if res.status_code == 200:
            return res.json().get("assets", [])
        return []
    except Exception:
        return []

def get_real_futures_positions():
    timestamp = int(time.time() * 1000)
    params = {"timestamp": timestamp}
    query_string = urlencode(params)
    signature = hmac.new(API_SECRET.encode("utf-8"), query_string.encode("utf-8"), hashlib.sha256).hexdigest()
    params["signature"] = signature
    headers = {"X-MBX-APIKEY": API_KEY}
    
    url = "https://fapi.binance.com/fapi/v2/positionRisk"
    try:
        # NO proxy here - checks must NOT consume Fixie quota
        res = requests.get(url, headers=headers, params=params, timeout=10)
        if res.status_code == 200:
            positions = res.json()
            # Return only active positions
            return [p for p in positions if float(p.get("positionAmt", 0)) != 0.0]
        return []
    except Exception:
        return []

def get_real_futures_usdt_balance():
    assets = get_real_futures_balances()
    return sum([float(a["availableBalance"]) for a in assets if a["asset"] in ["USDT", "USDC"]])

def execute_real_spot_market_buy(symbol, usdt_amount):
    timestamp = int(time.time() * 1000)
    # Use full balance minus a tiny 1% safety buffer to avoid "Insufficient Balance" errors
    # Strict floor truncation to ensure we never exceed exactly available decimals
    clean_usd = int(usdt_amount * 0.99 * 100) / 100.0
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
    # Use full balance minus a 2% safety buffer for Futures margin and fees
    # Strict floor truncation to ensure we never exceed exactly available decimals
    clean_usd = int(usdt_amount * 0.98 * 100) / 100.0
    fapi_url = "https://fapi.binance.com"
    headers = {"X-MBX-APIKEY": API_KEY}

    # 1. Force Isolated Margin (Ignore if already Isolated)
    try:
        m_params = {"symbol": symbol, "marginType": "ISOLATED", "timestamp": timestamp}
        m_query = urlencode(m_params)
        m_sig = hmac.new(API_SECRET.encode("utf-8"), m_query.encode("utf-8"), hashlib.sha256).hexdigest()
        requests.post(f"{fapi_url}/fapi/v1/marginType", headers=headers, params={**m_params, "signature": m_sig}, proxies=PROXIES, timeout=5)
    except Exception:
        pass

    # 2. Fetch live price to calculate Qty and SL/TP Prices
    try:
        price_res = requests.get(f"{fapi_url}/fapi/v1/ticker/price?symbol={symbol}", proxies=PROXIES, timeout=5).json()
        price = float(price_res.get("price", 1.0))
        qty = round(clean_usd / price, 3)
        qty_str = f"{qty:.3f}"
        
        # Risk Management: SL +1.0% (loss), TP -2.0% (win) for SHORT
        sl_price = round(price * 1.01, 4)
        tp_price = round(price * 0.98, 4)
    except Exception as e:
        return {"error": f"Failed to calculate price/qty: {e}"}

    # 3. Execute Batch Order (Entry + SL + TP in 1 API call = 1 Fixie Request!)
    # We use STOP_MARKET and TAKE_PROFIT_MARKET based on Mark Price (Binance default)
    timestamp = int(time.time() * 1000)
    orders = [
        {"symbol": symbol, "side": "SELL", "type": "MARKET", "quantity": qty_str},
        {"symbol": symbol, "side": "BUY", "type": "STOP_MARKET", "quantity": qty_str, "stopPrice": str(sl_price), "reduceOnly": "true"},
        {"symbol": symbol, "side": "BUY", "type": "TAKE_PROFIT_MARKET", "quantity": qty_str, "stopPrice": str(tp_price), "reduceOnly": "true"}
    ]
    
    b_params = {
        "batchOrders": json.dumps(orders),
        "timestamp": timestamp
    }
    b_query = urlencode(b_params)
    b_sig = hmac.new(API_SECRET.encode("utf-8"), b_query.encode("utf-8"), hashlib.sha256).hexdigest()
    b_params["signature"] = b_sig
    
    try:
        res = requests.post(f"{fapi_url}/fapi/v1/batchOrders", headers=headers, params=b_params, proxies=PROXIES, timeout=10)
        return res.json()
    except Exception as e:
        return {"error": str(e)}

def execute_real_futures_market_close(symbol, quantity):
    timestamp = int(time.time() * 1000)
    
    fapi_url = "https://fapi.binance.com"
    params = {
        "symbol": symbol,
        "side": "BUY", # We are closing a SHORT, so we BUY
        "type": "MARKET",
        "quantity": str(quantity),
        "reduceOnly": "true",
        "timestamp": timestamp
    }
        
    query_string = urlencode(params)
    signature = hmac.new(API_SECRET.encode("utf-8"), query_string.encode("utf-8"), hashlib.sha256).hexdigest()
    params["signature"] = signature
    headers = {"X-MBX-APIKEY": API_KEY}
    
    try:
        res = requests.post(f"{fapi_url}/fapi/v1/order", headers=headers, params=params, proxies=PROXIES, timeout=10)
        return res.json()
    except Exception as e:
        return {"error": str(e)}

def evaluate_and_trade_real_money(best_symbol, best_score, current_price, is_bearish=False, is_learned_signal=False):
    state = load_real_account_state()
    # FIXIE OPTIMIZATION: We rely entirely on the local JSON state for balances 
    # to avoid burning Fixie Proxy requests every 5 minutes.
    usdt_free = state.get("current_balance_usd", 17.15) / 2.0
    futures_usdt_free = state.get("current_balance_usd", 17.15) / 2.0
    
    crypto_balances = []
    futures_positions = []
    
    # Hydrate crypto_balances and futures_positions flags artificially from local state
    if state.get("position"):
        pos = state["position"]
        qty = pos.get("quantity", pos.get("cost_usd", 10.0) / (pos.get("entry_price") or 1.0))
        if pos.get("side") == "LONG":
            crypto_balances = [{"asset": pos["symbol"].replace("USDT", ""), "free": qty}]
        elif pos.get("side") == "SHORT":
            futures_positions = [{"symbol": pos["symbol"], "positionAmt": -qty, "entryPrice": pos["entry_price"]}]
    
    now_str = datetime.now().strftime("%y-%m-%d<br>%H:%M")
    
    if crypto_balances:
        active_asset = crypto_balances[0]["asset"]
        active_qty = float(crypto_balances[0]["free"])
        active_symbol = f"{active_asset}USDT"
        
        try:
            active_price_res = requests.get(f"https://api.binance.com/api/v3/ticker/price?symbol={active_symbol}", timeout=5).json()
            active_current_price = float(active_price_res["price"])
        except:
            active_current_price = current_price
            
        est_val = active_qty * active_current_price if active_current_price > 0 else 17.0
        
        state["position"] = {
            "symbol": active_symbol,
            "quantity": active_qty,
            "entry_price": state.get("position", {}).get("entry_price", active_current_price),
            "cost_usd": round(est_val, 2),
            "side": "LONG"
        }
        state["status"] = f"🔵 En Vivo LONG ({active_asset}USDT @ ${active_current_price:.4f})"
        
        # Check for exit condition (Take Profit +2.0% or Stop Loss -1.0%)
        entry = state["position"].get("entry_price", active_current_price)
        if entry > 0:
            pnl_pct = ((active_current_price - entry) / entry) * 100.0
            
            # --- ESCUDO REAL: BREAK-EVEN DINÁMICO ---
            if pnl_pct >= 1.0 and not state["position"].get("break_even", False):
                state["position"]["break_even"] = True
                print(f"🛡️ ESCUDO REAL ACTIVADO: El precio subió +{pnl_pct:.2f}%. Stop-loss asegurado en Break-Even (+0.2%).")
                
            dynamic_sl = 0.2 if state["position"].get("break_even", False) else -1.0
            
            if pnl_pct >= 2.0 or pnl_pct <= dynamic_sl:
                reason_str = f"Ganancia Asegurada (+{pnl_pct:.2f}%)" if pnl_pct >= 2.0 or state["position"].get("break_even", False) else f"Stop Loss ({pnl_pct:.2f}%)"
                print(f"🎯 ALERTA REAL: Salida LONG por {reason_str} en {active_symbol}. Vendiendo...")
                # Format qty to 5 decimals for BTC, or 2 for cheap coins to respect Binance LOT_SIZE
                qty_str = f"{active_qty:.5f}" if active_current_price > 1000 else f"{active_qty:.2f}"
                sell_params = {
                    "symbol": active_symbol,
                    "side": "SELL",
                    "type": "MARKET",
                    "quantity": qty_str,
                    "timestamp": int(time.time() * 1000)
                }
                query_string = urlencode(sell_params)
                signature = hmac.new(API_SECRET.encode("utf-8"), query_string.encode("utf-8"), hashlib.sha256).hexdigest()
                sell_params["signature"] = signature
                headers = {"X-MBX-APIKEY": API_KEY}
                try:
                    res = requests.post(f"{BASE_URL}/api/v3/order", headers=headers, params=sell_params, proxies=PROXIES, timeout=10)
                    if res.status_code == 200:
                        import learning_engine
                        state["trades_count"] += 1
                        pnl_usd = (current_price - entry) * active_qty
                        
                        # Update daily counters
                        today_str = datetime.now().strftime("%Y-%m-%d")
                        if state.get("last_trading_day") != today_str:
                            state["daily_wins"] = 0
                            state["daily_losses"] = 0
                            state["last_trading_day"] = today_str
                            
                        if pnl_pct >= 3.0:
                            state["wins"] += 1
                            state["daily_wins"] = state.get("daily_wins", 0) + 1
                            res_type = "WIN"
                        else:
                            state["losses"] += 1
                            state["daily_losses"] = state.get("daily_losses", 0) + 1
                            res_type = "LOSS"
                            
                        state["current_balance_usd"] = state.get("current_balance_usd", 20.07) + pnl_usd
                            
                        learning_engine.record_trade_outcome(
                            symbol=active_symbol, side="BUY", entry_price=entry, exit_price=current_price,
                            pnl_usd=pnl_usd, result_type=res_type, notes=f"Real Money Trade closed with {pnl_pct:.2f}%",
                            account_id="R-01", group_name="CUENTA REAL"
                        )
                        state["position"] = None
                        state["status"] = "🟦 Buscando Entrada A+"
                except Exception as e:
                    print(f"Error ejecutando venta real: {e}")
                    
    elif futures_positions:
        # We have an active SHORT position
        active_pos = futures_positions[0]
        active_symbol = active_pos["symbol"]
        
        try:
            active_price_res = requests.get(f"https://fapi.binance.com/fapi/v1/ticker/price?symbol={active_symbol}", timeout=5).json()
            active_current_price = float(active_price_res["price"])
        except:
            active_current_price = current_price
            
        # Position amount is negative for SHORTs
        active_qty = abs(float(active_pos["positionAmt"]))
        entry = float(active_pos["entryPrice"])
        est_val = active_qty * active_current_price if active_current_price > 0 else 17.0
        
        state["position"] = {
            "symbol": active_symbol,
            "quantity": active_qty,
            "entry_price": entry,
            "cost_usd": round(est_val, 2),
            "side": "SHORT"
        }
        
        # PnL logic for SHORT: If current price drops, pnl is positive
        if entry > 0:
            pnl_pct = ((entry - active_current_price) / entry) * 100.0
            state["status"] = f"🔻 En Vivo SHORT ({active_symbol} @ ${active_current_price:.4f} | PnL: {pnl_pct:+.2f}%)"
            
    else:
        # If we had a SHORT but now it's gone, Binance closed it natively!
        if state.get("position") and state["position"].get("side") == "SHORT":
            import learning_engine
            closed_pos = state["position"]
            entry = closed_pos.get("entry_price", 1.0)
            active_qty = closed_pos.get("quantity", closed_pos.get("cost_usd", 10.0) / (entry or 1.0))
            active_symbol = closed_pos.get("symbol", "UNKNOWN")
            
            # Update daily counters
            today_str = datetime.now().strftime("%Y-%m-%d")
            if state.get("last_trading_day") != today_str:
                state["daily_wins"] = 0
                state["daily_losses"] = 0
                state["last_trading_day"] = today_str
                
            # Infer result based on current price relative to entry
            if current_price < entry:
                state["wins"] += 1
                state["daily_wins"] = state.get("daily_wins", 0) + 1
                res_type = "WIN"
                pnl_usd = entry * 0.02 * active_qty # Approx +2% win
            else:
                state["losses"] += 1
                state["daily_losses"] = state.get("daily_losses", 0) + 1
                res_type = "LOSS"
                pnl_usd = -(entry * 0.01 * active_qty) # Approx -1.0% loss
                
            state["current_balance_usd"] = state.get("current_balance_usd", 20.07) + pnl_usd
            state["trades_count"] += 1
            learning_engine.record_trade_outcome(
                symbol=active_symbol, side="SHORT", entry_price=entry, exit_price=current_price,
                pnl_usd=pnl_usd, result_type=res_type, notes=f"Real Money SHORT auto-closed by Binance",
            )
            print(f"🎯 ALERTA REAL: Posición SHORT en {active_symbol} fue cerrada automáticamente por Binance ({res_type})")
            
        state["position"] = None
        state["status"] = "🟦 Buscando Entrada A+"
        
        import strategy_engine
        dyn_t = strategy_engine.load_thresholds()
        real_long_score = dyn_t.get("group_0", {}).get("long_score", 80)
        real_short_score = dyn_t.get("group_0", {}).get("short_score", 20)
        
        # 1. LONG Entry Signal (Score >= Dynamic Pts OR AI Learned Signal)
        if best_symbol and not is_bearish and (best_score >= real_long_score or is_learned_signal) and usdt_free >= 8.0:
            trigger_reason = "AUTO-APRENDIZAJE" if is_learned_signal else f"Score {real_long_score}+"
            print(f"🚀 SEÑAL ALCISTA (LONG) ({best_symbol} @ {best_score} Pts - {trigger_reason}). Comprando en Binance Spot...")
            buy_res = execute_real_spot_market_buy(best_symbol, usdt_free)
            if "orderId" in buy_res:
                state["position"] = {
                    "symbol": best_symbol,
                    "entry_price": current_price,
                    "cost_usd": round(usdt_free, 2),
                    "side": "LONG"
                }
                state["status"] = f"🔵 En Vivo LONG ({best_symbol})"
                
        # 2. SHORT Entry Signal (Bearish Score <= Dynamic Pts OR AI Learned Signal)
        elif best_symbol and is_bearish and (best_score <= real_short_score or is_learned_signal) and futures_usdt_free >= 8.0:
            trigger_reason = "AUTO-APRENDIZAJE" if is_learned_signal else f"Score <= {real_short_score}"
            print(f"📉 SEÑAL BAJISTA (SHORT) ({best_symbol} @ Score {best_score} - {trigger_reason}). Abriendo Short en Binance Futuros...")
            short_res = execute_real_futures_market_short(best_symbol, futures_usdt_free)
            if "orderId" in short_res:
                state["position"] = {
                    "symbol": best_symbol,
                    "entry_price": current_price,
                    "cost_usd": round(futures_usdt_free, 2),
                    "side": "SHORT"
                }
                state["status"] = f"🔻 En Vivo SHORT ({best_symbol})"
            else:
                print(f"⚠️ SHORT no ejecutado: {short_res}")

    state["current_balance_usd"] = round(state.get("current_balance_usd", 20.07), 2)
    state["net_pnl_usd"] = round(state["current_balance_usd"] - 20.07, 2)
    save_real_account_state(state)
    return state

if __name__ == "__main__":
    sys.stdout.reconfigure(encoding='utf-8')
    st = load_real_account_state()
    print(f"💰 Real Account State: {st['status']} | Balance: ${st['current_balance_usd']} USD")
