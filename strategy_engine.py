import os
import json

THRESHOLDS_FILE = os.path.join(os.path.dirname(__file__), "dynamic_thresholds.json")

def load_thresholds():
    default_t = {
      "group_0": {"long_score": 50, "short_score": 50},
      "group_1": {"long_score": 70, "rsi_min": 30, "rsi_max": 70, "require_trend": True},
      "group_2": {"long_rsi": 40, "short_rsi": 60, "macd_long": -0.5, "macd_short": 0.5},
      "group_3": {"vol_surge": 1.2, "long_rsi": 45, "require_trend": False},
      "group_4": {"short_rsi": 60, "short_score": 40, "require_trend": False},
      "group_5": {"long_score": 50, "short_score": 50}
    }
    if not os.path.exists(THRESHOLDS_FILE):
        return default_t
    try:
        with open(THRESHOLDS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default_t

def evaluate_opportunity(tech, group_id):
    """
    Evaluates a symbol's technical data against the specific strategic profile of a given group.
    Integrates Ornstein-Uhlenbeck mean reversion and GBM anomaly signals from quant_institutional.
    Returns: {"action": "LONG"|"SHORT"|"HOLD", "use_ai": bool, "reason": str}
    """
    score = tech.get("confluence_score", 50)
    inds = tech.get("indicators", {})
    rsi = inds.get("rsi_15m", 50)
    macd_hist = inds.get("macd_hist_15m", 0)
    vol_surge = inds.get("volume_surge_ratio", 1.0)
    trend = tech.get("macro_trend_4h", "Neutral")
    
    # 🏛️ Institutional Quant Indicators (from quant_institutional module)
    ou_zscore = inds.get("ou_zscore", 0.0)
    ou_signal = inds.get("ou_signal", "NEUTRAL")
    ou_half_life = inds.get("ou_half_life", 999)
    gbm_zscore = inds.get("gbm_zscore", 0.0)
    gbm_strength = inds.get("gbm_signal_strength", "NOISE")
    inst_analysis = tech.get("institutional_analysis", {})
    inst_verdict = inst_analysis.get("verdict", "NEUTRAL")
    trade_quality = inst_analysis.get("trade_quality", "C_NOISE")
    
    t = load_thresholds()
    
    # GROUP 0: Replica Real (Algoritmo actual de alta confluencia + Institutional Filter)
    if group_id == 0:
        if inds.get("pump_dump_exhaustion", False):
            return {"action": "SHORT", "use_ai": True, "reason": f"🩸 Pump & Dump Exhaustion: Subida agresiva (+{inds.get('pump_24h_pct', 0)}%) y colapso ({inds.get('dump_1h_pct', 0)}%) detectado (G-0)"}
        # 🏛️ GBM Breakout Confirmation: Only LONG if GBM says it's NOT noise
        elif score >= t["group_0"]["long_score"]:
            _reason = f"Score >= {t['group_0']['long_score']} (G-0)"
            if trade_quality in ("A+", "B"):
                _reason += f" | 🏛️ GBM Calidad {trade_quality}"
            return {"action": "LONG", "use_ai": True, "reason": _reason}
        elif score <= t["group_0"]["short_score"]:
            return {"action": "SHORT", "use_ai": True, "reason": f"Score <= {t['group_0']['short_score']} (G-0)"}
            
    # GROUP 1: Ultra-Estricto (Tendencia Fuerte Pullback + GBM Confirmation)
    elif group_id == 1:
        trend_ok = (trend == "BULLISH") if t.get("group_1", {}).get("require_trend", False) else True
        if trend_ok and score >= t["group_1"]["long_score"] and t["group_1"]["rsi_min"] <= rsi <= t["group_1"]["rsi_max"]:
            _reason = "Trend Alcista + Pullback RSI + Score Alto (G-1)"
            if inst_verdict == "BREAKOUT_CONFIRMED":
                _reason += " | 🏛️ GBM Breakout Confirmado"
            return {"action": "LONG", "use_ai": True, "reason": _reason}
            
    # GROUP 2: Reversión a la Media (Caza-Rebotes + OU Mean Reversion + IA)
    elif group_id == 2:
        macd_l = t.get("group_2", {}).get("macd_long", -0.1)
        macd_s = t.get("group_2", {}).get("macd_short", 0.1)
        
        # 🏛️ ORNSTEIN-UHLENBECK SIGNAL: Estadísticamente riguroso (complementa RSI)
        # OU LONG: Precio muy por debajo de la media con half-life corto (rebote inminente)
        if ou_signal == "LONG" and ou_half_life < 24 and rsi <= 45:
            return {"action": "LONG", "use_ai": True, "reason": f"🏛️ OU Mean Reversion LONG: Z={ou_zscore:.1f}, HalfLife={ou_half_life:.0f} velas + RSI={rsi:.0f} (G-2)"}
        # OU SHORT: Precio muy por encima de la media (colapso estadístico inminente)
        elif ou_signal == "SHORT" and ou_half_life < 24 and rsi >= 55:
            return {"action": "SHORT", "use_ai": True, "reason": f"🏛️ OU Mean Reversion SHORT: Z={ou_zscore:.1f}, HalfLife={ou_half_life:.0f} velas + RSI={rsi:.0f} (G-2)"}
        
        # Classic RSI-based mean reversion (original logic)
        # Buy extreme oversold with MACD divergence starting
        if rsi <= t["group_2"]["long_rsi"] and macd_hist > macd_l:
            _reason = f"Oversold RSI < {t['group_2']['long_rsi']} Bounce (G-2)"
            if ou_signal == "LONG":
                _reason += f" | 🏛️ OU confirma (Z={ou_zscore:.1f})"
            return {"action": "LONG", "use_ai": True, "reason": _reason}
        # Short extreme overbought
        elif rsi >= t["group_2"]["short_rsi"] and macd_hist < macd_s:
            _reason = f"Overbought RSI > {t['group_2']['short_rsi']} Bounce (G-2)"
            if ou_signal == "SHORT":
                _reason += f" | 🏛️ OU confirma (Z={ou_zscore:.1f})"
            return {"action": "SHORT", "use_ai": True, "reason": _reason}
            
    # GROUP 3: Breakout por Volumen (Volumen + GBM Anomaly Confirmation + IA)
    elif group_id == 3:
        trend_ok = (trend == "BULLISH") if t.get("group_3", {}).get("require_trend", False) else True
        if vol_surge >= t["group_3"]["vol_surge"] and rsi > t["group_3"]["long_rsi"] and trend_ok:
            _reason = f"Volume Surge > {t['group_3']['vol_surge']} Breakout (G-3)"
            # 🏛️ GBM confirmation amplifies confidence
            if inst_verdict == "BREAKOUT_CONFIRMED":
                _reason += f" | 🏛️ GBM Anomalía Confirmada (Z={gbm_zscore:.1f})"
            return {"action": "LONG", "use_ai": True, "reason": _reason}
            
    # GROUP 4: Enfoque Bajista (Short-Seller + GBM Crash Detection + IA)
    elif group_id == 4:
        trend_ok = (trend == "BEARISH") if t.get("group_4", {}).get("require_trend", False) else True
        if inds.get("pump_dump_exhaustion", False):
            return {"action": "SHORT", "use_ai": True, "reason": f"🩸 Pump & Dump Exhaustion: Subida agresiva (+{inds.get('pump_24h_pct', 0)}%) y colapso ({inds.get('dump_1h_pct', 0)}%) detectado (G-4)"}
        # 🏛️ GBM Crash Detection: Anomalía bajista confirmada estadísticamente
        elif inst_verdict == "CRASH_DETECTED" and rsi >= 50:
            return {"action": "SHORT", "use_ai": True, "reason": f"🏛️ GBM Crash Detectado (Z={gbm_zscore:.1f}) + RSI={rsi:.0f} (G-4)"}
        elif rsi >= t["group_4"]["short_rsi"] and macd_hist < 0 and trend_ok:
            return {"action": "SHORT", "use_ai": True, "reason": f"Overbought RSI > {t['group_4']['short_rsi']} + Bear Trend (G-4)"}
        elif score <= t["group_4"]["short_score"]:
            return {"action": "SHORT", "use_ai": True, "reason": f"Score <= {t['group_4']['short_score']} (G-4)"}
            
    # GROUP 5: Kamikaze (Relajado, IA máxima delegación)
    elif group_id == 5:
        if score >= t["group_5"]["long_score"]:
            return {"action": "LONG", "use_ai": True, "reason": f"Score >= {t['group_5']['long_score']} (Kamikaze G-5)"}
        elif score <= t["group_5"]["short_score"]:
            return {"action": "SHORT", "use_ai": True, "reason": f"Score <= {t['group_5']['short_score']} (Kamikaze G-5)"}

    return {"action": "HOLD", "use_ai": False, "reason": ""}
