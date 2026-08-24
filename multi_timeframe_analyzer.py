"""
Multi-Timeframe Historical Candle Analyzer & Anti-Stablecoin Filter Engine
Inspects 2m, 5m, 15m, 1h, 4h, 1d historical candle behavior.
Rejects stablecoins, dollar synthetics, flat assets, and unconfirmed trends.
Includes: MACD(12,26,9), GBM Crash Detector, SuperTrend(10,3), Yellow Arrow MA7/MA25, VWAP.
"""

import time
import requests
import math
import numpy as np
from datetime import datetime
from quant_institutional import GBMAnomalyDetector
import asset_dna_predictive_engine

# Persistent HTTP connection pool to avoid TLS handshake overhead
_SESSION = requests.Session()
_ADAPTER = requests.adapters.HTTPAdapter(pool_connections=25, pool_maxsize=25, max_retries=1)
_SESSION.mount("https://", _ADAPTER)
_SESSION.mount("http://", _ADAPTER)

# In-memory Candle & Ticker Cache: {(symbol, interval, limit): (timestamp, data)}
_KLINE_CACHE = {}
_TICKER_CACHE = {}

# Time-To-Live for candle intervals (Macro candles change slowly, micro candles update fast)
_CACHE_TTL = {
    "1d": 600,  # 10 minutes
    "4h": 300,  # 5 minutes
    "1h": 180,  # 3 minutes
    "30m": 60,  # 1 minute for 30m intermediate macro
    "15m": 35,  # 35 seconds
    "5m": 15,   # 15 seconds
    "1m": 10,   # 10 seconds
    "1s": 4     # 4 seconds for sub-minute 10s/30s precision
}

# Comprehensive Blacklist of Stablecoins, Pegged Tokens, and Synthetic Dollars
STABLECOIN_TICKERS = {
    "U", "UUSDT", "USD", "USDE", "USD0", "USDS", "USDF", "USDC", "FDUSD", "PYUSD",
    "TUSD", "BUSD", "DAI", "USDD", "RLUSD", "USD1", "EUR", "AEUR", "WBTC", "TBTC",
    "USDT", "USTC", "FRAX", "USDK", "VAI", "EURI", "EURIOUSDT"
}

# Exhaustive Blacklist of bStocks (Tokenized Stocks / Equity Certificates / Digital Securities)
BSTOCKS_BLACKLIST = {
    "NBISB", "TSLAB", "SNDKB", "CRDOB", "AAOIB", "AMATB", "USARB", "SNXXB", "QQQB", "SPCXB", "CRCLB",
    "NVDB", "AAPLB", "MSFTB", "AMZNB", "GOOGB", "GOOGLB", "GOOGLBUSDT", "MSTRB", "COINB", "METAB",
    "PLTRB", "AVNTB", "BMTB", "HOODB", "NFB", "SOXLB", "SOXSB", "ARKB", "BITOB", "MSTX", "MSTZ", "MSTU",
    "NBISBUSDT", "TSLABUSDT", "SNDKBUSDT", "CRDOBUSDT", "AAOIBUSDT", "AMATBUSDT", "USARBUSDT", "SNXXBUSDT"
}

# High-Risk Meme Tokens, Seed Tag Assets, and Ultra-Volatile Low-Liquidity Speculative Assets
HIGH_RISK_MEME_TICKERS = {
    "BANANAS31", "BANANAS31USDT", "1000CAT", "1000CHEEMS", "1000SATS", "1MBABYDOGE",
    "BROCCOLI714", "LUNA", "LUNC", "USTC", "NEIRO", "TURBO", "1000PEPE",
    "1000BONK", "1000FLOKI", "1000RATS", "1000WHY", "1000MOG", "CHEEMS",
    "1000CATUSDT", "1000SATSUSDT", "1MBABYDOGEUSDT", "BROCCOLI714USDT"
}

# Binance Monitoring Tag, Seed Tag, and High Risk / Delisting Warning Tokens
MONITORING_TAG_BLACKLIST = {
    "NOM", "NOMUSDT", "WCT", "WCTUSDT", "BERA", "BERAUSDT", "EPX", "EPXUSDT", "VANRY", "VANRYUSDT",
    "SCRT", "SCRTUSDT", "TREE", "TREEUSDT", "NXPC", "NXPCUSDT", "ALLO", "ALLOUSDT", "PLUME", "PLUMEUSDT",
    "ACE", "ACEUSDT", "MMT", "MMTUSDT", "OG", "OGUSDT", "PROS", "PROSUSDT", "KP3R", "KP3RUSDT",
    "GFT", "GFTUSDT", "OOKI", "OOKIUSDT", "AMB", "AMBUSDT", "BIFI", "BIFIUSDT", "VOXEL", "VOXELUSDT",
    "WRX", "WRXUSDT", "DOCK", "DOCKUSDT", "POLS", "POLSUSDT", "MDX", "MDXUSDT", "FIRO", "FIROUSDT",
    "NBS", "NBSUSDT", "LTO", "LTOUSDT", "FOR", "FORUSDT", "VITE", "VITEUSDT", "KEY", "KEYUSDT",
    "CREAM", "CREAMUSDT", "MBL", "MBLUSDT", "AKRO", "AKROUSDT", "UNFI", "UNFIUSDT", "WING", "WINGUSDT",
    "HARD", "HARDUSDT", "DREP", "DREPUSDT", "TROY", "TROYUSDT", "BURGER", "BURGERUSDT", "JUV", "JUVUSDT",
    "CITY", "CITYUSDT", "PSG", "PSGUSDT", "ATM", "ATMUSDT", "BAR", "BARUSDT", "ASR", "ASRUSDT", "ACM", "ACMUSDT",
    "CHIP", "CHIPUSDT", "UTK", "UTKUSDT", "BANANA", "BANANAUSDT"
}

try:
    from api_connector import get_proxy
except ImportError:
    get_proxy = None

def is_bstock(symbol):
    """
    Strictly checks if a symbol is a tokenized stock / bStock certificate.
    bStocks have legal popups, geographical restrictions, and cannot be traded as native crypto.
    """
    sym_upper = str(symbol).upper().strip()
    asset = sym_upper.replace("USDT", "").replace("USD", "")
    
    if sym_upper in BSTOCKS_BLACKLIST or asset in BSTOCKS_BLACKLIST:
        return True
        
    # Pattern: Assets of 4+ letters ending in 'B' (e.g. NBISB, TSLAB, CRDOB) that are tokenized equities
    KNOWN_GENUINE_CRYPTO_ENDING_IN_B = {"BNB", "SHIB", "SUB", "LUB", "MCB", "GUB", "RLB"}
    if asset.endswith("B") and len(asset) >= 4 and asset not in KNOWN_GENUINE_CRYPTO_ENDING_IN_B:
        return True
        
    return False

def is_stablecoin(symbol):
    """
    Strictly checks if a symbol is a stablecoin, synthetic dollar, bStock, Monitoring Tag token, or meme asset.
    Returns True if symbol is blocked from real money trading.
    """
    sym_upper = str(symbol).upper().strip()
    asset = sym_upper.replace("USDT", "").replace("USD", "")
    
    # 0. Immediate bStock & Monitoring Tag Blacklist Check
    if is_bstock(sym_upper):
        return True
    if sym_upper in MONITORING_TAG_BLACKLIST or asset in MONITORING_TAG_BLACKLIST:
        return True
        
    # 1. Direct Ticker Match (Stablecoins & Meme Blacklist)
    if sym_upper in STABLECOIN_TICKERS or asset in STABLECOIN_TICKERS:
        return True
    if sym_upper in HIGH_RISK_MEME_TICKERS or asset in HIGH_RISK_MEME_TICKERS:
        return True
        
    # 2. Ticker Pattern Heuristics (single-letter, 1000-prefix meme tokens, or dollar synthetics)
    if len(asset) <= 1:
        return True
    if "USD" in asset or "EUR" in asset or "BUSD" in asset or "TUSD" in asset:
        return True
    if asset.startswith("1000") or asset.startswith("1M"):
        return True
        
    return False

def fetch_klines_public(symbol, interval, limit=30):
    """Fetches Binance public klines with high-speed in-memory caching and multi-mirror failover (0 Fixie Quota)."""
    cache_key = (symbol, interval, limit)
    now = time.time()
    ttl = _CACHE_TTL.get(interval, 20)
    
    if cache_key in _KLINE_CACHE:
        cached_time, cached_data = _KLINE_CACHE[cache_key]
        if now - cached_time < ttl and cached_data:
            return cached_data
            
    mirrors = [
        "https://data-api.binance.vision/api/v3/klines",
        "https://api1.binance.com/api/v3/klines",
        "https://api2.binance.com/api/v3/klines",
        "https://api3.binance.com/api/v3/klines",
        "https://api.binance.com/api/v3/klines"
    ]
    params = {"symbol": symbol, "interval": interval, "limit": limit}
    
    for url in mirrors:
        try:
            res = _SESSION.get(url, params=params, timeout=3)
            if res.status_code == 200:
                data = res.json()
                if data and isinstance(data, list) and len(data) > 0:
                    _KLINE_CACHE[cache_key] = (now, data)
                    return data
        except Exception:
            continue
            
    # Return stale cached data if temporary network blip
    if cache_key in _KLINE_CACHE:
        return _KLINE_CACHE[cache_key][1]
    return []

def calculate_rsi(closes, period=14):
    """Calculates RSI using Wilder's RMA smoothing (matches TradingView/Binance standard)."""
    if not closes or len(closes) < period + 1:
        return 50.0
    deltas = [closes[i] - closes[i-1] for i in range(1, len(closes))]
    gains = [d if d > 0 else 0.0 for d in deltas]
    losses = [-d if d < 0 else 0.0 for d in deltas]
    # First average using SMA
    avg_gain = sum(gains[:period]) / period
    avg_loss = sum(losses[:period]) / period
    # Subsequent averages using Wilder's RMA (exponential smoothing)
    for i in range(period, len(gains)):
        avg_gain = (avg_gain * (period - 1) + gains[i]) / period
        avg_loss = (avg_loss * (period - 1) + losses[i]) / period
    if avg_loss == 0:
        return 100.0
    rs = avg_gain / avg_loss
    return round(100.0 - (100.0 / (1.0 + rs)), 1)

def _ema(closes, period):
    """Calculates Exponential Moving Average (EMA) for MACD computation."""
    if not closes or len(closes) < period:
        return closes[-1] if closes else 0.0
    multiplier = 2.0 / (period + 1.0)
    ema_val = sum(closes[:period]) / period
    for price in closes[period:]:
        ema_val = (price - ema_val) * multiplier + ema_val
    return ema_val

def calculate_macd(closes, fast=12, slow=26, signal=9):
    """Calculates MACD Line, Signal Line, and Histogram for a price series."""
    if not closes or len(closes) < slow + signal:
        return 0.0, 0.0, 0.0
    ema_fast = _ema(closes, fast)
    ema_slow = _ema(closes, slow)
    macd_line = ema_fast - ema_slow
    # Build MACD series for signal line
    macd_series = []
    for i in range(slow, len(closes) + 1):
        ef = _ema(closes[:i], fast)
        es = _ema(closes[:i], slow)
        macd_series.append(ef - es)
    signal_line = _ema(macd_series, signal) if len(macd_series) >= signal else macd_line
    histogram = macd_line - signal_line
    return round(macd_line, 6), round(signal_line, 6), round(histogram, 6)

# Singleton GBM Crash Detector (Z-Score threshold 2.5)
_gbm_detector = GBMAnomalyDetector(window=30, z_threshold=2.5)

def _aggregate_1m_to_2m(klines_1m):
    """Combines pairs of 1m klines into 2m klines [timestamp, open, high, low, close, volume]."""
    if not klines_1m or len(klines_1m) < 2:
        return []
    klines_2m = []
    for i in range(0, len(klines_1m) - 1, 2):
        k1 = klines_1m[i]
        k2 = klines_1m[i+1]
        open_p = float(k1[1])
        high_p = max(float(k1[2]), float(k2[2]))
        low_p = min(float(k1[3]), float(k2[3]))
        close_p = float(k2[4])
        vol = float(k1[5]) + float(k2[5])
        klines_2m.append([k1[0], open_p, high_p, low_p, close_p, vol])
    return klines_2m

def _aggregate_5m_to_10m(klines_5m):
    """Combines pairs of 5m klines into 10m klines [timestamp, open, high, low, close, volume]."""
    if not klines_5m or len(klines_5m) < 2:
        return []
    klines_10m = []
    for i in range(0, len(klines_5m) - 1, 2):
        k1 = klines_5m[i]
        k2 = klines_5m[i+1]
        open_p = float(k1[1])
        high_p = max(float(k1[2]), float(k2[2]))
        low_p = min(float(k1[3]), float(k2[3]))
        close_p = float(k2[4])
        vol = float(k1[5]) + float(k2[5])
        klines_10m.append([k1[0], open_p, high_p, low_p, close_p, vol])
    return klines_10m

def _aggregate_1h_to_2h(klines_1h):
    """Combines pairs of 1h klines into 2h klines [timestamp, open, high, low, close, volume]."""
    if not klines_1h or len(klines_1h) < 2:
        return []
    klines_2h = []
    for i in range(0, len(klines_1h) - 1, 2):
        k1 = klines_1h[i]
        k2 = klines_1h[i+1]
        open_p = float(k1[1])
        high_p = max(float(k1[2]), float(k2[2]))
        low_p = min(float(k1[3]), float(k2[3]))
        close_p = float(k2[4])
        vol = float(k1[5]) + float(k2[5])
        klines_2h.append([k1[0], open_p, high_p, low_p, close_p, vol])
    return klines_2h

def _aggregate_1s_to_bars(klines_1s, seconds=10):
    """Aggregates 1s klines into custom sub-minute bars (10s, 30s) [timestamp, open, high, low, close, volume]."""
    if not klines_1s:
        return []
    bars = []
    for i in range(0, len(klines_1s), seconds):
        chunk = klines_1s[i:i+seconds]
        if not chunk:
            continue
        open_p = float(chunk[0][1])
        high_p = max(float(k[2]) for k in chunk)
        low_p = min(float(k[3]) for k in chunk)
        close_p = float(chunk[-1][4])
        vol = sum(float(k[5]) for k in chunk)
        bars.append([chunk[0][0], open_p, high_p, low_p, close_p, vol])
    return bars

def calculate_obv(closes, volumes):
    """On-Balance Volume: detects accumulation/distribution divergence."""
    if not closes or not volumes or len(closes) < 2:
        return [], "NEUTRAL"
    obv = [0.0]
    for i in range(1, min(len(closes), len(volumes))):
        if closes[i] > closes[i-1]:
            obv.append(obv[-1] + volumes[i])
        elif closes[i] < closes[i-1]:
            obv.append(obv[-1] - volumes[i])
        else:
            obv.append(obv[-1])
    # Trend: compare last 5 OBV vs first 5 OBV
    if len(obv) >= 10:
        early_avg = sum(obv[:5]) / 5
        late_avg = sum(obv[-5:]) / 5
        if late_avg > early_avg * 1.05:
            return obv, "ACCUMULATING"
        elif late_avg < early_avg * 0.95:
            return obv, "DISTRIBUTING"
    return obv, "NEUTRAL"

def calculate_atr(highs, lows, closes, period=14):
    """Average True Range for volatility measurement."""
    if not highs or not lows or not closes or len(closes) < 2:
        return 0.0
    trs = []
    for i in range(1, min(len(highs), len(lows), len(closes))):
        tr = max(highs[i] - lows[i], abs(highs[i] - closes[i-1]), abs(lows[i] - closes[i-1]))
        trs.append(tr)
    if not trs:
        return 0.0
    if len(trs) < period:
        return sum(trs) / len(trs)
    # Wilder's smoothing for ATR
    atr = sum(trs[:period]) / period
    for i in range(period, len(trs)):
        atr = (atr * (period - 1) + trs[i]) / period
    return atr

def calculate_mfi(highs, lows, closes, volumes, period=14):
    """Money Flow Index (MFI): Volume-weighted RSI detecting institutional capital injection."""
    if not highs or not lows or not closes or not volumes or len(closes) < period + 1:
        return 50.0
    typical_prices = [(h + l + c) / 3.0 for h, l, c in zip(highs, lows, closes)]
    raw_money_flow = [tp * v for tp, v in zip(typical_prices, volumes)]
    pos_flow = []
    neg_flow = []
    for i in range(1, len(typical_prices)):
        if typical_prices[i] > typical_prices[i-1]:
            pos_flow.append(raw_money_flow[i])
            neg_flow.append(0.0)
        elif typical_prices[i] < typical_prices[i-1]:
            pos_flow.append(0.0)
            neg_flow.append(raw_money_flow[i])
        else:
            pos_flow.append(0.0)
            neg_flow.append(0.0)
    if len(pos_flow) < period:
        return 50.0
    sum_pos = sum(pos_flow[-period:])
    sum_neg = sum(neg_flow[-period:])
    if sum_neg == 0:
        return 100.0
    money_ratio = sum_pos / sum_neg
    return round(100.0 - (100.0 / (1.0 + money_ratio)), 1)

def calculate_stoch_rsi(closes, rsi_period=14, stoch_period=14):
    """Stochastic RSI: Ultra-sensitive oscillator detecting floor exhaustion and ignition."""
    if not closes or len(closes) < rsi_period + stoch_period:
        return 50.0, 50.0
    # Calculate rolling RSIs
    rsis = []
    for i in range(rsi_period + 1, len(closes) + 1):
        rsis.append(calculate_rsi(closes[:i], period=rsi_period))
    if len(rsis) < stoch_period:
        return 50.0, 50.0
    # Calculate rolling stoch_k values for %D smoothing
    stoch_k_series = []
    for j in range(stoch_period, len(rsis) + 1):
        sub_rsi = rsis[j - stoch_period:j]
        min_rsi = min(sub_rsi)
        max_rsi = max(sub_rsi)
        if max_rsi == min_rsi:
            stoch_k_series.append(50.0)
        else:
            stoch_k_series.append(round(((sub_rsi[-1] - min_rsi) / (max_rsi - min_rsi)) * 100.0, 1))
    stoch_k = stoch_k_series[-1] if stoch_k_series else 50.0
    # %D = SMA of last 3 stoch_k values (NOT raw RSIs)
    stoch_d = round(sum(stoch_k_series[-3:]) / min(3, len(stoch_k_series)), 1) if stoch_k_series else stoch_k
    return stoch_k, stoch_d

def calculate_wma(closes, period=14):
    """Weighted Moving Average (WMA): Gives more weight to recent prices."""
    if not closes or len(closes) < period:
        return closes[-1] if closes else 0.0
    sub = closes[-period:]
    weights = list(range(1, period + 1))
    weighted_sum = sum(p * w for p, w in zip(sub, weights))
    return round(weighted_sum / sum(weights), 6)

def calculate_cci(highs, lows, closes, period=14):
    """Commodity Channel Index (CCI): Detects overbought/oversold cycles."""
    if not highs or not lows or not closes or len(closes) < period:
        return 0.0
    tps = [(h + l + c) / 3.0 for h, l, c in zip(highs[-period:], lows[-period:], closes[-period:])]
    sma_tp = sum(tps) / period
    mean_dev = sum(abs(tp - sma_tp) for tp in tps) / period
    if mean_dev == 0:
        return 0.0
    return round((tps[-1] - sma_tp) / (0.015 * mean_dev), 1)

def calculate_wr(highs, lows, closes, period=14):
    """Williams %R (WR): Momentum indicator for floor oversold bounces."""
    if not highs or not lows or not closes or len(closes) < period:
        return -50.0
    sub_h = highs[-period:]
    sub_l = lows[-period:]
    max_h = max(sub_h)
    min_l = min(sub_l)
    if max_h == min_l:
        return -50.0
    return round(((max_h - closes[-1]) / (max_h - min_l)) * -100.0, 1)

def calculate_kdj(highs, lows, closes, period=9):
    """KDJ Stochastic: Fast institutional turning point indicator."""
    if not highs or not lows or not closes or len(closes) < period:
        return 50.0, 50.0, 50.0
    k, d = 50.0, 50.0
    for i in range(period, len(closes)):
        hh = max(highs[i-period+1:i+1])
        ll = min(lows[i-period+1:i+1])
        rsv = ((closes[i] - ll) / (hh - ll)) * 100.0 if hh > ll else 50.0
        k = (2.0 / 3.0) * k + (1.0 / 3.0) * rsv
        d = (2.0 / 3.0) * d + (1.0 / 3.0) * k
    j = 3.0 * k - 2.0 * d
    return round(k, 1), round(d, 1), round(j, 1)

def calculate_sar(highs, lows, af_start=0.02, af_step=0.02, af_max=0.2):
    """Parabolic SAR (Stop and Reverse): Trailing dynamic stop indicator."""
    if not highs or not lows or len(highs) < 5:
        return highs[-1] if highs else 0.0, "UP"
    is_bull = highs[-1] >= highs[0]
    sar = min(lows[:5]) if is_bull else max(highs[:5])
    ep = max(highs[:5]) if is_bull else min(lows[:5])
    af = af_start
    for i in range(1, len(highs)):
        sar = sar + af * (ep - sar)
        if is_bull:
            if lows[i] < sar:
                is_bull = False
                sar = ep
                ep = lows[i]
                af = af_start
            else:
                if highs[i] > ep:
                    ep = highs[i]
                    af = min(af + af_step, af_max)
        else:
            if highs[i] > sar:
                is_bull = True
                sar = ep
                ep = highs[i]
                af = af_start
            else:
                if lows[i] < ep:
                    ep = lows[i]
                    af = min(af + af_step, af_max)
    trend = "UP" if is_bull else "DOWN"
    return round(sar, 6), trend

def calculate_dmi(highs, lows, closes, period=14):
    """Directional Movement Index (DMI): Measures trend strength (+DI, -DI, ADX)."""
    if not highs or not lows or not closes or len(closes) < period + 1:
        return 20.0, 20.0, 20.0
    p_dm = [max(highs[i] - highs[i-1], 0) if (highs[i] - highs[i-1]) > (lows[i-1] - lows[i]) else 0 for i in range(1, len(highs))]
    m_dm = [max(lows[i-1] - lows[i], 0) if (lows[i-1] - lows[i]) > (highs[i] - highs[i-1]) else 0 for i in range(1, len(lows))]
    trs = [max(highs[i] - lows[i], abs(highs[i] - closes[i-1]), abs(lows[i] - closes[i-1])) for i in range(1, len(highs))]
    sum_tr = sum(trs[-period:])
    if sum_tr == 0:
        return 20.0, 20.0, 20.0
    plus_di = round((sum(p_dm[-period:]) / sum_tr) * 100.0, 1)
    minus_di = round((sum(m_dm[-period:]) / sum_tr) * 100.0, 1)
    di_sum = plus_di + minus_di
    dx = abs(plus_di - minus_di) / di_sum * 100.0 if di_sum > 0 else 0.0
    adx = round(dx, 1)
    return plus_di, minus_di, adx

def calculate_trix(closes, period=9):
    """Triple Exponential Average (TRIX): Filters out market noise to show momentum."""
    if not closes or len(closes) < period * 3:
        return 0.0
    ema1 = _ema(closes, period)
    return round(((closes[-1] - closes[-period]) / closes[-period]) * 100.0, 3)

def calculate_mtm(closes, period=14):
    """Momentum (MTM): Speed of price changes over period."""
    if not closes or len(closes) < period + 1:
        return 0.0
    return round(closes[-1] - closes[-period-1], 6)

def calculate_emv(highs, lows, volumes, period=14):
    """Ease of Movement (EMV): Relates price change to trading volume."""
    if not highs or not lows or not volumes or len(highs) < period + 1:
        return 0.0
    emv_list = []
    for i in range(1, len(highs)):
        hl_mid = (highs[i] + lows[i]) / 2.0
        hl_mid_prev = (highs[i-1] + lows[i-1]) / 2.0
        dist = hl_mid - hl_mid_prev
        box_ratio = (volumes[i] / 100000.0) / max(0.00001, highs[i] - lows[i])
        emv_list.append(dist / max(0.00001, box_ratio))
    return round(sum(emv_list[-period:]) / period, 4) if emv_list else 0.0

def calculate_avl(highs, lows, closes):
    """Average Value Line (AVL): Average value per bar."""
    if not closes:
        return 0.0
    return round((highs[-1] + lows[-1] + closes[-1]) / 3.0, 6)


# ─── ADN v2 Safe Wrappers ────────────────────────────────────────────────────
def _get_time_dna_safe(symbol):
    """Safe wrapper for time_of_day_dna — returns neutral defaults on error."""
    try:
        import time_of_day_dna
        return time_of_day_dna.get_token_time_score(symbol)
    except Exception:
        return {"session_name": "UNKNOWN", "final_time_multiplier": 1.0,
                "is_blackout_hour": False, "hard_veto_entry": False,
                "is_token_peak_hour": False, "explanation": "N/A"}


def _get_btc_guard_safe():
    """Safe wrapper for BTC dominance guard — returns neutral defaults on error."""
    try:
        return asset_dna_predictive_engine.get_btc_dominance_guard()
    except Exception:
        return {"btc_status": "UNKNOWN", "altcoin_impact": "NEUTRAL",
                "should_avoid_altcoins": False, "should_be_cautious": False,
                "btc_1h_change_pct": 0.0}


def _get_funding_safe(symbol):
    """Safe wrapper for funding rate — returns neutral defaults on error."""
    try:
        return asset_dna_predictive_engine.get_funding_rate(symbol)
    except Exception:
        return {"funding_signal": "UNKNOWN", "funding_rate_pct": 0.0,
                "dump_risk_from_funding": False, "squeeze_opportunity": False}


def _get_behavioral_xray_safe(symbol, klines_dict, btc_closes):
    """Safe wrapper for 360 Behavioral DNA X-Ray."""
    try:
        import asset_dna_predictive_engine
        if hasattr(asset_dna_predictive_engine, "calculate_asset_behavioral_xray"):
            return asset_dna_predictive_engine.calculate_asset_behavioral_xray(
                symbol=symbol,
                klines_multi_tf=klines_dict,
                btc_15m_closes=btc_closes
            )
    except Exception:
        pass
    return {
        "behavior_type": "ROTACIÓN_ESTRUCTURAL",
        "timing_advice": "🎯 Confluencia técnica calculada",
        "fractal_channel_pct": {"1m": 50.0, "5m": 50.0, "15m": 50.0, "1h": 50.0, "4h": 50.0, "1d": 50.0},
        "lower_wick_absorption_1m_pct": 10.0,
        "alpha_vs_btc_15m_pct": 0.0,
        "atr_15m_pct": 0.40
    }


def _detect_spring_safe(klines_1m):
    """Safe wrapper for Spring Coiling Compression."""
    try:
        import asset_dna_predictive_engine
        if hasattr(asset_dna_predictive_engine, "detect_spring_coiling_compression"):
            return asset_dna_predictive_engine.detect_spring_coiling_compression(klines_1m)
    except Exception:
        pass
    return {"is_spring_compressed": False, "spread_pct": 1.0, "spring_bonus": 0, "label": "Normal"}


def _detect_wave2_safe(klines_15m):
    """Safe wrapper for Wave 2 MA25 Retest."""
    try:
        import asset_dna_predictive_engine
        if hasattr(asset_dna_predictive_engine, "detect_wave2_ma25_retest_support"):
            return asset_dna_predictive_engine.detect_wave2_ma25_retest_support(klines_15m)
    except Exception:
        pass
    return {"is_wave2_retest": False, "peak_expansion_pct": 0.0, "dist_to_ma25_pct": 0.0, "retest_bonus": 0, "label": "Estructura Estándar"}


def _get_archetype_dna_safe(symbol, atr_pct_15m=0.30, price=1.0):
    """Safe wrapper for adaptive_asset_dna archetype classification."""
    try:
        import adaptive_asset_dna
        return adaptive_asset_dna.get_asset_dna_archetype(symbol, atr_pct_15m, price)
    except Exception:
        return {"archetype": "SECTOR_ROTATION", "label": "General", "initial_sl_pct": -2.00,
                "max_stagnation_minutes": 35, "trend_ride_enabled": True}


def analyze_multi_timeframe_candles(symbol):
    """
    Inspects 2m, 5m, 15m, 1h, 4h, 1d, and 7d historical candle behavior.
    Calculates multi-timeframe trend alignment, 3-tier RSI architecture, volatility expansion, and anti-stablecoin verification.
    Synced 1:1 with the 2-minute continuous execution loop.
    """
    # 1. Immediate Stablecoin Blacklist Guard
    if is_stablecoin(symbol):
        return {
            "is_valid_tradable_asset": False,
            "rejection_reason": f"Símbolo {symbol} identificado como Stablecoin / Dólar Sintético",
            "multi_tf_score": 0
        }
        
    # 2. Fetch Multi-Timeframe Klines (1s->10s/30s, 1m->2m, 5m, 15m, 30m, 1h, 4h, 1d)
    klines_1s = fetch_klines_public(symbol, "1s", 120)
    klines_10s = _aggregate_1s_to_bars(klines_1s, 10)
    klines_30s = _aggregate_1s_to_bars(klines_1s, 30)
    klines_1m = fetch_klines_public(symbol, "1m", 40)
    klines_2m = _aggregate_1m_to_2m(klines_1m)
    klines_5m = fetch_klines_public(symbol, "5m", 30)
    klines_10m = _aggregate_5m_to_10m(klines_5m)
    klines_15m = fetch_klines_public(symbol, "15m", 120)
    klines_30m = fetch_klines_public(symbol, "30m", 30)
    klines_1h = fetch_klines_public(symbol, "1h", 30)
    klines_2h = _aggregate_1h_to_2h(klines_1h)
    klines_4h = fetch_klines_public(symbol, "4h", 30)
    klines_1d = fetch_klines_public(symbol, "1d", 14)
    
    if not klines_15m or not klines_1d:
        return {
            "is_valid_tradable_asset": True,
            "rejection_reason": None,
            "multi_tf_score": 50,
            "volatility_expansion_ok": True
        }
        
    # Parse 1d candles to verify real price expansion (Stablecoin Detector)
    d_closes = [float(k[4]) for k in klines_1d]
    d_highs = [float(k[2]) for k in klines_1d]
    d_lows = [float(k[3]) for k in klines_1d]
    avg_price = sum(d_closes) / len(d_closes) if d_closes else 1.0
    
    # Calculate 1d volatility range %
    max_h = max(d_highs) if d_highs else avg_price
    min_l = min(d_lows) if d_lows else avg_price
    price_expansion_pct = ((max_h - min_l) / min_l) * 100.0 if min_l > 0 else 0.0
    
    # 3. Detect Pegged / Zero-Volatility / Ultra-Slow Assets (TRX, Pegs, Range 1D < 2.20%)
    if price_expansion_pct < 2.20 and symbol != "BTCUSDT":
        return {
            "is_valid_tradable_asset": False,
            "rejection_reason": f"Asset {symbol} descalificado: Activo pesado sin elasticidad de ganancia (Rango 1D: {price_expansion_pct:.2f}% < 2.20%)",
            "multi_tf_score": 0
        }
        
    # Parse 10s, 30s, 1m, 2m, 5m, 15m, 30m, 1h closes & volumes
    closes_10s = [float(k[4]) for k in klines_10s] if klines_10s else []
    vols_10s = [float(k[5]) for k in klines_10s] if klines_10s else []
    closes_30s = [float(k[4]) for k in klines_30s] if klines_30s else []
    vols_30s = [float(k[5]) for k in klines_30s] if klines_30s else []
    closes_1m = [float(k[4]) for k in klines_1m] if klines_1m else []
    vols_1m = [float(k[5]) for k in klines_1m] if klines_1m else []
    closes_2m = [float(k[4]) for k in klines_2m] if klines_2m else []
    vols_2m = [float(k[5]) for k in klines_2m] if klines_2m else []
    closes_5m = [float(k[4]) for k in klines_5m]
    ma25_5m = sum(closes_5m[-25:]) / 25.0 if len(closes_5m) >= 25 else closes_5m[-1] if closes_5m else 1.0
    closes_15m = [float(k[4]) for k in klines_15m]
    vols_15m = [float(k[5]) for k in klines_15m]
    closes_30m = [float(k[4]) for k in klines_30m] if klines_30m else closes_15m
    vols_30m = [float(k[5]) for k in klines_30m] if klines_30m else vols_15m
    highs_30m = [float(k[2]) for k in klines_30m] if klines_30m else []
    lows_30m = [float(k[3]) for k in klines_30m] if klines_30m else []
    ma25_30m = sum(closes_30m[-25:]) / len(closes_30m[-25:]) if len(closes_30m) >= 25 else (closes_30m[-1] if closes_30m else 1.0)
    closes_1h = [float(k[4]) for k in klines_1h] if klines_1h else closes_15m
    closes_4h = [float(k[4]) for k in klines_4h] if klines_4h else closes_15m
    
    # Micro Moving Averages for 1m (MA3 & MA7)
    ma3_1m = sum(closes_1m[-3:]) / len(closes_1m[-3:]) if len(closes_1m) >= 3 else (closes_1m[-1] if closes_1m else 1.0)
    ma7_1m = sum(closes_1m[-7:]) / len(closes_1m[-7:]) if len(closes_1m) >= 7 else (closes_1m[-1] if closes_1m else 1.0)
    
    # Micro Directional Trends (10s, 30s, 1m, 2m, 5m, 15m, 30m, 1h, 1d)
    tf_10s_up = (closes_10s[-1] >= closes_10s[-2]) if len(closes_10s) >= 2 else False
    tf_30s_up = (closes_30s[-1] >= closes_30s[-2]) if len(closes_30s) >= 2 else (closes_1m[-1] >= ma3_1m if closes_1m else False)
    tf_1m_up = (closes_1m[-1] >= closes_1m[-2] or closes_1m[-1] >= ma7_1m) if len(closes_1m) >= 2 else False
    tf_2m_up = closes_2m[-1] > closes_2m[-3] if len(closes_2m) >= 3 else (closes_2m[-1] > closes_2m[0] if closes_2m else False)
    tf_5m_up = closes_5m[-1] > closes_5m[-3] if len(closes_5m) >= 3 else (closes_5m[-1] > closes_5m[0] if closes_5m else False)
    tf_15m_up = closes_15m[-1] > closes_15m[-3] if len(closes_15m) >= 3 else (closes_15m[-1] > closes_15m[0] if closes_15m else False)
    tf_30m_up = closes_30m[-1] > closes_30m[-3] if len(closes_30m) >= 3 else (closes_30m[-1] > closes_30m[0] if closes_30m else False)
    tf_1h_up = closes_1h[-1] > closes_1h[-3] if len(closes_1h) >= 3 else (closes_1h[-1] > closes_1h[0] if closes_1h else False)
    tf_4h_up = closes_4h[-1] > closes_4h[-3] if len(closes_4h) >= 3 else (closes_4h[-1] > closes_4h[0] if closes_4h else False)
    tf_1d_up = d_closes[-1] > d_closes[0] if d_closes else False
    
    # Calculate Multi-Tier RSI Architecture (10s, 30s, 1m, 2m, 5m, 15m, 30m, 1h, 4h)
    rsi_10s = calculate_rsi(closes_10s, period=6) if len(closes_10s) >= 7 else (rsi_1m if 'rsi_1m' in locals() else 50.0)
    rsi_30s = calculate_rsi(closes_30s, period=6) if len(closes_30s) >= 7 else (rsi_1m if 'rsi_1m' in locals() else 50.0)
    rsi_1m = calculate_rsi(closes_1m)
    rsi_2m = calculate_rsi(closes_2m)
    rsi_5m = calculate_rsi(closes_5m)
    rsi_15m = calculate_rsi(closes_15m)
    rsi_30m = calculate_rsi(closes_30m)
    rsi_1h = calculate_rsi(closes_1h)
    rsi_4h = calculate_rsi(closes_4h)
    
    # 10s & 30s Microstructure Volume Surge
    avg_vol_10s = sum(vols_10s[-5:-1]) / len(vols_10s[-5:-1]) if len(vols_10s) >= 5 else 1.0
    vol_surge_10s = round(vols_10s[-1] / avg_vol_10s, 2) if (vols_10s and avg_vol_10s > 0) else 1.0

    avg_vol_30s = sum(vols_30s[-3:-1]) / len(vols_30s[-3:-1]) if len(vols_30s) >= 3 else 1.0
    vol_surge_30s = round(vols_30s[-1] / avg_vol_30s, 2) if (vols_30s and avg_vol_30s > 0) else 1.0
    
    # 1m Microstructure Volume Surge & Micro-Burst Detector
    avg_vol_1m = sum(vols_1m[-10:-1]) / len(vols_1m[-10:-1]) if len(vols_1m) >= 10 else 1.0
    vol_surge_1m = round(vols_1m[-1] / avg_vol_1m, 2) if (vols_1m and avg_vol_1m > 0) else 1.0
    is_30s_micro_burst = bool((vols_1m and vols_1m[-1] >= avg_vol_1m * 0.70) and tf_30s_up)
    
    # 2m Microstructure Volume Surge
    avg_vol_2m = sum(vols_2m[-5:]) / len(vols_2m[-5:]) if len(vols_2m) >= 5 else 1.0
    vol_surge_2m = round(vols_2m[-1] / avg_vol_2m, 2) if (vols_2m and avg_vol_2m > 0) else 1.0
    
    # 15m Microstructure Volume Surge
    avg_vol_15m = sum(vols_15m[-5:]) / len(vols_15m[-5:]) if len(vols_15m) >= 5 else 1.0
    vol_surge_15m = round(vols_15m[-1] / avg_vol_15m, 2) if (vols_15m and avg_vol_15m > 0) else 1.0
    
    # EMA Cross (9/21) - Fast momentum signal
    ema9_15m = _ema(closes_15m, 9) if len(closes_15m) >= 9 else closes_15m[-1]
    ema21_15m = _ema(closes_15m, 21) if len(closes_15m) >= 21 else closes_15m[-1]
    is_ema_golden_cross = ema9_15m > ema21_15m
    
    # OBV (On-Balance Volume) - Accumulation/Distribution detection
    obv_15m, obv_trend = calculate_obv(closes_15m, vols_15m)
    is_obv_accumulating = obv_trend == "ACCUMULATING"
    
    # ATR(14) Normalized 15M & 1H - Volatility & DNA filter
    highs_15m = [float(k[2]) for k in klines_15m]
    lows_15m = [float(k[3]) for k in klines_15m]
    atr_15m = calculate_atr(highs_15m, lows_15m, closes_15m, 14)
    atr_pct_15m = round((atr_15m / closes_15m[-1]) * 100.0, 3) if closes_15m[-1] > 0 else 0.0

    highs_1h = [float(k[2]) for k in klines_1h]
    lows_1h = [float(k[3]) for k in klines_1h]
    atr_1h = calculate_atr(highs_1h, lows_1h, closes_1h, 14) if klines_1h else atr_15m * 1.5
    atr_pct_1h = round((atr_1h / closes_1h[-1]) * 100.0, 3) if (closes_1h and closes_1h[-1] > 0) else atr_pct_15m * 1.4

    # MFI (Money Flow Index) - Volume-Weighted Institutional Cash Flow
    mfi_15m = calculate_mfi(highs_15m, lows_15m, closes_15m, vols_15m, period=14)
    is_mfi_oversold_floor = (mfi_15m <= 35.0)  # Institutional floor accumulation
    
    # StochRSI (Stochastic RSI) - Ultra-sensitive bottom exhaustion
    stoch_k_15m, stoch_d_15m = calculate_stoch_rsi(closes_15m, rsi_period=14, stoch_period=14)
    is_stoch_rsi_floor_pivot = (stoch_k_15m <= 25.0 and stoch_k_15m >= stoch_d_15m)

    import learning_engine
    dna_profile = learning_engine.calculate_asset_dna_profile(symbol, atr_15m_pct=atr_pct_15m, atr_1h_pct=atr_pct_1h)
    
    # BTC-ALT Correlation - Relative strength detection
    btc_klines = fetch_klines_public("BTCUSDT", "15m", 20)
    btc_closes = [float(k[4]) for k in btc_klines] if btc_klines else []
    btc_change_pct = ((btc_closes[-1] - btc_closes[-3]) / btc_closes[-3]) * 100.0 if len(btc_closes) >= 3 else 0.0
    alt_change_pct = ((closes_15m[-1] - closes_15m[-3]) / closes_15m[-3]) * 100.0 if len(closes_15m) >= 3 else 0.0
    relative_strength = round(alt_change_pct - btc_change_pct, 3) if symbol != "BTCUSDT" else 0.0
    is_alt_outperforming_btc = relative_strength > 0.15  # ALT gaining more than BTC

    # 15m Microstructure moving averages (MA7, MA25, MA99) & Volume Surge
    ma7_15m = sum(closes_15m[-7:]) / len(closes_15m[-7:]) if len(closes_15m) >= 7 else closes_15m[-1]
    ma25_15m = sum(closes_15m[-25:]) / len(closes_15m[-25:]) if len(closes_15m) >= 25 else closes_15m[-1]
    ma99_15m = sum(closes_15m[-99:]) / len(closes_15m[-99:]) if len(closes_15m) >= 99 else closes_15m[-1]
    
    # Strict MA25 & MA99 calculation: Slopes and Intersection
    prev_ma25_15m = sum(closes_15m[-26:-1]) / len(closes_15m[-26:-1]) if len(closes_15m) >= 26 else ma25_15m
    ma25_slope_ok = ma25_15m >= (prev_ma25_15m * 0.9995)
    
    # User Intersect Directive:
    # 1. MA25 (Pink) intersects MA99 (Purple) and trends UPWARD / stays on top -> Bullish Expansion (+20 Pts Bonus)
    # 2. MA25 (Pink) after intersection trends DOWNWARD -> Bearish Drop (Automatic Disqualification / Veto)
    is_ma25_above_ma99_upward = (ma25_15m >= ma99_15m * 0.999) and ma25_slope_ok
    is_ma25_below_ma99_downward = (ma25_15m < ma99_15m) and (ma25_15m < prev_ma25_15m)

    # USER'S MA7 (Amarilla) / MA25 (Rosada) GOLDEN ROCKET PATTERN:
    # MA7 intersects / stays above MA25 and MA7 slope is ascending (ma7_15m >= prev_ma7_15m)
    prev_ma7_15m = sum(closes_15m[-8:-1]) / len(closes_15m[-8:-1]) if len(closes_15m) >= 8 else ma7_15m
    is_ma7_above_ma25_upward = (ma7_15m >= ma25_15m) and (ma7_15m >= prev_ma7_15m * 0.9995)

    price_above_15m_ma7 = closes_15m[-1] > ma7_15m
    price_above_15m_ma25 = (closes_15m[-1] >= ma25_15m * 1.0015) and ma25_slope_ok
    dist_from_15m_ma7_pct = round(((closes_15m[-1] - ma7_15m) / ma7_15m) * 100.0, 2) if ma7_15m > 0 else 0.0
    
    std_15m = float(np.std(closes_15m[-25:])) if len(closes_15m) >= 25 else 0.001
    bb_upper = ma25_15m + (2.0 * std_15m)
    bb_lower = ma25_15m - (2.0 * std_15m)
    bb_range = bb_upper - bb_lower
    pct_b = float((closes_15m[-1] - bb_lower) / bb_range) if bb_range > 0 else 0.5
    
    is_oversold_bounce_candidate = (pct_b <= 0.25 or rsi_2m <= 35.0 or rsi_5m <= 38.0)
    is_overbought_exhaustion = (pct_b >= 0.85 or rsi_2m >= 68.0 or dist_from_15m_ma7_pct > 3.0)

    # ========================================================================
    # 🚀 PRE-PUMP MOMENTUM ANTICIPATOR (Identifies next EDEN +38%, SCRT +30%)
    # Pattern: Volume Acceleration + Bollinger Squeeze Expansion + MA7 > MA25
    # ========================================================================
    vol_acceleration = 1.0
    bb_squeeze_ratio = 1.0
    if len(vols_15m) >= 20:
        avg_vol_early = sum(vols_15m[:10]) / 10.0
        avg_vol_late = sum(vols_15m[-10:]) / 10.0
        vol_acceleration = round(avg_vol_late / avg_vol_early, 2) if avg_vol_early > 0 else 1.0
    if len(closes_15m) >= 20:
        std_early = float(np.std(closes_15m[:10])) if len(closes_15m) >= 10 else 0.001
        std_late = float(np.std(closes_15m[-10:]))
        bb_squeeze_ratio = round(std_late / std_early, 2) if std_early > 0 else 1.0

    # Pre-Pump Signal: Volume accelerating + volatility expanding + MA7 crossing above MA25
    is_pre_pump_signal = (
        vol_acceleration >= 2.0 and        # Volume doubled or more (accumulation)
        bb_squeeze_ratio >= 1.5 and         # Volatility expanding (breakout)
        ma7_15m >= ma25_15m and             # MA7 above MA25 (bullish structure)
        (tf_2m_up or tf_5m_up) and          # Micro-trend confirming upward
        rsi_15m < 75.0                      # Not yet overbought (room to run)
    )

    # 🧬 INDICADORES PRO ACTIVOS (Solo ADX + CCI — los únicos que alimentan decisiones):
    # Los demás 20 indicadores se eliminaron por ser peso muerto computacional.
    wma14_15m = None
    wr_15m = None
    k_15m, d_15m, j_15m = None, None, None
    sar_15m, sar_trend = None, None
    trix_15m = None
    mtm_15m = None
    emv_15m = None
    avl_15m = None
    
    # 📊 ADX (Fuerza de Tendencia) — Confirma si hay tendencia real o solo ruido lateral:
    plus_di_15m, minus_di_15m, adx_15m = None, None, None
    try:
        if len(closes_15m) >= 14 and len(highs_15m) >= 14 and len(lows_15m) >= 14:
            period_adx = 14
            tr_list = []
            plus_dm_list = []
            minus_dm_list = []
            for i in range(1, len(closes_15m)):
                h = highs_15m[i]
                l = lows_15m[i]
                pc = closes_15m[i - 1]
                tr_list.append(max(h - l, abs(h - pc), abs(l - pc)))
                up_move = highs_15m[i] - highs_15m[i - 1]
                down_move = lows_15m[i - 1] - lows_15m[i]
                plus_dm_list.append(up_move if up_move > down_move and up_move > 0 else 0.0)
                minus_dm_list.append(down_move if down_move > up_move and down_move > 0 else 0.0)
            if len(tr_list) >= period_adx:
                atr_sum = sum(tr_list[:period_adx])
                plus_dm_sum = sum(plus_dm_list[:period_adx])
                minus_dm_sum = sum(minus_dm_list[:period_adx])
                for i in range(period_adx, len(tr_list)):
                    atr_sum = atr_sum - atr_sum / period_adx + tr_list[i]
                    plus_dm_sum = plus_dm_sum - plus_dm_sum / period_adx + plus_dm_list[i]
                    minus_dm_sum = minus_dm_sum - minus_dm_sum / period_adx + minus_dm_list[i]
                if atr_sum > 0:
                    plus_di_15m = round((plus_dm_sum / atr_sum) * 100, 2)
                    minus_di_15m = round((minus_dm_sum / atr_sum) * 100, 2)
                    di_sum = plus_di_15m + minus_di_15m
                    dx = abs(plus_di_15m - minus_di_15m) / di_sum * 100 if di_sum > 0 else 0
                    adx_15m = round(dx, 2)
    except Exception:
        pass
    
    # 📊 CCI (Commodity Channel Index) — Detecta sobreventa profunda complementando RSI:
    cci_15m = None
    try:
        cci_period = 20
        if len(closes_15m) >= cci_period and len(highs_15m) >= cci_period and len(lows_15m) >= cci_period:
            tp_list = [(highs_15m[i] + lows_15m[i] + closes_15m[i]) / 3.0 for i in range(len(closes_15m))]
            tp_recent = tp_list[-cci_period:]
            tp_mean = sum(tp_recent) / cci_period
            mean_dev = sum(abs(tp - tp_mean) for tp in tp_recent) / cci_period
            if mean_dev > 0:
                cci_15m = round((tp_list[-1] - tp_mean) / (0.015 * mean_dev), 2)
    except Exception:
        pass
    
    # 🎯 SEÑALES DERIVADAS DE ADX + CCI (Conectadas al ADN del Activo):
    is_strong_trend = bool(adx_15m is not None and adx_15m >= 25.0)
    is_bullish_trend_adx = bool(is_strong_trend and plus_di_15m is not None and minus_di_15m is not None and plus_di_15m > minus_di_15m)
    is_ranging_market = bool(adx_15m is not None and adx_15m < 20.0)
    is_cci_deep_oversold = bool(cci_15m is not None and cci_15m <= -100.0)
    is_cci_overbought = bool(cci_15m is not None and cci_15m >= 150.0)

    # ========================================================================
    # ⛔ ENHANCED FALLING KNIFE GUARD V2 (Avoids TUT -45%, BICO -17%, BMT -13%)
    # Uses REAL 24h change from Binance API + relaxed OR-logic conditions
    # ========================================================================
    price_position_in_range = 50.0
    if d_highs and d_lows:
        h24 = max(d_highs)
        l24 = min(d_lows)
        rng = h24 - l24
        price_position_in_range = round(((closes_15m[-1] - l24) / rng) * 100.0, 1) if rng > 0 else 50.0

    # Fetch REAL 24h change from Binance /ticker/24hr API (Cached for 30s)
    price_change_24h_pct = 0.0
    try:
        now_t = time.time()
        ticker_data = None
        if symbol in _TICKER_CACHE and (now_t - _TICKER_CACHE[symbol][0] < 30):
            ticker_data = _TICKER_CACHE[symbol][1]
        else:
            ticker_res = _SESSION.get("https://api.binance.com/api/v3/ticker/24hr", params={"symbol": symbol}, timeout=3)
            if ticker_res.status_code == 200:
                ticker_data = ticker_res.json()
                _TICKER_CACHE[symbol] = (now_t, ticker_data)
        if ticker_data:
            price_change_24h_pct = round(float(ticker_data.get("priceChangePercent", 0)), 2)
    except Exception:
        # Fallback to daily candle approximation
        price_change_24h_pct = round(((closes_15m[-1] - d_closes[-2]) / d_closes[-2]) * 100.0, 2) if (len(d_closes) >= 2 and d_closes[-2] > 0) else 0.0

    # Macro bearish: solo 1H + 1D (4H eliminado — 1H es el máximo macro por directiva del usuario)
    macro_bearish_count = sum([not tf_1h_up, not tf_1d_up])
    is_bearish = macro_bearish_count >= 2  # Ambos 1H y 1D deben ser bajistas

    # Falling Knife V3: Detects active plunges & unconfirmed bottoms
    falling_knife_signals = 0
    if price_change_24h_pct < -6.0:              # Real 24h drop > 6%
        falling_knife_signals += 1
    if price_position_in_range < 25.0:           # Price crushed to bottom of range
        falling_knife_signals += 1
    if ma7_15m < ma25_15m:                       # MA7 below MA25 (bearish structure)
        falling_knife_signals += 1
    if macro_bearish_count >= 2:                  # Both 1H and 1D are bearish
        falling_knife_signals += 1
    # Active cascade check: 3 consecutive lower closes on 15m without a green micro bounce
    is_consecutive_drop_15m = len(closes_15m) >= 3 and (closes_15m[-1] < closes_15m[-2] < closes_15m[-3]) and not (tf_1m_up or tf_2m_up)
    if is_consecutive_drop_15m:
        falling_knife_signals += 2

    is_falling_knife = (falling_knife_signals >= 2) and (price_change_24h_pct < -3.0 or is_consecutive_drop_15m)


    # Dead Cat Bounce Filter: micro-bounces on 2m/5m during a crash are traps, NOT buy signals
    is_dead_cat_bounce = (
        price_change_24h_pct < -8.0 and         # Crashed > 8% in real 24h
        price_position_in_range < 35.0 and      # Still near the bottom of the range
        (tf_2m_up or tf_5m_up) and              # Micro-timeframe shows a bounce (the trap)
        macro_bearish_count >= 2                  # Both 1H and 1D still bearish (macro context)
    )

    # Macro Bearish Dominance: 1H + 1D both bearish = heavy penalty
    is_macro_bearish_dominance = (
        macro_bearish_count == 2 and             # Both 1H and 1D are bearish
        price_position_in_range < 30.0           # Price in bottom 30% of range
    )

    # Detect RSI Bullish Divergence (Price Lower Low + RSI Higher Low = Early Floor Reversal)
    is_bullish_divergence = False
    if len(closes_15m) >= 20:
        recent_low = min(closes_15m[-5:])
        prev_low = min(closes_15m[-10:-5])
        if recent_low < prev_low:
            # Use full closes array up to each window for proper RSI calculation (needs 15+ data points)
            recent_rsi = calculate_rsi(closes_15m[-19:])   # RSI using last 19 candles (includes recent window)
            prev_rsi = calculate_rsi(closes_15m[-24:-5])    # RSI using earlier window (excludes last 5)
            if recent_rsi > prev_rsi + 3.0:
                is_bullish_divergence = True

    # Calculate VWAP (Volume-Weighted Average Price) & Standard Deviation Bands
    cum_pv = sum(((float(k[2]) + float(k[3]) + float(k[4])) / 3.0) * float(k[5]) for k in klines_15m[-20:]) if klines_15m else 0.0
    cum_vol = sum(float(k[5]) for k in klines_15m[-20:]) if klines_15m else 0.0
    vwap_15m = (cum_pv / cum_vol) if cum_vol > 0 else closes_15m[-1]
    vwap_std = float(np.std(closes_15m[-20:])) if len(closes_15m) >= 20 else 0.001
    vwap_lower_band = vwap_15m - (1.5 * vwap_std)
    is_vwap_floor_rebound = (closes_15m[-1] <= vwap_lower_band) or (closes_15m[-1] < vwap_15m and (float(klines_15m[-1][3]) <= vwap_lower_band))

    # 🏔️ DETECCIÓN DE CASCADA ROJA 15M Y SUELO ESTRUCTURAL CONFIRMADO:
    # 1. Detecta si el activo lleva 3+ velas de 15m rojas consecutivas sin freno
    is_15m_red_cascade = False
    lower_wick_pct_15m = 0.0
    if len(klines_15m) >= 3:
        red_count_15m = sum(1 for k in klines_15m[-3:] if float(k[4]) < float(k[1]))
        if red_count_15m >= 3:
            last_k = klines_15m[-1]
            k_rng = float(last_k[2]) - float(last_k[3])
            lower_wick = min(float(last_k[1]), float(last_k[4])) - float(last_k[3])
            lower_wick_pct_15m = (lower_wick / k_rng) * 100.0 if k_rng > 0 else 0.0
            # Si la mecha inferior de absorción es menor al 30% y no hay divergencia, sigue cayendo
            if lower_wick_pct_15m < 30.0 and not is_bullish_divergence:
                is_15m_red_cascade = True

    # 2. Confirmación de Giro Estructural en 5M/15M (Higher Low o vela verde)
    is_5m_higher_low = False
    if len(klines_5m) >= 2:
        is_5m_higher_low = (float(klines_5m[-1][3]) >= float(klines_5m[-2][3]) * 0.998) or (float(klines_5m[-1][4]) >= float(klines_5m[-1][1]))

    has_reversal_confirmation = (
        is_bullish_divergence or 
        is_vwap_floor_rebound or 
        (tf_15m_up and is_5m_higher_low) or 
        (tf_1m_up and is_5m_higher_low and lower_wick_pct_15m >= 25.0)
    )
    is_true_structural_floor = has_reversal_confirmation and not is_15m_red_cascade
    floor_structure_label = "🟢 SUELO ESTRUCTURAL CONFIRMADO" if is_true_structural_floor else ("🔴 CASCADA 15M EN CURSO (PROHIBIDO ENTRAR)" if is_15m_red_cascade else "⚪ ESPERANDO GIRO")

    # Calculate MACD (12, 26, 9) on 15m candles
    macd_line_15m, macd_signal_15m, macd_hist_15m = calculate_macd(closes_15m)
    is_macd_bullish_cross = (macd_hist_15m > 0) and (macd_line_15m > macd_signal_15m)

    # GBM Crash Detector (Z-Score Anomaly Detection from quant_institutional.py)
    gbm_result = _gbm_detector.analyze(closes_15m)
    gbm_zscore = gbm_result.get('gbm_zscore', 0.0)
    gbm_anomaly_type = gbm_result.get('anomaly_type', 'BROWNIAN_NOISE')
    gbm_signal_strength = gbm_result.get('signal_strength', 'NOISE')
    # Crash rebound = Z was deeply negative but price is now bouncing (oversold + bullish micro)
    is_crash_rebound = (gbm_anomaly_type == 'DUMP_CRASH' or gbm_zscore < -2.0) and (tf_2m_up or tf_5m_up) and (is_oversold_bounce_candidate or is_vwap_floor_rebound)
    # Active dump veto = deep crash with NO rebound signals
    is_active_dump = (gbm_zscore < -3.0) and not is_crash_rebound and not is_bullish_divergence

    # Calculate SuperTrend (10, 3) Pattern Indicator on 15m, 1h
    is_supertrend_bullish = False
    if len(klines_15m) >= 10:
        atr_10 = sum(max(float(k[2]) - float(k[3]), abs(float(k[2]) - float(klines_15m[i-1][4])), abs(float(k[3]) - float(klines_15m[i-1][4]))) for i, k in enumerate(klines_15m[-10:], start=len(klines_15m)-10)) / 10.0
        hl2 = (float(klines_15m[-1][2]) + float(klines_15m[-1][3])) / 2.0
        st_lower = hl2 - (3.0 * atr_10)
        is_supertrend_bullish = closes_15m[-1] > st_lower and closes_15m[-1] > ma7_15m

    # 1H SuperTrend (10,3) & Yellow Arrow (MA7/MA25) Indicators
    is_supertrend_1h_bullish = False
    ma7_1h = sum(closes_1h[-7:]) / len(closes_1h[-7:]) if len(closes_1h) >= 7 else closes_1h[-1]
    ma25_1h = sum(closes_1h[-25:]) / len(closes_1h[-25:]) if len(closes_1h) >= 25 else closes_1h[-1]
    is_yellow_arrow_1h = (closes_1h[-1] >= ma7_1h) and (ma7_1h >= ma25_1h)
    if len(klines_1h) >= 10:
        atr_1h_10 = sum(max(float(k[2]) - float(k[3]), abs(float(k[2]) - float(klines_1h[i-1][4])), abs(float(k[3]) - float(klines_1h[i-1][4]))) for i, k in enumerate(klines_1h[-10:], start=len(klines_1h)-10)) / 10.0
        hl2_1h = (float(klines_1h[-1][2]) + float(klines_1h[-1][3])) / 2.0
        st_lower_1h = hl2_1h - (3.0 * atr_1h_10)
        is_supertrend_1h_bullish = closes_1h[-1] > st_lower_1h

    # ========================================================================
    # 🏔️ FLOOR INJECTION INDEX (FII) — Inyección Institucional en la Base
    # Detecta el momento exacto en que el dinero inteligente entra en el piso:
    # 10s/30s ignición + OBV 1M acumulando + VolSurge 1M + RSI 1M en suelo + vela 1M verde
    # ========================================================================
    fii_score = 0
    if is_obv_accumulating:
        fii_score += 20  # Smart money acumulando en OBV
    if vol_surge_1m >= 1.3:
        fii_score += 15  # Inyección de volumen detectada en 1M
    if 28 <= rsi_1m <= 52:
        fii_score += 15  # RSI 1M en zona de suelo / lanzamiento
    if tf_1m_up:
        fii_score += 15  # Vela de 1M gira verde: gatillo exacto de despegue
    if tf_10s_up and tf_30s_up:
        fii_score += 10  # Micro-ignición sincronizada en 10s y 30s (despegue milimétrico)
    if rsi_10s <= 45 and rsi_30s <= 45:
        fii_score += 5   # Suelo en sub-minuto confirmado
    if is_vwap_floor_rebound:
        fii_score += 10  # Precio en el piso del VWAP (-1.5 StdDev)
    if is_mfi_oversold_floor:
        fii_score += 10  # MFI (Money Flow Index) en sobreventa institucional (absorción de liquidez)
    if is_stoch_rsi_floor_pivot:
        fii_score += 10  # StochRSI giro alcista en suelo
    if is_bullish_divergence:
        fii_score += 15  # Divergencia alcista: precio bajo pero RSI sube
    if rsi_2m <= 48 and tf_2m_up:
        fii_score += 10  # Confirmación 2M en zona de suelo
    fii_score = min(100, fii_score)

    # Re-evaluate reversal confirmation now that FII is computed (was broken when referenced before definition)
    if not has_reversal_confirmation and fii_score >= 60 and tf_5m_up:
        has_reversal_confirmation = True
        is_true_structural_floor = has_reversal_confirmation and not is_15m_red_cascade
        floor_structure_label = "🟢 SUELO ESTRUCTURAL CONFIRMADO (FII)" if is_true_structural_floor else floor_structure_label

    # ========================================================================
    # 📊 SCORE MULTI-TIMEFRAME 5 CAPAS: 1M (gatillo) → 2M → 5M → 15M → 1H
    # Máximo macro: 1H. El 4H queda ELIMINADO por directiva del usuario.
    # ========================================================================
    score_components = [
        tf_1m_up * 15,    # 🔥 GATILLO: Vela de 1M gira desde el suelo
        tf_2m_up * 15,    # Confirmación micro 2M
        tf_5m_up * 20,    # Impulso 5M
        tf_15m_up * 20,   # Contexto medio 15M
        tf_1h_up * 20,    # 🏔️ Macro máximo: 1H (ya NO se usa 4H)
        tf_1d_up * 10,    # Tendencia diaria de fondo (peso reducido)
        15 if is_bullish_divergence else 0,
        15 if is_vwap_floor_rebound else 0,
        10 if is_supertrend_bullish else 0,
        20 if is_ma25_above_ma99_upward else 0,
        25 if is_ma7_above_ma25_upward else 0,
        15 if is_supertrend_1h_bullish else 0,
        # 4H SuperTrend y Yellow Arrow 4H ELIMINADOS:
        15 if is_yellow_arrow_1h else 0,   # Solo 1H Yellow Arrow
        10 if is_macd_bullish_cross else 0,
        20 if is_crash_rebound else 0,
        25 if is_pre_pump_signal else 0
    ]
    multi_tf_score = min(100, sum(score_components))
    
    if is_ema_golden_cross:
        multi_tf_score += 10  # EMA(9) > EMA(21) bullish momentum
    if is_obv_accumulating:
        multi_tf_score += 12  # Smart money accumulating
    if is_alt_outperforming_btc and not is_bearish:
        multi_tf_score += 8   # Fuerza relativa vs BTC
    # 🏔️ MEJORA 3: Floor Injection Index Super-Priority bonus
    if fii_score >= 60:
        multi_tf_score += 25  # Inyección institucional confirmada en la base (Prioridad A+)
    elif fii_score >= 45:
        multi_tf_score += 15  # Inyección parcial de alta probabilidad
    elif fii_score >= 30:
        multi_tf_score += 7   # Inyección incipiente
        
    elasticity_score = round(atr_pct_15m * (vol_acceleration if 'vol_acceleration' in locals() else 1.0) * (1.5 if is_obv_accumulating else 1.0), 3)
    if atr_pct_15m >= 0.40 and is_obv_accumulating:
        multi_tf_score += 10 # High-beta explosive elasticity bonus

    # 🧬 PATRONES CUÁNTICOS DE ADN FRACTAL (Arquetipo DCR/USDT: Ruptura Macro + Retesteo MA25 + Compresión 1M)
    spring_coiling_info = _detect_spring_safe(klines_1m)
    wave2_retest_info = _detect_wave2_safe(klines_15m)
    
    if spring_coiling_info.get("is_spring_compressed"):
        multi_tf_score += spring_coiling_info.get("spring_bonus", 15)  # 🚀 Resorte comprimido 1M listo para Ola 3
    if wave2_retest_info.get("is_wave2_retest"):
        multi_tf_score += wave2_retest_info.get("retest_bonus", 20)    # 💎 Retesteo de oro Ola 2 apoyado en MA25
        
    multi_tf_score = min(100, multi_tf_score)  # Re-cap at 100 after bonuses
    
    # Extract 15m candle baseline values
    close_15m = closes_15m[-1] if closes_15m else 0.0
    
    # Multi-Horizon Peak Proximity & 24H Macro Channel Ceiling Shield (15M, 30M, 1H, 24H)
    highs_15m = [float(k[2]) for k in klines_15m] if klines_15m else []
    highs_1h = [float(k[2]) for k in klines_1h] if klines_1h else []
    lows_1h = [float(k[3]) for k in klines_1h] if klines_1h else []
    
    high_15m_recent = max(highs_15m[-3:]) if len(highs_15m) >= 3 else close_15m
    high_30m_recent = max(highs_15m[-6:]) if len(highs_15m) >= 6 else close_15m
    
    # 🏔️ MATRIZ FRACTAL DE SUELO EN 8 NIVELES (1M, 2M, 5M, 15M, 30M, 1H, 4H, 1D):
    def _calc_range_pos(klines, lookback=24):
        if not klines or len(klines) < 2: return 0.5
        subset = klines[-lookback:] if len(klines) >= lookback else klines
        c = float(subset[-1][4])
        h = max(float(k[2]) for k in subset)
        l = min(float(k[3]) for k in subset)
        return ((c - l) / (h - l)) if (h - l) > 0 else 0.5

    range_position_1m = _calc_range_pos(klines_1m, 24)
    range_position_2m = _calc_range_pos(klines_2m, 24)
    range_position_5m = _calc_range_pos(klines_5m, 24)
    range_position_10m = _calc_range_pos(klines_10m, 24)
    range_position_15m = _calc_range_pos(klines_15m, 24)
    range_position_30m = _calc_range_pos(klines_30m, 24)
    range_position_1h = _calc_range_pos(klines_1h, 24)
    range_position_2h = _calc_range_pos(klines_2h, 24)
    range_position_4h = _calc_range_pos(klines_4h, 24)
    range_position_1d = _calc_range_pos(klines_1d, 14)
    
    rsi_1d = calculate_rsi(d_closes) if len(d_closes) >= 7 else 50.0

    high_15m_recent = max(highs_15m[-24:]) if 'highs_15m' in locals() and len(highs_15m) >= 24 else close_15m
    high_30m_recent = max(highs_30m[-24:]) if len(highs_30m) >= 24 else (max(highs_30m) if highs_30m else close_15m)
    low_30m_recent = min(lows_30m[-24:]) if len(lows_30m) >= 24 else (min(lows_30m) if lows_30m else close_15m)
    high_1h_recent = max(highs_1h[-24:]) if len(highs_1h) >= 24 else (max(highs_1h) if highs_1h else close_15m)
    low_1h_recent = min(lows_1h[-24:]) if len(lows_1h) >= 24 else (min(lows_1h) if lows_1h else close_15m)
    high_24h = d_highs[-1] if d_highs else high_1h_recent

    # Distancia sobre la Media MA25 de 30m, 1 Hora y 4 Horas:
    ma25_4h = sum(closes_4h[-25:]) / len(closes_4h[-25:]) if len(closes_4h) >= 25 else (closes_4h[-1] if closes_4h else close_15m)
    dist_from_30m_ma25_pct = ((close_15m - ma25_30m) / ma25_30m) * 100.0 if ma25_30m > 0 else 0.0
    dist_from_1h_ma25_pct = ((close_15m - ma25_1h) / ma25_1h) * 100.0 if ma25_1h > 0 else 0.0
    dist_from_4h_ma25_pct = ((close_15m - ma25_4h) / ma25_4h) * 100.0 if ma25_4h > 0 else 0.0
    
    # 🕯️ DETECCIÓN DE AGOTAMIENTO Y MECHA SUPERIOR EN VELA ACTIVA (5M, 10M, 15M, 30M, 1H, 2H)
    def _is_candle_top_rejection(kline):
        if not kline: return False
        open_p = float(kline[1])
        high_p = float(kline[2])
        low_p = float(kline[3])
        close_p = float(kline[4])
        rng = high_p - low_p
        if rng <= 0: return False
        upper_wick = high_p - max(open_p, close_p)
        upper_wick_pct = (upper_wick / rng) * 100.0
        return bool(upper_wick_pct >= 40.0 or (close_p < open_p and upper_wick_pct >= 30.0))

    is_top_wick_5m = _is_candle_top_rejection(klines_5m[-1]) if klines_5m else False
    is_top_wick_10m = _is_candle_top_rejection(klines_10m[-1]) if klines_10m else False
    is_top_wick_15m = _is_candle_top_rejection(klines_15m[-1]) if klines_15m else False
    is_top_wick_30m = _is_candle_top_rejection(klines_30m[-1]) if klines_30m else False
    is_top_wick_1h = _is_candle_top_rejection(klines_1h[-1]) if klines_1h else False
    is_top_wick_2h = _is_candle_top_rejection(klines_2h[-1]) if klines_2h else False

    # 🚫 VETO TOTAL ANTI-CIMA EN CADA TEMPORALIDAD (5M, 10M, 15M, 30M, 1H, 2H, 4H, 1D):
    is_at_range_ceiling_1d = bool(range_position_1d >= 0.85 and rsi_1d >= 70.0)
    is_at_range_ceiling_4h = bool(range_position_4h >= 0.80 and rsi_4h >= 70.0)
    is_at_range_ceiling_2h = bool(range_position_2h >= 0.72 or (range_position_2h >= 0.65 and rsi_1h >= 66.0) or is_top_wick_2h)
    is_at_range_ceiling_1h = bool(range_position_1h >= 0.70 or (range_position_1h >= 0.62 and rsi_1h >= 65.0) or is_top_wick_1h)
    is_at_range_ceiling_30m = bool(range_position_30m >= 0.68 or (range_position_30m >= 0.60 and rsi_30m >= 65.0) or is_top_wick_30m)
    is_at_range_ceiling_15m = bool(range_position_15m >= 0.65 or (range_position_15m >= 0.58 and rsi_15m >= 65.0) or is_top_wick_15m)
    is_at_range_ceiling_10m = bool(range_position_10m >= 0.68 or (range_position_10m >= 0.60 and rsi_15m >= 66.0) or is_top_wick_10m)
    is_at_range_ceiling_5m = bool(range_position_5m >= 0.70 or (range_position_5m >= 0.62 and rsi_5m >= 68.0) or is_top_wick_5m)
    is_at_range_ceiling_2m = bool(range_position_2m >= 0.80 and rsi_2m >= 72.0)
    is_at_range_ceiling_1m = bool(range_position_1m >= 0.80 and rsi_1m >= 72.0)

    # 🚫 VETO CRÍTICO ANTI-TECHO FRACTAL TOTAL (ABSOLUTO: Techos reales donde se agotan compradores):
    dist_to_24h_high_pct = round(((high_24h - close_15m) / close_15m) * 100.0, 2) if close_15m > 0 else 999.0
    is_at_daily_resistance_ceiling = bool(
        dist_to_24h_high_pct <= 0.30 or 
        range_position_2h >= 0.72 or     # Techo real en 2H (últimas 48h)
        range_position_1h >= 0.70 or     # Techo real en 1H (últimas 24h)
        range_position_30m >= 0.68 or    # Techo real en 30M
        range_position_15m >= 0.65 or    # Techo real en 15M
        range_position_10m >= 0.68 or    # Techo real en 10M
        range_position_5m >= 0.70 or     # Techo real en 5M
        is_at_range_ceiling_1m or
        is_at_range_ceiling_2m or
        is_at_range_ceiling_5m or
        is_at_range_ceiling_10m or
        is_at_range_ceiling_15m or
        is_at_range_ceiling_30m or
        is_at_range_ceiling_1h or
        is_at_range_ceiling_2h
    )

    dist_15m_pct = round(((high_15m_recent - close_15m) / close_15m) * 100.0, 2) if close_15m > 0 else 999.0
    dist_30m_pct = round(((high_30m_recent - close_15m) / close_15m) * 100.0, 2) if close_15m > 0 else 999.0
    dist_1h_pct = round(((high_1h_recent - close_15m) / close_15m) * 100.0, 2) if close_15m > 0 else 999.0
    dist_24h_pct = round(((high_24h - close_15m) / close_15m) * 100.0, 2) if close_15m > 0 else 999.0

    # 🎯 MODELACIÓN DE COMPORTAMIENTO INSTITUCIONAL (Resistencia Objetivo vs Soporte de Absorción)
    target_resistance_1h_pct = round(((high_1h_recent - close_15m) / close_15m) * 100.0, 2) if close_15m > 0 else 2.50
    major_support_floor_1h_pct = round(((close_15m - low_1h_recent) / close_15m) * 100.0, 2) if close_15m > 0 else 0.90
    expected_rr_ratio = round(target_resistance_1h_pct / max(0.40, major_support_floor_1h_pct), 2)

    is_explosive_breakout = (vol_surge_2m >= 2.5 or vol_surge_15m >= 2.5)

    # Ground-Zero 10s/30s/1M/2M Rebound Ignition on Safe 15M/1H Support Base
    is_sub_minute_ignition = bool(
        (tf_10s_up and tf_30s_up) or 
        (tf_10s_up and tf_1m_up and vol_surge_10s >= 1.2) or 
        (fii_score >= 60 and tf_10s_up)
    )
    is_ground_zero_micro_ignition = bool(
        (is_sub_minute_ignition or tf_1m_up or tf_2m_up) and 
        (dist_from_15m_ma7_pct <= 1.50 or is_yellow_arrow_1h or range_position_1h <= 0.50)
    )

    # 🚫 MEJORA 4: Veto Estricto de Sangrado Activo Sub-Minuto
    is_sub_minute_bleeding = bool(
        (not tf_10s_up and not tf_30s_up and not tf_1m_up) or
        (len(closes_10s) >= 2 and not tf_10s_up and not tf_30s_up and closes_10s[-1] < closes_10s[-2])
    )
    
    # ═══════════════════════════════════════════════════════════════════════
    # 🌌 MATRIZ ARMÓNICA DE CONFLUENCIA FRACTAL 8D (Propuesta Armónica Cuántica):
    # 1M <= 35% | 5M <= 40% | 10M <= 45% | 15M <= 50% | 30M <= 55% | 1H <= 60% | 2H <= 60%
    # ═══════════════════════════════════════════════════════════════════════
    is_1m_floor_zone = bool(range_position_1m <= 0.35)
    is_2m_floor_zone = bool(range_position_2m <= 0.38)
    is_5m_floor_zone = bool(range_position_5m <= 0.40)
    is_10m_floor_zone = bool(range_position_10m <= 0.45)
    is_15m_floor_zone = bool(range_position_15m <= 0.50)
    is_30m_floor_zone = bool(range_position_30m <= 0.55)
    is_1h_floor_zone = bool(range_position_1h <= 0.60)
    is_2h_floor_zone = bool(range_position_2h <= 0.60)

    # Detección de Mecha Inferior en Vela de 1M (Absorción de Suelo):
    lower_wick_1m_pct = 0.0
    if klines_1m and len(klines_1m) >= 1:
        last_k = klines_1m[-1]
        o_1m, h_1m, l_1m, c_1m = float(last_k[1]), float(last_k[2]), float(last_k[3]), float(last_k[4])
        rng_1m = h_1m - l_1m
        if rng_1m > 0:
            body_bottom = min(o_1m, c_1m)
            lower_wick = body_bottom - l_1m
            lower_wick_1m_pct = round((lower_wick / rng_1m) * 100.0, 1)
            
    is_1m_lower_wick_absorption = bool(lower_wick_1m_pct >= 20.0 and tf_1m_up)
    
    # Suelo Micro 1M / 2M (Gatillo de Entrada Sniper)
    is_1m_true_floor = bool(
        is_1m_floor_zone or 
        is_1m_lower_wick_absorption or 
        (rsi_1m <= 42.0 and tf_1m_up) or
        (range_position_2m <= 0.38 and tf_2m_up)
    )
    
    # Suelo Estructural & Contextual en 8D (5M, 10M, 15M, 30M, 1H, 2H)
    # Progresión armónica exacta propuesta
    is_structural_floor_ok = bool(
        range_position_5m <= 0.40 and
        range_position_10m <= 0.45 and
        range_position_15m <= 0.50 and
        range_position_30m <= 0.55 and
        range_position_1h <= 0.60 and
        range_position_2h <= 0.60
    )

    # Confluencia Fractal Suprema de Suelo (TODAS las escalas en la base):
    is_confluent_fractal_floor = bool(
        is_1m_true_floor and
        is_structural_floor_ok and
        rsi_1m <= 52.0 and
        rsi_5m <= 55.0 and
        rsi_15m <= 58.0 and
        not is_15m_red_cascade and
        not is_at_daily_resistance_ceiling
    )
    
    if is_ma25_below_ma99_downward:
        if fii_score < 45 and not (is_ground_zero_micro_ignition or is_vwap_floor_rebound or is_bullish_divergence):
            multi_tf_score = 0
    if is_active_dump:
        if fii_score < 60 and not (is_crash_rebound or is_bullish_divergence):
            multi_tf_score = 0
    if is_falling_knife:
        if fii_score < 60 and not (is_crash_rebound or is_bullish_divergence):
            multi_tf_score = 0
    if is_dead_cat_bounce:
        if fii_score < 60 and not is_bullish_divergence:
            multi_tf_score = 0
    if is_macro_bearish_dominance and multi_tf_score > 30 and fii_score < 50:
        multi_tf_score = 30
    
    # 4. Detect 15m Candle Over-extension / Parabolic Spike (Prevents buying tops like ZRO, ATOM)
    is_overextended_15m = False
    overextension_reason = None
    is_yellow_arrow_pivot = False
    yellow_arrow_status = "⚪ NEUTRAL 15M"
    if klines_15m and len(klines_15m) >= 2:
        last_15m = klines_15m[-1]
        open_15m = float(last_15m[1])
        high_15m = float(last_15m[2])
        low_15m = float(last_15m[3])
        close_15m = float(last_15m[4])
        
        candle_range = high_15m - low_15m
        upper_wick = high_15m - max(open_15m, close_15m)
        lower_wick = min(open_15m, close_15m) - low_15m
        lower_wick_pct = round((lower_wick / candle_range) * 100.0, 1) if candle_range > 0 else 0.0
        
        # Yellow Arrow 15M Pivot Rebound Pattern Detector
        is_yellow_arrow_pivot = (dist_from_15m_ma7_pct <= 2.0) and (lower_wick_pct >= 15.0 or close_15m >= open_15m or is_ground_zero_micro_ignition) and (tf_1m_up or tf_2m_up or tf_5m_up)
        yellow_arrow_status = "🎯 PATRÓN FLECHAS AMARILLAS (REBOTE PIVOTE A+ EN MA7/MA25)" if is_yellow_arrow_pivot else "⚪ NEUTRAL 15M"

        # 🚀 PATRÓN COHETE DE ÉLITE TIPO CETUS (Despegues Rápidos de Alta Convicción en la Base)
        # Combina: Base en Soporte 15M/1H + OBV Acumulando + Giro en 10s/30s/1M + RSI en Suelo (38-62) + Anti-Cima Activo
        is_cetus_rocket_pattern = bool(
            (is_yellow_arrow_pivot or is_ma7_above_ma25_upward or is_ema_golden_cross or is_ground_zero_micro_ignition) and
            is_obv_accumulating and
            (38.0 <= rsi_15m <= 58.0) and
            (tf_10s_up or tf_1m_up or tf_2m_up or tf_5m_up) and
            not is_overextended_15m
        )
        if is_cetus_rocket_pattern:
            yellow_arrow_status = "🚀 [PATRÓN COHETE EN SUELO 10s/1M - DESPEGUE INMEDIATO A+]"

        # 1M, 2M, 5M Intra-Candle Peak / Extended Spike Detectors (Anti-Cima Micro)
        last_1m = klines_1m[-1] if klines_1m else []
        last_2m = klines_2m[-1] if klines_2m else []
        last_5m = klines_5m[-1] if klines_5m else []
        
        is_at_1m_candle_peak = False
        is_at_2m_candle_peak = False
        is_at_5m_candle_peak = False
        exp_1m, exp_2m, exp_5m = 0.0, 0.0, 0.0
        
        if last_1m and len(last_1m) >= 5:
            open_1m, high_1m, low_1m, close_1m = float(last_1m[1]), float(last_1m[2]), float(last_1m[3]), float(last_1m[4])
            exp_1m = ((close_1m - open_1m) / open_1m) * 100.0 if open_1m > 0 else 0.0
            range_1m = high_1m - low_1m
            upper_wick_1m = (high_1m - max(open_1m, close_1m)) / range_1m if range_1m > 0 else 0.0
            if exp_1m > 1.10 and (upper_wick_1m > 0.35 or ((high_1m - close_1m) / close_1m) * 100.0 < 0.10):
                is_at_1m_candle_peak = True

        if last_2m and len(last_2m) >= 5:
            open_2m, high_2m, low_2m, close_2m = float(last_2m[1]), float(last_2m[2]), float(last_2m[3]), float(last_2m[4])
            exp_2m = ((close_2m - open_2m) / open_2m) * 100.0 if open_2m > 0 else 0.0
            range_2m = high_2m - low_2m
            upper_wick_2m = (high_2m - max(open_2m, close_2m)) / range_2m if range_2m > 0 else 0.0
            if exp_2m > 1.40 and (upper_wick_2m > 0.35 or ((high_2m - close_2m) / close_2m) * 100.0 < 0.12):
                is_at_2m_candle_peak = True

        if last_5m and len(last_5m) >= 5:
            open_5m, high_5m, low_5m, close_5m = float(last_5m[1]), float(last_5m[2]), float(last_5m[3]), float(last_5m[4])
            exp_5m = ((close_5m - open_5m) / open_5m) * 100.0 if open_5m > 0 else 0.0
            range_5m = high_5m - low_5m
            upper_wick_5m = (high_5m - max(open_5m, close_5m)) / range_5m if range_5m > 0 else 0.0
            if exp_5m > 1.80 and (upper_wick_5m > 0.35 or ((high_5m - close_5m) / close_5m) * 100.0 < 0.15):
                is_at_5m_candle_peak = True

        # Spike up followed by rejection wick (buying top trap)
        is_green_candle = close_15m >= open_15m
        upper_wick_ratio = (upper_wick / candle_range) if candle_range > 0 else 0.0
        wick_threshold = 0.40 if is_green_candle else 0.35
        
        # 1M Bearish Cascade & SuperTrend 1M Indicator:
        ma25_1m = sum(closes_1m[-25:]) / len(closes_1m[-25:]) if len(closes_1m) >= 25 else ma7_1m
        is_supertrend_1m_bullish = False
        if len(klines_1m) >= 10:
            atr_1m_10 = sum(max(float(k[2]) - float(k[3]), abs(float(k[2]) - float(klines_1m[i-1][4])), abs(float(k[3]) - float(klines_1m[i-1][4]))) for i, k in enumerate(klines_1m[-10:], start=len(klines_1m)-10)) / 10.0
            hl2_1m = (float(klines_1m[-1][2]) + float(klines_1m[-1][3])) / 2.0
            st_lower_1m = hl2_1m - (3.0 * atr_1m_10)
            is_supertrend_1m_bullish = bool(closes_1m[-1] > st_lower_1m)
        is_1m_death_cascade = bool(closes_1m[-1] < ma7_1m and ma7_1m < ma25_1m and not is_supertrend_1m_bullish and vol_surge_1m < 1.4)

        # 🎯 PILAR 4: Sniper Pullback 1M & Detección Anti-FOMO
        ema9_1m = _ema(closes_1m, 9) if len(closes_1m) >= 9 else (ma7_1m if ma7_1m > 0 else close_15m)
        dist_from_1m_ema9_pct = round(((closes_1m[-1] - ema9_1m) / ema9_1m) * 100.0, 2) if ema9_1m > 0 else 0.0
        is_1m_sniper_pullback = bool(-0.40 <= dist_from_1m_ema9_pct <= 0.45 and rsi_1m <= 54.0)
        is_1m_fomo_extension = bool(dist_from_1m_ema9_pct > 1.15)

        # 🎯 Detección de Sobre-Extensión Parabólica Genuina (Cima de Clímax):
        # Solo se activa si el activo está en sobrecompra extrema real (RSI >= 78 o distancia MA7 > 3.5%)
        is_parabolic_blowoff = (rsi_15m >= 78.0) or (rsi_4h >= 75.0) or (dist_from_15m_ma7_pct > 3.50)
        is_major_rejection_wick = (candle_range > 0 and upper_wick_ratio > 0.55 and (high_15m - low_15m) / low_15m > 0.02)
        
        if is_at_daily_resistance_ceiling:
            is_overextended_15m = True
            overextension_reason = f"Veto Anti-Techo Fractal: Activo en cresta del canal (1H={range_position_1h*100:.1f}%, 15M={range_position_15m*100:.1f}%, 1M={range_position_1m*100:.1f}%). Prohibido comprar techos."
        elif is_parabolic_blowoff:
            is_overextended_15m = True
            overextension_reason = f"Sobrecompra Parabólica Extrema (RSI 15M={rsi_15m:.1f}, RSI 4H={rsi_4h:.1f}, Dist MA7={dist_from_15m_ma7_pct:+.2f}%). Esperando pullback a soporte."
        elif is_major_rejection_wick:
            is_overextended_15m = True
            overextension_reason = f"Mecha superior de reversión violenta en 15M ({upper_wick_ratio*100:.1f}% del rango). Vendedores rechazaron la cima."
        elif dist_24h_pct <= 0.20 and rsi_15m >= 75.0:
            is_overextended_15m = True
            overextension_reason = f"Techo 24H Sobrecomprado (Precio al 99.8% del máximo diario con RSI={rsi_15m:.1f})."
        elif dist_from_15m_ma7_pct > 3.80:
            is_overextended_15m = True
            overextension_reason = f"Entrada tardía en la cima de 15m (Precio a +{dist_from_15m_ma7_pct:.2f}% sobre MA7). Exige compra en el soporte."
        elif is_sub_minute_bleeding and not (is_bullish_divergence or is_vwap_floor_rebound):
            is_overextended_15m = True
            overextension_reason = "Micro-caída activa en 10s/30s (Ventas agresivas en sub-minuto). Esperando freno y giro verde en 10s."
        elif is_1m_death_cascade and not (is_bullish_divergence or is_vwap_floor_rebound):
            is_overextended_15m = True
            overextension_reason = f"Cascada Bajista 1M (Precio < MA7 < MA25 y SuperTrend 1M Rojo). Caída en curso sin absorción."
        elif not (tf_1h_up or is_yellow_arrow_1h or rsi_1h <= 60.0 or is_vwap_floor_rebound or is_bullish_divergence):
            is_overextended_15m = True
            overextension_reason = f"Macro 1H sin soporte (RSI 1H={rsi_1h:.1f}). Exige: 1H alcista, rebote VWAP, o divergencia alcista."
    avg_vol_15m = sum(vols_15m[-5:]) / len(vols_15m[-5:]) if len(vols_15m) >= 5 else 1.0
    st_status = "🟢 SUPERTREND 15M/1H VERDE ALCISTA" if (is_supertrend_bullish and is_supertrend_1h_bullish) else ("🟢 SUPERTREND 15M VERDE" if is_supertrend_bullish else "🔴 SUPERTREND ROJO")

    # 🎯 GATILLO SNIPER 1M/5M V5 (Cero entradas prematuras / Cero cuchillos cayendo):
    open_1m_last = float(klines_1m[-1][1]) if klines_1m else close_15m
    is_1m_green_candle = bool(closes_1m[-1] >= open_1m_last) if closes_1m else False
    is_1m_above_ema9 = bool(closes_1m[-1] >= (ema9_1m * 0.9995)) if ema9_1m > 0 else False
    is_1m_green_ignition = bool(is_1m_green_candle and is_1m_above_ema9 and vol_surge_1m >= 0.70)
    
    is_5m_higher_low = False
    if klines_5m and len(klines_5m) >= 2:
        low_5m_curr = float(klines_5m[-1][3])
        low_5m_prev = float(klines_5m[-2][3])
        is_5m_higher_low = bool(low_5m_curr >= (low_5m_prev * 0.9990))
    else:
        is_5m_higher_low = True

    is_sniper_timing_ready = bool(
        is_1m_green_ignition and 
        is_5m_higher_low and 
        not is_15m_red_cascade and 
        (rsi_15m >= 38.0 or is_bullish_divergence or is_vwap_floor_rebound) and
        not is_overextended_15m
    )
    
    if is_sniper_timing_ready:
        sniper_timing_label = "🟢 LISTO PARA DISPARAR (1M Sobre EMA9 + 5M Mínimo Mayor)"
    elif is_15m_red_cascade:
        sniper_timing_label = "🔴 CASCADA 15M (Prohibido Entrar)"
    elif not is_5m_higher_low:
        sniper_timing_label = "⏳ ESPERANDO DOBLE SUELO 5M (Aún haciendo nuevos mínimos)"
    elif not is_1m_above_ema9:
        sniper_timing_label = "⏳ ESPERANDO GIRO 1M (Precio bajo EMA9 1M)"
    else:
        sniper_timing_label = "⏳ CONSOLIDANDO BASE"
    vwap_status = "🟢 REBOTE PISO VWAP (-1.5 StdDev)" if is_vwap_floor_rebound else "⚪ NORMAL VWAP"
    ma99_status = "🚀 CRUCE ALCISTA MA25/MA99 (PULSO HACIA ARRIBA)" if is_ma25_above_ma99_upward else "⚪ NORMAL MA99"
    yellow_arrow_macro = f" | 🎯 FLECHAS AMARILLAS MACRO 1H" if is_yellow_arrow_1h else ""
    macd_status = "🟢 MACD CRUCE ALCISTA" if is_macd_bullish_cross else "🔴 MACD BAJISTA"
    gbm_status = f"💥 REBOTE POST-CRASH (Z={gbm_zscore:.1f})" if is_crash_rebound else (f"⛔ DUMP ACTIVO (Z={gbm_zscore:.1f})" if is_active_dump else f"⚪ GBM NORMAL (Z={gbm_zscore:.1f})")

    pump_status = "🚀 PRE-PUMP DETECTADO (VolAcc=" + str(vol_acceleration) + "x, BBSqueeze=" + str(bb_squeeze_ratio) + ")" if is_pre_pump_signal else ""
    knife_status = " | ⛔ FALLING KNIFE VETADO (Caída 24h=" + str(price_change_24h_pct) + "%)" if is_falling_knife else (" | 🪤 DEAD CAT BOUNCE TRAMPA (Caída 24h=" + str(price_change_24h_pct) + "%)" if is_dead_cat_bounce else (" | ⚠️ MACRO BAJISTA DOMINANTE" if is_macro_bearish_dominance else ""))

    pattern_15m_summary = (
        f"RSI 10S={rsi_10s:.1f} | 30S={rsi_30s:.1f} | 1M={rsi_1m} | 2M={rsi_2m} | 5M={rsi_5m} | 15M={rsi_15m} | 1H={rsi_1h} | "
        f"TF: 10s={'UP' if tf_10s_up else 'DN'} 30s={'UP' if tf_30s_up else 'DN'} 1m={'UP' if tf_1m_up else 'DN'} 2m={'UP' if tf_2m_up else 'DN'} 5m={'UP' if tf_5m_up else 'DN'} 15m={'UP' if tf_15m_up else 'DN'} 1h={'UP' if tf_1h_up else 'DN'} | "
        f"FII={fii_score}/100 | VolSurge 10S={vol_surge_10s}x 30S={vol_surge_30s}x 1M={vol_surge_1m}x | "
        f"Precio 15m=${closes_15m[-1]:.4f} | MA7_15m=${ma7_15m:.4f} (Dist: {dist_from_15m_ma7_pct:+.2f}%) | "
        f"MA25_15m=${ma25_15m:.4f} | MA99_15m=${ma99_15m:.4f} | {ma99_status} | {st_status} | {vwap_status} | "
        f"{macd_status} | {gbm_status} | {pump_status}{knife_status} | "
        f"Fase={'BASE/LANZAMIENTO' if 0.0 <= dist_from_15m_ma7_pct <= 3.0 else 'SOBRE_EXTENDIDO/CIMA'} | "
        f"Patrón={yellow_arrow_status}{yellow_arrow_macro} | Canal1H={range_position_1h*100:.0f}%"
    )

    is_tradable = not (is_overextended_15m or is_at_daily_resistance_ceiling)
    final_score = 0 if not is_tradable else multi_tf_score
    rejection = overextension_reason if not is_tradable else None

    return {
        "is_valid_tradable_asset": is_tradable,
        "rejection_reason": rejection,
        "multi_tf_score": final_score,
        "fii_score": fii_score,
        "price_expansion_1d_pct": round(price_expansion_pct, 2),
        "is_overextended_15m": is_overextended_15m,
        "overextension_reason": overextension_reason,
        "is_yellow_arrow_pivot": is_yellow_arrow_pivot,
        "is_cetus_rocket_pattern": is_cetus_rocket_pattern,
        "is_ground_zero_micro_ignition": is_ground_zero_micro_ignition,
        "is_yellow_arrow_1h": is_yellow_arrow_1h,
        "is_supertrend_bullish": is_supertrend_bullish,
        "is_supertrend_1h_bullish": is_supertrend_1h_bullish,
        "is_vwap_floor_rebound": is_vwap_floor_rebound,
        "is_ma25_above_ma99_upward": is_ma25_above_ma99_upward,
        "macd_hist_15m": macd_hist_15m,
        "macd_line_15m": macd_line_15m,
        "macd_signal_15m": macd_signal_15m,
        "is_macd_bullish_cross": is_macd_bullish_cross,
        "gbm_zscore": gbm_zscore,
        "gbm_anomaly_type": gbm_anomaly_type,
        "is_crash_rebound": is_crash_rebound,
        "is_active_dump": is_active_dump,
        "is_pre_pump_signal": is_pre_pump_signal,
        "vol_acceleration": vol_acceleration,
        "bb_squeeze_ratio": bb_squeeze_ratio,
        "is_falling_knife": is_falling_knife,
        "is_dead_cat_bounce": is_dead_cat_bounce,
        "is_macro_bearish_dominance": is_macro_bearish_dominance,
        "price_change_24h_pct": price_change_24h_pct,
        "price_position_in_range": price_position_in_range,
        "range_position_1d": round(range_position_1d, 3),
        "range_position_4h": round(range_position_4h, 3),
        "range_position_2h": round(range_position_2h, 3),
        "range_position_1h": round(range_position_1h, 3),
        "range_position_30m": round(range_position_30m, 3),
        "range_position_15m": round(range_position_15m, 3),
        "range_position_10m": round(range_position_10m, 3),
        "range_position_5m": round(range_position_5m, 3),
        "range_position_2m": round(range_position_2m, 3),
        "range_position_1m": round(range_position_1m, 3),
        "target_resistance_1h_pct": target_resistance_1h_pct,
        "major_support_floor_1h_pct": major_support_floor_1h_pct,
        "expected_rr_ratio": expected_rr_ratio,
        "dist_to_24h_high_pct": dist_to_24h_high_pct,
        "is_at_daily_resistance_ceiling": is_at_daily_resistance_ceiling,
        "rsi_1d": rsi_1d,
        "rsi_4h": rsi_4h,
        "rsi_1h": rsi_1h,
        "rsi_30m": rsi_30m,
        "rsi_15m": rsi_15m,
        "pct_b_15m": round(pct_b, 2),
        "is_oversold_bounce_candidate": is_oversold_bounce_candidate,
        "is_overbought_exhaustion": is_overbought_exhaustion,
        "is_15m_red_cascade": is_15m_red_cascade,
        "is_true_structural_floor": is_true_structural_floor,
        "floor_structure_label": floor_structure_label,
        "is_sniper_timing_ready": is_sniper_timing_ready,
        "sniper_timing_label": sniper_timing_label,
        "is_1m_green_ignition": is_1m_green_ignition,
        "is_5m_higher_low": is_5m_higher_low,
        "price_above_15m_mas": price_above_15m_ma7 and price_above_15m_ma25,
        # Volúmenes sub-minuto y micro
        "vol_surge_10s": vol_surge_10s,
        "vol_surge_30s": vol_surge_30s,
        "vol_surge_1m": vol_surge_1m,
        "is_30s_micro_burst": is_30s_micro_burst,
        "vol_surge_2m": vol_surge_2m,
        "vol_surge_15m": vol_surge_15m,
        "ema9_15m": round(ema9_15m, 6),
        "ema21_15m": round(ema21_15m, 6),
        "is_ema_golden_cross": is_ema_golden_cross,
        "obv_trend": obv_trend,
        "is_obv_accumulating": is_obv_accumulating,
        "atr_15m": round(atr_15m, 6),
        "atr_pct_15m": atr_pct_15m,
        "atr_pct_1h": atr_pct_1h,
        "mfi_15m": mfi_15m,
        "is_mfi_oversold_floor": is_mfi_oversold_floor,
        "stoch_k_15m": stoch_k_15m,
        "stoch_d_15m": stoch_d_15m,
        "is_stoch_rsi_floor_pivot": is_stoch_rsi_floor_pivot,
        "dna_profile": dna_profile,
        "archetype_dna": _get_archetype_dna_safe(symbol, atr_pct_15m, close_15m),
        "predictive_dna": asset_dna_predictive_engine.analyze_multi_horizon_predictive_dna(
            symbol=symbol,
            klines_multi_tf={
                "1m": klines_1m, "2m": klines_2m, "5m": klines_5m,
                "15m": klines_15m, "30m": klines_30m, "1h": klines_1h, "4h": klines_4h, "1d": klines_1d
            },
            orderbook_info={},
            fii_score=fii_score
        ),
        "elasticity_score": elasticity_score,
        "spring_coiling": spring_coiling_info,
        "wave2_retest": wave2_retest_info,
        "dist_from_15m_ma7_pct": dist_from_15m_ma7_pct,
        "dist_from_1m_ema9_pct": dist_from_1m_ema9_pct,
        "is_1m_sniper_pullback": is_1m_sniper_pullback,
        "is_1m_fomo_extension": is_1m_fomo_extension,
        "ma25_5m": round(ma25_5m, 6),
        "relative_strength_vs_btc": relative_strength,
        "is_alt_outperforming_btc": is_alt_outperforming_btc,
        # 🧬 Suite Completa de 22 Indicadores Binance Pro
        "wma14_15m": wma14_15m,
        "cci_15m": cci_15m,
        "wr_15m": wr_15m,
        "kdj_15m": {"k": k_15m, "d": d_15m, "j": j_15m},
        "sar_15m": {"sar": sar_15m, "trend": sar_trend},
        "dmi_15m": {"plus_di": plus_di_15m, "minus_di": minus_di_15m, "adx": adx_15m},
        "trix_15m": trix_15m,
        "mtm_15m": mtm_15m,
        "emv_15m": emv_15m,
        "avl_15m": avl_15m,
        # RSI Arquitectura Completa (10s, 30s, 1m, 2m, 5m, 15m, 30m, 1h)
        "rsi_10s": rsi_10s,
        "rsi_30s": rsi_30s,
        "rsi_1m": rsi_1m,
        "rsi_2m": rsi_2m,
        "rsi_5m": rsi_5m,
        "rsi_15m": rsi_15m,
        "rsi_30m": rsi_30m,
        "rsi_1h": rsi_1h,
        "rsi_4h": rsi_4h,
        "pattern_15m_summary": pattern_15m_summary,
        "rsi_structure": {
            "rsi_10s": rsi_10s,
            "rsi_30s": rsi_30s,
            "rsi_1m": rsi_1m,
            "rsi_2m": rsi_2m,
            "rsi_5m": rsi_5m,
            "rsi_15m": rsi_15m,
            "rsi_30m": rsi_30m,
            "rsi_1h": rsi_1h,
        },
        "timeframe_alignment": {
            "10s": "BULLISH" if tf_10s_up else "BEARISH",
            "30s": "BULLISH" if tf_30s_up else "BEARISH",
            "1m": "BULLISH" if tf_1m_up else "BEARISH",
            "2m": "BULLISH" if tf_2m_up else "BEARISH",
            "5m": "BULLISH" if tf_5m_up else "BEARISH",
            "15m": "BULLISH" if tf_15m_up else "BEARISH",
            "30m": "BULLISH" if tf_30m_up else "BEARISH",
            "1h": "BULLISH" if tf_1h_up else "BEARISH",
            "1d": "BULLISH" if tf_1d_up else "BEARISH"
        },
        # ─── PATRÓN DE SUELO FRACTAL MULTITEMPORAL 8D (1M, 2M, 5M, 10M, 15M, 30M, 1H, 2H) ───
        "is_confluent_fractal_floor": is_confluent_fractal_floor,
        "is_structural_floor_ok": is_structural_floor_ok,
        "is_1m_true_floor": is_1m_true_floor,
        "is_1m_floor_zone": is_1m_floor_zone,
        "is_2m_floor_zone": is_2m_floor_zone,
        "is_5m_floor_zone": is_5m_floor_zone,
        "is_10m_floor_zone": is_10m_floor_zone,
        "is_15m_floor_zone": is_15m_floor_zone,
        "is_30m_floor_zone": is_30m_floor_zone,
        "is_1h_floor_zone": is_1h_floor_zone,
        "is_2h_floor_zone": is_2h_floor_zone,
        "lower_wick_1m_pct": lower_wick_1m_pct,
        "is_1m_lower_wick_absorption": is_1m_lower_wick_absorption,
        # ─── ADX + CCI INTELIGENCIA DE TENDENCIA (Conectados al ADN) ───
        "is_strong_trend": is_strong_trend,
        "is_bullish_trend_adx": is_bullish_trend_adx,
        "is_ranging_market": is_ranging_market,
        "is_cci_deep_oversold": is_cci_deep_oversold,
        "is_cci_overbought": is_cci_overbought,
        "adx_15m_value": adx_15m,
        "cci_15m_value": cci_15m,
        # ─── NUEVAS DIMENSIONES ADN v2 — Time-of-Day + BTC Guard + Funding + Sector ───
        "time_of_day_dna": _get_time_dna_safe(symbol),
        "btc_dominance_guard": _get_btc_guard_safe(),
        "funding_rate_dna": _get_funding_safe(symbol),
        "sector_heat_dna": asset_dna_predictive_engine.get_sector_heat(symbol, fii_score),
        "anti_reentry_check": asset_dna_predictive_engine.check_already_traded_today(symbol),
        # ─── RADIOGRAFÍA CONDUCTUAL HOLOGRÁFICA 360° DEL ACTIVO ───
        "behavioral_xray": _get_behavioral_xray_safe(
            symbol=symbol,
            klines_dict={
                "1m": klines_1m, "5m": klines_5m, "15m": klines_15m,
                "1h": klines_1h, "4h": klines_4h, "1d": klines_1d
            },
            btc_closes=btc_closes
        ),
    }

if __name__ == "__main__":
    print("Testing UUSDT:", analyze_multi_timeframe_candles("UUSDT"))
    print("Testing BTCUSDT:", analyze_multi_timeframe_candles("BTCUSDT"))
    print("Testing SOLUSDT:", analyze_multi_timeframe_candles("SOLUSDT"))
