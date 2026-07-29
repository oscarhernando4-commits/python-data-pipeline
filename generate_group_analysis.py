import os
import sys
import json
from datetime import datetime

sys.stdout.reconfigure(encoding='utf-8')

TRADE_MEMORY_FILE = os.path.join(os.path.dirname(__file__), "trade_memory.json")

def _get_obsidian_folder():
    local_path = r"C:\Users\hosca\Documents\Antigravity\Obsidian\01_PROYECTOS\BINANCE_QUANT_TRADING"
    if os.path.exists(os.path.dirname(local_path)):
        os.makedirs(local_path, exist_ok=True)
        return local_path
    rel_path = os.path.join(os.getcwd(), "Obsidian", "01_PROYECTOS", "BINANCE_QUANT_TRADING")
    os.makedirs(rel_path, exist_ok=True)
    return rel_path

OBSIDIAN_FOLDER = _get_obsidian_folder()

def load_memory():
    if not os.path.exists(TRADE_MEMORY_FILE):
        return []
    with open(TRADE_MEMORY_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
        return data.get("history", [])

def generate_report():
    trades = load_memory()
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    group_stats = {}
    
    # 1. Aggregate Stats
    for t in trades:
        g = t.get("group_name", "Sin Grupo")
        if g not in group_stats:
            group_stats[g] = {
                "trades": 0,
                "wins": 0,
                "losses": 0,
                "pnl": 0.0,
                "long_pnl": 0.0,
                "short_pnl": 0.0,
                "symbols": {},
                "movements": []
            }
        
        st = group_stats[g]
        st["trades"] += 1
        pnl = float(t.get("pnl_usd", 0.0))
        st["pnl"] += pnl
        
        if t.get("side") == "LONG":
            st["long_pnl"] += pnl
        else:
            st["short_pnl"] += pnl
            
        if t.get("result") == "WIN":
            st["wins"] += 1
        else:
            st["losses"] += 1
            
        sym = t.get("symbol", "UNKNOWN")
        st["symbols"][sym] = st["symbols"].get(sym, 0.0) + pnl
        
        # Save movement for the log
        st["movements"].append(t)
        
    # 2. Build Markdown Report
    md = f"""---
tags:
  - analisis_grupos
  - trading
date: {now_str}
---

# 📊 ANÁLISIS GLOBAL DE GANANCIAS Y PÉRDIDAS POR GRUPO

> **Última Actualización:** `{now_str}`
> Este reporte desglosa el rendimiento matemático de cada Estrategia de IA. 

## 🏆 Resumen de Rendimiento (Ranking de Grupos)

| Grupo de IA | Operaciones | Tasa de Acierto (WinRate) | PnL en LONGs | PnL en SHORTs | 💰 PnL NETO TOTAL |
| :--- | :---: | :---: | :---: | :---: | :---: |
"""
    
    # Sort groups by Net PnL descending
    sorted_groups = sorted(group_stats.items(), key=lambda x: x[1]["pnl"], reverse=True)
    
    for g_name, st in sorted_groups:
        wr = (st["wins"] / st["trades"]) * 100 if st["trades"] > 0 else 0
        long_pnl_str = f"${st['long_pnl']:+.2f}"
        short_pnl_str = f"${st['short_pnl']:+.2f}"
        net_pnl_str = f"**${st['pnl']:+.2f}**"
        
        md += f"| **{g_name}** | {st['trades']} | `{wr:.1f}%` | {long_pnl_str} | {short_pnl_str} | {net_pnl_str} |\n"
        
    md += "\n---\n\n## 📝 Historial de Movimientos por Grupo\n\n"
    
    for g_name, st in sorted_groups:
        md += f"### {g_name}\n\n"
        
        # Best pair
        best_pair = "N/A"
        if st["symbols"]:
            best_pair_tuple = max(st["symbols"].items(), key=lambda x: x[1])
            best_pair = f"{best_pair_tuple[0]} (${best_pair_tuple[1]:+.2f})"
            
        md += f"> **Mejor Par Operado:** `{best_pair}`\n\n"
        
        md += "| Fecha | Par | Lado | Precio Entrada | Precio Salida | PnL | Resultado |\n"
        md += "| :--- | :--- | :--- | :--- | :--- | :--- | :--- |\n"
        
        for t in reversed(st["movements"]): # Newest first
            emoji = "🟢 WIN" if t["result"] == "WIN" else "🔴 LOSS"
            md += f"| {t['timestamp']} | **{t['symbol']}** | {t['side']} | ${t['entry_price']} | ${t['exit_price']} | `${float(t.get('pnl_usd', 0)):+.2f}` | {emoji} |\n"
            
        md += "\n\n"
        
    file_path = os.path.join(OBSIDIAN_FOLDER, "📊_Analisis_Por_Grupo_y_Movimientos.md")
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(md)
        
    print(f"Reporte generado exitosamente en: {file_path}")

if __name__ == "__main__":
    generate_report()
