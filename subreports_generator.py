import os
import json
from datetime import datetime, timedelta

TRADE_MEMORY_FILE = os.path.join(os.path.dirname(__file__), "trade_memory.json")
def _get_obsidian_folder():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    obs_path = os.path.join(base_dir, "Obsidian", "01_PROYECTOS", "BINANCE_QUANT_TRADING", "Reportes")
    os.makedirs(obs_path, exist_ok=True)
    return obs_path

OBSIDIAN_FOLDER = _get_obsidian_folder()
def ensure_obsidian_dir():
    if not os.path.exists(OBSIDIAN_FOLDER):
        os.makedirs(OBSIDIAN_FOLDER, exist_ok=True)

def load_memory():
    if not os.path.exists(TRADE_MEMORY_FILE):
        return []
    with open(TRADE_MEMORY_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
        return data.get("history", [])

def calculate_stats(trades, now):
    # returns dict with stats for 1D, 3D, 1W, 2W, 1M
    windows = {
        "1 Día": timedelta(days=1),
        "3 Días": timedelta(days=3),
        "1 Semana": timedelta(days=7),
        "2 Semanas": timedelta(days=14),
        "1 Mes": timedelta(days=30)
    }
    
    stats = {}
    for w_name, delta in windows.items():
        w_trades = []
        for t in trades:
            try:
                t_time = datetime.strptime(t["timestamp"], "%Y-%m-%d %H:%M:%S")
                if now - t_time <= delta:
                    w_trades.append(t)
            except ValueError:
                pass
        
        wins = sum(1 for t in w_trades if t["result"] == "WIN")
        losses = sum(1 for t in w_trades if t["result"] == "LOSS")
        pnl_wins = sum(t.get("pnl_usd", 0.0) for t in w_trades if t["result"] == "WIN")
        pnl_losses = sum(t.get("pnl_usd", 0.0) for t in w_trades if t["result"] == "LOSS")
        
        total = wins + losses
        win_rate = (wins / total * 100) if total > 0 else 0.0
        
        stats[w_name] = {
            "total": total,
            "wins": wins,
            "losses": losses,
            "win_rate": win_rate,
            "pnl_wins": pnl_wins,
            "pnl_losses": pnl_losses,
            "net_pnl": pnl_wins + pnl_losses
        }
    return stats

def generate_markdown(group_name, stats):
    md = f"# Reporte Temporal: {group_name}\n\n"
    md += f"> Actualizado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
    
    md += "| Ventana de Tiempo | Total Operaciones | Ganadoras | Perdedoras | Win Rate | PnL Neto |\n"
    md += "| :--- | :--- | :--- | :--- | :--- | :--- |\n"
    
    for w_name, s in stats.items():
        wins_str = f"{s['wins']} (+${s['pnl_wins']:.2f})" if s['wins'] > 0 else "0"
        loss_str = f"{s['losses']} (-${abs(s['pnl_losses']):.2f})" if s['losses'] > 0 else "0"
        pnl_str = f"+${s['net_pnl']:.2f}" if s['net_pnl'] >= 0 else f"-${abs(s['net_pnl']):.2f}"
        
        # Color code the win rate
        wr = s['win_rate']
        wr_str = f"**{wr:.1f}%** 🟢" if wr >= 60 else (f"{wr:.1f}% 🟡" if wr >= 40 else f"{wr:.1f}% 🔴")
        if s['total'] == 0:
            wr_str = "-"
            
        md += f"| **{w_name}** | {s['total']} | {wins_str} | {loss_str} | {wr_str} | {pnl_str} |\n"
        
    return md

def generate_all_subreports():
    ensure_obsidian_dir()
    trades = load_memory()
    now = datetime.now()
    
    # We must ensure there is a file for every group even if no trades exist yet
    # Extract current group names dynamically from matrix
    all_groups = ["CUENTA REAL"]
    matrix_file = os.path.join(os.path.dirname(__file__), "matrix_100_simulations.json")
    if os.path.exists(matrix_file):
        with open(matrix_file, "r", encoding="utf-8") as f:
            m_data = json.load(f)
            groups_set = set()
            for acc in m_data.get("accounts", []):
                groups_set.add(acc.get("group_name", "Desconocido"))
            all_groups.extend(sorted(list(groups_set)))
    
    grouped = {g: [] for g in all_groups}
    for t in trades:
        g = t.get("group_name", "Desconocido")
        if g not in grouped:
            grouped[g] = []
        grouped[g].append(t)
        
    for group_name, g_trades in grouped.items():
        stats = calculate_stats(g_trades, now)
        md = generate_markdown(group_name, stats)
        
        safe_name = group_name.replace(" ", "_").replace("/", "_").replace(":", "").replace("?", "")
        filepath = os.path.join(OBSIDIAN_FOLDER, f"{safe_name}.md")
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(md)
    print(f"Generated {len(grouped)} subreports in Obsidian.")

if __name__ == '__main__':
    generate_all_subreports()
