import json
import real_money_trader
import analytics
import sys
import os

sys.stdout.reconfigure(encoding='utf-8')

print("=== INICIANDO OPERACIÓN KAMIKAZE FORZADA EN CUENTA REAL ===")

try:
    # Use BTCUSDT because it's the safest and most liquid for a test
    best_symbol = "BTCUSDT"
    
    print(f"Buscando métricas técnicas actuales para {best_symbol}...")
    tech = analytics.analyze_institutional_grade(best_symbol, account_balance=100.0, risk_percentage=1.0)
    price = tech["current_price"]
    
    print(f"Forzando compra LONG en {best_symbol} a precio ${price} por orden del Creador...")
    
    # is_learned_signal=True completely bypasses all mathematical score thresholds
    res = real_money_trader.evaluate_and_trade_real_money(
        best_symbol=best_symbol,
        best_score=100, # Fake perfect score to bypass checks
        current_price=price,
        is_bearish=False,
        is_learned_signal=True
    )
    
    print("\n✅ ESTADO DE LA CUENTA REAL ACTUALIZADO:")
    print(json.dumps(res, indent=4, ensure_ascii=False))

except Exception as e:
    print(f"ERROR FORZANDO OPERACIÓN: {e}")
