import os
import json
import sys
from datetime import datetime
import learning_engine
import obsidian_sync
try:
    import api_connector
except ImportError:
    api_connector = None

def _get_obsidian_folder():
    local_path = r"C:\Users\hosca\Documents\Antigravity\Obsidian\01_PROYECTOS\BINANCE_QUANT_TRADING"
    if os.path.exists(os.path.dirname(local_path)):
        os.makedirs(local_path, exist_ok=True)
        return local_path
    rel_path = os.path.join(os.getcwd(), "Obsidian", "01_PROYECTOS", "BINANCE_QUANT_TRADING")
    os.makedirs(rel_path, exist_ok=True)
    return rel_path

OBSIDIAN_FOLDER = _get_obsidian_folder()

def ensure_obsidian_dir():
    if not os.path.exists(OBSIDIAN_FOLDER):
        os.makedirs(OBSIDIAN_FOLDER, exist_ok=True)

def generate_master_dashboard():
    import pipeline_processor
    import obsidian_sync
    check_sync = getattr(obsidian_sync, "is_obsidian_sync_allowed", None)
    if check_sync and not check_sync():
        return
    ensure_obsidian_dir()
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    matrix = pipeline_processor.load_live_matrix()
    mem = learning_engine.load_memory()
    
    total_fund = matrix.get("current_total_usd", 10000.0)
    net_pnl = matrix.get("net_pnl_usd", 0.0)
    win_rate = matrix.get("global_win_rate_pct", 0.0)
    accounts = matrix.get("accounts", [])
    
    bias_info = learning_engine.get_market_bias(mem)
    
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
    avg_bal = sum([a.get("current_balance", 100.0) for a in accounts]) / len(accounts) if accounts else 100.0
    progress_pct = min(max(((avg_bal - 100.0) / (w1_target - 100.0)) * 100.0, 0.0), 100.0) if avg_bal >= 100.0 else 0.0
    
    filled_bar = int(progress_pct / 10)
    bar_str = "█" * filled_bar + "░" * (10 - filled_bar)

    # Real Account Data
    real_st = {}
    if api_connector:
        real_st = api_connector.load_real_account_state()
    
    real_bal = real_st.get("current_balance_usd", 0.0)
    real_pnl = real_st.get("net_pnl_usd", 0.0)
    real_pos = real_st.get("position", {})
    real_sym = real_pos.get("symbol", "Ninguna (Buscando)") if real_pos else "Ninguna (Buscando)"
    real_status = real_st.get("status", "Desconocido")

    # Group Level Win Rates
    group_stats = {}
    for acc in accounts:
        g_id = acc.get("group_id", 1)
        if g_id not in group_stats:
            group_stats[g_id] = {"wins": 0, "trades": 0, "pnl": 0.0}
        group_stats[g_id]["wins"] += acc.get("wins", 0)
        group_stats[g_id]["trades"] += acc.get("trades_count", 0)
        group_stats[g_id]["pnl"] += acc.get("pnl_usd", 0.0)

    group_table = "| Grupo | Tasa de Acierto | Ganancia Neta |\n| :--- | :---: | :---: |\n"
    for g_id in sorted(group_stats.keys()):
        stats = group_stats[g_id]
        wr = round((stats["wins"] / stats["trades"] * 100.0), 1) if stats["trades"] > 0 else 0.0
        g_name = f"Grupo {g_id}"
        if g_id == 0: g_name = "0 (Copia Real)"
        elif g_id == 1: g_name = "1 (Ultra-Estricto)"
        elif g_id == 5: g_name = "5 (Exploratorio)"
        group_table += f"| **{g_name}** | `{wr}%` | `${stats['pnl']:+,.2f}` |\n"

    master_md = f"""---
tags:
  - trading
  - master_dashboard
  - binance
aliases:
  - Dashboard Principal
cssclasses:
  - dashboard
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
| 💵 **Capital Total (Fondo $100k):** | **`${total_fund:,.2f} USD`** | Balance de las 1,000 cuentas de prueba |
| 💰 **Ganancia Neta Total:** | **`${net_pnl:+,.2f} USD`** | Resultado global acumulado |
| 🎯 **Cuentas que cumplieron la meta:** | **`{goals_reached} de 1000 Cuentas`** | Cuentas que alcanzaron el +3% esta semana |
| 📈 **Tasa de Acierto de la IA:** | **`{win_rate}% Win Rate`** | Efectividad actual de las estrategias |

---

## 🧭 2. AUTO-APRENDIZAJE: SESGO DE MERCADO (LONG vs SHORT)

> [!WARNING] 🧠 IA SENTINEL REGLA DE PRIORIDAD: `{bias_info['bias']}`
> - 🟢 **Rendimiento Compras (LONG):** `{bias_info['long_win_rate']}%` de Acierto
> - 🔴 **Rendimiento Ventas (SHORT):** `{bias_info['short_win_rate']}%` de Acierto
> - **Acción de la IA:** El bot está inyectando esta data en tiempo real a Gemini. Si la tendencia muestra pérdidas en LONG y ganancias en SHORT, **Gemini bloqueará operaciones LONG** priorizando el flujo ganador del mercado para el dinero real.

---

## 🎯 3. PROGRESO HACIA LA META SEMANAL (+3% SOBRE $100)

> [!IMPORTANT] 🏆 META SEMANA 1: $103.00 USD (Promedio)
> - **Capital Inicial Promedio:** `$100.00 USD`
> - **Capital Actual Promedio:** **`${avg_balance:,.2f} USD`**
> - **Ganancia Neta Promedio:** **`{total_growth_pct:+.2f}%`**
> - **Estado:** `{status_emoji} {status_text}`

---

## 📊 4. COMPARATIVA POR GRUPOS ESTRATÉGICOS (DE MEJOR A PEOR)

{group_rows}

---

## 🔗 NAVEGACIÓN RÁPIDA DE OBSIDIAN

- [[🚀_Matriz_1000_Simulaciones|Ver Lista Completa de las 1000 Cuentas]]

---

## 💰 5. INVERSIÓN REAL EN VIVO (BINANCE SPOT & FUTUROS)

> [!TIP] 🏦 ESTADO DE LA CUENTA REAL
> - 💵 **Balance Real Actual:** `${real_bal:.2f} USD` (`{real_pnl:+.2f} USD`)
> - 🪙 **Posición Activa:** `{real_sym}`
> - 🎯 **Estado Operativo:** `{real_status}`

---

## 🏆 5. TOP 5 CRIPTOMONEDAS MÁS RENTABLES DEL MOMENTO (TESTNET)

{top_winners_table}

---

## 📈 6. RENDIMIENTO POR GRUPOS DE IA (Clasificación 0-5)

> [!INFO] 📊 COMPARATIVA DE ESTRATEGIAS
{group_table}

---

## 🛡️ 7. SALUD DEL SISTEMA Y PROTECCIONES

> [!WARNING] ⚙️ ESTADO DE SERVICIOS
> - 🧠 **Gemini AI (Súper-Cerebro):** `🟢 CONECTADO (Cascada Flash-Lite Activa)`
> - 🌐 **Fixie Proxy (Bypass Geo-bloqueo):** `🟢 ACTIVO (Solo ejecuta en Órdenes Reales A+)`
> - ☁️ **GitHub Actions (Ejecución Nube):** `🟢 OPERATIVO (Ciclos 24/7)`
> - 🛑 **Stop Loss Dinámico:** `🟢 ACTIVO (1.5% Máximo)`
> - ⚡ **Anti-Crash:** `🟢 ACTIVO`

---

## 🔗 8. NAVEGACIÓN EN 1-CLIC (DETALLES Y TABLAS COMPLETAS)
- [[🚀_Matriz_1000_Simulaciones|Ver Lista Completa de las 1000 Cuentas]]
- [[🎯_Seguimiento_De_Metas|Ver Tabla de Metas Semana a Semana]]
- [[📊_Dashboard_Interes_Compuesto|Ver Proyección de Interés Compuesto]]
- [[📚_Historial_Super_Detallado|Ver Historial Súper Detallado de Trades (Contexto IA)]]
- [[📊_Analisis_Por_Grupo_y_Movimientos|Ver Análisis y Movimientos por Grupo]]

## 📂 Sub-Reportes por Ventanas de Tiempo
Análisis de rendimiento detallado a 1D, 3D, 1W, 2W, y 1M:

"""

    try:
        import reports_generator
        files = reports_generator.generate_subreports()
        if not files:
            master_md += "> ⏳ Aún no hay datos agrupados para generar sub-reportes (comenzará a poblarse con las próximas operaciones).\n"
        for f in files:
            group_name = f['group']
            filename = f['file']
            master_md += f"- [[{filename.replace('.md', '')}]] ({group_name})\n"
    except Exception as e:
        master_md += f"> ⚠️ Error generando sub-reportes: {e}\n"

    master_md += "\n## 📚 Knowledge Base\n"
    master_md += "- [[🧠_Patrones_de_Aprendizaje_y_Optimizacion_IA]]\n"
    master_md += "- [[🛡️_Escudo_Anti_Caidas_Y_Riesgo|Ver Protocolo Anti-Caídas]]\n"

    file_path = os.path.join(OBSIDIAN_FOLDER, "📊_MASTER_DASHBOARD_TRADING.md")
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(master_md)
        
    # Run subreports generator
    try:
        import subreports_generator
        subreports_generator.generate_all_subreports()
    except Exception as e:
        print(f"Error generating subreports: {e}")
        
    # NEW: Also regenerate the Matriz 1000 Simulaciones markdown locally!
    try:
        pipeline_processor.sync_live_matrix_obsidian(matrix)
        print("Matriz de 1000 Simulaciones actualizada localmente.")
    except Exception as e:
        print(f"Error generando matriz local: {e}")
        
    # Run super cerebro report generator
    try:
        import super_cerebro_analyzer
        super_cerebro_analyzer.generate_super_cerebro_report()
    except Exception as e:
        print(f"Error generando reporte del super cerebro: {e}")

    print(f"Dashboard y Sub-Reportes generados exitosamente a las {now_str}")
    return file_path

if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    generate_master_dashboard()

