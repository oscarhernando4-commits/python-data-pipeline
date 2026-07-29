import json
import real_money_trader
import analytics
import sys

sys.stdout.reconfigure(encoding='utf-8')

print("=== DEPURACIÓN DE ORDEN BINANCE ===")

try:
    best_symbol = "BTCUSDT"
    
    # 1. Chequeamos saldo disponible (para asegurar que mandamos la orden con el monto correcto)
    balances = real_money_trader.get_real_balances()
    usdt_free = sum([float(b["free"]) for b in balances if b["asset"] == "USDT"])
    
    # Si la API falla por la IP, forzamos a 17.15 para la orden
    if usdt_free == 0.0:
        usdt_free = 17.15
        
    print(f"Mandando orden a Binance por {usdt_free} USDT...")
    
    # We call the exact function directly to see the RAW API RESPONSE from Binance via Fixie
    res = real_money_trader.execute_real_spot_market_buy(best_symbol, usdt_free)
    
    print("\n✅ RAW BINANCE API RESPONSE:")
    print(json.dumps(res, indent=4, ensure_ascii=False))

except Exception as e:
    print(f"ERROR FORZANDO OPERACIÓN: {e}")
