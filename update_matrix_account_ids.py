import json
import os
import sys

MATRIX_FILE = r"c:\Users\hosca\Documents\Antigravity\BINANCE\matrix_100_simulations.json"

def update_account_numbering():
    if not os.path.exists(MATRIX_FILE):
        print("Matrix file not found.")
        return
        
    with open(MATRIX_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    accounts = data.get("accounts", [])
    if not accounts:
        return
        
    # Account 0 -> SIM-000 (Réplica Real)
    accounts[0]["account_id"] = "SIM-000 (Réplica Real)"
    
    # Renumber accounts 1 to N -> SIM-001, SIM-002, etc.
    for idx in range(1, len(accounts)):
        accounts[idx]["account_id"] = f"SIM-{idx:03d}"
        
    data["accounts"] = accounts
    
    with open(MATRIX_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        
    print(f"🎉 Matriz actualizada: {accounts[0]['account_id']} en primer lugar y {len(accounts)-1} cuentas reenumeradas (SIM-001 a SIM-{len(accounts)-1:03d}).")

if __name__ == "__main__":
    sys.stdout.reconfigure(encoding='utf-8')
    update_account_numbering()
