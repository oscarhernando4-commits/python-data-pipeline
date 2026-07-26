import urllib.request
import json
import time
import sys
import os
import analytics
import fundamental_sentinel
import learning_engine
import obsidian_sync
import master_dashboard_generator
from datetime import datetime

TOP_PAIRS = [
    'BTCUSDT', 'ETHUSDT', 'SOLUSDT', 'BNBUSDT', 'ADAUSDT', 
    'XRPUSDT', 'DOGEUSDT', 'NEARUSDT', 'LINKUSDT', 'AVAXUSDT',
    'DOTUSDT', 'UNIUSDT', 'ATOMUSDT', 'LTCUSDT', 'ETCUSDT',
    'FILUSDT', 'APTUSDT', 'TRXUSDT', 'ARBUSDT', 'OPUSDT'
]

DATA_MATRIX_FILE = os.path.join(os.path.dirname(__file__), "matrix_100_simulations.json")

def get_obsidian_folder():
    local_path = r"C:\Users\hosca\Documents\Antigravity\Obsidian\01_PROYECTOS\BINANCE_QUANT_TRADING"
    if os.path.exists(os.path.dirname(local_path)):
        os.makedirs(local_path, exist_ok=True)
        return local_path
    rel_path = os.path.join(os.getcwd(), "Obsidian", "01_PROYECTOS", "BINANCE_QUANT_TRADING")
    os.makedirs(rel_path, exist_ok=True)
    return rel_path

OBSIDIAN_FOLDER = get_obsidian_folder()

def load_live_matrix():
    now_date = datetime.now().strftime("%y-%m-%d")
    now_time = datetime.now().strftime("%H:%M")
    now_br = f"{now_date}<br>{now_time}"
    
    if not os.path.exists(DATA_MATRIX_FILE):
        accounts = []
        for i in range(1, 101):
            assigned_pair = TOP_PAIRS[(i - 1) % len(TOP_PAIRS)]
            accounts.append({
                "account_id": f"SIM-{i:03d}",
                "symbol": assigned_pair,
                "initial_capital": 100.0,
                "current_balance": 100.0,
                "pnl_usd": 0.0,
                "current_level": 1,
                "consecutive_losses": 0,
                "last_result": "Esperando",
                "last_trade_time": now_br,
                "position": None,
                "trades_count": 0,
                "wins": 0,
                "losses": 0,
                "status": "BUSCANDO_OPORTUNIDAD"
            })
        data = {
            "total_fund_usd": 10000.0,
            "current_total_usd": 10000.0,
            "net_pnl_usd": 0.0,
            "global_win_rate_pct": 0.0,
            "accounts": accounts
        }
        with open(DATA_MATRIX_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return data
    with open(DATA_MATRIX_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
        for acc in data.get("accounts", []):
            pnl = acc.get("pnl_usd", 0.0)
            if "last_result" not in acc or acc["last_result"] in ["NINGUNO", "-"]:
                if pnl > 0:
                    acc["last_result"] = f"🟢 Ganó +${pnl:.2f}"
                elif pnl < 0:
                    acc["last_result"] = f"🔴 Perdió -${abs(pnl):.2f}"
                elif acc.get("position") is not None:
                    acc["last_result"] = "🔵 En Curso"
                else:
                    acc["last_result"] = "Esperando"
            acc["last_trade_time"] = now_br
        return data

def save_live_matrix(data):
    with open(DATA_MATRIX_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    sync_live_matrix_obsidian(data)
    try:
        master_dashboard_generator.generate_master_dashboard()
    except Exception as e:
        print(f"Master dashboard sync note: {e}")

def run_infinite_trading_matrix_cycle():
    sys.stdout.reconfigure(encoding='utf-8')
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    now_date = datetime.now().strftime("%y-%m-%d")
    now_time = datetime.now().strftime("%H:%M")
    now_br = f"{now_date}<br>{now_time}"
    print(f"[{now_str}] 🚀 Running Screen-Optimized Matrix Cycle (100 Accounts)...")
    
    matrix = load_live_matrix()
    accounts = matrix["accounts"]
    
    symbol_analysis_map = {}
    best_market_opportunity = None
    max_market_score = -1

    for s in TOP_PAIRS:
        try:
            tech = analytics.analyze_institutional_grade(s, account_balance=100.0, risk_percentage=1.5)
            final_score = tech.get("confluence_score", 50)
            
            symbol_analysis_map[s] = {
                "tech": tech,
                "score": final_score,
                "price": tech.get("current_price", 0.0),
                "risk": tech.get("institutional_risk_plan", {})
            }
            
            if final_score > max_market_score:
                max_market_score = final_score
                best_market_opportunity = (s, symbol_analysis_map[s])
        except Exception as e:
            print(f"Error fetching live data for {s}: {e}")

    total_balance = 0.0
    global_trades = 0
    global_wins = 0

    for acc in accounts:
        curr_bal = acc["current_balance"]
        curr_level = acc.get("current_level", 1)

        if curr_bal <= 5.0:
            acc["status"] = "💀 Bancarrota"
            total_balance += curr_bal
            continue

        position = acc.get("position", None)

        # 1. EVALUATE LIVE OPEN POSITION
        if position is not None:
            symbol = acc["symbol"]
            analysis = symbol_analysis_map.get(symbol)
            curr_price = analysis["price"] if analysis else position["entry_price"]
            
            entry_p = position["entry_price"]
            tp_min_price = position.get("tp_min", position.get("tp", entry_p * 1.03))
            sl_price = position["sl"]
            
            # WIN CASE: Hit Take-Profit
            if curr_price >= tp_min_price:
                gain_ratio = max((curr_price - entry_p) / entry_p, 0.03)
                pnl = round(curr_bal * gain_ratio, 2)
                
                acc["current_balance"] += pnl
                acc["pnl_usd"] += pnl
                acc["wins"] += 1
                acc["trades_count"] += 1
                acc["consecutive_losses"] = 0
                acc["last_result"] = f"🟢 Ganó +${pnl:.2f}"
                acc["last_trade_time"] = now_br
                acc["position"] = None
                acc["current_level"] = acc.get("current_level", 1) + 1
                acc["status"] = "BUSCANDO_OPORTUNIDAD"
                
                learning_engine.record_trade_outcome(
                    symbol=symbol, side="BUY", entry_price=entry_p, exit_price=curr_price,
                    pnl_usd=pnl, result_type="WIN", notes=f"Win on {symbol} (+${pnl:.2f}) -> Level {acc['current_level']} Re-Trading Started!"
                )

            # LOSS CASE: Hit Stop-Loss (-1.5%)
            elif curr_price <= sl_price:
                loss = round(curr_bal * 0.015, 2)
                acc["current_balance"] -= loss
                acc["pnl_usd"] -= loss
                acc["losses"] += 1
                acc["trades_count"] += 1
                acc["consecutive_losses"] = acc.get("consecutive_losses", 0) + 1
                acc["last_result"] = f"🔴 Perdió -${loss:.2f}"
                acc["last_trade_time"] = now_br
                acc["position"] = None
                acc["status"] = "BUSCANDO_OPORTUNIDAD"
                
                learning_engine.record_trade_outcome(
                    symbol=symbol, side="BUY", entry_price=entry_p, exit_price=curr_price,
                    pnl_usd=-loss, result_type="LOSS", notes=f"Hit SL on {symbol} (-${loss:.2f}). Re-Trading!"
                )
            else:
                unr_pnl = (curr_price - entry_p) * position["qty"]
                unr_pct = ((curr_price - entry_p) / entry_p) * 100.0
                acc["last_trade_time"] = position.get("open_time_br", now_br)
                acc["last_result"] = f"🔵 En Curso"
                acc["status"] = f"EN_OPERACION_VIVO ({symbol} {unr_pct:+.1f}%)"

        # 2. DYNAMIC MARKET ROTATION: IF NO POSITION -> SELECT THE HIGHEST SCORE PAIR IN THE MARKET!
        else:
            selected_symbol = acc["symbol"]
            best_analysis = symbol_analysis_map.get(selected_symbol)
            
            for sym, data_item in symbol_analysis_map.items():
                if data_item["score"] > (best_analysis["score"] if best_analysis else 0):
                    selected_symbol = sym
                    best_analysis = data_item
                    
            if best_analysis and best_analysis["score"] >= 80:
                fundamental_report = fundamental_sentinel.get_crypto_fundamental_sentinel()
                if fundamental_report.get("macro_risk_level") == "HIGH_RISK":
                    acc["status"] = f"🛑 Riesgo Noticias ({fundamental_report.get('sentiment_label')})"
                else:
                    try:
                        import historical_catalyst_analyzer
                        historical_catalyst_analyzer.ensure_symbol_historically_analyzed(selected_symbol)
                    except Exception as e:
                        print(f"Auto-historical analysis notice for {selected_symbol}: {e}")
                        
                    curr_price = best_analysis["price"]
                    sl_dist = max(best_analysis["tech"]["indicators"].get("atr_15m", 0) * 1.5, curr_price * 0.01)
                    sl_target = curr_price - sl_dist
                    tp_min_target = curr_price + (sl_dist * 2.0)
                    tp_max_target = curr_price + (sl_dist * 3.5)
                    qty = round((curr_bal * 0.2) / curr_price, 4)
                    
                    current_hour = datetime.now().hour
                    acc["symbol"] = selected_symbol
                    acc["last_trade_time"] = now_br
                    acc["last_result"] = "🔵 En Curso"
                    acc["position"] = {
                        "entry_price": curr_price,
                        "qty": qty,
                        "sl": sl_target,
                        "tp_min": tp_min_target,
                        "tp_max": tp_max_target,
                        "open_time": now_str,
                        "open_time_br": now_br,
                        "open_hour": current_hour
                    }
                    acc["status"] = f"EN_OPERACION_VIVO ({selected_symbol} @ ${curr_price:.2f})"
            else:
                top_sym = best_market_opportunity[0] if best_market_opportunity else selected_symbol
                top_score = best_market_opportunity[1]["score"] if best_market_opportunity else 50
                acc["status"] = f"BUSCANDO_OPORTUNIDAD ({top_sym} {top_score}pts)"

        total_balance += acc["current_balance"]
        global_trades += acc["trades_count"]
        global_wins += acc["wins"]

    matrix["current_total_usd"] = round(total_balance, 2)
    matrix["net_pnl_usd"] = round(total_balance - 10000.0, 2)
    matrix["global_win_rate_pct"] = round((global_wins / global_trades * 100.0), 2) if global_trades > 0 else 0.0

    save_live_matrix(matrix)
    
    # Execute Real Money Trading Scan for $20 USD Account in parallel
    try:
        import real_money_trader
        real_usdt = real_money_trader.get_real_usdt_balance()
        if real_usdt >= 10.0:
            print(f"💰 Real Money Active Balance: ${real_usdt:.2f} USDT! Checking for A+ opportunities...")
            if best_market_opportunity and best_market_opportunity[1]["score"] >= 80:
                real_money_trader.execute_real_money_trade_if_eligible(
                    symbol=best_market_opportunity[0],
                    score=best_market_opportunity[1]["score"],
                    price=best_market_opportunity[1]["price"]
                )
    except Exception as e_real:
        print(f"Real trader notice: {e_real}")
        
    print(f"[{now_str}] Screen-Optimized Matrix Completed! Total Fund: ${total_balance:,.2f} USD")
    return matrix

def sync_live_matrix_obsidian(matrix):
    ensure_obsidian_dir()
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    now_date = datetime.now().strftime("%y-%m-%d")
    now_time = datetime.now().strftime("%H:%M")
    now_br = f"{now_date}<br>{now_time}"
    accounts = matrix["accounts"]
    
    table_rows = ""
    for acc in accounts:
        last_res = acc.get("last_result", "Esperando")
        last_time = acc.get("last_trade_time", now_br)
        trades_num = acc.get("trades_count", 0)
        pnl = acc.get("pnl_usd", 0.0)
        bal = acc.get("current_balance", 100.0)
        sym = acc.get("symbol", "USDT")
        status_raw = acc.get("status", "")
        
        if "EN_OPERACION_VIVO" in status_raw or acc.get("position") is not None:
            status_clean = f"🔵 En Vivo"
        elif "Riesgo Noticias" in status_raw or "🛑" in status_raw:
            status_clean = f"🛑 Pausado por Noticia"
        elif pnl < 0:
            status_clean = f"🔴 Buscando"
        elif pnl > 0:
            status_clean = f"🟢 Buscando"
        else:
            status_clean = f"🟦 Buscando"
            
        pnl_str = f"+${pnl:.2f}" if pnl >= 0 else f"-${abs(pnl):.2f}"
        
        # NO BACKTICKS AROUND last_time SO <br> COMPILES AS NATIVE HTML LINE BREAK!
        table_rows += f"| **{acc['account_id']}** | **{sym}** | `#{trades_num}` | `{acc['wins']}W/{acc['losses']}L` | {last_time} | `{last_res}` | **`${bal:.2f}`** (`{pnl_str}`) | {status_clean} |\n"

    # Calculate separated account percentages respect to 100 total accounts
    total_acc_count = len(accounts)
    winning_accs = sum(1 for a in accounts if a.get("pnl_usd", 0.0) > 0)
    losing_accs = sum(1 for a in accounts if a.get("pnl_usd", 0.0) < 0)
    active_live_accs = sum(1 for a in accounts if a.get("position") is not None or "En Vivo" in a.get("status", ""))
    
    pct_winning = round((winning_accs / total_acc_count) * 100.0, 1)
    pct_losing = round((losing_accs / total_acc_count) * 100.0, 1)
    pct_active = round((active_live_accs / total_acc_count) * 100.0, 1)

    import real_money_trader
    real_st = real_money_trader.load_real_account_state()

    content = f"""# 💰 INVERSIÓN REAL EN VIVO (BINANCE SPOT REAL - $20.07 USD)

> ⏱️ **Última Actualización del Reporte:** `{now_str}`

| 💵 Capital Depósito | 📈 Balance Actual | 💰 Beneficio Neto (PnL) | 📊 Racha Real | 🎯 Estado Operativo Real |
| :---: | :---: | :---: | :---: | :---: |
| **`$20.07 USD`** | **`${real_st['current_balance_usd']:.2f} USD`** | **`${real_st['net_pnl_usd']:+,.2f} USD`** | `{real_st['wins']}W/{real_st['losses']}L` | **`{real_st['status']}`** |

---

# 🚀 MATRIZ DE 100 CUENTAS TESTNET ($10,000 USD APRENDIZAJE IA)

## 📊 RESUMEN EJECUTIVO GLOBAL ($10,000 USD FONDO TOTAL TESTNET)

- 💵 **Fondo Inicial:** `$10,000.00 USD` (100 Cuentas x $100)
- 📈 **Capital Total Acumulado:** **`${matrix['current_total_usd']:,.2f} USD`**
- 💰 **Beneficio Neto Acumulado:** **`${matrix['net_pnl_usd']:+,.2f} USD`**

### 📊 ESTADO DESGLOSADO DE LAS 100 CUENTAS (% RESPECTO AL TOTAL):
- 🟢 **Cuentas Ganadoras (+3% o más):** **`{pct_winning}%`** (`{winning_accs}` de 100 Cuentas)
- 🔴 **Cuentas en Pérdida (-1.5%):** **`{pct_losing}%`** (`{losing_accs}` de 100 Cuentas)
- 🔵 **Cuentas Operando en Vivo (En Curso):** **`{pct_active}%`** (`{active_live_accs}` de 100 Cuentas)

---

## 💼 TABLA COMPACTA DE LAS 100 CUENTAS

| ID | Cripto | Ops (#) | Racha | Última Op (Fecha / Hora) | Último Resultado | Balance (PnL) | Estado |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
{table_rows}

---

## 🔗 NAVEGACIÓN RÁPIDA
- [[📊_MASTER_DASHBOARD_TRADING|Ver Master Dashboard]]
- [[🎯_Seguimiento_De_Metas|Ver Seguimiento de Metas $100 USD]]
- [[📊_Dashboard_Interes_Compuesto|Ver Dashboard de Interés Compuesto]]
- [[🧠_Matriz_De_Aprendizaje|Ver Matriz de IA y Aprendizaje]]
- [[🛡️_Escudo_Anti_Caidas_Y_Riesgo|Ver Escudo Anti-Caídas]]
"""

    file_path = os.path.join(OBSIDIAN_FOLDER, "🚀_Matriz_100_Simulaciones.md")
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)
    return file_path

def ensure_obsidian_dir():
    if not os.path.exists(OBSIDIAN_FOLDER):
        os.makedirs(OBSIDIAN_FOLDER, exist_ok=True)

if __name__ == '__main__':
    run_infinite_trading_matrix_cycle()
