
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

try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

# Dynamic Proxy Rotator for 24/7 Cloud Execution (10 Fixie EU West accounts, 5,000 requests/month)
FIXIE_POOL = [
    # 3 Cuentas 100% Nuevas (0/500 peticiones usadas) - PRIORIDAD MÁXIMA
    "http://fixie:YOtqrUO1HVYG2xM@ventoux.usefixie.com:80",   # observatorioforestalutn (0/500)
    "http://fixie:WWaxRExXfmPL05s@ventoux.usefixie.com:80",   # utnagp (0/500)
    "http://fixie:f9ibnMDQHLjZTpM@ventoux.usefixie.com:80",   # dronforestalutn (0/500)
    
    # 6 Cuentas de Uso Bajo/Moderado (93 - 155/500 peticiones usadas) - PRIORIDAD SECUNDARIA
    "http://fixie:zW3cwceDZ64c1lE@ventoux.usefixie.com:80",   # oscarhernandot11es (93/500)
    "http://fixie:ygTezfOLKeqEhhF@ventoux.usefixie.com:80",   # forestalutn (110/500)
    "http://fixie:V9uciGagtBF2MJc@ventoux.usefixie.com:80",   # sconcienciautn (129/500)
    "http://fixie:gnvJakG6jyBrS04@ventoux.usefixie.com:80",   # utn2024a (146/500)
    "http://fixie:ak4QPysr5gnUAQW@ventoux.usefixie.com:80",   # utn.sig (150/500)
    "http://fixie:SIOQ4x5oF0pbFju@ventoux.usefixie.com:80",   # oscarhernando4ec (155/500)
    
    # 1 Cuenta de Reserva de Emergencia (420/500 peticiones usadas) - RESPALDO
    "http://fixie:yqYN8TxTpLkrqC0@ventoux.usefixie.com:80",   # oscarhernando4 (420/500)
]

# Balanceador Inteligente: Prioriza las 9 cuentas con menor consumo (excluye la de 420/500 como reserva)
PROXY_URL = random.choice(FIXIE_POOL[:9])
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
        res = requests.get(url, headers=headers, params=params, proxies=PROXIES, timeout=10)
        if res.status_code == 200:
            return res.json().get("balances", [])
        return None
    except Exception:
        return None

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
        res = requests.get(url, headers=headers, params=params, proxies=PROXIES, timeout=10)
        if res.status_code == 200:
            return res.json().get("assets", [])
        return None
    except Exception:
        return None

def get_real_futures_positions():
    timestamp = int(time.time() * 1000)
    params = {"timestamp": timestamp}
    query_string = urlencode(params)
    signature = hmac.new(API_SECRET.encode("utf-8"), query_string.encode("utf-8"), hashlib.sha256).hexdigest()
    params["signature"] = signature
    headers = {"X-MBX-APIKEY": API_KEY}
    
    url = f"{FAPI_URL}/fapi/v2/positionRisk"
    try:
        res = requests.get(url, headers=headers, params=params, proxies=PROXIES, timeout=10)
        if res.status_code == 200:
            positions = res.json()
            return [p for p in positions if float(p.get("positionAmt", 0)) != 0.0]
        return []
    except Exception:
        return []

def get_real_futures_usdt_balance():
    assets = get_real_futures_balances()
    return sum([float(a["availableBalance"]) for a in assets if a["asset"] in ["USDT", "USDC"]])

def get_symbol_price(symbol, is_futures=False):
    """
    Ultra-resilient live price fetcher with multiple fallback mirrors and proxy backup.
    """
    endpoints = [
        f"https://data-api.binance.vision/api/v3/ticker/price?symbol={symbol}",
        f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}",
        f"https://api1.binance.com/api/v3/ticker/price?symbol={symbol}",
        f"https://api2.binance.com/api/v3/ticker/price?symbol={symbol}",
        f"https://api3.binance.com/api/v3/ticker/price?symbol={symbol}"
    ]
    
    for url in endpoints:
        try:
            res = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=3)
            if res.status_code == 200:
                p = float(res.json().get("price", 0))
                if p > 0:
                    return p
        except Exception:
            continue
            
    # Fallback to proxy if direct access has networking issues
    try:
        url = f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}"
        res = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, proxies=PROXIES, timeout=6)
        if res.status_code == 200:
            p = float(res.json().get("price", 0))
            if p > 0:
                return p
    except Exception:
        pass
        
    return None

# ============================================================
# ORDER EXECUTION (Uses Fixie proxy - counted towards quota)
# ============================================================

def execute_real_spot_market_buy(symbol, usdt_amount):
    """
    Executes a SPOT MARKET BUY using quoteOrderQty (100% free USDT).
    Uses 30-Minute Smart Balance Cache to conserve Fixie proxy requests (~0 extra API calls).
    """
    import math
    timestamp = int(time.time() * 1000)
    state = load_real_account_state()
    
    # Read cached USDT balance from 30m diagnosis state (zero Fixie proxy requests consumed)
    cached_usdt = state.get("_cached_usdt_free", 0.0)
    if cached_usdt > 0:
        usdt_amount = min(usdt_amount, cached_usdt * 0.99)
        
    clean_usd = math.floor(usdt_amount * 10) / 10.0
    if clean_usd < 5.1:
        return {"error": f"MIN_NOTIONAL not met (${clean_usd:.1f} < $5.10)"}
        
    params = {
        "symbol": symbol,
        "side": "BUY",
        "type": "MARKET",
        "quoteOrderQty": f"{clean_usd:.1f}",
        "timestamp": timestamp
    }
    query_string = urlencode(params)
    signature = hmac.new(API_SECRET.encode("utf-8"), query_string.encode("utf-8"), hashlib.sha256).hexdigest()
    params["signature"] = signature
    headers = {"X-MBX-APIKEY": API_KEY}
    
    url = f"{BASE_URL}/api/v3/order"
    try:
        res = requests.post(url, headers=headers, params=params, proxies=PROXIES, timeout=10)
        res_json = res.json()
        if "orderId" in res_json or res_json.get("status") == "FILLED":
            # Real-Time Balance Sync via Fixie Proxy upon Trade Opening
            print("🔄 [TRADE OPENED] Sincronizando balance real desde Binance API (Fixie Proxy)...")
            try:
                diagnose_full_spot_wallet()
            except Exception as se:
                print(f"Error re-syncing wallet after buy: {se}")
        return res_json
    except Exception as e:
        return {"error": str(e)}

def execute_real_spot_market_sell(symbol, quantity=None):
    """
    Executes a SPOT MARKET SELL.
    - If quantity is None, fetches the entire free balance of the asset.
    - Dynamically gets LOT_SIZE and stepSize precision to prevent API rejects.
    """
    import math
    asset = symbol.replace("USDT", "")
    
    if quantity is None:
        balances = get_real_balances()
        if balances:
            for b in balances:
                if b.get("asset") == asset:
                    quantity = float(b.get("free", 0))
                    break
                    
    if not quantity or quantity <= 0:
        return {"error": f"No available balance to sell for {symbol}"}
        
    try:
        ex_info = requests.get(f"{BASE_URL}/api/v3/exchangeInfo?symbol={symbol}", timeout=5).json()
        symbol_info = ex_info.get("symbols", [{}])[0]
        step_size = 0.01
        qty_precision = 2
        for f in symbol_info.get("filters", []):
            if f.get("filterType") == "LOT_SIZE":
                step_size = float(f.get("stepSize", "0.01"))
                if "." in f.get("stepSize", ""):
                    qty_precision = len(f.get("stepSize", "").split(".")[1].rstrip("0"))
                else:
                    qty_precision = 0
                break
    except Exception as e:
        print(f"Error fetching precision for {symbol}, defaulting: {e}")
        qty_precision = 2
        step_size = 0.01
        
    if step_size < 1.0 and qty_precision > 0:
        quantized_qty = math.floor(quantity / step_size) * step_size
        qty_str = f"{quantized_qty:.{qty_precision}f}"
    else:
        qty_str = str(int(math.floor(quantity)))
        
    params = {
        "symbol": symbol,
        "side": "SELL",
        "type": "MARKET",
        "quantity": qty_str,
        "timestamp": int(time.time() * 1000)
    }
    query_string = urlencode(params)
    signature = hmac.new(API_SECRET.encode("utf-8"), query_string.encode("utf-8"), hashlib.sha256).hexdigest()
    params["signature"] = signature
    headers = {"X-MBX-APIKEY": API_KEY}
    
    url = f"{BASE_URL}/api/v3/order"
    try:
        res = requests.post(url, headers=headers, params=params, proxies=PROXIES, timeout=10)
        res_json = res.json()
        if "orderId" in res_json or res_json.get("status") == "FILLED":
            # Real-Time Balance Sync via Fixie Proxy upon Trade Closing
            print("🔄 [TRADE CLOSED] Sincronizando balance real en vivo desde Binance API (Fixie Proxy)...")
            try:
                diagnose_full_spot_wallet()
            except Exception as se:
                print(f"Error re-syncing wallet after sell: {se}")
        return res_json
    except Exception as e:
        return {"error": str(e)}

def diagnose_full_spot_wallet():
    """
    30-MINUTE COMPREHENSIVE SPOT WALLET DIAGNOSIS (via Fixie Proxy).
    Runs every 30 minutes to conserve Fixie proxy requests (~48 req/day).
    - Inspects ALL assets held in Spot (USDT, BNB, and active cryptos).
    - Computes exact USD value for every coin.
    - Auto-detects and adopts active positions (> $5 USD) to ensure Take Profit (+2%) / Stop Loss.
    - Auto-clears positions if coin was manually sold/converted.
    - Updates real_money_account.json state.
    """
    state = load_real_account_state()
    balances = get_real_balances()
    if not balances:
        print("⚠️ [DIAGNÓSTICO] No se pudieron obtener los balances desde Binance API.")
        return state
        
    usdt_free = 0.0
    bnb_free = 0.0
    bnb_usd = 0.0
    total_wallet_usd = 0.0
    crypto_holdings = []
    
    # Fetch BNB price for fee shield calculation
    bnb_price = get_symbol_price("BNBUSDT", is_futures=False) or 575.0
    
    stablecoin_set = {
        "USDT", "USDC", "FDUSD", "TUSD", "BUSD", "DAI", "USDD", "USDE", "RLUSD", "USD1",
        "EUR", "AEUR", "WBTC", "TBTC", "USDS", "USTC", "FRAX", "PYUSD", "USD0", "SNDKB", "SNDK", "USD"
    }
    
    print("\n" + "="*60)
    print("🔍 [DIAGNÓSTICO INTEGRAL DE BILLETERA SPOT (FIXIE 30-MIN)]")
    print("="*60)
    
    for b in balances:
        asset = b.get("asset", "")
        free_qty = float(b.get("free", 0))
        locked_qty = float(b.get("locked", 0))
        total_qty = free_qty + locked_qty
        
        if total_qty <= 0.000001:
            continue
            
        if asset == "USDT":
            usdt_free = free_qty
            total_wallet_usd += free_qty
            print(f"  💵 USDT Disponible: ${free_qty:.4f} USDT")
        elif asset == "BNB":
            bnb_free = free_qty
            bnb_usd = free_qty * bnb_price
            total_wallet_usd += bnb_usd
            print(f"  🟡 BNB Escudo Comisiones: {free_qty:.6f} BNB (~${bnb_usd:.2f} USD @ ${bnb_price:.2f})")
        else:
            # Other crypto asset: calculate USD value
            sym = f"{asset}USDT"
            c_price = get_symbol_price(sym, is_futures=False) or 0.0
            usd_val = total_qty * c_price
            if usd_val >= 0.5:  # Only show non-dust assets
                total_wallet_usd += usd_val
                crypto_holdings.append({
                    "asset": asset,
                    "symbol": sym,
                    "quantity": free_qty,
                    "price": c_price,
                    "usd_value": round(usd_val, 2),
                    "is_stable": asset in stablecoin_set
                })
                print(f"  🪙 {asset}: {free_qty:.4f} @ ${c_price:.4f} = ${usd_val:.2f} USD")
                
    print(f"  💰 SALDO TOTAL NETO EN CUENTA: ${total_wallet_usd:.2f} USD")
    print("="*60 + "\n")
    
    # Auto-adoption or clearance of active positions
    current_pos = state.get("position")
    significant_cryptos = [c for c in crypto_holdings if c["usd_value"] >= 5.0 and not c["is_stable"]]
    
    if significant_cryptos:
        primary = significant_cryptos[0]
        if not current_pos or current_pos.get("symbol") != primary["symbol"]:
            state["position"] = {
                "symbol": primary["symbol"],
                "quantity": primary["quantity"],
                "entry_price": primary["price"],
                "cost_usd": primary["usd_value"],
                "side": "LONG",
                "break_even": False
            }
            state["status"] = f"🔵 En Vivo LONG ({primary['symbol']} @ ${primary['price']:.4f})"
            print(f"🎯 [AUTO-ADOPCIÓN] Posición en {primary['symbol']} adoptada automáticamente para gestión de Take Profit (+2%) / Stop Loss.")
    else:
        # If we thought we had a position but no non-stable crypto >= $4 USD exists in wallet
        if current_pos and current_pos.get("side") == "LONG":
            held_sym = current_pos.get("symbol", "").replace("USDT", "")
            is_still_held = any(c["asset"] == held_sym and c["usd_value"] >= 4.0 for c in crypto_holdings)
            if not is_still_held:
                print(f"🧹 [AUTO-LIMPIEZA] La posición {current_pos.get('symbol')} ya no existe en Binance Spot (vendida/convertida). Estado liberado a 'Buscando'.")
                state["position"] = None
                state["status"] = "🟦 Buscando Entrada A+"
                
    state["_cached_total_val"] = round(total_wallet_usd, 2)
    state["_cached_usdt_free"] = round(usdt_free, 4)
    state["_cached_bnb"] = bnb_free
    state["_cached_bnb_usd"] = round(bnb_usd, 2)
    state["current_balance_usd"] = round(total_wallet_usd, 2)
    state["net_pnl_usd"] = round(total_wallet_usd - state.get("initial_deposit_usdt", 17.13), 2)
    save_real_account_state(state)
    return state

def transfer_usdt(amount, to_futures=True):
    """
    Transfers USDT between Spot and Futures automatically.
    """
    timestamp = int(time.time() * 1000)
    params = {
        "type": "MAIN_UMFUTURE" if to_futures else "UMFUTURE_MAIN",
        "asset": "USDT",
        "amount": f"{amount:.2f}",
        "timestamp": timestamp
    }
    query = urlencode(params)
    sig = hmac.new(API_SECRET.encode("utf-8"), query.encode("utf-8"), hashlib.sha256).hexdigest()
    try:
        res = requests.post(f"{BASE_URL}/sapi/v1/asset/transfer", headers={"X-MBX-APIKEY": API_KEY}, params={**params, "signature": sig}, proxies=PROXIES, timeout=10)
        print(f"🔄 Auto-Transfer {'to Futures' if to_futures else 'to Spot'}: {res.json()}")
        return res.json()
    except Exception as e:
        print(f"Transfer failed: {e}")
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

    # 0. Ensure funds are in Futures wallet (Auto-transfer from Spot)
    try:
        f_balance = get_real_futures_usdt_balance()
        amount_needed = (clean_usd + 0.1) - f_balance
        if amount_needed > 1.0:
            transfer_usdt(amount_needed, to_futures=True)
    except Exception as e:
        print(f"Error checking futures balance before transfer: {e}")
        transfer_usdt(clean_usd + 0.1, to_futures=True) # Fallback

    # 1. Force Isolated Margin (Ignore if already Isolated)
    try:
        m_params = {"symbol": symbol, "marginType": "ISOLATED", "timestamp": timestamp}
        m_query = urlencode(m_params)
        m_sig = hmac.new(API_SECRET.encode("utf-8"), m_query.encode("utf-8"), hashlib.sha256).hexdigest()
        requests.post(f"{FAPI_URL}/fapi/v1/marginType", headers=headers, params={**m_params, "signature": m_sig}, proxies=PROXIES, timeout=5)
    except Exception:
        pass

    # 2. Fetch live price AND correct quantity precision from exchangeInfo
    try:
        price_res = requests.get(f"{FAPI_URL}/fapi/v1/ticker/price?symbol={symbol}", proxies=PROXIES, timeout=5).json()
        price = float(price_res.get("price", 1.0))
        
        # Get correct quantity precision for this symbol
        qty_precision = 3  # default
        try:
            exinfo = requests.get(f"{FAPI_URL}/fapi/v1/exchangeInfo", proxies=PROXIES, timeout=5).json()
            sym_info = next((s for s in exinfo['symbols'] if s['symbol'] == symbol), None)
            if sym_info:
                qty_precision = int(sym_info.get('quantityPrecision', 3))
        except:
            pass
        
        qty = clean_usd / price
        if qty_precision == 0:
            qty = max(int(qty), 1)
            # Ensure notional (qty * price) >= $5.0 minimum
            while qty * price < 5.0:
                qty += 1
            qty_str = str(qty)
        else:
            qty = round(qty, qty_precision)
            qty_str = f"{qty:.{qty_precision}f}"
        
        # Final notional check
        notional = qty * price
        if notional < 5.0:
            return {"error": f"Notional too small: {qty} x ${price:.4f} = ${notional:.2f} (min $5.0)"}
        
        # Risk Management: SL +1.0% (loss), TP -2.0% (win) for SHORT
        # Get price precision too
        price_precision = 4
        try:
            if sym_info:
                price_filter = next((f for f in sym_info['filters'] if f['filterType'] == 'PRICE_FILTER'), None)
                if price_filter:
                    tick = price_filter.get('tickSize', '0.0001')
                    price_precision = max(0, len(tick.rstrip('0').split('.')[-1])) if '.' in tick else 0
        except:
            pass
        sl_price = round(price * 1.01, price_precision)
        tp_price = round(price * 0.98, price_precision)
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
                "stopPrice": str(stop_px),
                "closePosition": "true",
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
    
    qty_precision = 3  # default
    try:
        exinfo = requests.get(f"{FAPI_URL}/fapi/v1/exchangeInfo", proxies=PROXIES, timeout=5).json()
        sym_info = next((s for s in exinfo['symbols'] if s['symbol'] == symbol), None)
        if sym_info:
            qty_precision = int(sym_info.get('quantityPrecision', 3))
    except:
        pass
        
    if qty_precision == 0:
        qty_str = str(int(quantity))
    else:
        qty_str = f"{quantity:.{qty_precision}f}"

    params = {
        "symbol": symbol,
        "side": "BUY",  # We are closing a SHORT, so we BUY
        "type": "MARKET",
        "quantity": qty_str,
        "reduceOnly": "true",
        "timestamp": timestamp
    }
        
    query_string = urlencode(params)
    signature = hmac.new(API_SECRET.encode("utf-8"), query_string.encode("utf-8"), hashlib.sha256).hexdigest()
    params["signature"] = signature
    headers = {"X-MBX-APIKEY": API_KEY}
    
    try:
        res = requests.post(f"{FAPI_URL}/fapi/v1/order", headers=headers, params=params, proxies=PROXIES, timeout=10)
        res_json = res.json()
        
        # Only transfer balance back to spot if the close order was successful
        if "orderId" in res_json:
            try:
                f_balance = get_real_futures_usdt_balance()
                if f_balance > 1.0:
                    transfer_usdt(f_balance - 0.1, to_futures=False)
            except Exception as te:
                print(f"Error transferring back to spot: {te}")
            
        return res_json
    except Exception as e:
        return {"error": str(e)}

# ============================================================
# MAIN EVALUATION & TRADING LOGIC
# ============================================================

def evaluate_and_trade_real_money(best_symbol, best_score, current_price, is_bearish=False, is_learned_signal=False):
    state = load_real_account_state()
    import math
    
    # Null guard on current_price
    if not current_price or current_price <= 0:
        current_price = 1.0
    
    # CAPITAL ALLOCATION (SPOT ONLY - EXACTLY 1 POSITION AT A TIME)
    # Truncate to 1 decimal place without rounding, then subtract 0.1 USD to stay safely below available capital
    raw_usdt = state.get("_cached_usdt_free", state.get("current_balance_usd", 17.29))
    truncated_1d = math.floor(float(raw_usdt) * 10) / 10.0
    usdt_free = max(0.0, round(truncated_1d - 0.1, 1))
    
    crypto_balances = []
    
    # Hydrate crypto_balances from local state
    if state.get("position"):
        pos = state["position"]
        qty = pos.get("quantity", pos.get("cost_usd", 10.0) / max(pos.get("entry_price", 1.0), 0.0001))
        if pos.get("side") == "LONG":
            crypto_balances = [{"asset": pos["symbol"].replace("USDT", ""), "free": qty}]
    
    # --- LEARNING ENGINE INTEGRATION ---
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
        
        import multi_timeframe_analyzer
        # AUTO-LIQUIDATION GUARD FOR UUSDT OR STABLECOIN POSITIONS
        if multi_timeframe_analyzer.is_stablecoin(active_symbol) or active_symbol == "UUSDT":
            print(f"🚨 DETECTADA POSICIÓN EN STABLECOIN / DÓLAR SINTÉTICO ({active_symbol}). Ejecutando Venta de Emergencia para restaurar saldo USDT...")
            sell_res = execute_real_spot_market_sell(active_symbol, active_qty)
            print(f"🔄 Venta de Emergencia {active_symbol}: {sell_res}")
            state["position"] = None
            state["status"] = "🟦 Buscando Entrada A+"
            save_real_account_state(state)
            return state
            
        # Fetch live price of the held asset
        active_current_price = get_symbol_price(active_symbol, is_futures=False)
        if not active_current_price:
            active_current_price = current_price  # Fallback
            
        est_val = active_qty * active_current_price
        entry = state["position"].get("entry_price", active_current_price)
        pnl_pct = ((active_current_price - entry) / entry) * 100.0 if entry > 0 else 0.0
        pnl_usd = (active_current_price - entry) * active_qty
        
        # Track Highest Price Reached for Dynamic Trailing Stop
        highest_price = max(state["position"].get("highest_price", entry), active_current_price)
        highest_pnl_pct = ((highest_price - entry) / entry) * 100.0 if entry > 0 else 0.0
        
        # Activate Break-Even at +1.0%
        break_even_active = state["position"].get("break_even", False)
        if pnl_pct >= 1.0 and not break_even_active:
            break_even_active = True
            print(f"🛡️ ESCUDO REAL ACTIVADO: El precio subió +{pnl_pct:.2f}%. Stop-loss asegurado en Break-Even (+0.2%).")
            
        # Activate Dynamic Trailing Stop when PnL hits +2.0% (Rides mega-pumps up to +10%, +20%)
        trailing_active = state["position"].get("trailing_active", False)
        if pnl_pct >= 2.0 and not trailing_active:
            trailing_active = True
            print(f"🚀 TRAILING STOP DINÁMICO ACTIVADO: El precio alcanzó +{pnl_pct:.2f}%. Persiguiendo super-tendencia...")
            
        holding_cycles = state["position"].get("holding_cycles", 0) + 1
        
        import atr_risk_calculator
        import orderbook_analyzer
        
        atr_info = atr_risk_calculator.calculate_adaptive_atr_stop_loss(entry, atr_15m=entry*0.008)
        adaptive_sl_pct = min(1.0, atr_info.get("sl_pct", 1.0))
        trailing_offset = atr_risk_calculator.get_adaptive_trailing_offset(active_symbol, atr_info.get("atr_pct", 0.8))

        # Progressive Time-Decay Escalation Ladder:
        time_regime_msg = ""
        if not break_even_active and not trailing_active:
            if holding_cycles >= 15:    # 10m + 20m = 30 mins
                adaptive_sl_pct = 0.2
                time_regime_msg = "⏳ Escalera 30m: SL Apretado a -0.20%"
            elif holding_cycles >= 5:   # 10 mins
                adaptive_sl_pct = 0.6
                time_regime_msg = "⏳ Escalera 10m: SL Apretado a -0.60%"

        # ESCUDO 1: BTC Flash Crash Circuit Breaker
        btc_price_now = get_symbol_price("BTCUSDT", is_futures=False)
        btc_crash_emergency = False
        if btc_price_now and active_symbol != "BTCUSDT":
            btc_prev = state.get("_btc_last_price", btc_price_now)
            state["_btc_last_price"] = btc_price_now
            btc_drop_pct = ((btc_price_now - btc_prev) / btc_prev) * 100.0 if btc_prev > 0 else 0.0
            if btc_drop_pct <= -1.2:
                btc_crash_emergency = True
                print(f"🚨 ESCUDO 1 (BTC Flash Crash): BTC cayó {btc_drop_pct:.2f}%. Freno de emergencia activado!")

        # ESCUDO 2: Guardia de Muro Inverso de Liquidez (Orderbook Wall Flip)
        ob_depth = orderbook_analyzer.fetch_orderbook_depth(active_symbol)
        ask_dominance = ob_depth.get("ask_dominance_pct", 50.0)
        orderbook_wall_emergency = False
        if ask_dominance >= 65.0:
            orderbook_wall_emergency = True
            print(f"🧱 ESCUDO 2 (Muro Inverso): Vendedores (Asks) dominan el {ask_dominance:.1f}%. Muro de ballena detectado!")

        # Ultra-Precision Adaptive Trailing Stop (0.15% - 0.25% based on liquidity)
        if trailing_active or highest_pnl_pct >= 2.0:
            trailing_active = True
            trailing_floor_pct = max(1.5, highest_pnl_pct - trailing_offset)
        elif break_even_active:
            trailing_floor_pct = 0.2
        else:
            trailing_floor_pct = -abs(adaptive_sl_pct)

        # Apply Emergency Tightening if Shield 1 or Shield 2 triggered
        if (btc_crash_emergency or orderbook_wall_emergency) and not trailing_active:
            trailing_floor_pct = max(-0.20, trailing_floor_pct)
            time_regime_msg = f"🛡️ ESCUDO DE EMERGENCIA ACTIVADO: Stop-Loss apretado a {trailing_floor_pct:+.2f}%"

        tp_target = entry * (1.0 + (adaptive_sl_pct * 2.0 / 100.0))
        sl_target = entry * (1.0 + (trailing_floor_pct / 100.0))
        
        state["position"] = {
            "symbol": active_symbol,
            "quantity": active_qty,
            "entry_price": entry,
            "highest_price": highest_price,
            "cost_usd": round(est_val, 2),
            "side": "LONG",
            "break_even": break_even_active,
            "trailing_active": trailing_active,
            "adaptive_sl_pct": adaptive_sl_pct,
            "holding_cycles": holding_cycles,
            "volatility_regime": time_regime_msg if time_regime_msg else atr_info.get("volatility_regime", "Estándar")
        }
        price_fmt = lambda p: f"${p:.8f}" if p < 0.01 else f"${p:.4f}"
        state["status"] = f"🔵 En Vivo LONG ({active_asset}USDT @ {price_fmt(active_current_price)})"
        
        # --- MONITOREO ACTIVO PRIORITARIO (CADA 2 MINUTOS) ---
        print("\n" + "="*65)
        print(f"📊 [SEGUIMIENTO DE POSICIÓN ACTIVA REAL - SPOT]")
        print(f"🪙 Moneda: {active_symbol} | Cantidad: {active_qty:,.2f} {active_asset} (Tiempo Abierto: {holding_cycles*2}m / 50m)")
        print(f"💵 Entrada: {price_fmt(entry)} USD | Máximo Pico: {price_fmt(highest_price)} USD (+{highest_pnl_pct:.2f}%)")
        print(f"📈 PnL Flotante Actual: {pnl_pct:+.2f}% (${pnl_usd:+.4f} USD)")
        print(f"🚀 Modo Trailing Stop: {'🔥 ACTIVO (Distancia ' + str(trailing_offset) + '%)' if trailing_active else '⚪ Esperando +2.0%'}")
        print(f"🛡️ Piso de Salida Dinámico: {price_fmt(sl_target)} USD ({trailing_floor_pct:+.2f}%)")
        print(f"🏰 Trilogía de Escudos: BTC Circuit Breaker [{'🔴 ALERTA' if btc_crash_emergency else '🟢 OK'}] | Muro Orderbook [{'🔴 ALERTA' if orderbook_wall_emergency else '🟢 OK'}] | Trailing Adaptativo [{trailing_offset:.2f}%]")
        if time_regime_msg:
            print(f"⏳ Alerta Institucional: {time_regime_msg}")
        print("="*65 + "\n")
        
        # Check for exit condition
        if entry and entry > 0:
            should_exit = False
            if trailing_active and pnl_pct <= trailing_floor_pct:
                should_exit = True
                reason_str = f"Trailing Stop Dinámico Pico (+{highest_pnl_pct:.2f}% -> Venta en +{pnl_pct:.2f}%)"
            elif not trailing_active and pnl_pct <= trailing_floor_pct:
                should_exit = True
                reason_str = f"Stop Loss Escalonado ({pnl_pct:.2f}%)"
            elif holding_cycles >= 25 and not break_even_active and not trailing_active:
                should_exit = True
                reason_str = f"Liberación Final por Estancamiento (50m sin movimiento PnL={pnl_pct:+.2f}%)"
                
            if should_exit:
                print(f"🎯 ALERTA REAL: Salida LONG por {reason_str} en {active_symbol}. Vendiendo...")
                
                try:
                    res_json = execute_real_spot_market_sell(active_symbol, active_qty)
                    if "orderId" in res_json or res_json.get("status") == "FILLED":
                        pnl_usd = (active_current_price - entry) * active_qty
                        
                        # Update daily counters
                        today_str = datetime.now().strftime("%Y-%m-%d")
                        if state.get("last_trading_day") != today_str:
                            state["daily_wins"] = 0
                            state["daily_losses"] = 0
                            state["last_trading_day"] = today_str
                        
                        if pnl_usd > 0:
                            state["wins"] = state.get("wins", 0) + 1
                            state["daily_wins"] = state.get("daily_wins", 0) + 1
                            res_type = "WIN"
                        else:
                            state["losses"] = state.get("losses", 0) + 1
                            state["daily_losses"] = state.get("daily_losses", 0) + 1
                            res_type = "LOSS"
                            
                        state["current_balance_usd"] = state.get("current_balance_usd", 20.07) + pnl_usd
                        state["_cached_usdt_free"] = state["current_balance_usd"]
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
                        print(f"⚠️ Spot SELL rejected: {res_json}")
                except Exception as e:
                    print(f"Error ejecutando venta real: {e}")
                    
    # ========================================
    # CASE 2: No active position - Look for SPOT LONG Entry
    # ========================================
    else:
        state["position"] = None
        state["status"] = "🟦 Buscando Entrada A+"
        
        # Stablecoin filter check
        stablecoins_blacklist = {
            "USDT", "USDC", "FDUSD", "TUSD", "BUSD", "DAI", "USDD", "USDE", "RLUSD", "USD1",
            "EUR", "AEUR", "WBTC", "TBTC", "USDS", "USTC", "FRAX", "PYUSD", "USD0", "SNDKB", "SNDK", "USD"
        }
        
        # --- ENTRY DECISION LOGIC (SPOT ONLY) ---
        import strategy_engine
        dyn_t = strategy_engine.load_thresholds()
        real_long_score = dyn_t.get("group_0", {}).get("long_score", 65)
        
        # Check learning engine bias before entering
        bias_ok = True
        if market_bias:
            bias_direction = market_bias.get("recommended_bias", "NEUTRAL")
            if not is_bearish and bias_direction == "STRONG_SHORT":
                bias_ok = False
                print(f"🧠 Learning Engine BLOCKED LONG: Market bias is STRONG_SHORT")
        
        is_stable = False
        if best_symbol:
            sym_clean = best_symbol.replace("USDT", "")
            if sym_clean in stablecoins_blacklist or best_symbol in stablecoins_blacklist:
                is_stable = True
                print(f"⛔ Compra rechazada: {best_symbol} es una stablecoin / activo no volátil.")
            else:
                import multi_timeframe_analyzer
                mtf_res = multi_timeframe_analyzer.analyze_multi_timeframe_candles(best_symbol)
                if not mtf_res.get("is_valid_tradable_asset", True):
                    is_stable = True
                    print(f"⛔ Compra rechazada: {best_symbol} descalificado por análisis histórico multi-temporal ({mtf_res.get('rejection_reason')}).")
                else:
                    print(f"📊 Análisis Multi-Temporal {best_symbol}: Score MTF={mtf_res.get('multi_tf_score')}/100 | Rango 1D={mtf_res.get('price_expansion_1d_pct')}% | Alignment={mtf_res.get('timeframe_alignment')}")
                
        if bias_ok and not is_stable:
            # 1. LONG Entry Signal (Operates with 100% of available USDT, strictly requires Score >= 65 Setup A+)
            min_required_score = max(65, real_long_score) if not is_learned_signal else 65
            if best_symbol and not is_bearish and best_score >= min_required_score and usdt_free >= 5.1:
                trigger_reason = "AUTO-APRENDIZAJE A+" if is_learned_signal else f"Score {real_long_score}+"
                print(f"🚀 SEÑAL ALCISTA (LONG) ({best_symbol} @ {best_score} Pts - {trigger_reason}). Comprando con ${usdt_free:.1f} USDT (100% Capital)...")
                buy_res = execute_real_spot_market_buy(best_symbol, usdt_free)
                if isinstance(buy_res, dict) and "orderId" in buy_res:
                    qty = float(buy_res.get("executedQty", 0))
                    cum_quote = float(buy_res.get("cummulativeQuoteQty", 0))
                    if qty > 0 and cum_quote > 0:
                        actual_entry_price = round(cum_quote / qty, 6)
                        actual_cost = round(cum_quote, 2)
                    else:
                        actual_entry_price = current_price
                        actual_cost = round(usdt_free, 2)
                    if qty == 0:
                        qty = round(usdt_free / current_price, 5)  # Fallback
                    state["position"] = {
                        "symbol": best_symbol,
                        "entry_price": actual_entry_price,
                        "cost_usd": actual_cost,
                        "side": "LONG",
                        "quantity": qty,
                        "break_even": False
                    }
                    state["status"] = f"🔵 En Vivo LONG ({best_symbol} @ ${actual_entry_price:.4f})"
                    state["_cached_usdt_free"] = 0.0
                    save_real_account_state(state)
                    print(f"✅ SPOT LONG ejecutado exitosamente: {best_symbol} ({qty} @ ${actual_entry_price:.4f} = ${actual_cost} USD)")
                else:
                    print(f"⚠️ LONG no ejecutado: {buy_res}")

    state["current_balance_usd"] = round(state.get("current_balance_usd", 20.07), 2)
    state["net_pnl_usd"] = round(state["current_balance_usd"] - state.get("initial_deposit_usdt", 17.13), 2)
    state["last_trade_time"] = now_str
    save_real_account_state(state)
    return state

if __name__ == "__main__":
    sys.stdout.reconfigure(encoding='utf-8')
    st = load_real_account_state()
    print(f"💰 Real Account State: {st['status']} | Balance: ${st['current_balance_usd']} USD")
