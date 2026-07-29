import json
import real_money_trader
import analytics
import sys

sys.stdout.reconfigure(encoding='utf-8')

print("=== INICIANDO OPERACIÓN KAMIKAZE FORZADA EN CUENTA REAL ===")

try:
    best_symbol = "BTCUSDT"
    
    print(f"Buscando precio actual para {best_symbol}...")
    tech = analytics.analyze_institutional_grade(best_symbol, account_balance=100.0, risk_percentage=1.0)
    price = tech["current_price"]
    
    print(f"Forzando compra LONG en {best_symbol} a precio ${price} por orden del Creador...")
    
    # is_learned_signal=True bypasses all score thresholds!
    res = real_money_trader.evaluate_and_trade_real_money(
        best_symbol=best_symbol,
        best_score=100, 
        current_price=price,
        is_bearish=False,  # False = Force LONG (Spot), True = Force SHORT (Futures)
        is_learned_signal=True
    )
    
    print("\n✅ ESTADO DE LA CUENTA REAL ACTUALIZADO:")
    print(json.dumps(res, indent=4, ensure_ascii=False))

except Exception as e:
    print(f"ERROR FORZANDO OPERACIÓN: {e}")
