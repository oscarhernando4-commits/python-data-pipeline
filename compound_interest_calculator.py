import os
import json
import sys
from datetime import datetime

OBSIDIAN_FOLDER = r"C:\Users\hosca\Documents\Antigravity\Obsidian\01_PROYECTOS\BINANCE_QUANT_TRADING"

def ensure_obsidian_dir():
    if not os.path.exists(OBSIDIAN_FOLDER):
        os.makedirs(OBSIDIAN_FOLDER, exist_ok=True)

def generate_compound_interest_note():
    ensure_obsidian_dir()
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    content = f"""---
tags:
  - trading
  - proyeccion_interes_compuesto
  - dinero_real_15_usdt
  - binance
date: {now_str}
---

# 📈 PROYECCIÓN DE INTERÉS COMPUESTO: DINERO REAL ($15.47 USDT)

> [!NOTE] 🧮 MODELO MATEMÁTICO DE CRECIMIENTO CONTINUO (KYLE CHISAMORE)
> **Última Actualización del Modelo:** `{now_str}`  
> **Capital Inicial Trading:** `$15.47 USDT`  
> **Escudo de Comisiones:** `$4.60 USD` en BNB (Descuento 25% Activo)  
> **Parámetros:** Take-Profit `+3.0%` | Stop-Loss `-1.5%` | Relación Riesgo/Beneficio `1:2`

---

## 🧮 1. MATEMÁTICA DE EXPECTATIVA POR OPERACIÓN

Con un Win Rate de Confluencia A+ del 60% (6 victorias por cada 4 pérdidas):

$$\\text{{Expectativa Neta por Trade}} = (0.60 \\times +3.0\\%) + (0.40 \\times -1.5\\%) = +1.80\\% - 0.60\\% = \\mathbf{{+1.20\\% \\text{{ neto por trade}}}}$$

---

## 📊 2. TABLA DE CRECIMIENTO ACUMULADO POR INTERÉS COMPUESTO

Cada vez que el bot gana (+3%), reinvierte el **100% del total capitalizado** en la siguiente operación.

| Tiempo | Escenario Conservador (+0.8% a +1.2% diario) | Escenario Moderado (+1.5% a +2.0% diario) | Multiplicador |
| :--- | :---: | :---: | :---: |
| **Inicio** | **`$15.47 USDT`** | **`$15.47 USDT`** | `1.0x` |
| **1 Mes (30 días)** | **`$19.50 – $22.00 USD`** | **`$25.00 – $28.00 USD`** | `1.4x – 1.8x` |
| **3 Meses (90 días)** | **`$31.00 – $44.00 USD`** | **`$65.00 – $90.00 USD`** | `2.0x – 5.8x` |
| **6 Meses (180 días)** | **`$62.00 – $125.00 USD`** | **`$275.00 – $500.00 USD`** | `4.0x – 32.0x` |
| **1 Año (365 días)** | **`$250.00 – $750.00 USD`** | **`$1,500.00 – $4,000.00+ USD`** | `16.0x – 250.0x` |

---

## 💡 3. LAS 3 REGLAS DE ORO DEL INTERÉS COMPUESTO

1. ❄️ **Efecto Bola de Nieve:** Al principio ($15.47 a $25 USD) los saltos parecen pequeños en dólares, pero al llegar a $100 USD cada trade del +3% suma **+$3.00 USD netos**.
2. 🛡️ **Pérdida Acotada:** Al perder (-1.5%), el bot arriesga solo el saldo actual disponible, evitando caídas profundas.
3. ☁️ **Nube 24/7:** Al estar en la nube de GitHub Actions, el bot no se pierde ninguna oportunidad A+ aunque estés durmiendo.

---

## 🔗 NAVEGACIÓN RÁPIDA
- [[📊_MASTER_DASHBOARD_TRADING|Ver Master Dashboard]]
- [[🚀_Matriz_100_Simulaciones|Ver Matriz de 100 Cuentas]]
- [[🏛️_Informe_Auditoria_Profunda_Sistema_Nube_IA|Ver Auditoría Nube]]
"""

    file_path = os.path.join(OBSIDIAN_FOLDER, "📈_Proyeccion_Interes_Compuesto_Dinero_Real.md")
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)
        
    print(f"Compound interest projection note created at: {file_path}")
    return file_path

if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    generate_compound_interest_note()
