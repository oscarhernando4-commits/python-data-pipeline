"""
Asset DNA Predictive Engine for Binance Crypto Assets
Multi-Horizon Predictive Modeling (Short-Term, Medium-Term, Long-Term),
Volatility Squeeze Detection, Order Flow CVD Acceleration, Thin Ask Vacuums,
Pump/Dump Catalyst Modeling, BTC Dominance Guard, Funding Rate Analysis,
Sector Rotation Heat Map, and Time-of-Day Session Intelligence.
"""

import math
import time
import requests
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional

# ─── Persistent HTTP session for Binance API calls ────────────────────────────
_DNA_SESSION = requests.Session()
_DNA_ADAPTER = requests.adapters.HTTPAdapter(pool_connections=5, pool_maxsize=5, max_retries=1)
_DNA_SESSION.mount("https://", _DNA_ADAPTER)

# ─── Cache for funding rates and BTC dominance (TTL 5 min) ───────────────────
_FUNDING_CACHE: Dict[str, Any] = {}
_BTC_DOM_CACHE: Dict[str, Any] = {}
_BTC_DOM_TTL = 300  # 5 minutes
_FUNDING_TTL = 180  # 3 minutes

# ─── Token → Sector mapping (Top 100 CMC Oficial) ──────────────────────────
TOKEN_SECTOR_MAP = {
    # DeFi / RWA / Yield
    "AAVE": "DeFi", "UNI": "DeFi", "ENA": "DeFi", "ONDO": "RWA", "CRV": "DeFi",
    "JUP": "DeFi", "AERO": "DeFi", "MORPHO": "DeFi", "CAKE": "DeFi", "INJ": "DeFi",
    "NEXO": "DeFi", "SKY": "DeFi", "LINK": "Oracle/DeFi", "PYTH": "Oracle",
    # Layer 1 / Core
    "BTC": "L1", "ETH": "L1", "SOL": "L1", "BNB": "L1", "XRP": "L1",
    "ADA": "L1", "AVAX": "L1", "SUI": "L1", "NEAR": "L1", "DOT": "L1",
    "ATOM": "L1", "ICP": "L1", "SEI": "L1", "APT": "L1", "TIA": "L1",
    "LTC": "Payments", "BCH": "Payments", "ETC": "L1", "XLM": "Payments", "TRX": "L1",
    "ALGO": "L1", "HBAR": "L1", "STX": "L1", "KAS": "L1", "QNT": "Infrastructure",
    # Layer 2 & Modular Infra
    "POL": "L2", "ARB": "L2", "OP": "L2", "IMX": "L2", "ETHFI": "L2", "ZRO": "L2", "STRK": "L2",
    # AI & Compute
    "TAO": "AI", "FET": "AI", "RENDER": "AI", "WLD": "AI", "FIL": "Infrastructure",
    # Memes & High-Beta Momentum
    "DOGE": "Meme", "SHIB": "Meme", "PEPE": "Meme", "PENGU": "Meme", "TRUMP": "Meme",
    "PUMP": "Meme", "WLFI": "Meme", "ASTER": "Meme", "FLOKI": "Meme", "BONK": "Meme", "WIF": "Meme",
    # Privacy / Utility
    "DASH": "Privacy", "ZEC": "Privacy", "VET": "Utility", "VIRTUAL": "AI", "SUN": "DeFi", "JST": "DeFi"
}

# ─── Sector strength tracking (updated each cycle) ───────────────────────────
_SECTOR_SCORES: Dict[str, List[float]] = {}
_TRADED_TODAY: List[str] = []  # Symbols already traded today (anti-reentry)
_TRADED_TODAY_DATE: str = ""


def get_btc_dominance_guard() -> Dict[str, Any]:
    """
    Checks BTC Dominance trend from Binance BTC 1h vs total stablecoins.
    If BTC.D rising aggressively (>0.3% in 1h), altcoins typically dump.
    Uses BTC/USDT price momentum as a proxy for dominance shift.
    """
    global _BTC_DOM_CACHE
    now = time.time()
    if _BTC_DOM_CACHE and (now - _BTC_DOM_CACHE.get("ts", 0)) < _BTC_DOM_TTL:
        return _BTC_DOM_CACHE["data"]
    
    try:
        # Get BTC 1h klines (last 4 hours) to detect dominance shift
        resp = _DNA_SESSION.get(
            "https://api.binance.com/api/v3/klines",
            params={"symbol": "BTCUSDT", "interval": "1h", "limit": 6},
            timeout=5
        )
        klines = resp.json()
        if not klines or not isinstance(klines, list):
            raise ValueError("No BTC klines")
        
        closes = [float(k[4]) for k in klines]
        current_btc = closes[-1]
        btc_1h_change = (closes[-1] - closes[-2]) / closes[-2] * 100 if len(closes) >= 2 else 0
        btc_4h_change = (closes[-1] - closes[0]) / closes[0] * 100 if len(closes) >= 4 else 0
        
        # BTC RSI (14 periods using 1h closes)
        btc_rsi = 50.0
        if len(closes) >= 6:
            gains = [max(0, closes[i] - closes[i-1]) for i in range(1, len(closes))]
            losses = [abs(min(0, closes[i] - closes[i-1])) for i in range(1, len(closes))]
            avg_gain = sum(gains) / len(gains) if gains else 0.001
            avg_loss = sum(losses) / len(losses) if losses else 0.001
            rs = avg_gain / avg_loss if avg_loss > 0 else 100
            btc_rsi = round(100 - (100 / (1 + rs)), 1)
        
        # Dominance guard logic:
        # If BTC surging (>1.5% in 1h) → capital rotating INTO BTC → altcoins dump
        # If BTC crashing (<-1.5% in 1h) → fear → altcoins also dump
        # If BTC stable (±0.5%) → altcoins can move independently
        btc_status = "NEUTRAL"
        altcoin_impact = "NEUTRAL"
        
        if btc_1h_change > 2.0:
            btc_status = "PUMP_DOMINANCE"
            altcoin_impact = "CAUTION"  # Capital flowing into BTC, altcoins may lag
        elif btc_1h_change > 0.4:
            btc_status = "BTC_LEADING"
            altcoin_impact = "POSITIVE"  # Healthy BTC rally often pulls altcoins up
        elif btc_1h_change < -1.5 or (btc_1h_change < -0.80 and btc_rsi < 35.0):
            btc_status = "BTC_CRASH"
            altcoin_impact = "AVOID"  # Fear spreading to all alts, protect 100% USDT
        elif btc_1h_change < -0.50:
            btc_status = "BTC_DECLINING"
            altcoin_impact = "CAUTION"
        else:
            btc_status = "BTC_STABLE"
            altcoin_impact = "POSITIVE" if btc_rsi >= 45 else "CAUTION"
        
        # RSI extremes add additional risk signals
        if btc_rsi > 82:
            altcoin_impact = "CAUTION"  # BTC overbought → potential correction risk
        elif btc_rsi < 32:
            altcoin_impact = "AVOID"  # BTC deep cascade momentum
        
        result = {
            "btc_price": current_btc,
            "btc_1h_change_pct": round(btc_1h_change, 2),
            "btc_4h_change_pct": round(btc_4h_change, 2),
            "btc_rsi_6h": btc_rsi,
            "btc_status": btc_status,
            "altcoin_impact": altcoin_impact,
            "should_avoid_altcoins": altcoin_impact == "AVOID",
            "should_be_cautious": altcoin_impact == "CAUTION",
        }
        _BTC_DOM_CACHE = {"ts": now, "data": result}
        return result
    except Exception as e:
        return {
            "btc_price": 0, "btc_1h_change_pct": 0, "btc_4h_change_pct": 0,
            "btc_rsi_6h": 50, "btc_status": "UNKNOWN", "altcoin_impact": "NEUTRAL",
            "should_avoid_altcoins": False, "should_be_cautious": False,
            "error": str(e)
        }


def get_funding_rate(symbol: str) -> Dict[str, Any]:
    """
    Fetches the latest perpetual futures funding rate for a symbol from Binance.
    Funding rate intelligence:
    - Positive rate (>0.02%): Longs paying shorts → market is overleveraged LONG → dump risk
    - Negative rate (<-0.02%): Shorts paying longs → bearish sentiment → potential SHORT SQUEEZE opportunity
    - Near zero (±0.01%): Neutral, no directional pressure from perps
    """
    global _FUNDING_CACHE
    cache_key = symbol.upper()
    now = time.time()
    
    if cache_key in _FUNDING_CACHE:
        cached = _FUNDING_CACHE[cache_key]
        if (now - cached.get("ts", 0)) < _FUNDING_TTL:
            return cached["data"]
    
    try:
        perp_symbol = symbol.upper()
        if not perp_symbol.endswith("USDT"):
            perp_symbol = perp_symbol + "USDT"
        
        resp = _DNA_SESSION.get(
            "https://fapi.binance.com/fapi/v1/fundingRate",
            params={"symbol": perp_symbol, "limit": 3},
            timeout=5
        )
        if resp.status_code != 200:
            # Symbol might not have perpetual futures (e.g. ZEC, BCH have limited perps)
            result = {"symbol": symbol, "funding_rate": 0.0, "funding_signal": "NO_PERPS",
                      "dump_risk_from_funding": False, "squeeze_opportunity": False, "error": f"HTTP {resp.status_code}"}
            _FUNDING_CACHE[cache_key] = {"ts": now, "data": result}
            return result
        
        rates = resp.json()
        if not rates:
            raise ValueError("Empty funding rate response")
        
        latest_rate = float(rates[-1].get("fundingRate", 0))
        rate_pct = round(latest_rate * 100, 4)
        
        if rate_pct > 0.05:
            funding_signal = "EXTREME_LONGS_OVERLEVERAGED"
            dump_risk = True
            squeeze_opp = False
        elif rate_pct > 0.02:
            funding_signal = "LONGS_DOMINANT_CAUTION"
            dump_risk = True
            squeeze_opp = False
        elif rate_pct < -0.05:
            funding_signal = "EXTREME_SHORTS_SQUEEZE_INCOMING"
            dump_risk = False
            squeeze_opp = True
        elif rate_pct < -0.02:
            funding_signal = "SHORTS_DOMINANT_POTENTIAL_SQUEEZE"
            dump_risk = False
            squeeze_opp = True
        else:
            funding_signal = "NEUTRAL_BALANCED"
            dump_risk = False
            squeeze_opp = False
        
        result = {
            "symbol": symbol,
            "funding_rate_pct": rate_pct,
            "funding_signal": funding_signal,
            "dump_risk_from_funding": dump_risk,
            "squeeze_opportunity": squeeze_opp,
        }
        _FUNDING_CACHE[cache_key] = {"ts": now, "data": result}
        return result
    except Exception as e:
        result = {"symbol": symbol, "funding_rate_pct": 0.0, "funding_signal": "UNKNOWN",
                  "dump_risk_from_funding": False, "squeeze_opportunity": False, "error": str(e)}
        _FUNDING_CACHE[cache_key] = {"ts": now, "data": result}
        return result


def get_sector_heat(symbol: str, score: float) -> Dict[str, Any]:
    """
    Tracks sector momentum: registers this token's score into its sector bucket.
    Returns which sector is hottest today and whether this token is in a hot sector.
    """
    global _SECTOR_SCORES
    asset = str(symbol).upper().replace("USDT", "").replace("USD", "")
    sector = TOKEN_SECTOR_MAP.get(asset, "Other")
    
    if sector not in _SECTOR_SCORES:
        _SECTOR_SCORES[sector] = []
    _SECTOR_SCORES[sector].append(score)
    # Keep only last 10 scores per sector
    _SECTOR_SCORES[sector] = _SECTOR_SCORES[sector][-10:]
    
    # Compute sector averages
    sector_avgs = {s: sum(scores) / len(scores) for s, scores in _SECTOR_SCORES.items() if scores}
    hottest_sector = max(sector_avgs, key=sector_avgs.get) if sector_avgs else "Unknown"
    hottest_avg = sector_avgs.get(hottest_sector, 0)
    my_sector_avg = sector_avgs.get(sector, score)
    
    is_in_hot_sector = (sector == hottest_sector) or (my_sector_avg >= 65)
    
    return {
        "token_sector": sector,
        "sector_avg_score": round(my_sector_avg, 1),
        "hottest_sector": hottest_sector,
        "hottest_sector_avg": round(hottest_avg, 1),
        "is_in_hot_sector": is_in_hot_sector,
        "sector_rotation_bonus": 10 if is_in_hot_sector else 0
    }


def check_already_traded_today(symbol: str) -> Dict[str, Any]:
    """
    Tracks symbols already traded today to avoid re-entry into exhausted tokens.
    A token that already ran +1.5% today has likely exhausted its intraday momentum.
    """
    global _TRADED_TODAY, _TRADED_TODAY_DATE
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    
    if _TRADED_TODAY_DATE != today:
        _TRADED_TODAY = []
        _TRADED_TODAY_DATE = today
    
    sym = str(symbol).upper()
    was_traded = sym in _TRADED_TODAY
    
    return {
        "symbol": sym,
        "already_traded_today": was_traded,
        "tokens_traded_today_count": len(_TRADED_TODAY),
        "tokens_traded_today": _TRADED_TODAY.copy()
    }


def register_trade_today(symbol: str):
    """Registers a symbol as traded today to prevent re-entry."""
    global _TRADED_TODAY, _TRADED_TODAY_DATE
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    if _TRADED_TODAY_DATE != today:
        _TRADED_TODAY = []
        _TRADED_TODAY_DATE = today
    sym = str(symbol).upper()
    if sym not in _TRADED_TODAY:
        _TRADED_TODAY.append(sym)



def calculate_bollinger_squeeze_ratio(closes: List[float], period: int = 20, num_std: float = 2.0) -> float:
    """
    Calculates normalized Bollinger Band Width (BBW).
    A low BBW indicates extreme volatility compression (Squeeze), historically preceding explosive moves.
    """
    if not closes or len(closes) < period:
        return 1.0
    recent = closes[-period:]
    sma = sum(recent) / period
    if sma == 0:
        return 1.0
    variance = sum((x - sma) ** 2 for x in recent) / period
    std = math.sqrt(variance)
    upper = sma + (num_std * std)
    lower = sma - (num_std * std)
    bbw_pct = round(((upper - lower) / sma) * 100.0, 3)
    return bbw_pct

def detect_thin_ask_vacuum(bids: List[List[float]], asks: List[List[float]]) -> Dict[str, Any]:
    """
    Detects if the sell side (Asks) is thin/depleted relative to the buy side (Bids) in the top 10 levels.
    When asks are depleted and buyers enter, price experiences low-friction explosive upward slippage (Pump).
    """
    if not bids or not asks:
        return {"ask_vacuum_detected": False, "liquidity_asymmetry_ratio": 1.0}
    
    top_bids_vol = sum(float(p) * float(q) for p, q in bids[:10])
    top_asks_vol = sum(float(p) * float(q) for p, q in asks[:10])
    
    ratio = round(top_bids_vol / top_asks_vol, 2) if top_asks_vol > 0 else 2.0
    vacuum_detected = bool(ratio >= 1.45)
    
    return {
        "ask_vacuum_detected": vacuum_detected,
        "liquidity_asymmetry_ratio": ratio,
        "top_bids_usdt": round(top_bids_vol, 2),
        "top_asks_usdt": round(top_asks_vol, 2)
    }

def analyze_multi_horizon_predictive_dna(
    symbol: str,
    klines_multi_tf: Dict[str, List[Any]],
    orderbook_info: Dict[str, Any],
    fii_score: int = 50,
    historical_trade_stats: Dict[str, Any] = None
) -> Dict[str, Any]:
    """
    Generates a comprehensive Multi-Horizon Predictive Asset DNA profile for the Super-Brain:
    
    1. CORTO PLAZO (10s - 15m): Ignición de volumen, Squeeze micro, Flujo CVD Taker y Retesteo.
    2. MEDIANO PLAZO (1H - 4H): Canales fractales 7D, Resistencia Techo, Squeeze 1H y Cruce EMA9/21.
    3. LARGO PLAZO (1D): Ciclo macro diario, Tendencia SuperTrend 1D, y Régimen Institucional.
    4. PREDICTOR DE PUMP vs DUMP: Probabilidad de disparo explosivo vs Riesgo de caída/trampa.
    """
    klines_1m = klines_multi_tf.get("1m", [])
    klines_5m = klines_multi_tf.get("5m", [])
    klines_15m = klines_multi_tf.get("15m", [])
    klines_1h = klines_multi_tf.get("1h", [])
    klines_4h = klines_multi_tf.get("4h", [])
    klines_1d = klines_multi_tf.get("1d", [])

    closes_1m = [float(k[4]) for k in klines_1m] if klines_1m else []
    closes_15m = [float(k[4]) for k in klines_15m] if klines_15m else []
    closes_1h = [float(k[4]) for k in klines_1h] if klines_1h else []
    closes_4h = [float(k[4]) for k in klines_4h] if klines_4h else []
    closes_1d = [float(k[4]) for k in klines_1d] if klines_1d else []

    current_price = closes_1m[-1] if closes_1m else (closes_15m[-1] if closes_15m else 1.0)

    # ── 1. HORIZONTE CORTO PLAZO (10s - 15m): Gatillo y Momentum Inmediato ────────
    bbw_15m = calculate_bollinger_squeeze_ratio(closes_15m, 20)
    is_15m_squeeze = bbw_15m <= 1.80  # Low volatility band compression
    
    cvd_ratio = orderbook_info.get("cvd_buy_ratio", 50.0)
    cvd_delta = orderbook_info.get("cvd_delta_usdt", 0.0)
    bid_dominance = orderbook_info.get("bid_dominance_pct", 50.0)
    is_bullish_cvd = orderbook_info.get("is_bullish_cvd", False)
    
    # ── 2. HORIZONTE MEDIANO PLAZO (1H - 4H): Estructura Fractal y Recorrido ───────
    bbw_1h = calculate_bollinger_squeeze_ratio(closes_1h, 20)
    is_1h_squeeze = bbw_1h <= 3.20

    highs_1h = [float(k[2]) for k in klines_1h] if klines_1h else []
    lows_1h = [float(k[3]) for k in klines_1h] if klines_1h else []
    
    resistance_1h = max(highs_1h[-24:]) if len(highs_1h) >= 24 else (max(highs_1h) if highs_1h else current_price * 1.03)
    support_1h = min(lows_1h[-24:]) if len(lows_1h) >= 24 else (min(lows_1h) if lows_1h else current_price * 0.98)
    
    target_expansion_pct = round(((resistance_1h - current_price) / current_price) * 100.0, 2) if current_price > 0 else 3.0
    support_depth_pct = round(((current_price - support_1h) / current_price) * 100.0, 2) if current_price > 0 else 1.0
    expected_rr = round(target_expansion_pct / max(0.40, support_depth_pct), 2)

    # ── 3. HORIZONTE LARGO PLAZO (1D): Ciclo Macro y Régimen de Mercado ──────────
    d_trend = "ALCISTA_EXPANSIÓN" if (len(closes_1d) >= 2 and closes_1d[-1] > closes_1d[0]) else "ACUMULACIÓN_PISO"

    # ── 4. SÍNTESIS PREDICTIVA DE CATALIZADORES (PUMP PROBABILITY vs DUMP RISK) ───
    pump_score = 0
    pump_catalysts = []
    
    if is_15m_squeeze or is_1h_squeeze:
        pump_score += 20
        pump_catalysts.append(f"Compresión de Volatilidad (Squeeze 15M={bbw_15m:.2f}%, 1H={bbw_1h:.2f}%)")
    if fii_score >= 60:
        pump_score += 25
        pump_catalysts.append(f"Inyección Institucional en Suelo (FII={fii_score}/100)")
    if is_bullish_cvd or cvd_ratio >= 55.0:
        pump_score += 20
        pump_catalysts.append(f"Flujo Taker Comprador Activo (CVD {cvd_ratio:.1f}% Compras)")
    if bid_dominance >= 55.0:
        pump_score += 15
        pump_catalysts.append(f"Muro de Soporte Comprador (Bids={bid_dominance:.1f}%)")
    if expected_rr >= 2.0:
        pump_score += 10
        pump_catalysts.append(f"Asimetría R:R Favorable ({expected_rr}:1 hacia Resistencia +{target_expansion_pct:.2f}%)")
    if target_expansion_pct >= 2.50:
        pump_score += 10
        pump_catalysts.append(f"Margen de Impulso Abierto a Resistencia (+{target_expansion_pct:.2f}%)")

    pump_probability_pct = min(98, max(5, pump_score))

    # Dump & Liquidation Risk
    dump_score = 0
    dump_warnings = []
    if bid_dominance <= 38.0:
        dump_score += 30
        dump_warnings.append(f"Pared Vendedora Pesada (Asks={100.0 - bid_dominance:.1f}%)")
    if cvd_ratio <= 40.0:
        dump_score += 25
        dump_warnings.append(f"Presión Taker Vendedora en Curso (CVD {100.0 - cvd_ratio:.1f}% Ventas)")
    if support_depth_pct > 2.50:
        dump_score += 20
        dump_warnings.append(f"Soporte Estructural Lejano (-{support_depth_pct:.2f}%)")
    if fii_score <= 30:
        dump_score += 15
        dump_warnings.append(f"Falta de Inyección de Capital (FII={fii_score}/100)")

    dump_risk_pct = min(95, max(5, dump_score))

    # ── 5. MODELACIÓN DE TRAILING STOP PERSONALIZADO POR ADN DEL TOKEN ───────────
    if pump_probability_pct >= 75 and dump_risk_pct <= 25:
        verdict = "🔥 PUMP_IMMINENT_A_PLUS"
        verdict_label = "🚀 ALTA PROBABILIDAD DE PUMP EXPLOSIVO (A+)"
        recommended_trailing_slack = 0.55
    elif pump_probability_pct >= 55 and dump_risk_pct <= 40:
        verdict = "🟢 ACCUMULATION_EXPANSION"
        verdict_label = "💎 ACUMULACIÓN Y EXPANSIÓN SALUDABLE"
        recommended_trailing_slack = 0.45
    elif dump_risk_pct >= 50:
        verdict = "🔴 DUMP_OR_TRAP_RISK"
        verdict_label = "⚠️ RIESGO DE DUMP / TRAMPA DE LIQUIDEZ"
        recommended_trailing_slack = 0.30
    else:
        verdict = "⚪ NEUTRAL_CONSOLIDATION"
        verdict_label = "🔵 CONSOLIDACIÓN NEUTRAL"
        recommended_trailing_slack = 0.40

    return {
        "symbol": symbol,
        "predictive_verdict": verdict,
        "predictive_label": verdict_label,
        "pump_probability_pct": pump_probability_pct,
        "dump_risk_pct": dump_risk_pct,
        "short_term_horizon": {
            "squeeze_15m_active": is_15m_squeeze,
            "bbw_15m_pct": bbw_15m,
            "cvd_buy_ratio": cvd_ratio,
            "cvd_delta_usdt": cvd_delta,
            "bid_dominance_pct": bid_dominance
        },
        "medium_term_horizon": {
            "squeeze_1h_active": is_1h_squeeze,
            "bbw_1h_pct": bbw_1h,
            "target_resistance_price": resistance_1h,
            "projected_target_expansion_pct": target_expansion_pct,
            "major_support_price": support_1h,
            "support_depth_pct": support_depth_pct,
            "risk_reward_ratio": expected_rr
        },
        "long_term_horizon": {
            "macro_regime": d_trend
        },
        "active_pump_catalysts": pump_catalysts,
        "active_dump_warnings": dump_warnings,
        "recommended_trailing_slack_pct": recommended_trailing_slack
    }

def detect_spring_coiling_compression(klines_1m: List[Any], klines_2m: List[Any] = None) -> Dict[str, Any]:
    """
    ⚡ DETECTOR DE COMPRESIÓN DE RESORTE (SPRING COILING) EN MICRO-TIMEFRAMES (1M / 2M):
    Inspirado en la anatomía fractal de DCR/USDT:
    Cuando MA7, MA25 y MA99 en 1m o 2m convergen en un rango estrecho (distancia <= 0.35%),
    la volatilidad se comprime al máximo antes del estallido de la Ola 3.
    """
    if not klines_1m or len(klines_1m) < 25:
        return {"is_spring_compressed": False, "spread_pct": 1.0, "spring_bonus": 0, "label": "Normal"}
    
    closes_1m = [float(k[4]) for k in klines_1m]
    ma7_1m = sum(closes_1m[-7:]) / 7.0
    ma25_1m = sum(closes_1m[-25:]) / 25.0
    ma99_1m = sum(closes_1m[-99:]) / 99.0 if len(closes_1m) >= 99 else ma25_1m
    
    # Measure spread between MA7 and MA25
    spread_7_25 = abs(ma7_1m - ma25_1m) / ma25_1m * 100.0 if ma25_1m > 0 else 1.0
    spread_25_99 = abs(ma25_1m - ma99_1m) / ma99_1m * 100.0 if ma99_1m > 0 else 1.0
    
    is_tight_squeeze = spread_7_25 <= 0.35
    is_full_squeeze = spread_7_25 <= 0.35 and spread_25_99 <= 0.85
    
    # Check if price is above MA25/MA99 floor
    c_now = closes_1m[-1]
    is_bullish_aligned = c_now >= ma25_1m * 0.998
    
    if is_full_squeeze and is_bullish_aligned:
        return {
            "is_spring_compressed": True,
            "spread_pct": round(spread_7_25, 2),
            "spring_bonus": 25,
            "label": "🚀 RESORTE COMPRIMIDO TOTAL (MA7 ≈ MA25 ≈ MA99 en 1M)"
        }
    elif is_tight_squeeze and is_bullish_aligned:
        return {
            "is_spring_compressed": True,
            "spread_pct": round(spread_7_25, 2),
            "spring_bonus": 15,
            "label": "⚡ COMPRESIÓN ACTIVA (MA7 ≈ MA25 en 1M)"
        }
    
    return {"is_spring_compressed": False, "spread_pct": round(spread_7_25, 2), "spring_bonus": 0, "label": "Disperso"}


def detect_wave2_ma25_retest_support(klines_15m: List[Any]) -> Dict[str, Any]:
    """
    💎 DETECTOR DE RETESTEO SANO A LA MA25 EN OLA 2 (ARQUETIPO DCR/USDT):
    Identifica activos que tuvieron una expansión inicial (Ola 1), retrocedieron ordenadamente
    y ahora se apoyan con firmeza sobre la MA25 de 15m/30m sin perforarla.
    Punto de entrada con máximo ratio Beneficio/Riesgo (R:R > 3:1).
    """
    if not klines_15m or len(klines_15m) < 25:
        return {"is_wave2_retest": False, "dist_to_ma25_pct": 1.0, "retest_bonus": 0, "label": "Sin retesteo"}
    
    closes_15m = [float(k[4]) for k in klines_15m]
    highs_15m = [float(k[2]) for k in klines_15m]
    
    ma25_15m = sum(closes_15m[-25:]) / 25.0
    ma99_15m = sum(closes_15m[-99:]) / 99.0 if len(closes_15m) >= 99 else ma25_15m * 0.95
    c_now = closes_15m[-1]
    
    # 1. Check if there was an expansion wave in recent 20 candles
    recent_peak = max(highs_15m[-20:])
    peak_expansion_pct = ((recent_peak - ma25_15m) / ma25_15m) * 100.0 if ma25_15m > 0 else 0.0
    had_prior_expansion = peak_expansion_pct >= 3.0  # Impulso previo >= +3.0%
    
    # 2. Check if price is currently resting on MA25 (within -0.5% to +1.2%)
    dist_to_ma25 = ((c_now - ma25_15m) / ma25_15m) * 100.0 if ma25_15m > 0 else 0.0
    is_resting_on_ma25 = -0.6 <= dist_to_ma25 <= 1.3
    
    # 3. Check if MA25 is above MA99 (Macro Bullish Structure)
    is_macro_bullish = ma25_15m > ma99_15m
    
    if had_prior_expansion and is_resting_on_ma25 and is_macro_bullish:
        return {
            "is_wave2_retest": True,
            "peak_expansion_pct": round(peak_expansion_pct, 2),
            "dist_to_ma25_pct": round(dist_to_ma25, 2),
            "retest_bonus": 25,
            "label": f"💎 RETESTEO DE ORO OLA 2 (Pico previo +{peak_expansion_pct:.1f}% | Apoyo en MA25 a {dist_to_ma25:+.2f}%)"
        }
    
    return {
        "is_wave2_retest": False,
        "peak_expansion_pct": round(peak_expansion_pct, 2),
        "dist_to_ma25_pct": round(dist_to_ma25, 2),
        "retest_bonus": 0,
        "label": "Estructura Estándar"
    }

def calculate_asset_behavioral_xray(
    symbol: str,
    klines_multi_tf: Dict[str, List[Any]],
    btc_15m_closes: List[float] = None
) -> Dict[str, Any]:
    """
    🔬 RADIOGRAFÍA CONDUCTUAL HOLOGRÁFICA 360° DEL ADN DEL ACTIVO:
    Analiza con precisión milimétrica:
    1. Canal Fractal (% desde el suelo) en 1M, 5M, 15M, 1H, 4H, 1D.
    2. Comportamiento y Arquetipo Dinámico (Sprinter, Trend Runner, Mean Reverter, Zombi).
    3. Alpha y Desacoplamiento vs Bitcoin (Relative Strength Divergence).
    4. Absorción de Compradores en Suelo (Mecha Inferior en 1M/5M).
    """
    klines_1m = klines_multi_tf.get("1m", [])
    klines_5m = klines_multi_tf.get("5m", [])
    klines_15m = klines_multi_tf.get("15m", [])
    klines_1h = klines_multi_tf.get("1h", [])
    klines_4h = klines_multi_tf.get("4h", [])
    klines_1d = klines_multi_tf.get("1d", [])

    closes_1m = [float(k[4]) for k in klines_1m] if klines_1m else []
    closes_15m = [float(k[4]) for k in klines_15m] if klines_15m else []
    
    def get_channel_pos(klines, period=20):
        if not klines or len(klines) < 2: return 50.0
        h = max([float(k[2]) for k in klines[-period:]])
        l = min([float(k[3]) for k in klines[-period:]])
        c = float(klines[-1][4])
        rng = h - l
        return round(((c - l) / rng) * 100.0, 1) if rng > 0 else 50.0

    pos_1m = get_channel_pos(klines_1m, 15)
    pos_5m = get_channel_pos(klines_5m, 15)
    pos_15m = get_channel_pos(klines_15m, 20)
    pos_1h = get_channel_pos(klines_1h, 24)
    pos_4h = get_channel_pos(klines_4h, 20)
    pos_1d = get_channel_pos(klines_1d, 14)

    # Lower Wick Absorption on 1m (Dip Buying Intensity)
    wicks_1m = []
    for k in klines_1m[-5:]:
        o, h, l, c = float(k[1]), float(k[2]), float(k[3]), float(k[4])
        body_bottom = min(o, c)
        candle_rng = h - l
        lower_wick = (body_bottom - l) / candle_rng if candle_rng > 0 else 0.0
        wicks_1m.append(lower_wick)
    avg_wick_1m = round((sum(wicks_1m) / len(wicks_1m)) * 100.0, 1) if wicks_1m else 0.0

    # Alpha Divergence vs BTC
    alpha_divergence = 0.0
    if btc_15m_closes and len(btc_15m_closes) >= 3 and len(closes_15m) >= 3 and symbol != "BTCUSDT":
        btc_15m_chg = ((btc_15m_closes[-1] - btc_15m_closes[-3]) / btc_15m_closes[-3]) * 100.0
        alt_15m_chg = ((closes_15m[-1] - closes_15m[-3]) / closes_15m[-3]) * 100.0
        alpha_divergence = round(alt_15m_chg - btc_15m_chg, 2)

    # Volatility Elasticity ATR 15M
    atr_pct_15m = 0.30
    if len(klines_15m) >= 14:
        highs_15m = [float(k[2]) for k in klines_15m]
        lows_15m = [float(k[3]) for k in klines_15m]
        trs = [max(highs_15m[i] - lows_15m[i], abs(highs_15m[i] - closes_15m[i-1]), abs(lows_15m[i] - closes_15m[i-1])) for i in range(1, len(closes_15m))]
        if trs:
            atr = sum(trs[-14:]) / min(len(trs), 14)
            atr_pct_15m = round((atr / closes_15m[-1]) * 100.0, 3) if closes_15m[-1] > 0 else 0.30

    # DCR Fractal Patterns: Spring Coiling & Wave 2 MA25 Retest
    spring_res = detect_spring_coiling_compression(klines_1m)
    wave2_res = detect_wave2_ma25_retest_support(klines_15m)

    # Dynamic Behavioral Categorization (Enriched with DCR Multi-Timeframe Patterns)
    if wave2_res.get("is_wave2_retest"):
        behavior_type = "PULLBACK_INSTITUCIONAL_ELITE (Retesteo MA25 Ola 2)"
        timing_advice = "💎 Setup A+ (Arquetipo DCR): Soporte firme en MA25 tras rotura macro. R:R óptimo > 3:1."
    elif spring_res.get("is_spring_compressed"):
        behavior_type = "RESORTE_COMPRIMIDO (Spring Coiling 1M)"
        timing_advice = "🚀 Setup A+ (Arquetipo DCR): Medias comprimidas en micro-base. Disparo de Ola 3 inminente."
    elif atr_pct_15m < 0.25:
        behavior_type = "ZOMBI_LENTO (Baja Volatilidad)"
        timing_advice = "⛔ Evitar: Rango insuficiente para scalping."
    elif atr_pct_15m >= 0.70 or pos_1m > 80:
        behavior_type = "SPRINT_EXPLOSIVO (Alta Elasticidad)"
        timing_advice = "⚡ Entrada rápida en base 1M con salida Wick Sniper."
    elif pos_1h <= 45 and pos_15m <= 50 and alpha_divergence > 0:
        behavior_type = "BASE_INSTITUCIONAL_ELITE (Suelo con Alpha)"
        timing_advice = "💎 Setup A+: Suelo 1H + Fuerza Relativa frente a Bitcoin."
    else:
        behavior_type = "ROTACIÓN_ESTRUCTURAL (Onda Normal)"
        timing_advice = "🎯 Entrada constructiva en soporte con R:R > 2:1."

    return {
        "behavior_type": behavior_type,
        "timing_advice": timing_advice,
        "spring_coiling": spring_res,
        "wave2_retest": wave2_res,
        "fractal_channel_pct": {
            "1m": pos_1m, "5m": pos_5m, "15m": pos_15m,
            "1h": pos_1h, "4h": pos_4h, "1d": pos_1d
        },
        "lower_wick_absorption_1m_pct": avg_wick_1m,
        "alpha_vs_btc_15m_pct": alpha_divergence,
        "atr_15m_pct": atr_pct_15m
    }

if __name__ == "__main__":
    test_res = analyze_multi_horizon_predictive_dna(
        "SUIUSDT",
        klines_multi_tf={},
        orderbook_info={"bid_dominance_pct": 58.0, "cvd_buy_ratio": 62.0, "is_bullish_cvd": True},
        fii_score=70
    )
    import json
    print(json.dumps(test_res, indent=2, ensure_ascii=False))
