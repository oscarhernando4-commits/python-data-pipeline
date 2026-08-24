import os
import json
from datetime import datetime
import obsidian_sync
import learning_engine

def _get_obsidian_folder():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    obs_path = os.path.join(base_dir, "Obsidian", "01_PROYECTOS", "BINANCE_QUANT_TRADING")
    os.makedirs(obs_path, exist_ok=True)
    return obs_path

OBSIDIAN_FOLDER = _get_obsidian_folder()

def generate_progress_bar(current, target, length=15):
    pct = min(max(current / target, 0.0), 1.0)
    filled = int(round(length * pct))
    bar = "█" * filled + "░" * (length - filled)
    return f"[{bar}] {pct*100:.1f}%"

def sync_simulated_goal_tracker(current_sim_balance=100.0, week_number=1, initial_capital=100.0):
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Calculate target for current week
    weekly_target = initial_capital * ((1 + 0.03) ** week_number)
    needed_for_target = weekly_target - current_sim_balance
    
    pnl_usd = current_sim_balance - initial_capital
    pnl_pct = (pnl_usd / initial_capital) * 100.0
    
    if current_sim_balance >= weekly_target:
        goal_status = f"✅ ¡META DE LA SEMANA {week_number} CUMPLIDA CON ÉXITO! 🎉"
        status_color = "🟢"
    else:
        goal_status = f"🟡 EN PROCESO | Faltan +${needed_for_target:.2f} USD para alcanzar la meta de la Semana {week_number} (${weekly_target:.2f} USD)"
        status_color = "🟡"
        
    progress_bar = generate_progress_bar(current_sim_balance, weekly_target)
    
    # Get active trade history from Learning Engine
    mem = learning_engine.load_memory()
    history = mem.get("history", [])
    
    history_md = ""
    for t in reversed(history[-5:]):
        res_emoji = "🟢 WIN (+3%)" if t['result'] == 'WIN' else "🔴 LOSS"
        history_md += f"| `{t['timestamp']}` | **{t['symbol']}** | {t['side']} | `${t['entry_price']}` | `${t['exit_price']}` | **`${t['pnl_usd']:+.2f} USD`** | {res_emoji} |\n"
    if not history_md:
        history_md = "| - | - | - | - | - | - | Sin operaciones registradas |\n"

    content = f"""---
tags:
  - trading
  - simulacion_100usd
  - seguimiento_metas
  - binance
date: {now_str}
---

# 🎯 SEGUIMIENTO DE METAS EN TIEMPO REAL ($100 USD SIMULACIÓN)

> [!NOTE] 🟢 ACTUALIZACIÓN EN VIVO DE LA SIMULACIÓN DE TRADING
> Última sincronización: `{now_str}`

---

## 📊 RASTREADOR DE CUMPLIMIENTO DE META SEMANAL

> [!IMPORTANT] 🏆 ESTADO DE LA META DE LA SEMANA {week_number}
> {status_color} **ESTADO:** `{goal_status}`
> 
> - 💵 **Capital Inicial:** `${initial_capital:,.2f} USD`
> - 📈 **Balance Actual Simulado:** `${current_sim_balance:,.2f} USD`
> - 🎯 **Meta Semanal {week_number} (+3%):** `${weekly_target:,.2f} USD`
> - 📊 **Barra de Progreso hacia la Meta:** `{progress_bar}`
> - 💰 **Beneficio Total Ganado:** `${pnl_usd:+,.2f} USD ({pnl_pct:+.2f}%)`

---

## 📈 COMPARATIVA DE CUMPLIMIENTO VS PROYECTADO

| Hito | Meta Proyectada | Balance Actual | Diferencia vs Meta | Estado |
| :--- | :--- | :--- | :--- | :--- |
| **Semana 1** | `$103.00 USD` | `${current_sim_balance:,.2f} USD` | `${current_sim_balance - 103.00:+,.2f} USD` | `{'✅ Cumplida' if current_sim_balance >= 103 else '⏳ En Proceso'}` |
| **Semana 2** | `$106.09 USD` | `${current_sim_balance:,.2f} USD` | `${current_sim_balance - 106.09:+,.2f} USD` | `{'✅ Cumplida' if current_sim_balance >= 106.09 else '⏳ Pendiente'}` |
| **Semana 3** | `$109.27 USD` | `${current_sim_balance:,.2f} USD` | `${current_sim_balance - 109.27:+,.2f} USD` | `{'✅ Cumplida' if current_sim_balance >= 109.27 else '⏳ Pendiente'}` |
| **Semana 4 (Mes 1)** | `$112.55 USD` | `${current_sim_balance:,.2f} USD` | `${current_sim_balance - 112.55:+,.2f} USD` | `{'✅ Cumplida' if current_sim_balance >= 112.55 else '⏳ Pendiente'}` |

---

## 📜 HISTORIAL DE TRADES SIMULADOS EN TIEMPO REAL

| Fecha / Hora | Par | Tipo | Precio Entrada | Precio Salida | Beneficio (PnL) | Resultado |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
{history_md}

---

## 🔗 NAVEGACIÓN RÁPIDA
- [[📊_Dashboard_Interes_Compuesto|Ver Dashboard de Interés Compuesto]]
- [[📊_Dashboard_Trading|Ver Dashboard de Operaciones en Vivo]]
- [[📈_Analisis_Mercado|Ver Último Análisis Técnico y Noticias]]
- [[🧠_Matriz_De_Aprendizaje|Ver Matriz de Aprendizaje e IA]]
"""

    file_path = os.path.join(OBSIDIAN_FOLDER, "🎯_Seguimiento_De_Metas.md")
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)
        
    print(f"Goal tracker note created at: {file_path}")
    return file_path

if __name__ == '__main__':
    import sys
    sys.stdout.reconfigure(encoding='utf-8')
    sync_simulated_goal_tracker(100.0, 1, 100.0)
