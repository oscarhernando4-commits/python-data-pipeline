
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

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

# Dynamic Proxy Rotator for 24/7 Cloud Execution (10 Fixie EU West accounts, 5,000 requests/month)
FIXIE_POOL = [
    "http://fixie:YOtqrUO1HVYG2xM@ventoux.usefixie.com:80",   # observatorioforestalutn
    "http://fixie:WWaxRExXfmPL05s@ventoux.usefixie.com:80",   # utnagp
    "http://fixie:f9ibnMDQHLjZTpM@ventoux.usefixie.com:80",   # dronforestalutn
    "http://fixie:zW3cwceDZ64c1lE@ventoux.usefixie.com:80",   # oscarhernandot11es
    "http://fixie:ygTezfOLKeqEhhF@ventoux.usefixie.com:80",   # forestalutn
    "http://fixie:V9uciGagtBF2MJc@ventoux.usefixie.com:80",   # sconcienciautn
    "http://fixie:gnvJakG6jyBrS04@ventoux.usefixie.com:80",   # utn2024a
    "http://fixie:ak4QPysr5gnUAQW@ventoux.usefixie.com:80",   # utn.sig
    "http://fixie:SIOQ4x5oF0pbFju@ventoux.usefixie.com:80",   # oscarhernando4ec
    "http://fixie:yqYN8TxTpLkrqC0@ventoux.usefixie.com:80",   # oscarhernando4
]

# Nombres legibles para tracking de uso por cuenta
FIXIE_ACCOUNTS = [
    "observatorioforestalutn", "utnagp", "dronforestalutn",
    "oscarhernandot11es", "forestalutn", "sconcienciautn",
    "utn2024a", "utn.sig", "oscarhernando4ec", "oscarhernando4"
]

# ============================================================
# SISTEMA HÍBRIDO LOCAL/NUBE + ROUND-ROBIN EQUITATIVO
# ============================================================
PROXY_STATE_FILE = os.path.join(os.path.dirname(__file__), "proxy_state.json")
EXECUTION_MODE_FILE = os.path.join(os.path.dirname(__file__), "execution_mode.json")

def _load_proxy_state():
    """Carga el estado persistente del rotador de proxies."""
    try:
        with open(PROXY_STATE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {"current_index": 0, "usage": {}}

def _save_proxy_state(state):
    """Guarda el estado del rotador de proxies."""
    try:
        with open(PROXY_STATE_FILE, "w", encoding="utf-8") as f:
            json.dump(state, f, indent=2, ensure_ascii=False)
    except Exception:
        pass

def get_execution_mode():
    """Lee el modo de ejecución actual: 'local' o 'cloud'."""
    try:
        with open(EXECUTION_MODE_FILE, "r", encoding="utf-8") as f:
            return json.load(f).get("mode", "cloud")
    except Exception:
        return "cloud"

def set_execution_mode(mode):
    """Cambia entre 'local' (sin proxy) y 'cloud' (con Fixie)."""
    data = {
        "mode": mode,
        "switched_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "switched_by": "api_connector"
    }
    try:
        with open(EXECUTION_MODE_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except Exception:
        pass
    emoji = "🖥️ LOCAL (Sin Proxy)" if mode == "local" else "☁️ NUBE (Fixie Proxy)"
    print(f"🔄 Modo de ejecución cambiado a: {emoji}")

def get_proxy():
    """Round-Robin equitativo: rota secuencialmente entre cuentas Fixie activas con auto-renovación mensual."""
    state = _load_proxy_state()
    idx = state.get("current_index", 9) % len(FIXIE_POOL)
    
    # Dynamic exhausted accounts (auto-clears on monthly renewal)
    exhausted = state.get("exhausted", {})
    current_month = datetime.now().strftime("%Y-%m")
    
    # Auto-renewal: if the month changed since last exhaustion, clear ALL exhausted flags
    last_exhaust_month = state.get("last_exhaust_month", "")
    if current_month != last_exhaust_month and exhausted:
        print(f"🔄 [FIXIE AUTO-RENOVACIÓN] Nuevo mes detectado ({current_month}). Reactivando las {len(exhausted)} cuentas Fixie pausadas.")
        exhausted = {}
        state["exhausted"] = {}
        state["last_exhaust_month"] = current_month
        _save_proxy_state(state)
    
    exhausted_indices = set(exhausted.get("indices", []))
    
    # Find next available account
    attempts = 0
    while idx in exhausted_indices and attempts < len(FIXIE_POOL):
        idx = (idx + 1) % len(FIXIE_POOL)
        attempts += 1
    
    # If ALL accounts exhausted, force reset (emergency fallback)
    if attempts >= len(FIXIE_POOL):
        print("⚠️ [FIXIE] TODAS las cuentas agotadas. Forzando reset de emergencia...")
        exhausted_indices = set()
        state["exhausted"] = {}
        idx = 9  # Start from primary account
        
    url = FIXIE_POOL[idx]
    
    # Advance to next for next call
    state["current_index"] = (idx + 1) % len(FIXIE_POOL)
    
    # Usage tracking per account
    usage = state.setdefault("usage", {})
    account_name = FIXIE_ACCOUNTS[idx]
    usage[account_name] = usage.get(account_name, 0) + 1
    state["last_used"] = account_name
    state["last_used_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    _save_proxy_state(state)
    return {"http": url, "https": url}

def mark_fixie_exhausted(account_index):
    """Marks a Fixie account as exhausted (quota depleted). Auto-clears on monthly renewal."""
    state = _load_proxy_state()
    exhausted = state.setdefault("exhausted", {})
    indices = exhausted.setdefault("indices", [])
    if account_index not in indices:
        indices.append(account_index)
        state["last_exhaust_month"] = datetime.now().strftime("%Y-%m")
        _save_proxy_state(state)
        name = FIXIE_ACCOUNTS[account_index] if account_index < len(FIXIE_ACCOUNTS) else f"#{account_index}"
        print(f"🚫 [FIXIE] Cuenta {name} marcada como agotada. Activas: {len(FIXIE_POOL) - len(indices)}/10")

def get_smart_proxy():
    """Proxy inteligente: usa directo si modo local, Fixie Round-Robin si modo nube."""
    if get_execution_mode() == "local":
        return None  # Sin proxy = conexión directa desde PC
    return get_proxy()  # Round-Robin Fixie equitativo

# Legacy compatibility (solo para imports externos)
PROXY_URL = FIXIE_POOL[0]
PROXIES = None  # Lazy: use get_smart_proxy() per-request instead of wasting Fixie quota on module reload

def get_api_key():
    return os.getenv("BINANCE_REAL_API_KEY", "").strip()

def get_api_secret():
    return os.getenv("BINANCE_REAL_API_SECRET", "").strip()

API_KEY = get_api_key()
API_SECRET = get_api_secret()
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
        res = requests.get(url, headers=headers, params=params, proxies=get_smart_proxy(), timeout=6)
        if res.status_code == 200:
            return res.json().get("balances", [])
    except Exception:
        pass
        
    # Direct Connection Fallback for Local PC
    try:
        res = requests.get(url, headers=headers, params=params, proxies=None, timeout=6)
        if res.status_code == 200:
            return res.json().get("balances", [])
    except Exception:
        pass
    return None

def get_real_usdt_balance():
    balances = get_real_balances()
    if not balances:
        return 0.0
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
        res = requests.get(url, headers=headers, params=params, proxies=get_smart_proxy(), timeout=10)
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
        res = requests.get(url, headers=headers, params=params, proxies=get_smart_proxy(), timeout=10)
        if res.status_code == 200:
            positions = res.json()
            return [p for p in positions if float(p.get("positionAmt", 0)) != 0.0]
        return []
    except Exception:
        return []

def get_real_futures_usdt_balance():
    assets = get_real_futures_balances()
    if not assets:
        return 0.0
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
        res = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, proxies=get_smart_proxy(), timeout=6)
        if res.status_code == 200:
            p = float(res.json().get("price", 0))
            if p > 0:
                return p
    except Exception:
        pass
        
    return None

def get_recent_kline_high(symbol, limit=5, start_time_ms=None):
    """
    Fetches the highest price peak (High wick) from recent 1-minute klines AFTER position entry.
    Works 100% seamlessly in both Local Mode (direct connection) and Cloud Mode (with proxy fallback).
    Ensures that 1-second price spikes are captured only during the active trade lifecycle.
    """
    mirrors = [
        "https://api.binance.com/api/v3/klines",
        "https://api1.binance.com/api/v3/klines",
        "https://api2.binance.com/api/v3/klines",
        "https://api3.binance.com/api/v3/klines"
    ]
    params = {"symbol": symbol, "interval": "1m", "limit": limit}
    if start_time_ms and start_time_ms > 0:
        params["startTime"] = int(start_time_ms)
    
    # 1. Try direct connection first (fastest for local and standard cloud)
    for url in mirrors:
        try:
            res = requests.get(url, params=params, timeout=2)
            if res.status_code == 200:
                k_data = res.json()
                if isinstance(k_data, list) and len(k_data) > 0:
                    if start_time_ms and start_time_ms > 0:
                        filtered = [k for k in k_data if int(k[0]) >= int(start_time_ms)]
                        if filtered:
                            return max([float(k[2]) for k in filtered])
                        return 0.0
                    return max([float(k[2]) for k in k_data])
        except Exception:
            continue
            
    # 2. Try with smart proxy (Fixie fallback in cloud mode)
    try:
        res = requests.get("https://api.binance.com/api/v3/klines", params=params, proxies=get_smart_proxy(), timeout=4)
        if res.status_code == 200:
            k_data = res.json()
            if isinstance(k_data, list) and len(k_data) > 0:
                if start_time_ms and start_time_ms > 0:
                    filtered = [k for k in k_data if int(k[0]) >= int(start_time_ms)]
                    if filtered:
                        return max([float(k[2]) for k in filtered])
                    return 0.0
                return max([float(k[2]) for k in k_data])
    except Exception:
        pass
        
    return 0.0

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
        usdt_amount = min(usdt_amount, cached_usdt)
        
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
    api_k = get_api_key()
    api_s = get_api_secret()
    signature = hmac.new(api_s.encode("utf-8"), query_string.encode("utf-8"), hashlib.sha256).hexdigest()
    params["signature"] = signature
    headers = {"X-MBX-APIKEY": api_k}
    
    url = f"{BASE_URL}/api/v3/order"
    try:
        res = requests.post(url, headers=headers, params=params, proxies=get_smart_proxy(), timeout=10)
        res_json = res.json()
        if "orderId" in res_json or res_json.get("status") == "FILLED":
            print("🔄 [TRADE OPENED] Sincronizando balance real desde Binance API...")
            try:
                diagnose_full_spot_wallet()
            except Exception as se:
                print(f"Error re-syncing wallet after buy: {se}")
        return res_json
    except Exception as e:
        print(f"⚠️ [API RETRY] Error en proxy ({e}). Reintentando compra Spot vía conexión directa...")
        try:
            res = requests.post(url, headers=headers, params=params, proxies=None, timeout=10)
            res_json = res.json()
            if "orderId" in res_json or res_json.get("status") == "FILLED":
                try:
                    diagnose_full_spot_wallet()
                except Exception:
                    pass
            return res_json
        except Exception as e2:
            return {"error": str(e2)}

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
        ex_info = requests.get(f"{BASE_URL}/api/v3/exchangeInfo?symbol={symbol}", proxies=get_smart_proxy(), timeout=5).json()
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
        res = requests.post(url, headers=headers, params=params, proxies=get_smart_proxy(), timeout=10)
        res_json = res.json()
        if "orderId" in res_json or res_json.get("status") == "FILLED":
            print("🔄 [TRADE CLOSED] Sincronizando balance real en vivo desde Binance API...")
            try:
                diagnose_full_spot_wallet()
            except Exception as se:
                print(f"Error re-syncing wallet after sell: {se}")
        return res_json
    except Exception as e:
        print(f"⚠️ [API RETRY] Error en proxy ({e}). Reintentando venta Spot vía conexión directa...")
        try:
            res = requests.post(url, headers=headers, params=params, proxies=None, timeout=10)
            res_json = res.json()
            if "orderId" in res_json or res_json.get("status") == "FILLED":
                try:
                    diagnose_full_spot_wallet()
                except Exception:
                    pass
            return res_json
        except Exception as e2:
            return {"error": str(e2)}

def get_exact_real_entry_price(symbol):
    """
    Queries Binance /api/v3/myTrades to extract the exact weighted average fill price
    for the most recent BUY order of the specified symbol.
    """
    try:
        api_k = get_api_key()
        api_s = get_api_secret()
        ts = int(time.time() * 1000)
        params = {"symbol": symbol, "timestamp": ts, "limit": 10}
        qs = urlencode(params)
        sig = hmac.new(api_s.encode("utf-8"), qs.encode("utf-8"), hashlib.sha256).hexdigest()
        params["signature"] = sig
        headers = {"X-MBX-APIKEY": api_k}
        
        url = f"{BASE_URL}/api/v3/myTrades"
        res = requests.get(url, headers=headers, params=params, proxies=get_smart_proxy(), timeout=5)
        trades = res.json()
        if isinstance(trades, list) and trades:
            buy_trades = [t for t in trades if t.get("isBuyer", False)]
            if buy_trades:
                last_order_id = buy_trades[-1].get("orderId")
                matching_fills = [t for t in buy_trades if t.get("orderId") == last_order_id]
                total_qty = sum(float(t["qty"]) for t in matching_fills)
                total_cost = sum(float(t["quoteQty"]) for t in matching_fills)
                if total_qty > 0 and total_cost > 0:
                    return round(total_cost / total_qty, 8), round(total_cost, 2), round(total_qty, 4)
    except Exception as e:
        print(f"Error fetching exact trades for {symbol}: {e}")
    return None, None, None

def diagnose_full_spot_wallet():
    """
    60-MINUTE COMPREHENSIVE SPOT WALLET DIAGNOSIS (via Fixie Proxy).
    Runs every 60 minutes to conserve Fixie proxy requests (~24 req/day).
    - Inspects ALL assets held in Spot (USDT, BNB, and active cryptos).
    - Computes exact USD value for every coin.
    - Auto-detects and adopts active positions (> $5 USD) using EXACT fill prices from myTrades.
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
            exact_entry, exact_cost, exact_qty = get_exact_real_entry_price(primary["symbol"])
            final_entry = exact_entry if exact_entry else primary["price"]
            final_cost = exact_cost if exact_cost else primary["usd_value"]
            final_qty = exact_qty if exact_qty else primary["quantity"]
            state["position"] = {
                "symbol": primary["symbol"],
                "quantity": final_qty,
                "entry_price": final_entry,
                "highest_price": final_entry,
                "cost_usd": final_cost,
                "side": "LONG",
                "phase": 1,
                "break_even": False,
                "entry_time_ms": int(time.time() * 1000)
            }
            price_fmt = lambda p: f"${p:.8f}" if p < 0.01 else f"${p:.4f}"
            state["status"] = f"🔵 En Vivo LONG ({primary['symbol']} @ {price_fmt(final_entry)})"
            print(f"🎯 [AUTO-ADOPCIÓN EXACTA] Posición en {primary['symbol']} adoptada con precio real Binance: {price_fmt(final_entry)} (Costo: ${final_cost} USD).")
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
        res = requests.post(f"{BASE_URL}/sapi/v1/asset/transfer", headers={"X-MBX-APIKEY": API_KEY}, params={**params, "signature": sig}, proxies=get_smart_proxy(), timeout=10)
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
        requests.post(f"{FAPI_URL}/fapi/v1/marginType", headers=headers, params={**m_params, "signature": m_sig}, proxies=get_smart_proxy(), timeout=5)
    except Exception:
        pass

    # 2. Fetch live price AND correct quantity precision from exchangeInfo
    try:
        price_res = requests.get(f"{FAPI_URL}/fapi/v1/ticker/price?symbol={symbol}", proxies=get_smart_proxy(), timeout=5).json()
        price = float(price_res.get("price", 1.0))
        
        # Get correct quantity precision for this symbol
        qty_precision = 3  # default
        try:
            exinfo = requests.get(f"{FAPI_URL}/fapi/v1/exchangeInfo", proxies=get_smart_proxy(), timeout=5).json()
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
        entry_res = requests.post(f"{FAPI_URL}/fapi/v1/order", headers=headers, params=entry_params, proxies=get_smart_proxy(), timeout=10)
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
            sl_tp_res = requests.post(f"{FAPI_URL}/fapi/v1/order", headers=headers, params=p, proxies=get_smart_proxy(), timeout=10)
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
        exinfo = requests.get(f"{FAPI_URL}/fapi/v1/exchangeInfo", proxies=get_smart_proxy(), timeout=5).json()
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
        res = requests.post(f"{FAPI_URL}/fapi/v1/order", headers=headers, params=params, proxies=get_smart_proxy(), timeout=10)
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

def quick_position_heartbeat():
    """
    Sub-second micro-monitor for active real-money Spot position.
    Runs every 5-10s between main matrix cycles.
    Instantly updates highest_price, unlocks phases, and triggers emergency SL/TP.
    """
    try:
        state = load_real_account_state()
        pos = state.get("position")
        if not pos or not pos.get("symbol"):
            return None
            
        sym = pos.get("symbol")
        qty = float(pos.get("quantity", 0))
        entry = float(pos.get("entry_price", 0))
        if qty <= 0 or entry <= 0:
            return None
            
        # Fast direct price ticker
        current_price = get_symbol_price(sym, is_futures=False)
        if not current_price or current_price <= 0:
            return None
            
        # 🚀 DETECTOR CUÁNTICO DE MECHAS: Consulta velas de 1m (Local + Nube) solo DESPUÉS de la entrada
        entry_time_ms = pos.get("entry_time_ms", 0)
        kline_high = get_recent_kline_high(sym, limit=5, start_time_ms=entry_time_ms)
        highest_price = max(pos.get("highest_price", entry), current_price, kline_high if kline_high > 0 else current_price)
        highest_pnl_pct = ((highest_price - entry) / entry) * 100.0
        current_pnl_pct = ((current_price - entry) / entry) * 100.0
        current_phase = pos.get("phase", 1)
        
        atr_15m_pct = pos.get("atr_pct_15m", 0.30)
        ma25_5m = pos.get("ma25_5m", 0.0)
        
        holding_cycles_hb = pos.get("holding_cycles", 0)
        
        # ═══════════════════════════════════════════════════════════════════════
        # 🎯 SISTEMA DE 4 FASES MEJORADO CON CEREBRO ADAPTATIVO:
        # FASE 0 (primeros 3 ciclos / ~15s): SL ultra-rápido -0.80% si el libro colapsa
        # FASE 1 (< +0.30%): SL -1.50% (Colchón de inicio)
        # FASE 2 (+0.30% a +0.60%): Piso ATR-adaptativo max(+0.15%, Pico - holgura)
        # FASE 3 (> +0.60%): Trailing Holgado ATR = CIMA - dynamic_trailing_distance
        # ═══════════════════════════════════════════════════════════════════════
        dynamic_trailing_distance = max(0.40, round(atr_15m_pct * 1.3, 2))
        
        if highest_pnl_pct >= 0.60:
            sl_pct = max(0.30, round(highest_pnl_pct - dynamic_trailing_distance, 2))
            new_phase = 3
        elif highest_pnl_pct >= 0.30:
            # 🔬 MEJORA 2: Holgura Fase 2 ATR-adaptativa (0.10% - 0.25% según volatilidad del par)
            holgura_f2 = min(0.25, max(0.10, round(atr_15m_pct * 0.5, 2)))
            sl_pct = max(0.15, round(highest_pnl_pct - holgura_f2, 2))
            new_phase = 2
        else:
            sl_pct = -1.50
            new_phase = 1
            
        # 🚀 MEJORA 1: FASE 0 — Freno Rápido en Ventana de los Primeros 3 Ciclos (~15s)
        # Si en los primeros 15s el precio ya cae -0.80%, el setup era incorrecto → salir YA
        if holding_cycles_hb <= 3 and current_pnl_pct <= -0.80 and new_phase == 1:
            sl_pct = -0.80
            new_phase = 1
            
        # Update if changed
        if highest_price > pos.get("highest_price", entry) or new_phase > current_phase:
            pos["highest_price"] = highest_price
            pos["phase"] = new_phase
            state["position"] = pos
            save_real_account_state(state)
            
        # Check if Stop Loss or Trailing Stop triggered
        should_exit = current_pnl_pct <= sl_pct
        exit_reason = f"Stop/Trailing ({current_pnl_pct:+.2f}% <= {sl_pct:+.2f}%)"
        
        # Pillar 4: Trend Ride Guard
        if new_phase >= 3 and should_exit and current_price > entry and ma25_5m > 0 and current_price >= ma25_5m * 0.999 and current_pnl_pct >= 0.30:
            should_exit = False
            exit_reason = f"Protegido por MA25 5m (Pnl: {current_pnl_pct:+.2f}%)"
        
        # SNIPER MEJORA B: Detección de Agotamiento de Mecha en Cima con holgura adaptativa
        wick_pullback_threshold = max(0.40, round(dynamic_trailing_distance if new_phase >= 3 else 0.40, 2))
        if not should_exit and new_phase >= 3 and highest_pnl_pct >= 0.80 and (highest_pnl_pct - current_pnl_pct) >= wick_pullback_threshold:
            should_exit = True
            exit_reason = f"🎯 SNIPER MECHA CIMA (Pico +{highest_pnl_pct:.2f}% -> Venta en {current_pnl_pct:+.2f}%)"
        
        # 🧱 MEJORA 4: Cancelación Preventiva de 30s — Libro de órdenes colapsó tras entrada
        # Si en el primer ciclo el libro cae < 38% Bids y tenemos pérdida > -0.20% → salir flat
        if not should_exit and holding_cycles_hb <= 1 and current_pnl_pct < -0.20:
            try:
                import orderbook_analyzer as _ob
                ob_check = _ob.fetch_orderbook_depth(sym, limit=20)
                bids_now = ob_check.get("bid_dominance_pct", 50.0)
                if bids_now < 38.0:
                    should_exit = True
                    exit_reason = f"⚡ CANCELACIÓN PREVENTIVA 30s: Libro colapsó (Bids={bids_now:.1f}% < 38%). Setup inválido."
            except Exception:
                pass
            
        if should_exit:
            print(f"\n🚨 [MICRO-HEARTBEAT 5S] Salida Inteligente ejecutada para {sym} @ ${current_price:.5f} ({exit_reason})")
            sell_res = execute_real_spot_market_sell(sym, qty)
            print(f"🔄 Venta Mercado Ejecutada: {sell_res}")
            
            # 📚 BUG FIX: Registrar win/loss correctamente + notificar learning engine
            pnl_usd = round((current_price - entry) * qty, 4)
            is_win_exit = current_pnl_pct > 0
            if is_win_exit:
                state["wins"] = state.get("wins", 0) + 1
                state["daily_wins"] = state.get("daily_wins", 0) + 1
            else:
                state["losses"] = state.get("losses", 0) + 1
                state["daily_losses"] = state.get("daily_losses", 0) + 1
            state["trades_count"] = state.get("trades_count", 0) + 1
            state["net_pnl_usd"] = round(state.get("net_pnl_usd", 0.0) + pnl_usd, 4)
            
            # 📖 Guardar en Learning Engine para memoria de futuros trades
            try:
                import learning_engine
                learning_engine.record_trade_outcome(
                    symbol=sym,
                    entry_price=entry,
                    exit_price=current_price,
                    qty=qty,
                    pnl_pct=current_pnl_pct,
                    pnl_usd=pnl_usd,
                    exit_reason=exit_reason,
                    phase=new_phase
                )
            except Exception as le_err:
                print(f"⚠️ Learning Engine registro fallido: {le_err}")
            
            state["position"] = None
            state["status"] = f"{'🟢 WIN' if is_win_exit else '🔴 LOSS'} Cerrado ({sym} PnL: {current_pnl_pct:+.2f}% / ${pnl_usd:+.4f})"
            state["_last_closed_symbol"] = sym
            state["_last_closed_time"] = time.time()
            state["_last_exit_price"] = current_price
            save_real_account_state(state)
            try:
                diagnose_full_spot_wallet()
            except Exception:
                pass
            return "EXIT"
            
        return {
            "symbol": sym,
            "price": current_price,
            "pnl_pct": current_pnl_pct,
            "highest_pnl": highest_pnl_pct,
            "phase": new_phase
        }
    except Exception:
        return None

def trunc_1d(val):
    """Truncates a float to exactly 1 decimal place WITHOUT rounding."""
    if val is None:
        return 0.0
    import math
    return math.floor(float(val) * 10.0) / 10.0

def evaluate_and_trade_real_money(best_symbol, best_score, current_price, is_bearish=False, is_learned_signal=False, best_confidence=75):
    state = load_real_account_state()
    import math
    
    # Null guard on current_price
    if not current_price or current_price <= 0:
        current_price = 1.0
    
    # AUTOMATIC COMPOUND INTEREST ALLOCATION (SPOT ONLY - EXACTLY 1 POSITION AT A TIME)
    # Strictly truncated to 1 decimal place WITHOUT rounding, minus 0.1 USD buffer for Binance spot fees
    raw_usdt = state.get("_cached_usdt_free", state.get("current_balance_usd", 17.29))
    truncated_1d = trunc_1d(raw_usdt)
    usdt_free = max(0.0, trunc_1d(truncated_1d - 0.1))
    
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
        
        # Track Highest Price Reached for Dynamic Trailing Stop (incluyendo mechas de velas 1m para Local y Nube)
        kline_high = get_recent_kline_high(active_symbol, limit=5)
        highest_price = max(state["position"].get("highest_price", entry), active_current_price, kline_high)
        highest_pnl_pct = ((highest_price - entry) / entry) * 100.0 if entry > 0 else 0.0
        
        holding_cycles = state["position"].get("holding_cycles", 0) + 1
        
        atr_15m_pct = state["position"].get("atr_pct_15m", 0.30)
        ma25_5m = state["position"].get("ma25_5m", 0.0)
        
        import orderbook_analyzer
        
        # ═══════════════════════════════════════════════════════════════
        # 🎯 SISTEMA ULTRA-EFICIENTE DE 3 FASES CUÁNTICAS:
        # FASE 1: Antes de +0.30% -> SL -1.50% (Colchón inicial).
        # FASE 2: +0.30% a +0.60% -> Piso = max(+0.15% NETO, Cima - 0.25%).
        # FASE 3: Superior a +0.60% -> Trailing Holgado ATR = CIMA - dynamic_trailing_distance.
        # ═══════════════════════════════════════════════════════════════
        if highest_pnl_pct >= 0.60:
            phase = 3
            dynamic_trailing_distance = max(0.40, round(atr_15m_pct * 1.3, 2))
            trailing_floor_pct = max(0.30, round(highest_pnl_pct - dynamic_trailing_distance, 2))
            phase_msg = f"💎 FASE 3 (COSECHA ADAPTATIVA ATR): Piso +{trailing_floor_pct:.2f}% (Cima +{highest_pnl_pct:.2f}% - {dynamic_trailing_distance:.2f}%)"
        elif highest_pnl_pct >= 0.30:
            phase = 2
            # 🔬 MEJORA 2: Holgura ATR-Adaptativa en Fase 2 (0.10%-0.25% según volatilidad del par)
            holgura_f2 = min(0.25, max(0.10, round(atr_15m_pct * 0.5, 2)))
            trailing_floor_pct = max(0.15, round(highest_pnl_pct - holgura_f2, 2))
            phase_msg = f"🔒 FASE 2 (+0.30% A +0.60%): Piso +{trailing_floor_pct:.2f}% (Cima +{highest_pnl_pct:.2f}% | ATR-Holgura={holgura_f2:.2f}% | Ganancia Verde)"
        else:
            phase = 1
            trailing_floor_pct = -1.50
            phase_msg = f"⚡ FASE 1 (ENTRADA Y DESARROLLO): SL -1.50% (Colchón de Seguridad Inicial)"

        # ESCUDO 1: BTC Flash Crash Circuit Breaker
        btc_price_now = get_symbol_price("BTCUSDT", is_futures=False)
        btc_crash_emergency = False
        if btc_price_now and active_symbol != "BTCUSDT":
            btc_prev = state.get("_btc_last_price", btc_price_now)
            state["_btc_last_price"] = btc_price_now
            btc_drop_pct = ((btc_price_now - btc_prev) / btc_prev) * 100.0 if btc_prev > 0 else 0.0
            if btc_drop_pct <= -1.5:
                btc_crash_emergency = True
                print(f"🚨 ESCUDO 1 (BTC Flash Crash): BTC cayó {btc_drop_pct:.2f}%. Freno de emergencia!")

        # ESCUDO 2: Guardia de Muro Inverso de Liquidez (Orderbook Wall Flip)
        ob_depth = orderbook_analyzer.fetch_orderbook_depth(active_symbol)
        ask_dominance = 100.0 - ob_depth.get("bid_dominance_pct", 50.0)
        orderbook_wall_emergency = False
        if ask_dominance >= 70.0:  # Raised from 65% to 70% to avoid false alarms
            orderbook_wall_emergency = True
            print(f"🧱 ESCUDO 2 (Muro Inverso): Vendedores dominan {ask_dominance:.1f}%!")

        # Emergency override: Only in Phase 1 (before any profit was reached)
        if (btc_crash_emergency or orderbook_wall_emergency) and phase == 1:
            trailing_floor_pct = max(-1.5, trailing_floor_pct)
            phase_msg = f"🛡️ ESCUDO DE EMERGENCIA: SL apretado a {trailing_floor_pct:+.2f}%"

        # Stagnation & Alpha Fast Rotation Rule (Límite Ágil de 60 Minutos):
        stagnation_exit = False
        reason_str = ""
        # 1. Liberación por Estancamiento Máximo (60 Minutos / 60 ciclos en Fase 1 sin movimiento):
        if holding_cycles >= 60 and phase == 1 and abs(pnl_pct) <= 0.60:
            stagnation_exit = True
            reason_str = f"🚀 Liberación por Estancamiento (60m en Fase 1 sin despegue, PnL={pnl_pct:+.2f}%)"
        # 2. 🔄 MEJORA 5: Rotación Alpha Dinámica — Score Relativo en lugar de Score Fijo 88
        # Antes exigía 88pts (muy raro), ahora acepta 72pts con delta >= 14 sobre el umbral base
        elif holding_cycles >= 25 and phase == 1 and abs(pnl_pct) <= 0.40:
            if best_symbol and best_symbol != active_symbol and best_score >= 72 and not is_bearish:
                score_delta = best_score - 58  # Delta sobre el umbral mínimo de entrada
                if score_delta >= 14:
                    stagnation_exit = True
                    reason_str = f"🔄 Rotación Alpha Dinámica ({holding_cycles}m plano → {best_symbol} @ {best_score}pts, delta={score_delta}pts)"
        
        # 🧠 MEJORA 6: FII en Tiempo Real durante el Holding — Re-evalúa cada 5 ciclos
        # Si el dinero institucional salió (FII < 25) y estamos en pérdida, salir antes del SL
        if not stagnation_exit and phase == 1 and holding_cycles >= 5 and holding_cycles % 5 == 0 and pnl_pct < -0.60:
            try:
                import multi_timeframe_analyzer as _mtf_live
                mtf_live_data = _mtf_live.analyze_multi_timeframe_candles(active_symbol)
                fii_live = mtf_live_data.get("fii_score", 50)
                if fii_live < 25:
                    stagnation_exit = True
                    reason_str = f"🧠 FII COLAPSÓ EN TIEMPO REAL ({fii_live}/100 < 25): Capital institucional salió. Salida anticipada al SL."
                    print(f"⚠️ [FII LIVE] {active_symbol} FII={fii_live}/100. Capital institucional salió → salida preventiva.")
            except Exception:
                pass

        sl_target = entry * (1.0 + (trailing_floor_pct / 100.0))
        
        state["position"] = {
            "symbol": active_symbol,
            "quantity": active_qty,
            "entry_price": entry,
            "highest_price": highest_price,
            "cost_usd": round(est_val, 2),
            "side": "LONG",
            "phase": phase,
            "holding_cycles": holding_cycles,
            "volatility_regime": phase_msg
        }
        price_fmt = lambda p: f"${p:.8f}" if p < 0.01 else f"${p:.4f}"
        state["status"] = f"🔵 En Vivo LONG ({active_asset}USDT @ {price_fmt(active_current_price)})"
        
        # --- MONITOREO ACTIVO PRIORITARIO (CADA 2 MINUTOS) ---
        print("\n" + "="*65)
        print(f"📊 [SEGUIMIENTO DE POSICIÓN ACTIVA REAL - SPOT]")
        print(f"🪙 Moneda: {active_symbol} | Cantidad: {active_qty:,.2f} {active_asset} (Tiempo: {holding_cycles}m / 2880m)")
        print(f"💵 Entrada: {price_fmt(entry)} USD | Máximo Pico: {price_fmt(highest_price)} USD (+{highest_pnl_pct:.2f}%)")
        print(f"📈 PnL Flotante Actual: {pnl_pct:+.2f}% (${pnl_usd:+.4f} USD)")
        print(f"🧠 {phase_msg}")
        print(f"🛡️ Piso de Salida: {price_fmt(sl_target)} USD ({trailing_floor_pct:+.2f}%)")
        print(f"🏰 Escudos: BTC [{'🔴' if btc_crash_emergency else '🟢'}] | Orderbook [{'🔴' if orderbook_wall_emergency else '🟢'}]")
        print("="*65 + "\n")
        
        # Check for exit condition (PRICE-DRIVEN, NOT TIME-DRIVEN)
        if entry and entry > 0:
            should_exit = False
            if pnl_pct <= trailing_floor_pct:
                should_exit = True
                if phase >= 2:
                    reason_str = f"Protección de Ganancia Fase {phase} (Pico +{highest_pnl_pct:.2f}% → Venta en {pnl_pct:+.2f}%)"
                else:
                    reason_str = f"Stop Loss Fase 1 ({pnl_pct:.2f}% tocó piso de {trailing_floor_pct:+.2f}%)"
                
                # Pillar 4: Trend Ride Guard
                if phase >= 3 and should_exit and active_current_price > entry and ma25_5m > 0 and active_current_price >= ma25_5m * 0.999 and pnl_pct >= 0.30:
                    should_exit = False
                    reason_str = f"Protegido por MA25 5m (Pnl: {pnl_pct:+.2f}%)"
            elif phase >= 2 and orderbook_wall_emergency:
                should_exit = True
                reason_str = f"⚡ Salida Relámpago por Agotamiento CVD (Fase {phase}, Pico +{highest_pnl_pct:.2f}% → Vendedores dominan {ask_dominance:.1f}%)"
            elif stagnation_exit:
                should_exit = True
                reason_str = f"Liberación por Estancamiento (2 Días en Fase 1, PnL={pnl_pct:+.2f}%)"
                
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
                            
                        state["trades_count"] = state.get("trades_count", 0) + 1
                        save_real_account_state(state)
                        # Sync exact live balances from Binance API
                        try:
                            diagnose_full_spot_wallet()
                        except Exception:
                            pass
                            
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
                        state["_last_closed_symbol"] = active_symbol
                        state["_last_closed_time"] = time.time()
                        state["_last_exit_price"] = active_current_price
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
        
        # Stablecoin & Pegged Low-Volatility Commodity filter check
        stablecoins_blacklist = {
            "USDT", "USDC", "FDUSD", "TUSD", "BUSD", "DAI", "USDD", "USDE", "RLUSD", "USD1",
            "EUR", "AEUR", "WBTC", "TBTC", "USDS", "USTC", "FRAX", "PYUSD", "USD0", "SNDKB", "SNDK", "USD",
            "PAXG", "XAUT", "XAUt", "GOLD"
        }
        
        # 🚫 BLACKLIST EMPÍRICA: Símbolos que destruyeron capital en 4,924 simulaciones
        # Fuente: Análisis estadístico de trade_memory.json — PROHIBIDO operar estos pares
        toxic_symbols_blacklist = {
            "PEPEUSDT", "PEPE",         # -$8,857,228 (catastrófico)
            "BARDUSDT", "BARD",         # -$23,999
            "APTUSDT", "APT",           # -$16,317
            "PENGUUSDT", "PENGU",       # -$7,027
            "POLUSDT", "POL",           # -$1,074
            "EULUSDT", "EUL",           # -$282
            "BICOUSDT", "BICO",         # -$320
            "KITEUSDT", "KITE",         # -$598
            "EDENUSDT", "EDEN",         # -$359
            "KAITOUSDT", "KAITO",       # -$310
        }
        
        # 🏆 WHITELIST PRIORITARIA: Símbolos con 100% Win Rate o WR >= 65% en historial
        # Estos pares reciben bonus de score +20 si cumplen los filtros base
        priority_whitelist = {
            "BNBUSDT", "BNB",           # 100% WR, +$204
            "2ZUSDT", "2Z",             # 100% WR, +$10
            "HOMEUSDT", "HOME",         # 100% WR, +$1.37
            "XPLUSDT", "XPLUS",         # 66.7% WR, +$659
            "DEXEUSDT", "DEXE",         # 80% WR, +$4.5
            "ATOMUSDT", "ATOM",         # 66.7% WR, +$15
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
            
            # 🛡️ MEJORA C: COOLDOWN INTELIGENTE POR DESCUENTO REAL Y PISO DE SUELO
            last_closed_sym = state.get("_last_closed_symbol")
            last_closed_time = state.get("_last_closed_time", 0)
            last_exit_price = state.get("_last_exit_price", 0.0)
            time_since_last_exit = time.time() - last_closed_time
            
            if best_symbol == last_closed_sym:
                discount_from_exit_pct = ((last_exit_price - current_price) / last_exit_price) * 100.0 if (last_exit_price > 0 and current_price > 0) else 0.0
                
                # Si el activo cayó >= 2.00% respecto a donde salimos, se levanta el cooldown inmediatamente:
                if discount_from_exit_pct >= 2.00 and time_since_last_exit >= 120:
                    print(f"🟢 Cooldown levantado inteligentemente: {best_symbol} con descuento real de -{discount_from_exit_pct:.2f}% (${last_exit_price:.6f} -> ${current_price:.6f}).")
                elif time_since_last_exit < 3600:
                    # 🚫 MEJORA A: Anti-Re-Entry 60 Min (previene el error de ONTUSDT x3)
                    is_stable = True
                    print(f"⛔ Compra rechazada: {best_symbol} en cooldown anti-re-entrada ({time_since_last_exit:.0f}s de los 3600s requeridos). Descuento actual: {discount_from_exit_pct:.2f}%. Evitando over-trading.")
            
            if not is_stable and (sym_clean in stablecoins_blacklist or best_symbol in stablecoins_blacklist):
                is_stable = True
                print(f"⛔ Compra rechazada: {best_symbol} es una stablecoin / activo no volátil.")
            elif not is_stable and (sym_clean in toxic_symbols_blacklist or best_symbol in toxic_symbols_blacklist):
                # 🚫 BLACKLIST EMPÍRICA: Símbolo destruyó capital en 4,924 simulaciones
                is_stable = True
                print(f"☠️ Compra rechazada: {best_symbol} está en la BLACKLIST EMPÍRICA (destruyó capital histórico). PROHIBIDO operar.")
            else:
                # 🏆 WHITELIST PRIORITARIA: Bonus de score para símbolos con WR >= 65% histórico
                if sym_clean in priority_whitelist or best_symbol in priority_whitelist:
                    best_score = min(100, best_score + 20)
                    print(f"⭐ [WHITELIST PRIORITARIA] {best_symbol} tiene historial ganador (WR >= 65%). Bonus score aplicado: {best_score}/100.")

                import multi_timeframe_analyzer
                mtf_res = multi_timeframe_analyzer.analyze_multi_timeframe_candles(best_symbol)
                tf_align = mtf_res.get("timeframe_alignment", {})
                
                # 🏛️ MATRIZ DE CONFLUENCIA DE BASE EN 5 TIMEFRAMES (1m, 2m, 5m, 15m, 1h - MÁXIMO 1H)
                # REGLA SUPREMA: Entrar en el suelo de 1M/2M cuando hay soporte en 15M/1H y FII positivo.
                tf_1m = tf_align.get("1m", "BEARISH")
                tf_2m = tf_align.get("2m", "BEARISH")
                tf_5m = tf_align.get("5m", "BEARISH")
                tf_15m = tf_align.get("15m", "BEARISH")
                tf_1h = tf_align.get("1h", "BEARISH")
                
                is_macro_base = (
                    tf_1h == "BULLISH" or 
                    mtf_res.get("is_yellow_arrow_1h") or 
                    mtf_res.get("rsi_1h", 50) <= 55.0 or 
                    mtf_res.get("range_position_1h", 0.5) <= 0.50 or 
                    mtf_res.get("is_vwap_floor_rebound") or
                    mtf_res.get("is_bullish_divergence")
                )
                is_structural_15m_base = (
                    tf_15m == "BULLISH" or 
                    mtf_res.get("is_yellow_arrow_pivot") or 
                    mtf_res.get("is_ma7_above_ma25_upward") or 
                    mtf_res.get("is_cetus_rocket_pattern") or
                    mtf_res.get("is_ground_zero_micro_ignition")
                )
                tf_10s = tf_align.get("10s", "BEARISH")
                tf_30s = tf_align.get("30s", "BEARISH")
                fii = mtf_res.get("fii_score", 0)
                
                # 🎯 MEJORA 2: Gatillo de Doble Ignición Sub-Minuto Obligatorio
                has_dual_sub_minute_ignition = bool(
                    (tf_10s == "BULLISH" and tf_30s == "BULLISH") or
                    (tf_10s == "BULLISH" and tf_1m == "BULLISH" and mtf_res.get("vol_surge_10s", 1.0) >= 1.2) or
                    (fii >= 60 and tf_10s == "BULLISH")
                )
                
                # 🚫 MEJORA 4: Veto de Sangrado Activo en Sub-Minuto
                is_sub_minute_bleeding = bool(
                    (tf_10s == "BEARISH" and tf_30s == "BEARISH" and tf_1m == "BEARISH") and
                    not mtf_res.get("is_bullish_divergence") and
                    fii < 65
                )
                
                if not is_macro_base:
                    is_stable = True
                    print(f"⛔ Compra rechazada: {best_symbol} descalificado por Macro 1H sin soporte (1H: {tf_1h}, RSI 1H: {mtf_res.get('rsi_1h')}, Canal 1H: {mtf_res.get('range_position_1h')}). Exige base macro.")
                elif not is_structural_15m_base:
                    is_stable = True
                    print(f"⛔ Compra rechazada: {best_symbol} descalificado por falta de estructura en 15M (15M: {tf_15m}, RSI: {mtf_res.get('rsi_15m')}). Exige rebote o soporte en 15M.")
                elif is_sub_minute_bleeding:
                    is_stable = True
                    print(f"⛔ Compra rechazada: {best_symbol} bloqueado por VETO DE SANGRADO SUB-MINUTO (10s: DN, 30s: DN, 1M: DN). Esperando freno.")
                elif not has_dual_sub_minute_ignition and fii < 60:
                    is_stable = True
                    print(f"⛔ Compra rechazada: {best_symbol} en base pero esperando GATILLO DE DOBLE IGNICIÓN (10s: {tf_10s}, 30s: {tf_30s}, FII: {fii}/100). Exige 10s+30s verdes.")
                elif mtf_res.get("is_overextended_15m"):
                    is_stable = True
                    print(f"⛔ Compra rechazada: {best_symbol} rechazado por vela sobre-extendida en la cima ({mtf_res.get('overextension_reason')}).")
                else:
                    import orderbook_analyzer
                    ob_info = orderbook_analyzer.fetch_orderbook_depth(best_symbol, limit=20)
                    
                    # 🚫 MEJORA B: Veto RSI 4H Sobreextendido (> 68) — previene el error de WLFIUSDT
                    rsi_4h = mtf_res.get("rsi_4h", 50.0)
                    if rsi_4h >= 68.0:
                        is_stable = True
                        print(f"⛔ Compra rechazada: {best_symbol} con RSI 4H sobreextendido ({rsi_4h:.1f} >= 68.0). Riesgo alto de agotamiento macro.")
                    elif ob_info.get("spread_pct", 0.0) > 0.75:
                        is_stable = True
                        print(f"⛔ Compra rechazada: {best_symbol} descalificado por Spread elevado ({ob_info.get('spread_pct'):.3f}% > 0.75%). Evitando deslizamiento de precio.")
                    else:
                        vol_1m_now = mtf_res.get("vol_surge_1m", 1.0)
                        vol_2m_now = mtf_res.get("vol_surge_2m", 1.0)
                        vol_15m_now = mtf_res.get("vol_surge_15m", 1.0)
                        is_30s_burst = mtf_res.get("is_30s_micro_burst", False)
                        vol_acc = mtf_res.get("vol_acceleration", 1.0)
                        is_pre_pump = mtf_res.get("is_pre_pump_signal", False)
                        is_yellow = mtf_res.get("is_yellow_arrow_pivot", False)
                        is_obv_acc = mtf_res.get("is_obv_accumulating", False)
                        is_ema_cross = mtf_res.get("is_ema_golden_cross", False)
                        
                        # ═══════════════════════════════════════════════════════════
                        # 🚀 FILTRO CUÁNTICO DE VOLUMEN REAL Y MOMENTUM GANADOR:
                        # PROHIBIDO comprar monedas dormidas o sin combustible (Volumen < 0.60x).
                        # Exige aceleración institucional real (OBV / VolSurge / EMA Cross) para garantizar despegue inmediato.
                        # ═══════════════════════════════════════════════════════════
                        has_real_volume = (vol_15m_now >= 0.60) or (vol_2m_now >= 0.75) or (vol_1m_now >= 0.90) or is_obv_acc or is_pre_pump or (vol_acc >= 1.5)
                        has_micro_thrust = (vol_2m_now >= 0.50) or (vol_1m_now >= 0.80) or is_30s_burst or is_pre_pump or is_obv_acc or is_ema_cross
                        
                        if not has_real_volume:
                            is_stable = True
                            print(f"⛔ Compra rechazada: {best_symbol} descartado por FALTA DE VOLUMEN REAL (15m={vol_15m_now:.2f}x, 2m={vol_2m_now:.2f}x, OBV={is_obv_acc}). Prohibido comprar monedas dormidas.")
                        elif not has_micro_thrust:
                            is_stable = True
                            print(f"⛔ Compra rechazada: {best_symbol} descartado por falta de empuje micro (1m={vol_1m_now:.2f}x, 2m={vol_2m_now:.2f}x, 30sBurst={is_30s_burst}). Exige micro-aceleración de entrada.")
                        elif ob_info.get("bid_dominance_pct", 50.0) < 44.0:
                            # 🧹 MEJORA D: Unificado en un solo umbral del 44% (elimina redundancia de 42%/50%)
                            is_stable = True
                            print(f"⛔ Compra rechazada: {best_symbol} descartado por Bids insuficientes ({ob_info.get('bid_dominance_pct'):.1f}% < 44.0%). Exige mayoría compradora en libro.")
                        else:
                            arrow_lbl = " 🎯 [PATRÓN FLECHAS AMARILLAS 15M PIVOT REBOUND]" if is_yellow else ""
                            print(f"📊 Análisis Multi-Temporal & Libro de Órdenes {best_symbol}{arrow_lbl}: Score MTF={mtf_res.get('multi_tf_score')}/100 | Spread={ob_info.get('spread_pct')}% (<=0.75% OK) | Bids={ob_info.get('bid_dominance_pct')}% (>=44% OK) | RSI4H={rsi_4h:.1f} | 🚀 Turbinas: 15m={vol_15m_now:.2f}x, 2m={vol_2m_now:.2f}x, 1m={vol_1m_now:.2f}x, OBV={is_obv_acc}, EMA={is_ema_cross}")
                
        if bias_ok and not is_stable:
            # 1. LONG Entry Signal (Operates with 100% of available USDT, strictly requires Score >= 55 Setup A+)
            min_required_score = max(55, real_long_score) if not is_learned_signal else 55
            if best_symbol and not is_bearish and best_score >= min_required_score and usdt_free >= 5.1:
                trigger_reason = "AUTO-APRENDIZAJE A+" if is_learned_signal else f"Score {real_long_score}+"
                print(f"🚀 SEÑAL ALCISTA (LONG) ({best_symbol} @ {best_score} Pts - {trigger_reason}). Comprando con ${usdt_free:.1f} USDT (100% Capital)...")
                buy_res = execute_real_spot_market_buy(best_symbol, usdt_free)
                if isinstance(buy_res, dict) and "orderId" in buy_res:
                    time.sleep(0.5)
                    exact_entry, exact_cost, exact_qty = get_exact_real_entry_price(best_symbol)
                    qty = exact_qty if exact_qty else float(buy_res.get("executedQty", 0))
                    cum_quote = exact_cost if exact_cost else float(buy_res.get("cummulativeQuoteQty", 0))
                    if exact_entry:
                        actual_entry_price = exact_entry
                        actual_cost = exact_cost
                    elif qty > 0 and cum_quote > 0:
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
                        "break_even": False,
                        "highest_price": actual_entry_price,
                        "phase": 1,
                        "vol_surge": mtf_res.get("vol_surge_2m", 1.0) if 'mtf_res' in locals() else 1.0,
                        "entry_time_ms": int(time.time() * 1000),
                        "atr_pct_15m": mtf_res.get("atr_pct_15m", 0.30) if 'mtf_res' in locals() else 0.30,
                        "ma25_5m": mtf_res.get("ma25_5m", current_price) if 'mtf_res' in locals() else current_price
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
