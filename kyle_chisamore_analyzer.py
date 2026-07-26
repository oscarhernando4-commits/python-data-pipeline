import os
import json
import sys
from datetime import datetime

OBSIDIAN_FOLDER = r"C:\Users\hosca\Documents\Antigravity\Obsidian\01_PROYECTOS\BINANCE_QUANT_TRADING"

def ensure_obsidian_dir():
    if not os.path.exists(OBSIDIAN_FOLDER):
        os.makedirs(OBSIDIAN_FOLDER, exist_ok=True)

def generate_kyle_chisamore_analysis_note():
    ensure_obsidian_dir()
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    content = f"""---
tags:
  - trading
  - estrategia_kyle_chisamore
  - wyckoff_bollinger_trend
  - interes_compuesto_extremo
  - binance
date: {now_str}
---

# 🧠 ANÁLISIS A PROFUNDIDAD: ESTRATEGIA DE KYLE CHISAMORE ($26 A $2.7M)

> [!NOTE] 💎 DE $26 DÓLARES A $2.7 MILLONES: DESGLOSE TÉCNICO Y SISTÉMICO
> **Última Actualización:** `{now_str}`  
> **Fundador:** InvestiShare (Kyle Chisamore)  
> **Núcleo de la Estrategia:** Expansión de Bandas de Bollinger (*Bollinger Squeeze Trend*), Método Wyckoff de Acumulación Institucional, Métricas Macro On-Chain (NUPL) y Reescalado de Interés Compuesto Acelerado.

---

## 🏛️ 1. LOS 4 PILARES TÉCNICOS DE LA ESTRATEGIA DE KYLE CHISAMORE

```
              [ ANÁLISIS DE MERCADO KYLE CHISAMORE ]
                                 │
     ┌───────────────────────────┼───────────────────────────┐
     ▼                           ▼                           ▼
1. BOLLINGER SQUEEZE       2. MÉTODO WYCKOFF          3. MÉTRICAS MACRO ON-CHAIN
 (Compresión de Volatilidad (Acumulación Institucional (NUPL / Net Unrealized
  y Ruptura de Tendencia)   y Falsa Caída Spring)      Profit/Loss Overheat)
```

---

### 1. 📈 Expansión de Bandas de Bollinger (*Bollinger Squeeze & Trend Following*)
- **La Compresión (BB Squeeze):** Cuando el ancho de las Bandas de Bollinger alcanza su nivel más estrecho de los últimos 20 periodos, indica que la volatilidad se ha reducido al mínimo. El mercado está **almacenando energía explosiva**.
- **Gatillo de Entrada:** El precio rompe la banda superior con una vela impulsiva acompañada de un **disparo de volumen comprador (> 1.5x - 2.0x el promedio)**.
- **Gestión de Tendencia:** La **Banda Media de Bollinger (EMA 20)** actúa como soporte dinámico. No se vende mientras el precio cierre por encima de la Banda Media.

---

### 2. 🕵️ Método Wyckoff de Acumulación Institucional (*Wyckoff Accumulation Schematics*)
- **Fase A/B (Rango de Consolidación):** Las instituciones acumulan silenciosamente posiciones sin mover el precio.
- **El *Spring* (Trampa de Osos):** El precio cae bruscamente por debajo del soporte del rango para sacar los Stop-Losses de los traders minoristas.
- **Gatillo de Confirmación (SOS - Sign of Strength):** Tras el *Spring*, el precio se recupera rápidamente, vuelve a entrar al rango con volumen explosivo y confirma la compra en el *LPS (Last Point of Support)*.

---

### 3. 🌐 Métricas Macro On-Chain (*Net Unrealized Profit/Loss - NUPL*)
- **Zona de Oportunidad / Capitulacion (NUPL < 0):** Zona de compra máxima cuando el mercado está en miedo o pérdidas no realizadas.
- **Zona de Sobrecalentamiento / Euforia (NUPL > 0.75):** Zona de toma de beneficios y reducción drástica de apalancamiento ante riesgo de corrección macro.

---

### 4. 🚀 Interés Compuesto Extremo en Cuentas Pequeñas ($26 a $1,000 USD)
- **Reinversión del 100% de las Ganancias:** En cuentas pequeñas ($26 USD), no se retiran beneficios. Cada dólar ganado se suma de inmediato al margen de la siguiente operación.
- **Riesgo Fijo Asimétrico:** Arriesgar máximo **1.5% a 2% del capital** por trade con un Take-Profit extendido de **1:3 a 1:5 (Ganancias del +4.5% a +10%)**.

---

## 📊 2. CASOS SIMILARES HISTÓRICOS DE TRANSFORMACIÓN DE CAPITAL PEQUEÑO

| Trader / Caso Leyenda | Capital Inicial | Capital Final | Estrategia Clave Utilizada |
| :--- | :---: | :---: | :--- |
| **Kyle Chisamore** | `$26.00 USD` | **`$2.7 Millones USD`** | Bollinger Squeeze + Wyckoff Spring + Interés Compuesto |
| **Dan Zanger** | `$10,775 USD` | **`$42 Millones USD`** | Patrones Chartistas (Cup & Handle, Chart Breakouts) + Volumen |
| **Kristjan Qullamaggie** | `$9,100 USD` | **`$80 Millones USD`** | Breakouts de Episodic Pivots + High Tight Flags + EMA 10/20 |
| **Richard Dennis (Turtles)** | `$400 USD` | **`$200 Millones USD`** | Seguimiento de Tendencia puro (Donchian Breakouts) + Pyramiding |

---

## 🛡️ 3. CÓMO INTEGRAR LA ESTRATEGIA CHISAMORE EN NUESTRO BOT DE BINANCE

Hemos programado los 3 elementos clave en nuestro motor `analytics.py`:

1. **Filtro Bollinger Squeeze Expansion:** Exigir que las Bandas de Bollinger estén comprimidas antes del disparo de volumen.
2. **Filtro Wyckoff Spring Recovery:** Si el precio rompe un soporte clave y se recupera en las siguientes 3 velas de 15m con volumen 1.5x, se clasifica como **Patrón Wyckoff A+ (+25% Puntos de Confluencia)**.
3. **Escala de Interés Compuesto Acelerado:** Avanzar de Nivel de inmediato reinvirtiendo el 100% de la ganancia en la siguiente cuenta.

---

## 🔗 NAVEGACIÓN RÁPIDA
- [[📊_MASTER_DASHBOARD_TRADING|Ver Master Dashboard]]
- [[🚀_Matriz_100_Simulaciones|Ver Matriz de 100 Cuentas]]
- [[🧠_Matriz_De_Aprendizaje|Ver Matriz de IA y Reglas]]
- [[🏛️_Analisis_Historial_Y_Noticias_Cripto|Ver Análisis Histórico Profundo]]
"""

    file_path = os.path.join(OBSIDIAN_FOLDER, "🧠_Estrategia_Kyle_Chisamore_Y_Wyckoff.md")
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)
        
    print(f"Kyle Chisamore strategy note created at: {file_path}")
    return file_path

if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    generate_kyle_chisamore_analysis_note()
