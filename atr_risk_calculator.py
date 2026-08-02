"""
Adaptive ATR Volatility Risk & Stop-Loss Calculator
Computes dynamic, volatility-adjusted Stop Loss levels based on 15m Average True Range (ATR).
Prevents premature stop-outs on high-volatility alts while maintaining tight precision on low-volatility assets.
"""

def calculate_adaptive_atr_stop_loss(current_price, atr_15m, min_sl_pct=0.8, max_sl_pct=2.5, multiplier=1.5):
    """
    Calculates adaptive Stop Loss percentage based on asset ATR volatility.
    - atr_pct: (atr_15m / current_price) * 100.0
    - dynamic_sl_pct: clamped between min_sl_pct (0.8%) and max_sl_pct (2.5%)
    Returns dict with sl_pct, sl_price, tp1_price, tp2_price, and volatility_regime.
    """
    if current_price <= 0:
        return {
            "sl_pct": 1.0,
            "sl_price": 0.0,
            "volatility_regime": "⚪ Neutral (Fallback)"
        }
        
    atr_val = atr_15m if (atr_15m and atr_15m > 0) else (current_price * 0.008)
    atr_pct = (atr_val / current_price) * 100.0
    
    # Calculate raw adaptive SL
    raw_sl_pct = atr_pct * multiplier
    
    # Clamp between min_sl_pct (0.8%) and max_sl_pct (2.5%)
    clamped_sl_pct = max(min_sl_pct, min(max_sl_pct, raw_sl_pct))
    clamped_sl_pct = round(clamped_sl_pct, 2)
    
    sl_price = current_price * (1.0 - (clamped_sl_pct / 100.0))
    tp1_price = current_price * (1.0 + ((clamped_sl_pct * 2.0) / 100.0))  # 1:2 R:R Ratio
    
    if clamped_sl_pct <= 1.0:
        vol_regime = "🟢 Volatilidad Baja / Ajuste Quirúrgico"
    elif clamped_sl_pct <= 1.8:
        vol_regime = "🔵 Volatilidad Estándar / Margen Óptimo"
    else:
        vol_regime = "🔥 Volatilidad Alta / Colchón Adaptativo"
        
    return {
        "sl_pct": clamped_sl_pct,
        "sl_price": round(sl_price, 4 if sl_price > 1.0 else 6),
        "tp1_price": round(tp1_price, 4 if tp1_price > 1.0 else 6),
        "atr_pct": round(atr_pct, 2),
        "volatility_regime": vol_regime
    }

if __name__ == "__main__":
    print("BTC Adaptativo:", calculate_adaptive_atr_stop_loss(63150.0, 320.0))
    print("INJ Adaptativo:", calculate_adaptive_atr_stop_loss(4.99, 0.045))
