import json
import real_money_trader
import analytics
import sys

sys.stdout.reconfigure(encoding='utf-8')

print("=== INICIANDO OPERACIÓN KAMIKAZE SHORT EN FUTUROS ===")

try:
    best_symbol = "BTCUSDT"
    
    # Check futures balance directly
    balances = real_money_trader.get_real_futures_balances()
    usdt_free = sum([float(b["availableBalance"]) for b in balances if b["asset"] in ["USDT", "USDC"]])
    
    if usdt_free == 0.0:
        usdt_free = 8.5
        
    print(f"Forzando SHORT en {best_symbol} con {usdt_free} USDT por orden del Creador...")
    
    # Llama directamente al motor de futuros para inyectar la orden Batch (Market Sell + SL + TP nativos)
    res = real_money_trader.execute_real_futures_market_short(best_symbol, usdt_free)
    
    print("\n✅ RESPUESTA RAW DE BINANCE (FUTUROS BATCH ORDER):")
    print(json.dumps(res, indent=4, ensure_ascii=False))

except Exception as e:
    print(f"ERROR FORZANDO OPERACIÓN: {e}")
