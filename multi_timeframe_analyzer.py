"""
Multi-Timeframe Historical Candle Analyzer & Anti-Stablecoin Filter Engine
Inspects 2m, 5m, 15m, 1h, 4h, 1d historical candle behavior.
Rejects stablecoins, dollar synthetics, flat assets, and unconfirmed trends.
Includes: MACD(12,26,9), GBM Crash Detector, SuperTrend(10,3), Yellow Arrow MA7/MA25, VWAP.
"""

import requests
import math
import numpy as np
from datetime import datetime
from quant_institutional import GBMAnomalyDetector

# Comprehensive Blacklist of Stablecoins, Pegged Tokens, and Synthetic Dollars
STABLECOIN_TICKERS = {
    "U", "UUSDT", "USD", "USDE", "USD0", "USDS", "USDF", "USDC", "FDUSD", "PYUSD",
    "TUSD", "BUSD", "DAI", "USDD", "RLUSD", "USD1", "EUR", "AEUR", "WBTC", "TBTC",
    "SNDK", "SNDKB", "CRCLB", "SPCXB", "QQQB", "USDT", "USTC", "FRAX", "USDK", "VAI"
}

# High-Risk Meme Tokens, Seed Tag Assets, and Ultra-Volatile Low-Liquidity Speculative Assets
HIGH_RISK_MEME_TICKERS = {
    "BANANAS31", "BANANAS31USDT", "1000CAT", "1000CHEEMS", "1000SATS", "1MBABYDOGE",
    "BROCCOLI714", "SNXXB", "LUNA", "LUNC", "USTC", "NEIRO", "TURBO", "1000PEPE",
    "1000SHIB", "1000BONK", "1000FLOKI", "1000RATS", "1000WHY", "1000MOG", "CHEEMS",
    "1000CATUSDT", "1000SATSUSDT", "1MBABYDOGEUSDT", "BROCCOLI714USDT"
}

try:
    from api_connector import get_proxy
except ImportError:
    get_proxy = None

def is_stablecoin(symbol):
    """
    Strictly checks if a symbol is a stablecoin, synthetic dollar, or high-risk meme/seed asset.
    Returns True if symbol is blocked from real money trading.
    """
    sym_upper = str(symbol).upper().strip()
    asset = sym_upper.replace("USDT", "").replace("USD", "")
    
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
    """Fetches Binance public klines without proxy if available, or using proxy rotation."""
    url = "https://api.binance.com/api/v3/klines"
    params = {"symbol": symbol, "interval": interval, "limit": limit}
    try:
        res = requests.get(url, params=params, timeout=5)
        if res.status_code == 200:
            return res.json()
    except Exception:
        pass
        
    # Fallback with proxy (dynamic rotation)
    if get_proxy:
        try:
            res = requests.get(url, params=params, proxies=get_proxy(), timeout=8)
            if res.status_code == 200:
                return res.json()
        except Exception:
            pass
    return []

def calculate_rsi(closes, period=14):
    """Calculates Relative Strength Index (RSI) for a price series."""
    if not closes or len(closes) < period + 1:
        return 50.0
    gains = []
    losses = []
    for i in range(1, len(closes)):
        diff = closes[i] - closes[i-1]
        if diff > 0:
            gains.append(diff)
            losses.append(0.0)
        else:
            gains.append(abs(diff))
            losses.append(abs(diff))
            
    if len(gains) < period:
        return 50.0
        
    avg_gain = sum(gains[-period:]) / period
    avg_loss = sum(losses[-period:]) / period
    
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
        
    # 2. Fetch Multi-Timeframe Klines (1m->2m, 5m, 15m, 1h, 4h, 1d)
    klines_1m = fetch_klines_public(symbol, "1m", 40)
    klines_2m = _aggregate_1m_to_2m(klines_1m)
    klines_5m = fetch_klines_public(symbol, "5m", 30)
    klines_15m = fetch_klines_public(symbol, "15m", 50)
    klines_1h = fetch_klines_public(symbol, "1h", 30)
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
    
    # 3. Detect Pegged / Zero-Volatility Assets (Price ~ $1.00 and 1d Range < 1.5%)
    if 0.95 <= avg_price <= 1.05 and price_expansion_pct < 1.5:
        return {
            "is_valid_tradable_asset": False,
            "rejection_reason": f"Asset {symbol} descalificado: Comportamiento plano de Stablecoin (Rango 1D: {price_expansion_pct:.2f}%)",
            "multi_tf_score": 0
        }
        
    # Parse 2m, 5m, 15m, 1h, 4h closes & volumes
    closes_2m = [float(k[4]) for k in klines_2m] if klines_2m else []
    vols_2m = [float(k[5]) for k in klines_2m] if klines_2m else []
    closes_5m = [float(k[4]) for k in klines_5m]
    closes_15m = [float(k[4]) for k in klines_15m]
    vols_15m = [float(k[5]) for k in klines_15m]
    closes_1h = [float(k[4]) for k in klines_1h] if klines_1h else closes_15m
    closes_4h = [float(k[4]) for k in klines_4h] if klines_4h else closes_15m
    
    tf_2m_up = closes_2m[-1] > closes_2m[0] if closes_2m else False
    tf_5m_up = closes_5m[-1] > closes_5m[0] if closes_5m else False
    tf_15m_up = closes_15m[-1] > closes_15m[0] if closes_15m else False
    tf_1h_up = closes_1h[-1] > closes_1h[0] if closes_1h else False
    tf_4h_up = closes_4h[-1] > closes_4h[0] if closes_4h else False
    tf_1d_up = d_closes[-1] > d_closes[0] if d_closes else False
    
    # Calculate 3-Tier Multi-Timeframe RSI Architecture
    rsi_2m = calculate_rsi(closes_2m)
    rsi_5m = calculate_rsi(closes_5m)
    rsi_15m = calculate_rsi(closes_15m)
    rsi_1h = calculate_rsi(closes_1h)
    rsi_4h = calculate_rsi(closes_4h)
    
    # 2m Microstructure Volume Surge
    avg_vol_2m = sum(vols_2m[-5:]) / len(vols_2m[-5:]) if len(vols_2m) >= 5 else 1.0
    vol_surge_2m = round(vols_2m[-1] / avg_vol_2m, 2) if (vols_2m and avg_vol_2m > 0) else 1.0
    
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

    # Fetch REAL 24h change from Binance /ticker/24hr API
    price_change_24h_pct = 0.0
    try:
        ticker_res = requests.get("https://api.binance.com/api/v3/ticker/24hr", params={"symbol": symbol}, timeout=3)
        if ticker_res.status_code == 200:
            price_change_24h_pct = round(float(ticker_res.json().get("priceChangePercent", 0)), 2)
    except Exception:
        # Fallback to daily candle approximation
        price_change_24h_pct = round(((closes_15m[-1] - d_closes[-2]) / d_closes[-2]) * 100.0, 2) if (len(d_closes) >= 2 and d_closes[-2] > 0) else 0.0

    # Macro bearish count: how many of 1h, 4h, 1d are bearish
    macro_bearish_count = sum([not tf_1h_up, not tf_4h_up, not tf_1d_up])

    # Falling Knife V2: Relaxed OR-logic (any 2 of these 4 conditions triggers the guard)
    falling_knife_signals = 0
    if price_change_24h_pct < -8.0:              # Real 24h drop > 8%
        falling_knife_signals += 1
    if price_position_in_range < 25.0:           # Price crushed to bottom of range
        falling_knife_signals += 1
    if ma7_15m < ma25_15m:                       # MA7 below MA25 (bearish structure)
        falling_knife_signals += 1
    if macro_bearish_count >= 2:                  # At least 2 of 3 macro TFs are bearish
        falling_knife_signals += 1

    is_falling_knife = (falling_knife_signals >= 2) and (price_change_24h_pct < -5.0)

    # Dead Cat Bounce Filter: micro-bounces on 2m/5m during a crash are traps, NOT buy signals
    is_dead_cat_bounce = (
        price_change_24h_pct < -8.0 and         # Crashed > 8% in real 24h
        price_position_in_range < 35.0 and      # Still near the bottom of the range
        (tf_2m_up or tf_5m_up) and              # Micro-timeframe shows a bounce (the trap)
        macro_bearish_count >= 2                  # But macro structure is still bearish
    )

    # Macro Bearish Dominance: 1h + 4h + 1d ALL bearish = heavy penalty
    is_macro_bearish_dominance = (
        macro_bearish_count == 3 and             # All three macro TFs bearish
        price_position_in_range < 30.0           # Price in bottom 30% of range
    )

    # Detect RSI Bullish Divergence (Price Lower Low + RSI Higher Low = Early Floor Reversal)
    is_bullish_divergence = False
    if len(closes_15m) >= 10:
        recent_low = min(closes_15m[-5:])
        prev_low = min(closes_15m[-10:-5])
        if recent_low < prev_low:
            recent_rsi = calculate_rsi(closes_15m[-5:])
            prev_rsi = calculate_rsi(closes_15m[-10:-5])
            if recent_rsi > prev_rsi + 3.0:
                is_bullish_divergence = True

    # Calculate VWAP (Volume-Weighted Average Price) & Standard Deviation Bands
    cum_pv = sum(((float(k[2]) + float(k[3]) + float(k[4])) / 3.0) * float(k[5]) for k in klines_15m[-20:]) if klines_15m else 0.0
    cum_vol = sum(float(k[5]) for k in klines_15m[-20:]) if klines_15m else 0.0
    vwap_15m = (cum_pv / cum_vol) if cum_vol > 0 else closes_15m[-1]
    vwap_std = float(np.std(closes_15m[-20:])) if len(closes_15m) >= 20 else 0.001
    vwap_lower_band = vwap_15m - (1.5 * vwap_std)
    is_vwap_floor_rebound = (closes_15m[-1] <= vwap_lower_band) or (closes_15m[-1] < vwap_15m and (float(klines_15m[-1][3]) <= vwap_lower_band))

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

    # Calculate SuperTrend (10, 3) Pattern Indicator on 15m, 1h, and 4h (As requested by user)
    is_supertrend_bullish = False
    if len(klines_15m) >= 10:
        atr_10 = sum(max(float(k[2]) - float(k[3]), abs(float(k[2]) - float(klines_15m[i-1][4])), abs(float(k[3]) - float(klines_15m[i-1][4]))) for i, k in enumerate(klines_15m[-10:], start=len(klines_15m)-10)) / 10.0
        hl2 = (float(klines_15m[-1][2]) + float(klines_15m[-1][3])) / 2.0
        st_lower = hl2 - (3.0 * atr_10)
        is_supertrend_bullish = closes_15m[-1] > st_lower and closes_15m[-1] > ma7_15m

    # 1H & 4H SuperTrend (10,3) & Yellow Arrow (MA7/MA25) Indicators
    is_supertrend_1h_bullish = False
    ma7_1h = sum(closes_1h[-7:]) / len(closes_1h[-7:]) if len(closes_1h) >= 7 else closes_1h[-1]
    ma25_1h = sum(closes_1h[-25:]) / len(closes_1h[-25:]) if len(closes_1h) >= 25 else closes_1h[-1]
    is_yellow_arrow_1h = (closes_1h[-1] >= ma7_1h) and (ma7_1h >= ma25_1h)
    if len(klines_1h) >= 10:
        atr_1h_10 = sum(max(float(k[2]) - float(k[3]), abs(float(k[2]) - float(klines_1h[i-1][4])), abs(float(k[3]) - float(klines_1h[i-1][4]))) for i, k in enumerate(klines_1h[-10:], start=len(klines_1h)-10)) / 10.0
        hl2_1h = (float(klines_1h[-1][2]) + float(klines_1h[-1][3])) / 2.0
        st_lower_1h = hl2_1h - (3.0 * atr_1h_10)
        is_supertrend_1h_bullish = closes_1h[-1] > st_lower_1h

    is_supertrend_4h_bullish = False
    ma7_4h = sum(closes_4h[-7:]) / len(closes_4h[-7:]) if len(closes_4h) >= 7 else closes_4h[-1]
    ma25_4h = sum(closes_4h[-25:]) / len(closes_4h[-25:]) if len(closes_4h) >= 25 else closes_4h[-1]
    is_yellow_arrow_4h = (closes_4h[-1] >= ma7_4h) and (ma7_4h >= ma25_4h)
    if len(klines_4h) >= 10:
        atr_4h_10 = sum(max(float(k[2]) - float(k[3]), abs(float(k[2]) - float(klines_4h[i-1][4])), abs(float(k[3]) - float(klines_4h[i-1][4]))) for i, k in enumerate(klines_4h[-10:], start=len(klines_4h)-10)) / 10.0
        hl2_4h = (float(klines_4h[-1][2]) + float(klines_4h[-1][3])) / 2.0
        st_lower_4h = hl2_4h - (3.0 * atr_4h_10)
        is_supertrend_4h_bullish = closes_4h[-1] > st_lower_4h

    # Multi-Timeframe Alignment Score (0 to 100) including MACD, GBM, Pre-Pump, SuperTrend & Yellow Arrow
    score_components = [
        tf_2m_up * 10,
        tf_5m_up * 20,
        tf_15m_up * 25,
        tf_1h_up * 20,
        tf_4h_up * 10,
        tf_1d_up * 15,
        15 if is_bullish_divergence else 0,
        15 if is_vwap_floor_rebound else 0,
        10 if is_supertrend_bullish else 0,
        20 if is_ma25_above_ma99_upward else 0,
        25 if is_ma7_above_ma25_upward else 0,
        15 if is_supertrend_1h_bullish else 0,
        15 if is_supertrend_4h_bullish else 0,
        15 if (is_yellow_arrow_1h or is_yellow_arrow_4h) else 0,
        10 if is_macd_bullish_cross else 0,
        20 if is_crash_rebound else 0,
        25 if is_pre_pump_signal else 0
    ]
    multi_tf_score = min(100, sum(score_components))
    
    if is_ma25_below_ma99_downward:
        multi_tf_score = 0
    if is_active_dump:
        multi_tf_score = 0
    if is_falling_knife:
        multi_tf_score = 0
    if is_dead_cat_bounce:
        multi_tf_score = 0
    if is_macro_bearish_dominance and multi_tf_score > 30:
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
        is_yellow_arrow_pivot = (0.0 <= dist_from_15m_ma7_pct <= 3.0) and (lower_wick_pct >= 20.0 or close_15m > open_15m) and (tf_5m_up or tf_2m_up)
        yellow_arrow_status = "🎯 PATRÓN FLECHAS AMARILLAS (REBOTE PIVOTE A+ EN MA7/MA25)" if is_yellow_arrow_pivot else "⚪ NEUTRAL 15M"

        # Peak Proximity Guard: Check if price is within 1.5% of the 24h High
        dist_from_24h_high_pct = round(((d_highs[-1] - close_15m) / close_15m) * 100.0, 2) if (d_highs and close_15m > 0) else 999.0

        # Spike up followed by rejection wick (buying top trap)
        is_green_candle = close_15m >= open_15m
        upper_wick_ratio = (upper_wick / candle_range) if candle_range > 0 else 0.0
        # Adaptive wick threshold: 50% for healthy green candles (Shooting Star standard), 35% for red/reversal candles
        wick_threshold = 0.50 if is_green_candle else 0.35
        
        if candle_range > 0 and upper_wick_ratio > wick_threshold and (high_15m - low_15m) / low_15m > 0.012:
            is_overextended_15m = True
            overextension_reason = f"Mecha superior de reversión en vela de 15m ({upper_wick_ratio*100:.1f}% del rango, umbral={wick_threshold*100:.0f}%)"
        elif dist_from_24h_high_pct <= 1.0 and price_expansion_pct >= 6.0:
            is_overextended_15m = True
            overextension_reason = f"Entrada en el Pico Máximo 24H (Precio a solo {dist_from_24h_high_pct}% del máximo 24H de ${d_highs[-1]:.4f}). Exige compra en el suelo."
        elif close_15m > open_15m and ((close_15m - open_15m) / open_15m) * 100.0 > 4.0:
            is_overextended_15m = True
            overextension_reason = f"Vela de 15m sobre-extendida en la cima (+{((close_15m - open_15m) / open_15m) * 100.0:.2f}%)"
        elif dist_from_15m_ma7_pct > 2.5:
            is_overextended_15m = True
            overextension_reason = f"Entrada tardía en la cima de 15m (Precio a +{dist_from_15m_ma7_pct}% sobre MA7). Exige ruptura fresca <= 2.5%"
        elif (not price_above_15m_ma7 and not price_above_15m_ma25) and not (is_oversold_bounce_candidate or is_yellow_arrow_pivot or is_bullish_divergence or is_ma7_above_ma25_upward):
            is_overextended_15m = True
            overextension_reason = f"Tendencia bajista sin estructura de rebote en el suelo"
    avg_vol_15m = sum(vols_15m[-5:]) / len(vols_15m[-5:]) if len(vols_15m) >= 5 else 1.0
    vol_surge_15m = round(vols_15m[-1] / avg_vol_15m, 2) if avg_vol_15m > 0 else 1.0

    st_status = "🟢 SUPERTREND 15M/1H/4H VERDE ALCISTA" if (is_supertrend_bullish and is_supertrend_1h_bullish and is_supertrend_4h_bullish) else ("🟢 SUPERTREND 15M VERDE" if is_supertrend_bullish else "🔴 SUPERTREND ROJO")
    vwap_status = "🟢 REBOTE PISO VWAP (-1.5 StdDev)" if is_vwap_floor_rebound else "⚪ NORMAL VWAP"
    ma99_status = "🚀 CRUCE ALCISTA MA25/MA99 (PULSO HACIA ARRIBA)" if is_ma25_above_ma99_upward else "⚪ NORMAL MA99"
    yellow_arrow_macro = f" | 🎯 FLECHAS AMARILLAS MACRO 1H/4H" if (is_yellow_arrow_1h or is_yellow_arrow_4h) else ""
    macd_status = "🟢 MACD CRUCE ALCISTA" if is_macd_bullish_cross else "🔴 MACD BAJISTA"
    gbm_status = f"💥 REBOTE POST-CRASH (Z={gbm_zscore:.1f})" if is_crash_rebound else (f"⛔ DUMP ACTIVO (Z={gbm_zscore:.1f})" if is_active_dump else f"⚪ GBM NORMAL (Z={gbm_zscore:.1f})")

    pump_status = "🚀 PRE-PUMP DETECTADO (VolAcc=" + str(vol_acceleration) + "x, BBSqueeze=" + str(bb_squeeze_ratio) + ")" if is_pre_pump_signal else ""
    knife_status = " | ⛔ FALLING KNIFE VETADO (Caída 24h=" + str(price_change_24h_pct) + "%)" if is_falling_knife else (" | 🪤 DEAD CAT BOUNCE TRAMPA (Caída 24h=" + str(price_change_24h_pct) + "%)" if is_dead_cat_bounce else (" | ⚠️ MACRO BAJISTA DOMINANTE" if is_macro_bearish_dominance else ""))

    pattern_15m_summary = (
        f"RSI Triggers: 2m={rsi_2m} | 5m={rsi_5m} || Contexto Medio: 15m={rsi_15m} || Contexto Macro: 1h={rsi_1h} | 4h={rsi_4h} | "
        f"2m={'UP' if tf_2m_up else 'DOWN'} (VolSurge2m={vol_surge_2m}x) | "
        f"Precio 15m=${closes_15m[-1]:.4f} | MA7_15m=${ma7_15m:.4f} (Distancia: {dist_from_15m_ma7_pct:+.2f}%) | "
        f"MA25_15m=${ma25_15m:.4f} | MA99_15m=${ma99_15m:.4f} | {ma99_status} | {st_status} | {vwap_status} | "
        f"{macd_status} | {gbm_status} | {pump_status}{knife_status} | "
        f"Fase 15m={'RUPTURA_FRESCA (INICIO)' if 0.0 <= dist_from_15m_ma7_pct <= 3.0 else 'SOBRE_EXTENDIDO (CIMA)'} | "
        f"Patrón={yellow_arrow_status}{yellow_arrow_macro} | VolSurge 15m={vol_surge_15m}x"
    )

    return {
        "is_valid_tradable_asset": True,
        "rejection_reason": None,
        "multi_tf_score": multi_tf_score,
        "price_expansion_1d_pct": round(price_expansion_pct, 2),
        "is_overextended_15m": is_overextended_15m,
        "overextension_reason": overextension_reason,
        "is_yellow_arrow_pivot": is_yellow_arrow_pivot,
        "is_yellow_arrow_1h": is_yellow_arrow_1h,
        "is_yellow_arrow_4h": is_yellow_arrow_4h,
        "is_supertrend_bullish": is_supertrend_bullish,
        "is_supertrend_1h_bullish": is_supertrend_1h_bullish,
        "is_supertrend_4h_bullish": is_supertrend_4h_bullish,
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
        "pct_b_15m": round(pct_b, 2),
        "is_oversold_bounce_candidate": is_oversold_bounce_candidate,
        "is_overbought_exhaustion": is_overbought_exhaustion,
        "is_bullish_divergence": is_bullish_divergence,
        "price_above_15m_mas": price_above_15m_ma7 and price_above_15m_ma25,
        "vol_surge_2m": vol_surge_2m,
        "vol_surge_15m": vol_surge_15m,
        "pattern_15m_summary": pattern_15m_summary,
        "rsi_structure": {
            "rsi_2m": rsi_2m,
            "rsi_5m": rsi_5m,
            "rsi_15m": rsi_15m,
            "rsi_1h": rsi_1h,
            "rsi_4h": rsi_4h
        },
        "timeframe_alignment": {
            "2m": "BULLISH" if tf_2m_up else "BEARISH",
            "5m": "BULLISH" if tf_5m_up else "BEARISH",
            "15m": "BULLISH" if tf_15m_up else "BEARISH",
            "1h": "BULLISH" if tf_1h_up else "BEARISH",
            "4h": "BULLISH" if tf_4h_up else "BEARISH",
            "1d": "BULLISH" if tf_1d_up else "BEARISH"
        }
    }

if __name__ == "__main__":
    print("Testing UUSDT:", analyze_multi_timeframe_candles("UUSDT"))
    print("Testing BTCUSDT:", analyze_multi_timeframe_candles("BTCUSDT"))
    print("Testing SOLUSDT:", analyze_multi_timeframe_candles("SOLUSDT"))
