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

def get_market_bias(data=None):
    if data is None:
        data = load_memory()
    trades = data.get("history", [])[-100:] # Look at last 100 trades for group learning
    long_w=0; long_l=0; short_w=0; short_l=0
    group_stats = {}
    
    for t in trades:
        side = t.get("side", "LONG")
        res = t.get("result", "LOSS")
        grp = t.get("group_name", "Unknown")
        
        if grp not in group_stats:
            group_stats[grp] = {"w": 0, "l": 0, "pnl": 0.0}
            
        group_stats[grp]["pnl"] += float(t.get("pnl_usd", 0.0))
        if res == "WIN":
            group_stats[grp]["w"] += 1
            if side == "LONG": long_w += 1
            elif side == "SHORT": short_w += 1
        else:
            group_stats[grp]["l"] += 1
            if side == "LONG": long_l += 1
            elif side == "SHORT": short_l += 1
            
    # Find Best Group
    best_group_name = None
    best_group_wr = 0.0
    best_group_pnl = -9999
    
    for g, st in group_stats.items():
        total = st["w"] + st["l"]
        if total >= 3: # Must have at least 3 trades to be considered
            wr = (st["w"] / total) * 100
            if wr >= 50.0 and st["pnl"] > 0 and st["pnl"] > best_group_pnl:
                best_group_wr = wr
                best_group_pnl = st["pnl"]
                best_group_name = g
                
    long_total = long_w + long_l
    short_total = short_w + short_l
    long_wr = (long_w / long_total * 100) if long_total > 0 else 0
    short_wr = (short_w / short_total * 100) if short_total > 0 else 0
    
    bias = "NEUTRAL"
    if short_wr > long_wr + 10:
        bias = "FAVOR_SHORT"
    elif long_wr > short_wr + 10:
        bias = "FAVOR_LONG"
        
    return {
        "bias": bias,
        "long_win_rate": round(long_wr, 1),
        "short_win_rate": round(short_wr, 1),
        "long_trades": long_total,
        "short_trades": short_total,
        "best_group": best_group_name,
        "best_group_wr": round(best_group_wr, 1),
        "best_group_pnl": round(best_group_pnl, 2)
    }

def record_trade_outcome(symbol, side, entry_price, exit_price, pnl_usd, result_type, notes="", account_id="Histórico", group_name="Sin Grupo"):
    data = load_memory()
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    trade_entry = {
        "timestamp": now_str,
        "account_id": account_id,
        "group_name": group_name,
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
    bias_info = get_market_bias(data)
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

## 🧭 Sesgo de Aprendizaje Automático (Últimos 100 Trades)
- **Sesgo Actual (Market Bias):** `{bias_info['bias']}`
- **Rendimiento LONG (Compras):** `{bias_info['long_win_rate']}%` de Acierto (en {bias_info['long_trades']} ops recientes)
- **Rendimiento SHORT (Ventas):** `{bias_info['short_win_rate']}%` de Acierto (en {bias_info['short_trades']} ops recientes)
- 🏆 **Grupo de IA Más Rentable:** `{bias_info['best_group'] if bias_info['best_group'] else 'Ninguno superó el umbral'}` (WinRate: {bias_info['best_group_wr']}%, PnL: ${bias_info['best_group_pnl']})
- *Nota:* La IA utilizará este sesgo en tiempo real para descartar operaciones que vayan contra la tendencia comprobada. Y el Dinero Real copiará automáticamente al Grupo Más Rentable.

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
