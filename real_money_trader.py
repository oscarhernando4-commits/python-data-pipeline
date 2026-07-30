
import os
import sys
import time
import json
import hmac
import hashlib
import requests
import tempfile
from urllib.parse import urlencode
from datetime import datetime
import random

# Dynamic Proxy Rotator for 24/7 Cloud Execution (7 Fixie EU West accounts, 3500 requests/month)
# Ordered: Fresh accounts first, nearly-depleted account LAST
FIXIE_POOL = [
    "http://fixie:ak4QPysr5gnUAQW@ventoux.usefixie.com:80",   # utn.sig (0/500)
    "http://fixie:ygTezfOLKeqEhhF@ventoux.usefixie.com:80",   # forestalutn (0/500)
    "http://fixie:zW3cwceDZ64c1lE@ventoux.usefixie.com:80",   # oscarhernandot11es (0/500)
    "http://fixie:SIOQ4x5oF0pbFju@ventoux.usefixie.com:80",   # oscarhernando4ec (0/500)
    "http://fixie:V9uciGagtBF2MJc@ventoux.usefixie.com:80",   # sconcienciautn (0/500)
    "http://fixie:gnvJakG6jyBrS04@ventoux.usefixie.com:80",   # utn2024a (0/500)
    "http://fixie:yqYN8TxTpLkrqC0@ventoux.usefixie.com:80",   # oscarhernando4 (405/500 - RESERVA)
]
# Select randomly from the 6 FRESH accounts only (exclude the depleted #7 as reserve)
PROXY_URL = random.choice(FIXIE_POOL[:6])
PROXIES = {"http": PROXY_URL, "https": PROXY_URL}

API_KEY = os.getenv("BINANCE_REAL_API_KEY", "")
API_SECRET = os.getenv("BINANCE_REAL_API_SECRET", "")
BASE_URL = "https://api.binance.com"
FAPI_URL = "https://fapi.binance.com"

REAL_STATE_FILE = os.path.join(os.path.dirname(__file__), "real_money_account.json")

# ============================================================
# STATE MANAGEMENT (Atomic writes to prevent corruption)
# ============================================================

def load_real_account_state():
    if os.path.exists(REAL_STATE_FILE):
        try:
            with open(REAL_STATE_FILE, "r", encoding="utf-8") as f:
                state = json.load(f)
                # Ensure all required keys exist with safe defaults
                state.setdefault("initial_deposit_usdt", 15.47)
                state.setdefault("initial_total_usd", 20.07)
                state.setdefault("current_balance_usd", 20.07)
                state.setdefault("net_pnl_usd", 0.0)
                state.setdefault("wins", 0)
                state.setdefault("losses", 0)
                state.setdefault("trades_count", 0)
                state.setdefault("daily_wins", 0)
                state.setdefault("daily_losses", 0)
                state.setdefault("position", None)
                state.setdefault("last_trade_time", datetime.now().strftime("%y-%m-%d<br>%H:%M"))
                state.setdefault("status", "🟦 Buscando Entrada A+")
                return state
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
        "daily_wins": 0,
        "daily_losses": 0,
        "position": None,
        "last_trade_time": datetime.now().strftime("%y-%m-%d<br>%H:%M"),
        "status": "🟦 Buscando Entrada A+"
    }

def save_real_account_state(state):
    """Atomic write: write to temp file first, then rename to prevent corruption."""
    dir_path = os.path.dirname(REAL_STATE_FILE)
    try:
        fd, tmp_path = tempfile.mkstemp(suffix=".json", dir=dir_path)
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(state, f, indent=2, ensure_ascii=False)
        # Atomic rename (on same filesystem)
        if os.path.exists(REAL_STATE_FILE):
            os.replace(tmp_path, REAL_STATE_FILE)
        else:
            os.rename(tmp_path, REAL_STATE_FILE)
    except Exception:
        # Fallback to direct write if atomic fails
        with open(REAL_STATE_FILE, "w", encoding="utf-8") as f:
            json.dump(state, f, indent=2, ensure_ascii=False)

# ============================================================
# BALANCE & POSITION QUERIES (NO Fixie proxy - free API calls)
# ============================================================

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
    
    url = f"{FAPI_URL}/fapi/v2/account"
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
    
    url = f"{FAPI_URL}/fapi/v2/positionRisk"
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

def get_symbol_price(symbol, is_futures=False):
    """Fetch live price for a specific symbol. NO proxy needed (public endpoint)."""
    try:
        base = FAPI_URL if is_futures else BASE_URL
        endpoint = "/fapi/v1/ticker/price" if is_futures else "/api/v3/ticker/price"
        res = requests.get(f"{base}{endpoint}?symbol={symbol}", timeout=5).json()
        price = float(res.get("price", 0))
        return price if price > 0 else None
    except Exception:
        return None

# ============================================================
# ORDER EXECUTION (Uses Fixie proxy - counted towards quota)
# ============================================================

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
    """
    Opens a SHORT position on Binance Futures.
    STEP 1: Execute MARKET SELL to open the SHORT.
    STEP 2: Place SL/TP orders AFTER the position exists (fixes reduceOnly rejection).
    """
    timestamp = int(time.time() * 1000)
    clean_usd = int(usdt_amount * 0.98 * 100) / 100.0
    headers = {"X-MBX-APIKEY": API_KEY}

    # 1. Force Isolated Margin (Ignore if already Isolated)
    try:
        m_params = {"symbol": symbol, "marginType": "ISOLATED", "timestamp": timestamp}
        m_query = urlencode(m_params)
        m_sig = hmac.new(API_SECRET.encode("utf-8"), m_query.encode("utf-8"), hashlib.sha256).hexdigest()
        requests.post(f"{FAPI_URL}/fapi/v1/marginType", headers=headers, params={**m_params, "signature": m_sig}, proxies=PROXIES, timeout=5)
    except Exception:
        pass

    # 2. Fetch live price to calculate Qty and SL/TP Prices
    try:
        price_res = requests.get(f"{FAPI_URL}/fapi/v1/ticker/price?symbol={symbol}", timeout=5).json()
        price = float(price_res.get("price", 1.0))
        qty = round(clean_usd / price, 3)
        qty_str = f"{qty:.3f}"
        
        # Risk Management: SL +1.0% (loss), TP -2.0% (win) for SHORT
        sl_price = round(price * 1.01, 4)
        tp_price = round(price * 0.98, 4)
    except Exception as e:
        return {"error": f"Failed to calculate price/qty: {e}"}

    # 3. STEP 1: Execute MARKET SELL entry order FIRST
    timestamp = int(time.time() * 1000)
    entry_params = {
        "symbol": symbol,
        "side": "SELL",
        "type": "MARKET",
        "quantity": qty_str,
        "timestamp": timestamp
    }
    entry_query = urlencode(entry_params)
    entry_sig = hmac.new(API_SECRET.encode("utf-8"), entry_query.encode("utf-8"), hashlib.sha256).hexdigest()
    entry_params["signature"] = entry_sig
    
    try:
        entry_res = requests.post(f"{FAPI_URL}/fapi/v1/order", headers=headers, params=entry_params, proxies=PROXIES, timeout=10)
        entry_data = entry_res.json()
        if "orderId" not in entry_data:
            return {"error": f"Entry order failed: {entry_data}"}
    except Exception as e:
        return {"error": f"Entry order exception: {e}"}
    
    # 4. STEP 2: Place SL and TP orders AFTER position exists (fixes reduceOnly -2022 rejection)
    time.sleep(0.5)  # Brief pause to ensure position is registered
    
    for sl_tp_type, stop_px, order_type in [("SL", sl_price, "STOP_MARKET"), ("TP", tp_price, "TAKE_PROFIT_MARKET")]:
        try:
            ts = int(time.time() * 1000)
            p = {
                "symbol": symbol,
                "side": "BUY",
                "type": order_type,
                "quantity": qty_str,
                "stopPrice": str(stop_px),
                "reduceOnly": "true",
                "timestamp": ts
            }
            q = urlencode(p)
            s = hmac.new(API_SECRET.encode("utf-8"), q.encode("utf-8"), hashlib.sha256).hexdigest()
            p["signature"] = s
            sl_tp_res = requests.post(f"{FAPI_URL}/fapi/v1/order", headers=headers, params=p, proxies=PROXIES, timeout=10)
            print(f"  ✅ {sl_tp_type} order placed: {sl_tp_res.json().get('orderId', sl_tp_res.text)}")
        except Exception as e:
            print(f"  ⚠️ {sl_tp_type} order failed: {e}")
    
    # Return the entry order result with orderId for state tracking
    return entry_data

def execute_real_futures_market_close(symbol, quantity):
    """Close an active SHORT position by placing a BUY MARKET order."""
    timestamp = int(time.time() * 1000)
    
    params = {
        "symbol": symbol,
        "side": "BUY",  # We are closing a SHORT, so we BUY
        "type": "MARKET",
        "quantity": str(round(quantity, 3)),
        "reduceOnly": "true",
        "timestamp": timestamp
    }
        
    query_string = urlencode(params)
    signature = hmac.new(API_SECRET.encode("utf-8"), query_string.encode("utf-8"), hashlib.sha256).hexdigest()
    params["signature"] = signature
    headers = {"X-MBX-APIKEY": API_KEY}
    
    try:
        res = requests.post(f"{FAPI_URL}/fapi/v1/order", headers=headers, params=params, proxies=PROXIES, timeout=10)
        return res.json()
    except Exception as e:
        return {"error": str(e)}

# ============================================================
# MAIN EVALUATION & TRADING LOGIC
# ============================================================

def evaluate_and_trade_real_money(best_symbol, best_score, current_price, is_bearish=False, is_learned_signal=False):
    state = load_real_account_state()
    
    # Null guard on current_price
    if not current_price or current_price <= 0:
        current_price = 1.0
    
    # FIXIE OPTIMIZATION: We rely on local JSON state for balances 
    # to avoid burning Fixie Proxy requests every 5 minutes.
    # Split 50/50 between Spot (LONG) and Futures (SHORT) as user confirmed
    usdt_free = state.get("current_balance_usd", 17.15) / 2.0
    futures_usdt_free = state.get("current_balance_usd", 17.15) / 2.0
    
    crypto_balances = []
    futures_positions = []
    
    # Hydrate crypto_balances and futures_positions from local state
    if state.get("position"):
        pos = state["position"]
        qty = pos.get("quantity", pos.get("cost_usd", 10.0) / max(pos.get("entry_price", 1.0), 0.0001))
        if pos.get("side") == "LONG":
            crypto_balances = [{"asset": pos["symbol"].replace("USDT", ""), "free": qty}]
        elif pos.get("side") == "SHORT":
            futures_positions = [{"symbol": pos["symbol"], "positionAmt": -qty, "entryPrice": pos.get("entry_price", 1.0)}]
    
    # --- LEARNING ENGINE INTEGRATION (Bug #8 fix) ---
    market_bias = None
    try:
        import learning_engine
        market_bias = learning_engine.get_market_bias()
    except Exception:
        pass
    
    now_str = datetime.now().strftime("%y-%m-%d<br>%H:%M")
    
    # ========================================
    # CASE 1: We have an active LONG position
    # ========================================
    if crypto_balances:
        active_asset = crypto_balances[0]["asset"]
        active_qty = float(crypto_balances[0]["free"])
        active_symbol = f"{active_asset}USDT"
        
        # FIX Bug #4: Fetch ACTUAL price of the held asset, not the new prospect
        active_current_price = get_symbol_price(active_symbol, is_futures=False)
        if not active_current_price:
            active_current_price = current_price  # Fallback
            
        est_val = active_qty * active_current_price
        
        state["position"] = {
            "symbol": active_symbol,
            "quantity": active_qty,
            "entry_price": state.get("position", {}).get("entry_price", active_current_price),
            "cost_usd": round(est_val, 2),
            "side": "LONG",
            "break_even": state.get("position", {}).get("break_even", False)
        }
        state["status"] = f"🔵 En Vivo LONG ({active_asset}USDT @ ${active_current_price:.4f})"
        
        # Check for exit condition (Take Profit +2.0% or Stop Loss -1.0%)
        entry = state["position"].get("entry_price", active_current_price)
        if entry and entry > 0:
            pnl_pct = ((active_current_price - entry) / entry) * 100.0
            
            # --- ESCUDO REAL: BREAK-EVEN DINÁMICO ---
            if pnl_pct >= 1.0 and not state["position"].get("break_even", False):
                state["position"]["break_even"] = True
                print(f"🛡️ ESCUDO REAL ACTIVADO: El precio subió +{pnl_pct:.2f}%. Stop-loss asegurado en Break-Even (+0.2%).")
                
            dynamic_sl = 0.2 if state["position"].get("break_even", False) else -1.0
            
            if pnl_pct >= 2.0 or pnl_pct <= dynamic_sl:
                reason_str = f"Ganancia Asegurada (+{pnl_pct:.2f}%)" if pnl_pct >= 2.0 or state["position"].get("break_even", False) else f"Stop Loss ({pnl_pct:.2f}%)"
                print(f"🎯 ALERTA REAL: Salida LONG por {reason_str} en {active_symbol}. Vendiendo...")
                
                # FIX Bug #7: Dynamic LOT_SIZE precision
                if active_current_price > 10000:    # BTC
                    qty_str = f"{active_qty:.5f}"
                elif active_current_price > 100:    # ETH, BNB, SOL
                    qty_str = f"{active_qty:.3f}"
                elif active_current_price > 1:      # LINK, DOT, etc
                    qty_str = f"{active_qty:.1f}"
                else:                               # DOGE, PEPE, SHIB
                    qty_str = f"{int(active_qty)}"
                
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
                        # FIX Bug #4: Use active_current_price, not current_price
                        pnl_usd = (active_current_price - entry) * active_qty
                        
                        # Update daily counters
                        today_str = datetime.now().strftime("%Y-%m-%d")
                        if state.get("last_trading_day") != today_str:
                            state["daily_wins"] = 0
                            state["daily_losses"] = 0
                            state["last_trading_day"] = today_str
                        
                        # FIX Bug #3: Win threshold matches TP threshold (>= 2.0, not >= 3.0)
                        if pnl_pct >= 2.0:
                            state["wins"] = state.get("wins", 0) + 1
                            state["daily_wins"] = state.get("daily_wins", 0) + 1
                            res_type = "WIN"
                        else:
                            state["losses"] = state.get("losses", 0) + 1
                            state["daily_losses"] = state.get("daily_losses", 0) + 1
                            res_type = "LOSS"
                            
                        state["current_balance_usd"] = state.get("current_balance_usd", 20.07) + pnl_usd
                        state["trades_count"] = state.get("trades_count", 0) + 1
                            
                        try:
                            import learning_engine
                            learning_engine.record_trade_outcome(
                                symbol=active_symbol, side="BUY", entry_price=entry, exit_price=active_current_price,
                                pnl_usd=pnl_usd, result_type=res_type, notes=f"Real Money Trade closed with {pnl_pct:.2f}%",
                                account_id="R-01", group_name="CUENTA REAL"
                            )
                        except Exception as le:
                            print(f"Learning engine error: {le}")
                        
                        state["position"] = None
                        state["status"] = "🟦 Buscando Entrada A+"
                        print(f"✅ LONG cerrado exitosamente: {res_type} ({pnl_pct:+.2f}% | ${pnl_usd:+.2f})")
                    else:
                        print(f"⚠️ Spot SELL rejected (HTTP {res.status_code}): {res.text}")
                except Exception as e:
                    print(f"Error ejecutando venta real: {e}")
                    
    # ========================================
    # CASE 2: We have an active SHORT position
    # ========================================
    elif futures_positions:
        active_pos = futures_positions[0]
        active_symbol = active_pos["symbol"]
        
        # FIX Bug #4: Fetch ACTUAL price of the held SHORT asset
        active_current_price = get_symbol_price(active_symbol, is_futures=True)
        if not active_current_price:
            active_current_price = current_price  # Fallback
            
        active_qty = abs(float(active_pos["positionAmt"]))
        entry = float(active_pos["entryPrice"])
        est_val = active_qty * active_current_price
        
        state["position"] = {
            "symbol": active_symbol,
            "quantity": active_qty,
            "entry_price": entry,
            "cost_usd": round(est_val, 2),
            "side": "SHORT"
        }
        
        # PnL logic for SHORT: If current price drops, pnl is positive
        if entry and entry > 0:
            pnl_pct = ((entry - active_current_price) / entry) * 100.0
            state["status"] = f"🔻 En Vivo SHORT ({active_symbol} @ ${active_current_price:.4f} | PnL: {pnl_pct:+.2f}%)"
            
            # FIX Bug #6: SOFTWARE-SIDE SHORT EXIT MONITORING
            # If SL/TP native orders failed (Bug #2), we close via software
            if pnl_pct >= 2.0 or pnl_pct <= -1.0:
                reason = f"TP alcanzado (+{pnl_pct:.2f}%)" if pnl_pct >= 2.0 else f"SL alcanzado ({pnl_pct:.2f}%)"
                print(f"🎯 ALERTA REAL: Cierre SHORT por {reason} en {active_symbol}. Cerrando posición...")
                close_res = execute_real_futures_market_close(active_symbol, active_qty)
                if close_res.get("orderId"):
                    pnl_usd = (entry - active_current_price) * active_qty
                    
                    today_str = datetime.now().strftime("%Y-%m-%d")
                    if state.get("last_trading_day") != today_str:
                        state["daily_wins"] = 0
                        state["daily_losses"] = 0
                        state["last_trading_day"] = today_str
                    
                    if pnl_pct >= 2.0:
                        state["wins"] = state.get("wins", 0) + 1
                        state["daily_wins"] = state.get("daily_wins", 0) + 1
                        res_type = "WIN"
                    else:
                        state["losses"] = state.get("losses", 0) + 1
                        state["daily_losses"] = state.get("daily_losses", 0) + 1
                        res_type = "LOSS"
                    
                    state["current_balance_usd"] = state.get("current_balance_usd", 20.07) + pnl_usd
                    state["trades_count"] = state.get("trades_count", 0) + 1
                    
                    try:
                        import learning_engine
                        learning_engine.record_trade_outcome(
                            symbol=active_symbol, side="SHORT", entry_price=entry, exit_price=active_current_price,
                            pnl_usd=pnl_usd, result_type=res_type, notes=f"Real Money SHORT closed by software ({pnl_pct:.2f}%)",
                            account_id="R-01", group_name="CUENTA REAL"
                        )
                    except Exception as le:
                        print(f"Learning engine error: {le}")
                    
                    state["position"] = None
                    state["status"] = "🟦 Buscando Entrada A+"
                    print(f"✅ SHORT cerrado exitosamente: {res_type} ({pnl_pct:+.2f}% | ${pnl_usd:+.2f})")
                else:
                    print(f"⚠️ SHORT close failed: {close_res}")
            
    # ========================================
    # CASE 3: No active position - look for entries
    # ========================================
    else:
        # If we had a SHORT but now it's gone, Binance closed it natively!
        if state.get("position") and state["position"].get("side") == "SHORT":
            closed_pos = state["position"]
            entry = closed_pos.get("entry_price", 1.0)
            active_qty = closed_pos.get("quantity", closed_pos.get("cost_usd", 10.0) / max(entry, 0.0001))
            active_symbol = closed_pos.get("symbol", "UNKNOWN")
            
            # Fetch the actual close price
            close_price = get_symbol_price(active_symbol, is_futures=True) or current_price
            
            # Update daily counters
            today_str = datetime.now().strftime("%Y-%m-%d")
            if state.get("last_trading_day") != today_str:
                state["daily_wins"] = 0
                state["daily_losses"] = 0
                state["last_trading_day"] = today_str
                
            # Infer result using actual close price
            pnl_usd = (entry - close_price) * active_qty
            if close_price < entry:
                state["wins"] = state.get("wins", 0) + 1
                state["daily_wins"] = state.get("daily_wins", 0) + 1
                res_type = "WIN"
            else:
                state["losses"] = state.get("losses", 0) + 1
                state["daily_losses"] = state.get("daily_losses", 0) + 1
                res_type = "LOSS"
                
            state["current_balance_usd"] = state.get("current_balance_usd", 20.07) + pnl_usd
            state["trades_count"] = state.get("trades_count", 0) + 1
            
            try:
                import learning_engine
                learning_engine.record_trade_outcome(
                    symbol=active_symbol, side="SHORT", entry_price=entry, exit_price=close_price,
                    pnl_usd=pnl_usd, result_type=res_type, notes=f"Real Money SHORT auto-closed by Binance",
                )
            except Exception as le:
                print(f"Learning engine error: {le}")
            print(f"🎯 ALERTA REAL: Posición SHORT en {active_symbol} fue cerrada automáticamente por Binance ({res_type})")
            
        state["position"] = None
        state["status"] = "🟦 Buscando Entrada A+"
        
        # --- ENTRY DECISION LOGIC ---
        import strategy_engine
        dyn_t = strategy_engine.load_thresholds()
        real_long_score = dyn_t.get("group_0", {}).get("long_score", 65)
        real_short_score = dyn_t.get("group_0", {}).get("short_score", 35)
        
        # FIX Bug #8: Check learning engine bias before entering
        bias_ok = True
        if market_bias:
            bias_direction = market_bias.get("recommended_bias", "NEUTRAL")
            if is_bearish and bias_direction == "STRONG_LONG":
                bias_ok = False
                print(f"🧠 Learning Engine BLOCKED SHORT: Market bias is STRONG_LONG")
            elif not is_bearish and bias_direction == "STRONG_SHORT":
                bias_ok = False
                print(f"🧠 Learning Engine BLOCKED LONG: Market bias is STRONG_SHORT")
        
        if bias_ok:
            # 1. LONG Entry Signal
            if best_symbol and not is_bearish and (best_score >= real_long_score or is_learned_signal) and usdt_free >= 5.0:
                trigger_reason = "AUTO-APRENDIZAJE" if is_learned_signal else f"Score {real_long_score}+"
                print(f"🚀 SEÑAL ALCISTA (LONG) ({best_symbol} @ {best_score} Pts - {trigger_reason}). Comprando en Binance Spot...")
                buy_res = execute_real_spot_market_buy(best_symbol, usdt_free)
                if isinstance(buy_res, dict) and "orderId" in buy_res:
                    state["position"] = {
                        "symbol": best_symbol,
                        "entry_price": current_price,
                        "cost_usd": round(usdt_free, 2),
                        "side": "LONG"
                    }
                    state["status"] = f"🔵 En Vivo LONG ({best_symbol})"
                else:
                    print(f"⚠️ LONG no ejecutado: {buy_res}")
                    
            # 2. SHORT Entry Signal
            elif best_symbol and is_bearish and (best_score <= real_short_score or is_learned_signal) and futures_usdt_free >= 5.0:
                trigger_reason = "AUTO-APRENDIZAJE" if is_learned_signal else f"Score <= {real_short_score}"
                print(f"📉 SEÑAL BAJISTA (SHORT) ({best_symbol} @ Score {best_score} - {trigger_reason}). Abriendo Short en Binance Futuros...")
                short_res = execute_real_futures_market_short(best_symbol, futures_usdt_free)
                # FIX Bug #1: short_res is now a dict (entry order), not a list
                if isinstance(short_res, dict) and "orderId" in short_res:
                    state["position"] = {
                        "symbol": best_symbol,
                        "entry_price": current_price,
                        "cost_usd": round(futures_usdt_free, 2),
                        "side": "SHORT"
                    }
                    state["status"] = f"🔻 En Vivo SHORT ({best_symbol})"
                    print(f"✅ SHORT abierto exitosamente: {best_symbol}")
                else:
                    print(f"⚠️ SHORT no ejecutado: {short_res}")

    state["current_balance_usd"] = round(state.get("current_balance_usd", 20.07), 2)
    state["net_pnl_usd"] = round(state["current_balance_usd"] - 20.07, 2)
    state["last_trade_time"] = now_str
    save_real_account_state(state)
    return state

if __name__ == "__main__":
    sys.stdout.reconfigure(encoding='utf-8')
    st = load_real_account_state()
    print(f"💰 Real Account State: {st['status']} | Balance: ${st['current_balance_usd']} USD")
