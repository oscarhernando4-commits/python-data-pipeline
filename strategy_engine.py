"""
Unified Quantitative Strategy Engine — Real Account Parity
===========================================================
Eliminates fragmented groups and sub-groups.
All 1,000 parallel accounts execute under the EXACT same ecosystem, rules,
8D Harmonic Base Matrix, FII, OBV, and Volume filters as the Real Account
(standard A+ mode, without extreme sniper constraints).
"""

import os
import json

THRESHOLDS_FILE = os.path.join(os.path.dirname(__file__), "dynamic_thresholds.json")

def load_thresholds():
    default_t = {
        "group_0": {
            "long_score": 55,
            "min_fii": 46,
            "max_canal_1h": 0.55,
            "max_rsi_15m": 60,
            "min_vol_surge": 0.20
        }
    }
    if not os.path.exists(THRESHOLDS_FILE):
        return default_t
    try:
        with open(THRESHOLDS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            if "group_0" in data:
                return data
            return default_t
    except Exception:
        return default_t

def evaluate_opportunity(tech, group_id=0):
    """
    Evaluates a symbol's technical data against the UNIFIED Real Account A+ Standard Strategy.
    All 1,000 parallel simulation accounts evaluate under identical conditions:
    1. 8D Harmonic Base Matrix (1M<=38%, 5M<=42%, 10M<=45%, 15M<=48%, 30M<=52%, 1H<=55%, 2H<=60%)
    2. Floor Turnaround (1M/2M green, lower wick absorption, VWAP floor rebound, bullish divergence)
    3. Floor Injection Index (FII >= 46, and FII >= 65 if RSI 15M >= 40)
    4. OBV Accumulation (not distributing)
    5. Active Volume & Ignition (vol_1m >= 0.20x and active volume surge/ignition)
    6. Vetoes: Not falling knife, not dead cat bounce, not at daily resistance ceiling, not 5M dump
    7. Spot LONG only (Score >= 55)

    Returns: {"action": "LONG"|"HOLD", "use_ai": bool, "reason": str}
    """
    inds = tech.get("indicators", {})
    mtf = tech.get("mtf_analysis", {})
    score = tech.get("confluence_score", 50)
    
    # 1. Check Falling Knife / Dead Cat / Daily Ceiling
    is_knife = inds.get("is_falling_knife", False) or mtf.get("is_falling_knife", False)
    is_dead_cat = inds.get("is_dead_cat_bounce", False) or mtf.get("is_dead_cat_bounce", False)
    is_daily_ceiling = mtf.get("is_at_daily_resistance_ceiling", False)
    
    if is_knife or is_dead_cat or is_daily_ceiling:
        return {
            "action": "HOLD",
            "use_ai": False,
            "reason": "⛔ Descartado por Cuchillo Cayendo, Rebote Gato Muerto o Techo Diario"
        }

    # 2. OBV Flow Check
    obv_trend = mtf.get("obv_trend", inds.get("obv_trend", "NEUTRAL"))
    if obv_trend == "DISTRIBUTING":
        return {
            "action": "HOLD",
            "use_ai": False,
            "reason": "⛔ Descartado por Distribución Institucional (OBV=DISTRIBUTING)"
        }

    # 3. 8D Harmonic Base Matrix Check (Multi-Temporal Proportional)
    r1m = mtf.get("range_position_1m", 0.50)
    r2m = mtf.get("range_position_2m", 0.50)
    r5m = mtf.get("range_position_5m", 0.50)
    r10m = mtf.get("range_position_10m", 0.50)
    r15m = mtf.get("range_position_15m", 0.50)
    r30m = mtf.get("range_position_30m", 0.50)
    r1h = mtf.get("range_position_1h", 0.50)
    r2h = mtf.get("range_position_2h", 0.50)
    r4h = mtf.get("range_position_4h", 0.50)
    r1d = mtf.get("range_position_1d", 0.50)

    # Convert to 0.0-1.0 float if in 0-100 scale
    r1m = r1m / 100.0 if r1m > 1.0 else r1m
    r2m = r2m / 100.0 if r2m > 1.0 else r2m
    r5m = r5m / 100.0 if r5m > 1.0 else r5m
    r10m = r10m / 100.0 if r10m > 1.0 else r10m
    r15m = r15m / 100.0 if r15m > 1.0 else r15m
    r30m = r30m / 100.0 if r30m > 1.0 else r30m
    r1h = r1h / 100.0 if r1h > 1.0 else r1h
    r2h = r2h / 100.0 if r2h > 1.0 else r2h
    r4h = r4h / 100.0 if r4h > 1.0 else r4h
    r1d = r1d / 100.0 if r1d > 1.0 else r1d

    # 3. 8D Harmonic Base Matrix Check (Matriz Cuántica Simulaciones: Inicia en 1M <= 38%)
    # Las 1,000 simulaciones operan a partir de 38% para recopilar experiencia y aprendizaje continuo.
    is_8d_base = (
        r1m <= 0.38 and
        r2m <= 0.40 and
        r5m <= 0.42 and
        r10m <= 0.45 and
        r15m <= 0.48 and
        r30m <= 0.52 and
        r1h <= 0.55 and
        r2h <= 0.60 and
        r4h <= 0.65 and
        r1d <= 0.70
    )

    if not is_8d_base:
        return {
            "action": "HOLD",
            "use_ai": False,
            "reason": f"⛔ Fuera de Matriz 8D [1M={r1m*100:.0f}% (max 38) 5M={r5m*100:.0f}% 15M={r15m*100:.0f}% 1H={r1h*100:.0f}%]"
        }


    # 4. Floor Turnaround
    tf_1m_up = mtf.get("tf_1m_up", False)
    tf_2m_up = mtf.get("tf_2m_up", False)
    is_1m_wick = mtf.get("is_1m_lower_wick_absorption", False)
    is_vwap_rebound = mtf.get("is_vwap_floor_rebound", False)
    is_bullish_div = mtf.get("is_bullish_divergence", False)
    is_yellow_arrow = mtf.get("is_yellow_arrow_pivot", False)
    is_ema_cross = mtf.get("is_ema_golden_cross", False)

    has_floor_turnaround = (
        tf_1m_up or tf_2m_up or is_1m_wick or is_vwap_rebound or
        is_bullish_div or is_yellow_arrow or is_ema_cross
    )

    if not has_floor_turnaround:
        return {
            "action": "HOLD",
            "use_ai": False,
            "reason": "⛔ Falta de Giro de Suelo en 1M/2M"
        }

    # 5. Floor Injection Index (FII) & Anti-RENDER Filter
    fii = mtf.get("fii_score", inds.get("fii_score", 0))
    rsi_15m = mtf.get("rsi_15m", inds.get("rsi_15m", 50.0))

    if fii < 46:
        return {
            "action": "HOLD",
            "use_ai": False,
            "reason": f"⛔ FII bajo ({fii} < 46)"
        }

    if rsi_15m >= 40.0 and fii < 65:
        return {
            "action": "HOLD",
            "use_ai": False,
            "reason": f"⛔ FII insuficiente con RSI neutral (RSI15M={rsi_15m:.1f}, FII={fii} < 65)"
        }

    # 6. Volume & Ignition Check
    vol_1m = mtf.get("vol_surge_1m", inds.get("vol_surge_1m", 1.0))
    vol_15m = mtf.get("vol_surge_15m", inds.get("vol_surge_15m", 1.0))
    vol_2m = mtf.get("vol_surge_2m", inds.get("vol_surge_2m", 1.0))
    vol_acc = mtf.get("vol_acceleration", 1.0)
    is_spring = mtf.get("spring_coiling", {}).get("is_spring_compressed", False)
    is_wave2 = mtf.get("wave2_retest", {}).get("is_wave2_retest", False)
    is_pre_pump = mtf.get("is_pre_pump_signal", False)
    is_30s_burst = mtf.get("is_30s_micro_burst", False)

    if vol_1m < 0.20:
        return {
            "action": "HOLD",
            "use_ai": False,
            "reason": f"⛔ Volumen 1M muerto ({vol_1m:.2f}x < 0.20x)"
        }

    has_active_ignition = (
        (vol_1m >= 0.50 and vol_15m >= 0.15) or
        (vol_2m >= 0.50 and vol_15m >= 0.15) or
        (vol_15m >= 0.50) or
        (vol_1m >= 0.80) or
        (vol_acc >= 1.10 and vol_15m >= 0.15) or
        (fii >= 60 and vol_1m >= 0.25) or
        is_spring or is_wave2 or is_pre_pump or is_30s_burst
    )

    if not has_active_ignition:
        return {
            "action": "HOLD",
            "use_ai": False,
            "reason": "⛔ Sin ignición activa de volumen"
        }

    # 7. Confluence Score Check
    if score < 55:
        return {
            "action": "HOLD",
            "use_ai": False,
            "reason": f"⛔ Score insuficiente ({score} < 55)"
        }

    # 🎯 ALL UNIFIED REAL A+ STANDARD CRITERIA MET -> LONG
    reason_str = (
        f"💎 REAL A+ CONFLUENCIA: 8D Base [1M:{r1m*100:.0f}% 5M:{r5m*100:.0f}% 15M:{r15m*100:.0f}% 1H:{r1h*100:.0f}%] "
        f"| FII={fii} | Vol={vol_1m:.2f}x | RSI15m={rsi_15m:.1f} | Score={score}/100 | OBV={obv_trend}"
    )

    return {
        "action": "LONG",
        "use_ai": False,
        "reason": reason_str
    }
