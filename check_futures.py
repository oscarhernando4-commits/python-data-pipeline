import json
import real_money_trader
import sys

sys.stdout.reconfigure(encoding='utf-8')

print("=== VERIFICANDO POSICIONES ACTIVAS EN FUTUROS ===")

try:
    positions = real_money_trader.get_real_futures_positions()
    
    if not positions:
        print("❌ No hay ninguna posición abierta en Futuros.")
    else:
        print("✅ POSICIONES ACTIVAS ENCONTRADAS:")
        for p in positions:
            print(f"- Símbolo: {p['symbol']}")
            print(f"- Tamaño: {p['positionAmt']} (Negativo = SHORT)")
            print(f"- Precio de Entrada: {p['entryPrice']}")
            print(f"- PnL No Realizado (Ganancia/Pérdida): {p['unRealizedProfit']} USDT")
            print(f"- Margen Aislado: {p['isolatedMargin']} USDT")
            print("-------------------------------------------------")
            
except Exception as e:
    print(f"Error: {e}")
