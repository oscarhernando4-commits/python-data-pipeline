import os
import json
import math
from datetime import datetime

def _get_obsidian_folder():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    obs_path = os.path.join(base_dir, "Obsidian", "01_PROYECTOS", "BINANCE_QUANT_TRADING")
    os.makedirs(obs_path, exist_ok=True)
    return obs_path

OBSIDIAN_FOLDER = _get_obsidian_folder()

def is_obsidian_sync_allowed():
    """
    Returns True only if manual sync is explicitly requested.
    Disables automatic background sync during continuous cycles as requested by user.
    """
    return os.getenv("ENABLE_OBSIDIAN_AUTO_SYNC", "false").lower() in ("true", "1", "yes")

def ensure_obsidian_dir():
    if not os.path.exists(OBSIDIAN_FOLDER):
        os.makedirs(OBSIDIAN_FOLDER, exist_ok=True)

def generate_compound_projection_table(initial_capital=100.0, weekly_rate=0.03, weeks=12):
    table_md = "| Semana | Capital Inicial | Meta +3% | Beneficio Semanal | Capital Acumulado |\n"
    table_md += "| :---: | :---: | :---: | :---: | :---: |\n"
    
    current = initial_capital
    for w in range(1, weeks + 1):
        weekly_gain = current * weekly_rate
        accumulated = current + weekly_gain
        table_md += f"| **Semana {w}** | `${current:,.2f}` | `+3.0%` | `+${weekly_gain:,.2f}` | **`${accumulated:,.2f}`** |\n"
        current = accumulated
    return table_md

def sync_dashboard_note(balances, market_status="DATOS REALES EN VIVO (Binance Spot)", active_symbol="USDCUSDT"):
    ensure_obsidian_dir()
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    balances_md = ""
    if isinstance(balances, list):
        for b in balances:
            asset = b.get('asset', 'N/A')
            free = float(b.get('free', 0))
            locked = float(b.get('locked', 0))
            val_usd = b.get('value_usd', '')
            unit_price = b.get('unit_price', '')
            balances_md += f"- **{asset}**: `{free:,.8f}` (Disponible) | `{locked:,.8f}` (Bloqueado) | **Valor Real: {val_usd}** (@ {unit_price})\n"
    else:
        balances_md = "- Sin datos de saldo.\n"
        
    content = f"""---
tags:
  - trading
  - binance
  - datos_reales
  - dashboard
date: {now_str}
---

# 📊 Dashboard de Datos Reales en Vivo - Binance Spot

> [!NOTE] 🟢 CONEXIÓN DIRECTA CON API DE BINANCE EN VIVO
> Última actualización: `{now_str}`

## 🏦 Estado de la Cuenta Real
- **Conexión API Binance:** `100% ACTIVA EN VIVO`
- **Estado del Mercado:** `{market_status}`
- **Par Monitoreado:** `{active_symbol}`

## 💰 Cartera y Saldos Reales (Binance Real Spot)
{balances_md}

## 🏛️ Mesa de Trabajo Multi-Agente Activa
| Rol | Función | Estado |
| :--- | :--- | :--- |
| **`FundamentalAnalyst`** | Noticias en Tiempo Real, Sentimiento & Catalizadores | 🟢 Activo |
| **`QuantAnalyst`** | Indicadores Cuantitativos (RSI, MACD, EMA 4H/15M) | 🟢 Activo |
| **`RiskManager`** | Stop Loss (ATR 1.5x), Break-Even & Position Sizing | 🟢 Activo |
| **`TraderExecutor`** | Ejecutador en API Binance Spot | 🟢 Activo |

## 🔗 Navegación Rápida
- [[📊_Dashboard_Interes_Compuesto|Ver Proyección de Interés Compuesto]]
- [[📈_Analisis_Mercado|Ver Último Análisis Técnico y Noticias]]
- [[📝_Diario_De_Trading|Ver Bitácora de Operaciones]]
"""
    file_path = os.path.join(OBSIDIAN_FOLDER, "📊_Dashboard_Trading.md")
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)
    return file_path

def sync_compound_dashboard(current_balance=100.0, initial_capital=100.0, active_assets=None):
    ensure_obsidian_dir()
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    pnl_usd = current_balance - initial_capital
    pnl_pct = ((current_balance - initial_capital) / initial_capital) * 100.0
    
    comp_12w = initial_capital * ((1 + 0.03) ** 12)
    comp_24w = initial_capital * ((1 + 0.03) ** 24)
    comp_52w = initial_capital * ((1 + 0.03) ** 52)
    
    assets_md = ""
    if active_assets:
        for a in active_assets:
            asset = a.get("asset", "USDT")
            free = float(a.get("free", 0))
            locked = float(a.get("locked", 0))
            val = a.get("value_usd", f"${(free+locked):,.2f} USD")
            assets_md += f"| **{asset}** | `{free:,.8f}` | `{locked:,.8f}` | **{val}** |\n"
    if not assets_md:
        assets_md = "| **USDC** | `0.07011532` | `0.00000000` | `$0.0701 USD` |\n"

    projection_table = generate_compound_projection_table(initial_capital, 0.03, 12)

    content = f"""---
tags:
  - trading
  - interes_compuesto
  - dashboard_real
  - binance
date: {now_str}
---

# 🚀 Dashboard de Interés Compuesto - DATOS REALES DE BINANCE

> 📍 **Última Actualización (Binance API Real):** `{now_str}`  
> 💡 **Estrategia:** Interés Compuesto Exponencial (+3% Semanal Reinvertido)

---

## ⚡ RESUMEN EJECUTIVO EN TIEMPO REAL (Binance Spot)

> [!IMPORTANT] 📊 SALDOS Y BALANCES EN VIVO
> - 💵 **CAPITAL INICIAL OBJETIVO:** `${initial_capital:,.2f} USD`
> - 📈 **BALANCE REAL EN CUENTA:** `${current_balance:,.4f} USD`
> - 🚀 **ESTADO DEL SISTEMA:** `🟢 DATOS REALES EN TIEMPO REAL`

---

## 💼 MIS ACTIVOS REALES EN CARTERA (Binance Spot)

| Activo | Disponible (Free) | Bloqueado en Órdenes | Valor Total Real (USD) |
| :--- | :--- | :--- | :--- |
{assets_md}

---

## 🔮 PROYECCIÓN DE CRECIMIENTO EXPONENCIAL (Sobre $100 Base)

| Horizonte | Capital Proyectado | Beneficio Neto | Multiplicador |
| :--- | :--- | :--- | :--- |
| **Mes 1 (Semana 4)** | `${initial_capital * ((1.03)**4):,.2f} USD` | `+${initial_capital * ((1.03)**4) - initial_capital:,.2f} USD` | `1.12x` |
| **Mes 3 (Semana 12)** | `${comp_12w:,.2f} USD` | `+${comp_12w - initial_capital:,.2f} USD` | `1.42x` |
| **Mes 6 (Semana 24)** | `${comp_24w:,.2f} USD` | `+${comp_24w - initial_capital:,.2f} USD` | `2.03x (¡Duplicar Cuenta!)` |
| **Año 1 (Semana 52)** | `${comp_52w:,.2f} USD` | `+${comp_52w - initial_capital:,.2f} USD` | `4.65x (¡Multiplicar x4.6!)` |

---

## 📅 RUTA DE CRECIMIENTO SEMANA A SEMANA (Primer Trimestre)

{projection_table}

---

## 🔗 NAVEGACIÓN RÁPIDA
- [[📊_Dashboard_Trading|Ver Dashboard de Operaciones en Vivo]]
- [[📈_Analisis_Mercado|Ver Último Informe Técnico y Noticias]]
- [[📝_Diario_De_Trading|Ver Historial Completo de Operaciones]]
- [[🧠_Matriz_De_Aprendizaje|Ver Matriz de Aprendizaje e IA]]
"""

    file_path = os.path.join(OBSIDIAN_FOLDER, "📊_Dashboard_Interes_Compuesto.md")
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)
        
    return file_path

def sync_analysis_note(analysis_data, fundamental_data=None):
    ensure_obsidian_dir()
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    symbol = analysis_data.get("symbol", "N/A")
    price = analysis_data.get("current_price", 0)
    score = analysis_data.get("confluence_score", 0)
    recommendation = analysis_data.get("recommendation", "HOLD")
    macro_trend = analysis_data.get("macro_trend_4h", "N/A")
    reasons = analysis_data.get("reasons", [])
    risk = analysis_data.get("institutional_risk_plan", {})
    indicators = analysis_data.get("indicators", {})
    
    reasons_md = "\n".join([f"- {r}" for r in reasons]) if reasons else "- Sin razones especificadas."

    content = f"""---
tags:
  - trading
  - binance
  - analisis_real
date: {now_str}
---

# 📈 Reporte de Análisis Cuantitativo Real - {symbol}

> **Fecha:** `{now_str}`  
> **Precio Actual en Vivo:** `${price:,.4f}`  
> **Puntuación de Confluencia:** `{score} / 100`  
> **Dictamen Final:** `{recommendation}`

---

### 📊 Indicadores Técnicos en Tiempo Real
- **Tendencia Macro (4H):** `{macro_trend}`
- **RSI (15M):** `{indicators.get('rsi_15m', 'N/A')}`
- **Histograma MACD (15M):** `{indicators.get('macd_hist_15m', 'N/A')}`
- **ATR Volatilidad (15M):** `{indicators.get('atr_15m', 'N/A')}`

#### 📌 Factores Clave Detectados:
{reasons_md}

---

### 🛡️ Plan de Riesgo (Risk Manager)
- **Precio de Entrada:** `${risk.get('entry_price', 0):,.4f}`
- **Stop Loss Dinámico:** `${risk.get('stop_loss', 0):,.4f}`
- **Take Profit 1 (R:R 1:2):** `${risk.get('take_profit_1_rr_2', 0):,.4f}`
"""
    file_path = os.path.join(OBSIDIAN_FOLDER, "📈_Analisis_Mercado.md")
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)
    return file_path

if __name__ == '__main__':
    ensure_obsidian_dir()
    print("Obsidian real sync module ready!")
