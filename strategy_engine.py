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
    
    # GROUP 0: Replica Real (Algoritmo actual de alta confluencia)
    if group_id == 0:
        if score >= 85:
            return {"action": "LONG", "use_ai": True, "reason": "Score >= 85 (G-0)"}
        elif score <= 15:
            return {"action": "SHORT", "use_ai": True, "reason": "Score <= 15 (G-0)"}
            
    # GROUP 1: Ultra-Estricto (Tendencia Fuerte Pullback)
    elif group_id == 1:
        if trend == "Alcista" and score >= 85 and 40 <= rsi <= 60:
            return {"action": "LONG", "use_ai": True, "reason": "Trend Alcista + Pullback RSI + Score Alto (G-1)"}
            
    # GROUP 2: Reversión a la Media (Caza-Rebotes mecánicos sin IA)
    elif group_id == 2:
        # Buy extreme oversold with MACD divergence starting
        if rsi <= 30 and macd_hist > -0.05:  # Histograma perdiendo fuerza bajista
            return {"action": "LONG", "use_ai": False, "reason": "Oversold RSI < 30 Bounce (G-2)"}
            
    # GROUP 3: Breakout por Volumen (Mecánico)
    elif group_id == 3:
        if vol_surge >= 2.0 and rsi > 55 and trend == "Alcista":
            return {"action": "LONG", "use_ai": False, "reason": "Volume Surge > 2.0x Breakout (G-3)"}
            
    # GROUP 4: Enfoque Bajista (Short-Seller con IA)
    elif group_id == 4:
        if rsi >= 70 and macd_hist < 0 and trend == "Bajista":
            return {"action": "SHORT", "use_ai": True, "reason": "Overbought RSI > 70 + MACD Cross + Bear Trend (G-4)"}
        elif score <= 25:
            return {"action": "SHORT", "use_ai": True, "reason": "Score <= 25 (G-4)"}
            
    # GROUP 5: Kamikaze (Relajado, IA máxima delegación)
    elif group_id == 5:
        if score >= 60:
            return {"action": "LONG", "use_ai": True, "reason": "Score > 60 (Kamikaze G-5)"}
        elif score <= 40:
            return {"action": "SHORT", "use_ai": True, "reason": "Score < 40 (Kamikaze G-5)"}

    return {"action": "HOLD", "use_ai": False, "reason": ""}
