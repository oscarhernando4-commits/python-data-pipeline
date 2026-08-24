import os
import json
from datetime import datetime, timedelta

DATA_FILE = os.path.join(os.path.dirname(__file__), "trade_memory.json")

def _get_obsidian_folder():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    obs_path = os.path.join(base_dir, "Obsidian", "01_PROYECTOS", "BINANCE_QUANT_TRADING")
    os.makedirs(obs_path, exist_ok=True)
    return obs_path

OBSIDIAN_FOLDER = _get_obsidian_folder()

def calculate_metrics_for_window(trades, start_time, end_time):
    filtered_trades = [t for t in trades if start_time <= datetime.strptime(t["timestamp"], "%Y-%m-%d %H:%M:%S") <= end_time]
    
    total = len(filtered_trades)
    wins = [t for t in filtered_trades if t.get("result") == "WIN"]
    losses = [t for t in filtered_trades if t.get("result") == "LOSS"]
    
    pnl_won = sum(t.get("pnl_usd", 0) for t in wins)
    pnl_lost = sum(t.get("pnl_usd", 0) for t in losses)
    
    return {
        "total": total,
        "wins_count": len(wins),
        "pnl_won": pnl_won,
        "losses_count": len(losses),
        "pnl_lost": pnl_lost,
        "net_pnl": pnl_won + pnl_lost
    }

def generate_subreports():
    if not os.path.exists(DATA_FILE):
        return []
        
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        memory = json.load(f)
        
    history = memory.get("history", [])
    
    # Agrupar por group_name
    grouped_history = {}
    for t in history:
        # Ignore legacy trades without group_name
        if "group_name" not in t or t["group_name"] == "Sin Grupo":
            continue
        g = t["group_name"]
        if g not in grouped_history:
            grouped_history[g] = []
        grouped_history[g].append(t)
        
    now = datetime.now()
    windows = {
        "1 Día (24h)": timedelta(days=1),
        "3 Días": timedelta(days=3),
        "1 Semana": timedelta(days=7),
        "2 Semanas": timedelta(days=14),
        "1 Mes (30d)": timedelta(days=30)
    }
    
    generated_files = []
    
    for group, trades in grouped_history.items():
        # Clean filename
        clean_group = group.replace(":", "").replace(" ", "_").replace("🥇", "").replace("🥈", "").replace("🥉", "")
        clean_group = "".join(c for c in clean_group if c.isalnum() or c == "_").strip("_")
        
        filename = f"📊_Reporte_Temporal_{clean_group}.md"
        filepath = os.path.join(OBSIDIAN_FOLDER, filename)
        
        lines = []
        lines.append("---")
        lines.append(f"tags: [reporte-temporal, {clean_group}]")
        lines.append(f"aliases: [Rendimiento {group}]")
        lines.append(f"cssclasses: [dashboard-view]")
        lines.append("---")
        lines.append(f"# 📊 Rendimiento por Periodos: {group}")
        lines.append(f"> Última actualización: {now.strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("")
        
        lines.append("| Periodo | Total Operaciones | ✅ Ganadoras | 💰 PnL Ganado | ❌ Perdedoras | 💸 PnL Perdido | 📈 Neto |")
        lines.append("| :--- | :---: | :---: | :---: | :---: | :---: | :---: |")
        
        for win_name, delta in windows.items():
            start_time = now - delta
            metrics = calculate_metrics_for_window(trades, start_time, now)
            
            pnl_neto_str = f"+${metrics['net_pnl']:.2f}" if metrics['net_pnl'] > 0 else f"${metrics['net_pnl']:.2f}"
            
            lines.append(
                f"| **{win_name}** | {metrics['total']} | {metrics['wins_count']} | +${metrics['pnl_won']:.2f} | {metrics['losses_count']} | -${abs(metrics['pnl_lost']):.2f} | **{pnl_neto_str}** |"
            )
            
        lines.append("")
        lines.append("## 🔍 Últimas 10 Operaciones")
        lines.append("| Fecha | Par | Lado | Entrada | Salida | PnL |")
        lines.append("| :--- | :--- | :--- | :--- | :--- | :--- |")
        
        recent = sorted(trades, key=lambda x: x["timestamp"], reverse=True)[:10]
        for r in recent:
            icon = "🟢" if r["result"] == "WIN" else "🔴"
            pnl_str = f"+${r['pnl_usd']:.2f}" if r["pnl_usd"] > 0 else f"-${abs(r['pnl_usd']):.2f}"
            lines.append(f"| {r['timestamp']} | **{r['symbol']}** | {r['side']} | ${r['entry_price']} | ${r['exit_price']} | {icon} {pnl_str} |")
            
        with open(filepath, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
            
        generated_files.append({"group": group, "file": filename})
        
    return generated_files

if __name__ == "__main__":
    files = generate_subreports()
    for f in files:
        print(f"Generated {f['file']}")
