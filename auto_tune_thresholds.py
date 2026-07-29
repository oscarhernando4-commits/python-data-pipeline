import json
import os

THRESHOLDS_FILE = os.path.join(os.path.dirname(__file__), "dynamic_thresholds.json")
TRADE_MEMORY_FILE = os.path.join(os.path.dirname(__file__), "trade_memory.json")

def auto_tune():
    if not os.path.exists(TRADE_MEMORY_FILE):
        return
        
    with open(TRADE_MEMORY_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
        history = data.get("history", [])
        
    if not os.path.exists(THRESHOLDS_FILE):
        # Rely on strategy_engine defaults to create file
        from strategy_engine import load_thresholds
        t = load_thresholds()
    else:
        with open(THRESHOLDS_FILE, "r", encoding="utf-8") as f:
            t = json.load(f)
            
    # Calculate win rate per group over the last 100 trades
    group_stats = {}
    for trade in history[-100:]:
        g = trade.get("group_name", "UNKNOWN")
        if g not in group_stats:
            group_stats[g] = {"wins": 0, "losses": 0}
            
        if trade.get("result") == "WIN":
            group_stats[g]["wins"] += 1
        else:
            group_stats[g]["losses"] += 1
            
    # Adjust thresholds based on WinRate and volume
    for g_id in range(6):
        g_name = ""
        if g_id == 0: g_name = "GRUPO 0: RÉPLICA REAL"
        elif g_id == 1: g_name = "GRUPO 1: Ultra-Estricto"
        elif g_id == 2: g_name = "GRUPO 2: Moderado-Estricto"
        elif g_id == 3: g_name = "GRUPO 3: Balanceado"
        elif g_id == 4: g_name = "GRUPO 4: Frecuencia Alta"
        elif g_id == 5: g_name = "GRUPO 5: Exploratorio de Máxima Frecuencia"
        
        # Find matching group stats
        stats = None
        for k, v in group_stats.items():
            if str(g_id) in k:
                stats = v
                break
                
        if stats:
            total = stats["wins"] + stats["losses"]
            wr = stats["wins"] / total if total > 0 else 0
            
            # If winrate is great, relax thresholds to trade more!
            # If winrate is terrible, tighten thresholds to protect capital.
            gk = f"group_{g_id}"
            if gk not in t:
                continue
                
            if wr >= 0.65:
                # Relax (Decrease long_score, increase short_score, etc.)
                if "long_score" in t[gk]: t[gk]["long_score"] = max(20, t[gk]["long_score"] - 1)
                if "short_score" in t[gk]: t[gk]["short_score"] = min(80, t[gk]["short_score"] + 1)
                if "rsi_min" in t[gk]: t[gk]["rsi_min"] = max(10, t[gk]["rsi_min"] - 1)
                if "rsi_max" in t[gk]: t[gk]["rsi_max"] = min(90, t[gk]["rsi_max"] + 1)
                if "long_rsi" in t[gk]: t[gk]["long_rsi"] = min(80, t[gk]["long_rsi"] + 1)
                if "short_rsi" in t[gk]: t[gk]["short_rsi"] = max(20, t[gk]["short_rsi"] - 1)
                if "vol_surge" in t[gk]: t[gk]["vol_surge"] = max(1.0, t[gk]["vol_surge"] - 0.1)
                
            elif wr < 0.40:
                # Tighten
                if "long_score" in t[gk]: t[gk]["long_score"] = min(95, t[gk]["long_score"] + 1)
                if "short_score" in t[gk]: t[gk]["short_score"] = max(5, t[gk]["short_score"] - 1)
                if "rsi_min" in t[gk]: t[gk]["rsi_min"] = min(40, t[gk]["rsi_min"] + 1)
                if "rsi_max" in t[gk]: t[gk]["rsi_max"] = max(60, t[gk]["rsi_max"] - 1)
                if "long_rsi" in t[gk]: t[gk]["long_rsi"] = max(20, t[gk]["long_rsi"] - 1)
                if "short_rsi" in t[gk]: t[gk]["short_rsi"] = min(80, t[gk]["short_rsi"] + 1)
                if "vol_surge" in t[gk]: t[gk]["vol_surge"] = min(3.0, t[gk]["vol_surge"] + 0.1)

    with open(THRESHOLDS_FILE, "w", encoding="utf-8") as f:
        json.dump(t, f, indent=2)

if __name__ == "__main__":
    auto_tune()
