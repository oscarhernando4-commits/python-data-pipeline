import os
import json
from datetime import datetime

DATA_FILE = os.path.join(os.path.dirname(__file__), "trade_memory.json")

def _get_obsidian_folder():
    local_path = r"C:\Users\hosca\Documents\Antigravity\Obsidian\01_PROYECTOS\BINANCE_QUANT_TRADING"
    if os.path.exists(os.path.dirname(local_path)):
        os.makedirs(local_path, exist_ok=True)
        return local_path
    rel_path = os.path.join(os.getcwd(), "Obsidian", "01_PROYECTOS", "BINANCE_QUANT_TRADING")
    os.makedirs(rel_path, exist_ok=True)
    return rel_path

OBSIDIAN_FOLDER = _get_obsidian_folder()

def load_memory():
    if not os.path.exists(DATA_FILE):
        initial_data = {
            "stats": {"total_trades": 0, "wins": 0, "losses": 0, "win_rate_pct": 0.0, "total_pnl_usd": 0.0},
            "learned_rules": {
                "blocked_patterns": [
                    "High impact news within 30 mins (Block Trade)",
                    "Volume surge < 1.1x average during trend reversals (Block Fakeouts)"
                ],
                "boosted_patterns": [
                    "RSI < 30 + MACD Bullish Cross + Volume > 1.5x (High Probability Win)",
                    "4H Macro Trend Alignment with 15M Reversal"
                ]
            },
            "history": []
        }
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(initial_data, f, indent=2, ensure_ascii=False)
        return initial_data
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_memory(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    sync_learning_note(data)

def record_trade_outcome(symbol, side, entry_price, exit_price, pnl_usd, result_type, notes=""):
    data = load_memory()
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    trade_entry = {
        "timestamp": now_str,
        "symbol": symbol.upper(),
        "side": side.upper(),
        "entry_price": entry_price,
        "exit_price": exit_price,
        "pnl_usd": pnl_usd,
        "result": result_type.upper(),  # "WIN" or "LOSS"
        "notes": notes
    }
    
    data["history"].append(trade_entry)
    stats = data["stats"]
    stats["total_trades"] += 1
    if result_type.upper() == "WIN":
        stats["wins"] += 1
    else:
        stats["losses"] += 1
    stats["total_pnl_usd"] += pnl_usd
    stats["win_rate_pct"] = round((stats["wins"] / stats["total_trades"]) * 100.0, 2)
    
    # Auto-adjust rules based on post-mortem
    if result_type.upper() == "LOSS":
        rule = f"Preventive Block for {symbol}: Loss logged at {entry_price} -> {notes or 'Market Whipsaw'}"
        if rule not in data["learned_rules"]["blocked_patterns"]:
            data["learned_rules"]["blocked_patterns"].append(rule)
    elif result_type.upper() == "WIN":
        rule = f"Optimized Setup for {symbol}: Profit logged (+${pnl_usd:.2f}) -> {notes or 'Trend Confluence'}"
        if rule not in data["learned_rules"]["boosted_patterns"]:
            data["learned_rules"]["boosted_patterns"].append(rule)
            
    save_memory(data)
    return trade_entry

def sync_learning_note(data):
    if not os.path.exists(OBSIDIAN_FOLDER):
        os.makedirs(OBSIDIAN_FOLDER, exist_ok=True)
        
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    stats = data["stats"]
    blocked = "\n".join([f"- 🛑 {r}" for r in data["learned_rules"]["blocked_patterns"]])
    boosted = "\n".join([f"- ⚡ {r}" for r in data["learned_rules"]["boosted_patterns"]])
    
    history_rows = ""
    for t in reversed(data["history"][-10:]):
        res_emoji = "🟢 WIN" if t['result'] == 'WIN' else "🔴 LOSS"
        history_rows += f"| {t['timestamp']} | {t['symbol']} | {t['side']} | `${t['entry_price']}` | `${t['exit_price']}` | `${t['pnl_usd']:+.2f}` | {res_emoji} |\n"
    if not history_rows:
        history_rows = "| - | - | - | - | - | - | Esperando primeras operaciones |"

    content = f"""---
tags:
  - trading
  - aprendizaje
  - inteligencia_artificial
  - binance
date: {now_str}
---

# 🧠 Matriz de Aprendizaje Reforzado (Reinforcement Learning Engine)

> **Última Actualización:** `{now_str}`  
> **Sistema:** Optimización Continua de Aciertos & Bloqueo de Fracasos

---

## 📊 Estadísticas Acumuladas
- **Total Operaciones:** `{stats['total_trades']}`
- **Ganadas (WIN):** `{stats['wins']}` | **Perdidas (LOSS):** `{stats['losses']}`
- **Tasa de Acierto (Win Rate):** `{stats['win_rate_pct']}%`
- **PnL Total Neto:** `${stats['total_pnl_usd']:+.2f} USD`

---

## 🛑 Reglas de Bloqueo de Fracasos (Filtros Anti-Pérdida)
*Estas condiciones han sido aprendidas tras fallos y BLOQUEAN automáticamente futuras operaciones de riesgo:*
{blocked}

---

## ⚡ Patrones Ganadores Optimizado (Modelos de Alta Probabilidad)
*Estos patrones han demostrado alta efectividad y AUMENTAN la puntuación de confluencia:*
{boosted}

---

## 📜 Registro de Post-Mortem de Operaciones
| Fecha | Par | Lado | Entrada | Salida | PnL | Resultado |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
{history_rows}
"""
    file_path = os.path.join(OBSIDIAN_FOLDER, "🧠_Matriz_De_Aprendizaje.md")
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)

if __name__ == '__main__':
    data = load_memory()
    sync_learning_note(data)
    print("Learning engine initialized and synced to Obsidian!")
