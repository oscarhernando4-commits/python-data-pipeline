"""
Multi-Timeframe Historical Candle Analyzer & Anti-Stablecoin Filter Engine
Inspects 5m, 15m, 1h, 4h, 1d, and 7d historical candle behavior.
Rejects stablecoins, dollar synthetics, flat assets, and unconfirmed trends.
"""

import requests
import math
import numpy as np
from datetime import datetime

# Comprehensive Blacklist of Stablecoins, Pegged Tokens, and Synthetic Dollars
STABLECOIN_TICKERS = {
    "U", "UUSDT", "USD", "USDE", "USD0", "USDS", "USDF", "USDC", "FDUSD", "PYUSD",
    "TUSD", "BUSD", "DAI", "USDD", "RLUSD", "USD1", "EUR", "AEUR", "WBTC", "TBTC",
    "SNDK", "SNDKB", "CRCLB", "SPCXB", "QQQB", "USDT", "USTC", "FRAX", "USDK", "VAI"
}

try:
    from api_connector import get_proxy
except ImportError:
    get_proxy = None

def is_stablecoin(symbol):
    """
    Strictly checks if a symbol is a stablecoin or synthetic dollar.
    Returns True if symbol is blocked.
    """
    sym_upper = str(symbol).upper().strip()
    asset = sym_upper.replace("USDT", "").replace("USD", "")
    
    # 1. Direct Ticker Match
    if sym_upper in STABLECOIN_TICKERS or asset in STABLECOIN_TICKERS:
        return True
        
    # 2. Ticker Pattern Heuristics (single-letter or dollar synthetics)
    if len(asset) <= 1:
        return True
    if "USD" in asset or "EUR" in asset or "BUSD" in asset or "TUSD" in asset:
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
    klines_15m = fetch_klines_public(symbol, "15m", 30)
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

    # 15m Microstructure moving averages (MA7, MA25) & Volume Surge
    ma7_15m = sum(closes_15m[-7:]) / len(closes_15m[-7:]) if len(closes_15m) >= 7 else closes_15m[-1]
    ma25_15m = sum(closes_15m[-25:]) / len(closes_15m[-25:]) if len(closes_15m) >= 25 else closes_15m[-1]
    
    # Strict MA25 calculation: Slope must be ascending and price must be strictly +0.15% above MA25
    prev_ma25_15m = sum(closes_15m[-26:-1]) / len(closes_15m[-26:-1]) if len(closes_15m) >= 26 else ma25_15m
    ma25_slope_ok = ma25_15m >= (prev_ma25_15m * 0.9995)
    
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

    # Multi-Timeframe Alignment Score (0 to 100) including 2m synchronization + Divergence Bonus
    score_components = [
        tf_2m_up * 10,
        tf_5m_up * 15,
        tf_15m_up * 25,
        tf_1h_up * 20,
        tf_4h_up * 15,
        tf_1d_up * 15,
        15 if is_bullish_divergence else 0
    ]
    multi_tf_score = min(100, sum(score_components))
    
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

        # Spike up followed by rejection wick (buying top trap)
        if candle_range > 0 and (upper_wick / candle_range) > 0.35 and (high_15m - low_15m) / low_15m > 0.012:
            is_overextended_15m = True
            overextension_reason = f"Mecha superior de reversión en vela de 15m ({upper_wick/candle_range*100:.1f}% del rango)"
        elif close_15m > open_15m and ((close_15m - open_15m) / open_15m) * 100.0 > 4.0:
            is_overextended_15m = True
            overextension_reason = f"Vela de 15m sobre-extendida en la cima (+{((close_15m - open_15m) / open_15m) * 100.0:.2f}%)"
        elif dist_from_15m_ma7_pct > 3.0:
            is_overextended_15m = True
            overextension_reason = f"Entrada tardía en la cima de 15m (Precio a +{dist_from_15m_ma7_pct}% sobre MA7). Exige ruptura fresca <= 3.0%"
        elif not price_above_15m_ma7 or not price_above_15m_ma25:
            is_overextended_15m = True
            overextension_reason = f"Precio de 15m por debajo de medias móviles (Precio: {closes_15m[-1]} < MA7: {ma7_15m:.4f} / MA25: {ma25_15m:.4f})"
    avg_vol_15m = sum(vols_15m[-5:]) / len(vols_15m[-5:]) if len(vols_15m) >= 5 else 1.0
    vol_surge_15m = round(vols_15m[-1] / avg_vol_15m, 2) if avg_vol_15m > 0 else 1.0

    pattern_15m_summary = (
        f"RSI Triggers: 2m={rsi_2m} | 5m={rsi_5m} || Contexto Medio: 15m={rsi_15m} || Contexto Macro: 1h={rsi_1h} | 4h={rsi_4h} | "
        f"2m={'UP' if tf_2m_up else 'DOWN'} (VolSurge2m={vol_surge_2m}x) | "
        f"Precio 15m=${closes_15m[-1]:.4f} | MA7_15m=${ma7_15m:.4f} (Distancia: {dist_from_15m_ma7_pct:+.2f}%) | "
        f"MA25_15m=${ma25_15m:.4f} | Por encima MA7/MA25={'SÍ' if price_above_15m_ma7 and price_above_15m_ma25 else 'NO'} | "
        f"Fase 15m={'RUPTURA_FRESCA (INICIO)' if 0.0 <= dist_from_15m_ma7_pct <= 3.0 else 'SOBRE_EXTENDIDO (CIMA)'} | "
        f"Patrón={yellow_arrow_status} | VolSurge 15m={vol_surge_15m}x"
    )

    return {
        "is_valid_tradable_asset": True,
        "rejection_reason": None,
        "multi_tf_score": multi_tf_score,
        "price_expansion_1d_pct": round(price_expansion_pct, 2),
        "is_overextended_15m": is_overextended_15m,
        "overextension_reason": overextension_reason,
        "is_yellow_arrow_pivot": is_yellow_arrow_pivot,
        "pct_b_15m": round(pct_b, 2),
        "is_oversold_bounce_candidate": is_oversold_bounce_candidate,
        "is_overbought_exhaustion": is_overbought_exhaustion,
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
