import os
import json
from datetime import datetime

MATRIX_FILE = os.path.join(os.path.dirname(__file__), "matrix_100_simulations.json")

def reset_matrix_simulations():
    now_date = datetime.now().strftime("%y-%m-%d")
    now_time = datetime.now().strftime("%H:%M")
    now_br = f"{now_date}<br>{now_time}"
    
    accounts = []
    for i in range(0, 100):
        if i == 0:
            g_id = 0
            g_name = "🥇 GRUPO 0: RÉPLICA REAL (Copia Fiel)"
        elif 1 <= i <= 20:
            g_id = 1
            g_name = "🛡️ GRUPO 1: Ultra-Estricto (Estrategia Real A+)"
        elif 21 <= i <= 40:
            g_id = 2
            g_name = "🔷 GRUPO 2: Moderado-Estricto"
        elif 41 <= i <= 60:
            g_id = 3
            g_name = "⚖️ GRUPO 3: Balanceado"
        elif 61 <= i <= 80:
            g_id = 4
            g_name = "⚡ GRUPO 4: Frecuencia Alta"
        else:
            g_id = 5
            g_name = "🔥 GRUPO 5: Exploratorio de Máxima Frecuencia"
            
        accounts.append({
            "account_id": f"SIM-{i:03d}" + (" (Réplica Real)" if i == 0 else ""),
            "group_id": g_id,
            "group_name": g_name,
            "symbol": "BTCUSDT",
            "position": None,
            "entry_price": 0.0,
            "highest_price": 0.0,
            "balance": 100.0,
            "initial_balance": 100.0,
            "pnl_net_usd": 0.0,
            "win_rate": "0.0%",
            "wins": 0,
            "losses": 0,
            "trades": 0,
            "shield_status": "🟢 En Espera",
            "last_update": now_br
        })
        
    matrix_payload = {
        "current_total_usd": 10000.00,
        "net_pnl_usd": 0.00,
        "win_rate_pct": 0.0,
        "accounts": accounts
    }
        
    with open(MATRIX_FILE, "w", encoding="utf-8") as f:
        json.dump(matrix_payload, f, indent=2, ensure_ascii=False)
        
    print(f"✅ Reset completado: 100 Cuentas Matrix restablecidas a $100.00 USD cada una ($10,000.00 USD total).")

if __name__ == "__main__":
    reset_matrix_simulations()
