import os
import json

THRESHOLDS_FILE = os.path.join(os.path.dirname(__file__), "dynamic_thresholds.json")

def load_thresholds():
    default_t = {
      "group_0": {"long_score": 80, "short_score": 20},
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
    Returns: {"action": "LONG"|"SHORT"|"HOLD", "use_ai": bool, "reason": str}
    """
    score = tech.get("confluence_score", 50)
    inds = tech.get("indicators", {})
    rsi = inds.get("rsi_15m", 50)
    macd_hist = inds.get("macd_hist_15m", 0)
    vol_surge = inds.get("volume_surge_ratio", 1.0)
    trend = tech.get("macro_trend_4h", "Neutral")
    
    t = load_thresholds()
    
    # GROUP 0: Replica Real (Algoritmo actual de alta confluencia)
    if group_id == 0:
        if score >= t["group_0"]["long_score"]:
            return {"action": "LONG", "use_ai": True, "reason": f"Score >= {t['group_0']['long_score']} (G-0)"}
        elif score <= t["group_0"]["short_score"]:
            return {"action": "SHORT", "use_ai": True, "reason": f"Score <= {t['group_0']['short_score']} (G-0)"}
            
    # GROUP 1: Ultra-Estricto (Tendencia Fuerte Pullback)
    elif group_id == 1:
        trend_ok = (trend == "BULLISH") if t.get("group_1", {}).get("require_trend", True) else True
        if trend_ok and score >= t["group_1"]["long_score"] and t["group_1"]["rsi_min"] <= rsi <= t["group_1"]["rsi_max"]:
            return {"action": "LONG", "use_ai": True, "reason": "Trend Alcista + Pullback RSI + Score Alto (G-1)"}
            
    # GROUP 2: Reversión a la Media (Caza-Rebotes + Inteligencia Artificial)
    elif group_id == 2:
        macd_l = t.get("group_2", {}).get("macd_long", -0.1)
        macd_s = t.get("group_2", {}).get("macd_short", 0.1)
        # Buy extreme oversold with MACD divergence starting
        if rsi <= t["group_2"]["long_rsi"] and macd_hist > macd_l:
            return {"action": "LONG", "use_ai": True, "reason": f"Oversold RSI < {t['group_2']['long_rsi']} Bounce (G-2)"}
        # Short extreme overbought
        elif rsi >= t["group_2"]["short_rsi"] and macd_hist < macd_s:
            return {"action": "SHORT", "use_ai": True, "reason": f"Overbought RSI > {t['group_2']['short_rsi']} Bounce (G-2)"}
            
    # GROUP 3: Breakout por Volumen (Volumen + Inteligencia Artificial)
    elif group_id == 3:
        trend_ok = (trend == "BULLISH") if t.get("group_3", {}).get("require_trend", False) else True
        if vol_surge >= t["group_3"]["vol_surge"] and rsi > t["group_3"]["long_rsi"] and trend_ok:
            return {"action": "LONG", "use_ai": True, "reason": f"Volume Surge > {t['group_3']['vol_surge']} Breakout (G-3)"}
            
    # GROUP 4: Enfoque Bajista (Short-Seller con IA)
    elif group_id == 4:
        trend_ok = (trend == "BEARISH") if t.get("group_4", {}).get("require_trend", False) else True
        if rsi >= t["group_4"]["short_rsi"] and macd_hist < 0 and trend_ok:
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
