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
        if score >= 80:
            return {"action": "LONG", "use_ai": True, "reason": "Score >= 80 (G-0)"}
        elif score <= 20:
            return {"action": "SHORT", "use_ai": True, "reason": "Score <= 20 (G-0)"}
            
    # GROUP 1: Ultra-Estricto (Tendencia Fuerte Pullback)
    elif group_id == 1:
        if trend == "BULLISH" and score >= 80 and 35 <= rsi <= 65:
            return {"action": "LONG", "use_ai": True, "reason": "Trend Alcista + Pullback RSI + Score Alto (G-1)"}
            
    # GROUP 2: Reversión a la Media (Caza-Rebotes + Inteligencia Artificial)
    elif group_id == 2:
        # Buy extreme oversold with MACD divergence starting
        if rsi <= 35 and macd_hist > -0.1:
            return {"action": "LONG", "use_ai": True, "reason": "Oversold RSI < 35 Bounce (G-2)"}
        # Short extreme overbought
        elif rsi >= 65 and macd_hist < 0.1:
            return {"action": "SHORT", "use_ai": True, "reason": "Overbought RSI > 65 Bounce (G-2)"}
            
    # GROUP 3: Breakout por Volumen (Volumen + Inteligencia Artificial)
    elif group_id == 3:
        if vol_surge >= 1.5 and rsi > 50 and trend == "BULLISH":
            return {"action": "LONG", "use_ai": True, "reason": "Volume Surge > 1.5x Breakout (G-3)"}
            
    # GROUP 4: Enfoque Bajista (Short-Seller con IA)
    elif group_id == 4:
        if rsi >= 65 and macd_hist < 0 and trend == "BEARISH":
            return {"action": "SHORT", "use_ai": True, "reason": "Overbought RSI > 65 + MACD Cross + Bear Trend (G-4)"}
        elif score <= 35:
            return {"action": "SHORT", "use_ai": True, "reason": "Score <= 35 (G-4)"}
            
    # GROUP 5: Kamikaze (Relajado, IA máxima delegación)
    elif group_id == 5:
        if score >= 55:
            return {"action": "LONG", "use_ai": True, "reason": "Score >= 55 (Kamikaze G-5)"}
        elif score <= 45:
            return {"action": "SHORT", "use_ai": True, "reason": "Score <= 45 (Kamikaze G-5)"}

    return {"action": "HOLD", "use_ai": False, "reason": ""}
