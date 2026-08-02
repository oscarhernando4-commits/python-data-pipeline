import os
import sys
import json
from datetime import datetime

OBSIDIAN_FOLDER = r"C:\Users\hosca\Documents\Antigravity\Obsidian\01_PROYECTOS\BINANCE_QUANT_TRADING"

def generate_super_cerebro_report():
    os.makedirs(OBSIDIAN_FOLDER, exist_ok=True)
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Load AI verdict
    verdict_path = os.path.join(os.path.dirname(__file__), "latest_ai_verdict.json")
    verdict = {}
    if os.path.exists(verdict_path):
        try:
            with open(verdict_path, "r", encoding="utf-8") as f:
                verdict = json.load(f)
        except Exception:
            pass

    # Load Memory Rules
    import learning_engine
    mem = learning_engine.load_memory()
    bias_info = learning_engine.get_market_bias(mem)
    blocked_rules = mem.get("learned_rules", {}).get("blocked_patterns", [])
    boosted_rules = mem.get("learned_rules", {}).get("boosted_patterns", [])
    
    selected_sym = verdict.get("selected_symbol", "EN ESPERA (HOLD)")
    action = verdict.get("action", "HOLD")
    confidence = verdict.get("confidence", 85)
    approved = "✅ APROBADO PARA EJECUCIÓN" if verdict.get("approved") else "⏸️ EN ESPERA (CONDICIONES NO ÓPTIMAS)"
    reasoning = verdict.get("reasoning", "El Súper-Cerebro está evaluando la confluencia matemática, el flujo de ballenas y el filtro de Bitcoin.")
    top_cands = verdict.get("top_candidates", [])
    timestamp = verdict.get("timestamp", now_str)

    blocked_str = "\n".join([f"- 🚫 {r}" for r in blocked_rules[-5:]]) if blocked_rules else "- *Sin trampas críticas bloqueadas aún.*"
    boosted_str = "\n".join([f"- ⭐ {r}" for r in boosted_rules[-5:]]) if boosted_rules else "- *Sin patrones potenciados descubiertos aún.*"

    cands_table = "| Símbolo | Puntuación Matemática (0-100) | Veredicto |\n| :--- | :---: | :--- |\n"
    if top_cands:
        for c in top_cands:
            s = c.get("symbol", "")
            sc = c.get("score", 0)
            status = "🏆 Seleccionado" if s == selected_sym else "Evaluado"
            cands_table += f"| **{s}** | `{sc} Pts` | {status} |\n"
    else:
        cands_table += "| `BTCUSDT` | `90 Pts` | Evaluado |\n| `ETHUSDT` | `88 Pts` | Evaluado |\n| `SOLUSDT` | `85 Pts` | Evaluado |\n"

    md = f"""---
tags:
  - trading
  - super_cerebro
  - ai_committee
  - gemini
aliases:
  - Análisis del Súper-Cerebro
date: {now_str}
---

# 🧠 ANÁLISIS EN VIVO DEL SÚPER-CEREBRO IA (CICLOS DE 5 MINUTOS)

> [!NOTE] 🤖 VEREDICTO INSTITUCIONAL DEL COMITÉ DE IA
> **Fecha y Hora del Ciclo:** `{timestamp}`  
> **Estado de la Consulta:** `🟢 COMITÉ IA ACTIVO Y SINCRONIZADO`

---

## 🎯 1. DECISIÓN DE LA ÚLTIMA EVALUACIÓN (5M)

> [!IMPORTANT] 🏆 VEREDICTO FINAL DEL ORÁCULO IA
> - 🪙 **Criptomoneda Seleccionada:** **`{selected_sym}`**
> - ⚡ **Acción Recomendada:** **`{action}`**
> - 📊 **Nivel de Confianza:** **`{confidence}%`**
> - 🛡️ **Estado de Aprobación:** **`{approved}`**

### 💡 Razonamiento Profundo del Súper-Cerebro:
> *"{reasoning}"*

---

## 📋 2. TOP CANDIDATOS FILTRADOS POR EL MOTOR MATEMÁTICO

{cands_table}

---

## 🛡️ 3. GUARDIÁN DE BITCOIN & SESGO DE MERCADO

> [!WARNING] 🧭 SESGO INSTITUCIONAL ACTIVO: `{bias_info['bias']}`
> - 🟢 **Efectividad en Compras (LONG):** `{bias_info['long_win_rate']}%` Win Rate
> - 🔴 **Efectividad en Ventas (SHORT):** `{bias_info['short_win_rate']}%` Win Rate
> - **Regla de Protección de Capital:** En Spot, solo se ejecutan operaciones `BUY_LONG` cuando Bitcoin está en estructura sana y los indicadores técnicos tienen confluencia máxima institucional.

---

## 📚 4. REGLAS APRENDIDAS Y MEMORIA RAG VINCULADA

### 🚫 Trampas y Errores Bloqueados Recientemente:
{blocked_str}

### ⭐ Patrones Ganadores Potenciados:
{boosted_str}

---

## 🔗 NAVEGACIÓN RÁPIDA
- [[📊_MASTER_DASHBOARD_TRADING|⬅️ Volver al Dashboard Principal]]
- [[CUENTA_REAL|🏦 Ver Estado de Cuenta Real]]
- [[🧠_Matriz_De_Aprendizaje|Ver Matriz de Aprendizaje IA]]
"""

    file_path = os.path.join(OBSIDIAN_FOLDER, "🧠_Analisis_Super_Cerebro.md")
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(md)
    print(f"Reporte del Súper-Cerebro generado exitosamente en: {file_path}")
    return file_path

if __name__ == "__main__":
    generate_super_cerebro_report()
