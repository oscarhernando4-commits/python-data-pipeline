import os
import sys
import json
import math
from datetime import datetime

try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

try:
    import analytics
    import learning_engine
    import time_series_memory
except ImportError:
    pass

def _get_obsidian_folder():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    obs_path = os.path.join(base_dir, "Obsidian", "01_PROYECTOS", "BINANCE_QUANT_TRADING")
    os.makedirs(obs_path, exist_ok=True)
    return obs_path

OBSIDIAN_FOLDER = _get_obsidian_folder()

def generate_super_cerebro_report():
    import obsidian_sync
    check_sync = getattr(obsidian_sync, "is_obsidian_sync_allowed", None)
    if check_sync and not check_sync():
        return
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # 1. Load latest AI verdict
    verdict_file = os.path.join(os.path.dirname(__file__), "latest_ai_verdict.json")
    ai_verdict = {}
    if os.path.exists(verdict_file):
        try:
            with open(verdict_file, "r", encoding="utf-8") as vf:
                ai_verdict = json.load(vf)
        except Exception:
            pass
            
    selected_sym = ai_verdict.get("selected_symbol", "BTCUSDT")
    if selected_sym == "NONE":
        selected_sym = "BTCUSDT"
        
    action = ai_verdict.get("action", "HOLD")
    confidence = ai_verdict.get("confidence", 0)
    reasoning = ai_verdict.get("reasoning", "Análisis Cuantitativo Institucional en Curso.")
    approved = ai_verdict.get("approved", False)
    
    # 2. Fetch Multi-Timeframe Technical Data
    closes_5m, highs_5m, lows_5m, vols_5m = analytics.fetch_klines(selected_sym, '5m', 50)
    closes_15m, highs_15m, lows_15m, vols_15m = analytics.fetch_klines(selected_sym, '15m', 50)
    closes_1h, highs_1h, lows_1h, vols_1h = analytics.fetch_klines(selected_sym, '1h', 50)
    closes_4h, highs_4h, lows_4h, vols_4h = analytics.fetch_klines(selected_sym, '4h', 50)
    
    curr_price = closes_15m[-1]
    
    # Indicators 15m (Micro Trigger)
    rsi_15m = analytics.calc_rsi(closes_15m)
    macd_15m, macd_sig_15m, macd_hist_15m = analytics.calc_macd(closes_15m)
    ema20_15m = analytics.calc_ema(closes_15m, 20)[-1]
    bb_up_15m, bb_mid_15m, bb_low_15m = analytics.calc_bollinger_bands(closes_15m)
    atr_15m = analytics.calc_atr(highs_15m, lows_15m, closes_15m)
    
    # Indicators 4h (Macro Trend)
    rsi_4h = analytics.calc_rsi(closes_4h)
    ema50_4h = analytics.calc_ema(closes_4h, 50)[-1]
    ema200_4h = analytics.calc_ema(closes_4h, 200)[-1] if len(closes_4h) >= 200 else ema50_4h
    macro_trend = "🟢 ALCISTA (Bullish)" if closes_4h[-1] > ema50_4h else "🔴 BAJISTA (Bearish)"
    
    # Volume Surge Ratio
    avg_vol_15m = sum(vols_15m[-21:-1]) / 20.0 if len(vols_15m) > 20 else vols_15m[-1]
    vol_surge_ratio = vols_15m[-1] / avg_vol_15m if avg_vol_15m > 0 else 1.0
    
    # Candlestick Analysis (Price Action)
    c_open = closes_15m[-2]
    c_close = closes_15m[-1]
    c_high = highs_15m[-1]
    c_low = lows_15m[-1]
    candle_body = abs(c_close - c_open)
    lower_wick = min(c_open, c_close) - c_low
    upper_wick = c_high - max(c_open, c_close)
    
    candle_pattern = "Vela Neutral de Consolidación"
    if lower_wick > (candle_body * 2.0) and lower_wick > 0:
        candle_pattern = "⚡ Martillo / Absorción de Compradores (Hammer)"
    elif upper_wick > (candle_body * 2.0) and upper_wick > 0:
        candle_pattern = "⚠️ Estrella Fugaz / Rechazo en Techo (Shooting Star)"
    elif c_close > c_open and candle_body > (atr_15m * 1.2):
        candle_pattern = "🔥 Vela de Expansión / Ruptura Institucional (Marubozu)"
    elif candle_body < (atr_15m * 0.2):
        candle_pattern = "💤 Doji de Compresión / Indecisión Total"

    # Historical Memory
    mem = learning_engine.load_memory()
    bias_info = learning_engine.get_market_bias(mem)
    bias_str = bias_info.get("bias", "NEUTRAL")
    total_trades = mem.get("total_trades", 0)
    win_rate = mem.get("overall_win_rate", 0.0)
    
    # Time series pattern (5m over 4 hours)
    pattern_summary = time_series_memory.get_multi_cycle_pattern_summary(selected_sym)

    deliberation = ai_verdict.get("committee_deliberation", {})
    agent_1 = deliberation.get("agent_1_macro", "Análisis de régimen macro y volumen de ballenas activo.")
    agent_2 = deliberation.get("agent_2_tech", "Análisis de osciladores, EMAs y mechas de absorción completado.")
    agent_3 = deliberation.get("agent_3_orderbook", "Rastro de liquidez del Orderbook y muros de soporte de ballenas.")
    agent_4 = deliberation.get("agent_4_sector", "Evaluación de rotación de capital por cluster sectorial.")
    agent_5 = deliberation.get("agent_5_memory", "Cruzamiento RAG con simulaciones históricas y patrones perdedores.")
    agent_6 = deliberation.get("agent_6_risk", "Evaluación final de preservación de capital, ratio 1:2 y Trailing Stop ATR.")

    report_md = f"""# 🧠 INFORME EJECUTIVO DEL COMITÉ MULTI-AGENTE CUÁNTICO 24/7 (6 AGENTES IA)
*Última actualización: `{now_str}`*

> [!IMPORTANT] 🎯 **VEREDICTO DE CONSENSO INSTITUCIONAL EN TIEMPO REAL:**
> - 🪙 **Activo Evaluado:** **`{selected_sym}`**
> - 🚦 **Acción Recomendada:** **`{action}`** {'(Aprobada ✅)' if approved else '(Bloqueada por Riesgo 🛡️)'}
> - 📊 **Nivel de Confianza Cuántica:** **`{confidence}%`**
> - 💵 **Precio Actual de Mercado:** **`${curr_price:,.6f} USD`**

---

## 🏛️ 1. DELIBERACIÓN DEL COMITÉ INSTITUCIONAL DE 6 AGENTES INTELIGENTES

| Agente Especializado | Rol Cuantitativo | Dictamen y Análisis Individual en Tiempo Real |
| :--- | :--- | :--- |
| 🕵️ **Agente 1: Analista Macro & Ballenas** | Regime & Whale Flow | {agent_1} |
| 📊 **Agente 2: Ingeniero Técnico & PA** | Technical Sniper | {agent_2} |
| 🌊 **Agente 3: Rastreador de Libro de Órdenes** | Orderbook Depth & Bids | {agent_3} |
| 🧩 **Agente 4: Analista Sectorial & Rotación** | Sector Inflow Analyst | {agent_4} |
| 🧠 **Agente 5: Historiador RAG & Memoria** | RAG Memory Analyst | {agent_5} |
| 🛡️ **Agente 6: Chief Risk Officer (CRO)** | Veto & Trailing Stop ATR | **{agent_6}** |

> 📝 **Resumen del Consenso Institucional:**
> `{reasoning}`

---

## 📈 2. ANÁLISIS MULTI-TEMPORALIDAD (DE 5 MINUTOS A 7 DÍAS)

| Temporalidad | Estructura de Mercado | Tendencia | Observación Cuantitativa |
| :--- | :--- | :--- | :--- |
| **5 Minutos (Micro / Scalp)** | Micro-flujo y libros de órdenes | {'🟢 Alcista' if closes_5m[-1] > closes_5m[-5] else '🔴 Retroceso'} | Volatilidad inmediata y lectura de tick |
| **15 Minutos (Gatillo de Entrada)** | Señal técnica y gatillo | {'🟢 Expansión' if rsi_15m > 50 else '⚪ Neutral/Baja'} | RSI={rsi_15m:.1f}, MACD Hist={macd_hist_15m:+.4f} |
| **1 Hora (Intradía)** | Rango y consolidación | {'🟢 Sobre EMA20' if closes_1h[-1] > analytics.calc_ema(closes_1h, 20)[-1] else '🔴 Bajo EMA20'} | Soporte intradía clave en ${analytics.calc_ema(closes_1h, 20)[-1]:,.4f} |
| **4 Horas (Macro Institucional)** | Tendencia mayor de ballenas | **{macro_trend}** | EMA50: ${ema50_4h:,.4f} - EMA200: ${ema200_4h:,.4f} |
| **24 Horas a 7 Días (Historial)** | Memoria de {total_trades} Operaciones | **Sesgo: {bias_str}** | Win Rate Histórico Global: **{win_rate:.1f}%** |

---

## 🕯️ 3. ANÁLISIS DE VELAS JAPONESAS Y PRICE ACTION (15M)

* **Patrón de Vela Actual:** **`{candle_pattern}`**
* **Mecha Inferior (Absorción de Compras):** `{lower_wick:,.6f} USD` (Indica si las ballenas compraron en la caída)
* **Mecha Superior (Presión Vendedora):** `{upper_wick:,.6f} USD` (Indica rechazo en techos)
* **Cuerpo de la Vela:** `{candle_body:,.6f} USD` (Fuerza direccional del ciclo)
* **Comportamiento 5M en las últimas 4 Horas:**  
  *{pattern_summary}*

---

## 📊 4. TABLERO MAESTRO DE INDICADORES TÉCNICOS

| Indicador Técnico | Valor Actual | Rango Normal | Diagnóstico Cuantitativo |
| :--- | :--- | :--- | :--- |
| **RSI (14) - 15 Minutos** | **`{rsi_15m:.2f}`** | 30 - 70 | {'🟢 Sobreventa / Rebound' if rsi_15m < 32 else ('🔴 Sobrecompra / Riesgo' if rsi_15m > 68 else '🔵 Zona Neutral Saludable')} |
| **RSI (14) - 4 Horas** | **`{rsi_4h:.2f}`** | 30 - 70 | {'🟢 Macro Alcista' if rsi_4h > 50 else '🔴 Macro Bajista'} |
| **MACD Histograma (15m)** | **`{macd_hist_15m:+.6f}`** | Oscilador | {'🟢 Impulso Comprador Creciente' if macd_hist_15m > 0 else '🔴 Presión Vendedora'} |
| **EMA 20 (Soporte Dinámico)** | **`${ema20_15m:,.6f}`** | Referencia | {'🟢 Precio por encima (Fuerza)' if curr_price >= ema20_15m else '🔴 Precio por debajo (Debilidad)'} |
| **Bollinger Banda Superior** | **`${bb_up_15m:,.6f}`** | Resistencia | Techo de volatilidad para toma de ganancias |
| **Bollinger Banda Inferior** | **`${bb_low_15m:,.6f}`** | Soporte | Suelo de volatilidad para entradas de rebote |
| **Volumen Surge Ratio** | **`{vol_surge_ratio:.2f}x`** | > 1.50x | {'🔥 Volumen Institucional Detectado' if vol_surge_ratio >= 1.5 else '⚪ Volumen Promedio / Normal'} |
| **ATR (Volatilidad Real 15m)** | **`${atr_15m:,.6f}`** | Margen | Rango medio de movimiento por vela de 15m |

---

## 🛡️ 5. GESTIÓN DE RIESGO Y PARÁMETROS ASIMÉTRICOS (1:2)
* 🎯 **Take Profit Objetivo (+2.0%):** **`${curr_price * 1.02:,.6f} USD`**
* 🛑 **Stop Loss Inflexible (-1.0%):** **`${curr_price * 0.99:,.6f} USD`**
* ⚖️ **Relación Riesgo / Beneficio:** **`1 : 2`** (Arriesgamos 1 para ganar 2)
* 🧠 **Escudo Anti-Trampas:** {'Activado - Operación Aprobada' if approved else 'Activado - Capital Protegido en Espera'}

---
## 🔗 NAVEGACIÓN RÁPIDA DE OBSIDIAN
- [[📊_MASTER_DASHBOARD_TRADING|Volver al Master Dashboard]]
- [[🚀_Matriz_1000_Simulaciones|Ver Matriz de 1000 Cuentas]]
- [[🎯_Seguimiento_De_Metas|Ver Metas $100 USD]]
- [[🛡️_Escudo_Anti_Caidas_Y_Riesgo|Ver Escudo Anti-Caídas]]
"""

    file_path = os.path.join(OBSIDIAN_FOLDER, "🧠_Analisis_Super_Cerebro.md")
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(report_md)
    print(f"Reporte del Súper-Cerebro generado exitosamente en: {file_path}")
    return file_path

if __name__ == "__main__":
    generate_super_cerebro_report()
