"""
Asset DNA Predictive Engine for Binance Crypto Assets
Multi-Horizon Predictive Modeling (Short-Term, Medium-Term, Long-Term),
Volatility Squeeze Detection, Order Flow CVD Acceleration, Thin Ask Vacuums,
and Pump/Dump Catalyst Modeling for the Gemini Super-Brain.
"""

import math
from typing import Dict, Any, List

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

if __name__ == "__main__":
    test_res = analyze_multi_horizon_predictive_dna(
        "SUIUSDT",
        klines_multi_tf={},
        orderbook_info={"bid_dominance_pct": 58.0, "cvd_buy_ratio": 62.0, "is_bullish_cvd": True},
        fii_score=70
    )
    import json
    print(json.dumps(test_res, indent=2, ensure_ascii=False))
