import json
import os
import sys
from datetime import datetime

MATRIX_FILE = r"c:\Users\hosca\Documents\Antigravity\BINANCE\matrix_100_simulations.json"

def reset_sim000_to_clean():
    if not os.path.exists(MATRIX_FILE):
        return
        
    with open(MATRIX_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    accounts = data.get("accounts", [])
    if not accounts:
        return
        
    now_date = datetime.now().strftime("%y-%m-%d")
    now_time = datetime.now().strftime("%H:%M")
    now_br = f"{now_date}<br>{now_time}"
    
    # Reset account 0 (SIM-000 Réplica Real) to 100% clean state
    accounts[0] = {
        "account_id": "SIM-000 (Réplica Real)",
        "symbol": "BTCUSDT",
        "initial_capital": 100.0,
        "current_balance": 100.0,
        "pnl_usd": 0.0,
        "current_level": 1,
        "consecutive_losses": 0,
        "last_result": "Esperando Entrada",
        "last_trade_time": now_br,
        "position": None,
        "trades_count": 0,
        "wins": 0,
        "losses": 0,
        "status": "BUSCANDO_OPORTUNIDAD"
    }
    
    data["accounts"] = accounts
    
    with open(MATRIX_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        
    print("🎉 SIM-000 (Réplica Real) reseteada a estado 100% limpio (#0 Ops, 0W/0L, $100.00 USD, 🟦 Buscando).")

if __name__ == "__main__":
    sys.stdout.reconfigure(encoding='utf-8')
    reset_sim000_to_clean()
