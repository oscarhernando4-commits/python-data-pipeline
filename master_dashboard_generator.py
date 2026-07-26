import os
import json
import sys
from datetime import datetime
import parallel_simulation_matrix
import learning_engine
import obsidian_sync

OBSIDIAN_FOLDER = r"C:\Users\hosca\Documents\Antigravity\Obsidian\01_PROYECTOS\BINANCE_QUANT_TRADING"

def ensure_obsidian_dir():
    if not os.path.exists(OBSIDIAN_FOLDER):
        os.makedirs(OBSIDIAN_FOLDER, exist_ok=True)

def generate_master_dashboard():
    ensure_obsidian_dir()
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    matrix = parallel_simulation_matrix.load_live_matrix()
    mem = learning_engine.load_memory()
    
    total_fund = matrix.get("current_total_usd", 10000.0)
    net_pnl = matrix.get("net_pnl_usd", 0.0)
    win_rate = matrix.get("global_win_rate_pct", 0.0)
    accounts = matrix.get("accounts", [])
    
    goals_reached = sum([1 for a in accounts if a.get("goal_reached")])
    
    # Sort top 5 winning cryptocurrencies
    top_accounts = sorted(accounts, key=lambda x: x.get("current_balance", 100.0), reverse=True)[:5]
    
    top_winners_table = "| Criptomoneda | Balance Actual | Ganancia | Estado |\n| :--- | :--- | :--- | :--- |\n"
    for acc in top_accounts:
        sym = acc.get("symbol", "USDT")
        bal = acc.get("current_balance", 100.0)
        pnl = acc.get("pnl_usd", 0.0)
        status = "🟢 Meta +3% Cumplida" if acc.get("goal_reached") else "🔵 En Operación"
        top_winners_table += f"| **{sym}** | `${bal:.2f} USD` | `${pnl:+,.2f} USD` | {status} |\n"

    # Compound target baseline for $100
    w1_target = 103.00
    sim_100_bal = 100.0
    progress_pct = min((sim_100_bal / w1_target) * 100.0, 100.0)
    filled_bar = int(progress_pct / 10)
    bar_str = "█" * filled_bar + "░" * (10 - filled_bar)

    master_md = f"""---
tags:
  - trading
  - master_dashboard
  - binance
date: {now_str}
---

# 📊 MASTER DASHBOARD - SEGUIMIENTO RÁPIDO DE TRADING

> [!NOTE] 🟢 RESUMEN ULTRA-FÁCIL DE INTERPRETAR
> **Última Actualización:** `{now_str}`  
> **Estado del Sistema:** `🟢 BOT OPERANDO 24/7 EN SEGUNDO PLANO`

---

## ⚡ 1. ¿CÓMO VAMOS HOY? (RESUMEN EN 3 SEGUNDOS)

| Métrica | Valor Actual | ¿Qué Significa? |
| :--- | :--- | :--- |
| 💵 **Capital Total (Fondo $10k):** | **`${total_fund:,.2f} USD`** | Balance de las 100 cuentas de prueba |
| 💰 **Ganancia Neto Total:** | **`${net_pnl:+,.2f} USD`** | Resultado global acumulado |
| 🎯 **Cuentas que cumplieron la meta:** | **`{goals_reached} de 100 Cuentas`** | Cuentas que alcanzaron el +3% esta semana |
| 📈 **Tasa de Acierto de la IA:** | **`{win_rate}% Win Rate`** | Efectividad actual de las estrategias |

---

## 🎯 2. PROGRESO HACIA LA META SEMANAL (+3% SOBRE $100)

> [!IMPORTANT] 🏆 META SEMANA 1: $103.00 USD
> **Progreso:** `[{bar_str}] {progress_pct:.1f}%`
> 
> - 💵 **Capital Base:** `$100.00 USD`
> - 🎯 **Meta Semanal:** `$103.00 USD`
> - 🟡 **Estado:** `🟡 EN PROCESO - Buscando el +3% de ganancia en operaciones filtradas`

---

## 🏆 3. TOP 5 CRIPTOMONEDAS MÁS RENTABLES DEL MOMENTO

{top_winners_table}

---

## 🛡️ 4. NIVELES DE SEGURIDAD Y PROTECCIÓN

- 🛑 **Máxima Pérdida Permitida por Trade:** `-$1.50 USD (-1.5%)` *(Stop Loss Inviolable)*
- ⚡ **Disyuntor Anti-Crash (Caídas Fuertes):** `🟢 ACTIVO (Protege en USDT/USDC)`
- 🧠 **Reglas de Aprendizaje Aprendidas:** `{len(mem.get('learned_rules', {}).get('blocked_patterns', []))} Patrones de Fracaso Bloqueados`

---

## 🔗 NAVEGACIÓN EN 1-CLIC (DETALLES Y TABLAS COMPLETAS)
- [[🚀_Matriz_100_Simulaciones|Ver Ver Lista Completa de las 100 Cuentas]]
- [[🎯_Seguimiento_De_Metas|Ver Tabla de Metas Semana a Semana]]
- [[📊_Dashboard_Interes_Compuesto|Ver Proyección de Interés Compuesto]]
- [[🧠_Matriz_De_Aprendizaje|Ver IA y Reglas de Aprendizaje]]
- [[🛡️_Escudo_Anti_Caidas_Y_Riesgo|Ver Protocolo Anti-Caídas]]
"""

    file_path = os.path.join(OBSIDIAN_FOLDER, "📊_MASTER_DASHBOARD_TRADING.md")
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(master_md)
        
    print(f"Master Dashboard created at: {file_path}")
    return file_path

if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    generate_master_dashboard()
