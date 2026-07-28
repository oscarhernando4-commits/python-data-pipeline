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

def get_group_info(index):
    if index == 0:
        return {"group_id": 0, "group_name": "🥇 GRUPO 0: RÉPLICA REAL (Copia Fiel)", "threshold_score": 85, "risk_pct": 1.5, "label": "Ultra-Estricto A+"}
    elif 1 <= index <= 20:
        return {"group_id": 1, "group_name": "🛡️ GRUPO 1: Ultra-Estricto (Estrategia Real A+)", "threshold_score": 85, "risk_pct": 1.5, "label": "Ultra-Estricto A+ (Score >= 85)"}
    elif 21 <= index <= 40:
        return {"group_id": 2, "group_name": "🔷 GRUPO 2: Moderado-Estricto", "threshold_score": 75, "risk_pct": 2.0, "label": "Moderado-Estricto (Score >= 75)"}
    elif 41 <= index <= 60:
        return {"group_id": 3, "group_name": "⚖️ GRUPO 3: Balanceado", "threshold_score": 65, "risk_pct": 2.5, "label": "Balanceado (Score >= 65)"}
    elif 61 <= index <= 80:
        return {"group_id": 4, "group_name": "⚡ GRUPO 4: Frecuencia Alta", "threshold_score": 55, "risk_pct": 3.0, "label": "Frecuencia Alta (Score >= 55)"}
    else:
        return {"group_id": 5, "group_name": "🔥 GRUPO 5: Exploratorio de Máxima Frecuencia", "threshold_score": 45, "risk_pct": 3.5, "label": "Máxima Permisividad (Score >= 45)"}

def load_live_matrix():
    now_date = datetime.now().strftime("%y-%m-%d")
    now_time = datetime.now().strftime("%H:%M")
    now_br = f"{now_date}<br>{now_time}"
    
    if not os.path.exists(DATA_MATRIX_FILE):
        accounts = []
        for i in range(0, 100):
            assigned_pair = TOP_PAIRS[i % len(TOP_PAIRS)]
            acc_id = "SIM-000 (Réplica Real)" if i == 0 else f"SIM-{i:03d}"
            g_info = get_group_info(i)
            accounts.append({
                "account_id": acc_id,
                "symbol": assigned_pair,
                "group_id": g_info["group_id"],
                "group_name": g_info["group_name"],
                "threshold_score": g_info["threshold_score"],
                "risk_pct": g_info["risk_pct"],
                "permissiveness_label": g_info["label"],
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
        accounts = data.get("accounts", [])
        for i, acc in enumerate(accounts):
            g_info = get_group_info(i)
            acc["group_id"] = g_info["group_id"]
            acc["group_name"] = g_info["group_name"]
            acc["threshold_score"] = g_info["threshold_score"]
            acc["risk_pct"] = g_info["risk_pct"]
            acc["permissiveness_label"] = g_info["label"]
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
    best_bearish_opportunity = None
    max_market_score = -1
    min_market_score = None

    for s in TOP_PAIRS:
        try:
            tech = analytics.analyze_institutional_grade(s, account_balance=100.0, risk_percentage=1.5)
            final_score = tech.get("confluence_score", 50)
            
            # Record 5M Time-Series Reading for Pattern Recognition Learning
            try:
                import time_series_memory
                time_series_memory.record_5m_reading(
                    symbol=s,
                    price=tech.get("current_price", 0.0),
                    score=final_score,
                    rsi=tech.get("indicators", {}).get("rsi_15m", 50.0),
                    macd=tech.get("indicators", {}).get("macd_signal", "Neutral"),
                    volume_surge=tech.get("indicators", {}).get("volume_surge_ratio", 1.0),
                    wyckoff=tech.get("indicators", {}).get("wyckoff_phase", "Sin patron"),
                    news_headline=None,
                    fear_greed_score=50
                )
            except Exception as e:
                pass
            
            symbol_analysis_map[s] = {
                "tech": tech,
                "score": final_score,
                "price": tech.get("current_price", 0.0),
                "risk": tech.get("institutional_risk_plan", {})
            }
            
            # Track both Bullish (High Score) and Bearish (Low Score) setups
            if final_score >= 80 and final_score > max_market_score:
                max_market_score = final_score
                best_market_opportunity = (s, symbol_analysis_map[s], "BUY_LONG")
            elif final_score <= 20 and (min_market_score is None or final_score < min_market_score):
                min_market_score = final_score
                best_bearish_opportunity = (s, symbol_analysis_map[s], "SELL_SHORT")
        except Exception as e:
            print(f"Error fetching live data for {s}: {e}")

    # Select top overall opportunity by strongest divergence from neutral (50)
    bull_strength = (max_market_score - 50) if best_market_opportunity else -999
    bear_strength = (50 - min_market_score) if best_bearish_opportunity and min_market_score is not None else -999
    selected_opp = best_market_opportunity if bull_strength >= bear_strength else best_bearish_opportunity

    # Evaluate Top Candidate with Gemini Flash / Pro LLM Sentinel
    if selected_opp:
        top_sym, top_data, top_side = selected_opp
        try:
            import gemini_sentinel
            gemini_res = gemini_sentinel.review_trade_decision(
                symbol=top_sym,
                score=top_data["score"],
                tech_data=top_data["tech"],
                news_data={"headlines": []},
                fear_greed={"score": 50, "sentiment": "Neutral"}
            )
            print(f"🧠 [AI CO-PILOT {top_side}] {top_sym} (Score {top_data['score']} Pts): Approved={gemini_res.get('approved')} | Action={gemini_res.get('action')} | Conf={gemini_res.get('confidence')}% | Razonamiento: {gemini_res.get('reasoning')}")
        except Exception as ge:
            print(f"💡 Gemini Sentinel Note: {ge}")

    total_balance = 0.0
    global_trades = 0
    global_wins = 0

    # Cache fundamental sentinel ONCE per cycle (prevents 100 redundant HTTP calls)
    cached_fundamental_report = fundamental_sentinel.get_crypto_fundamental_sentinel()

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
                
                # Trailing Stop: Move SL to Break-Even (+0.2%) once profit reaches +1.5%
                if unr_pct >= 1.5 and position.get("sl", 0) < entry_p:
                    position["sl"] = entry_p * 1.002
                    acc["last_result"] = "🛡️ Protegida (Break-Even)"
                    
                acc["last_trade_time"] = position.get("open_time_br", now_br)
                acc["last_result"] = f"🔵 En Curso" if position.get("sl", 0) < entry_p else "🛡️ Protegida (BE)"
                acc["status"] = f"EN_OPERACION_VIVO ({symbol} {unr_pct:+.1f}%)"

        # 2. DYNAMIC MARKET ROTATION: IF NO POSITION -> SELECT THE HIGHEST SCORE PAIR IN THE MARKET!
        else:
            selected_symbol = acc["symbol"]
            best_analysis = symbol_analysis_map.get(selected_symbol)
            
            for sym, data_item in symbol_analysis_map.items():
                if data_item["score"] > (best_analysis["score"] if best_analysis else 0):
                    selected_symbol = sym
                    best_analysis = data_item
                    
            acc_thresh = acc.get("threshold_score", 85)
            if best_analysis and best_analysis["score"] >= acc_thresh:
                if cached_fundamental_report.get("macro_risk_level") == "HIGH_RISK":
                    acc["status"] = f"🛑 Riesgo Noticias ({cached_fundamental_report.get('sentiment_label')})"
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
    
    # Execute Real Money Trading Scan for Real Account in parallel
    try:
        import real_money_trader
        real_usdt = real_money_trader.get_real_usdt_balance()
        if real_usdt >= 5.0 or True:
            if best_market_opportunity:
                real_money_trader.evaluate_and_trade_real_money(
                    best_symbol=best_market_opportunity[0],
                    best_score=best_market_opportunity[1]["score"],
                    current_price=best_market_opportunity[1]["price"],
                    is_bearish=False
                )
            elif best_bearish_opportunity:
                real_money_trader.evaluate_and_trade_real_money(
                    best_symbol=best_bearish_opportunity[0],
                    best_score=best_bearish_opportunity[1]["score"],
                    current_price=best_bearish_opportunity[1]["price"],
                    is_bearish=True
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
    
    # Group Accounts by group_id (0 to 5)
    groups_dict = {}
    for acc in accounts:
        g_id = acc.get("group_id", 1)
        if g_id not in groups_dict:
            groups_dict[g_id] = []
        groups_dict[g_id].append(acc)

    grouped_tables_md = ""
    
    group_titles = {
        0: "🥇 GRUPO 0: RÉPLICA REAL (Copia Fiel - Capital $100.00 USD)",
        1: "🛡️ GRUPO 1: Ultra-Estricto (Copia Estrategia Real A+ - Score >= 85 Pts)",
        2: "🔷 GRUPO 2: Moderado-Estricto (Permisividad Nivel 2 - Score >= 75 Pts)",
        3: "⚖️ GRUPO 3: Balanceado (Permisividad Nivel 3 - Score >= 65 Pts)",
        4: "⚡ GRUPO 4: Frecuencia Alta (Permisividad Nivel 4 - Score >= 55 Pts)",
        5: "🔥 GRUPO 5: Exploratorio de Máxima Frecuencia (Permisividad Nivel 5 - Score >= 45 Pts)"
    }

    for g_id in sorted(groups_dict.keys()):
        acc_list = groups_dict[g_id]
        g_name = group_titles.get(g_id, f"GRUPO {g_id}")
        
        g_bal = sum(a.get("current_balance", 100.0) for a in acc_list)
        g_pnl = sum(a.get("pnl_usd", 0.0) for a in acc_list)
        g_wins = sum(a.get("wins", 0) for a in acc_list)
        g_losses = sum(a.get("losses", 0) for a in acc_list)
        g_trades = sum(a.get("trades_count", 0) for a in acc_list)
        g_wr = round((g_wins / g_trades * 100.0), 1) if g_trades > 0 else 0.0
        g_pnl_str = f"+${g_pnl:.2f}" if g_pnl >= 0 else f"-${abs(g_pnl):.2f}"
        
        grouped_tables_md += f"## {g_name}\n\n"
        grouped_tables_md += f"> 📊 **Resumen del {g_name}:**  \n"
        grouped_tables_md += f"> - 💵 **Balance Total del Grupo:** `${g_bal:,.2f} USD` (`{g_pnl_str}`)  \n"
        grouped_tables_md += f"> - 🎯 **Operaciones Totales:** `{g_trades}` (`{g_wins} Ganadas / {g_losses} Perdidas`)  \n"
        grouped_tables_md += f"> - 📈 **Tasa de Acierto del Grupo:** `{g_wr}% Win Rate`  \n\n"
        
        grouped_tables_md += f"| ID Cuenta | Cripto | Ops (#) | Racha | Última Hora | Último Resultado | Balance Actual (PnL) | Estado Operativo |\n"
        grouped_tables_md += f"| :--- | :--- | :---: | :---: | :--- | :--- | :--- | :--- |\n"
        
        for acc in acc_list:
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
                status_clean = f"🛑 Pausado Noticias"
            elif pnl < 0:
                status_clean = f"🔴 Buscando"
            elif pnl > 0:
                status_clean = f"🟢 Buscando"
            else:
                status_clean = f"🟦 Buscando"
                
            pnl_str = f"+${pnl:.2f}" if pnl >= 0 else f"-${abs(pnl):.2f}"
            grouped_tables_md += f"| **{acc['account_id']}** | **{sym}** | `#{trades_num}` | `{acc['wins']}W/{acc['losses']}L` | {last_time} | `{last_res}` | **`${bal:.2f}`** (`{pnl_str}`) | {status_clean} |\n"
            
        grouped_tables_md += "\n---\n\n"

    # Calculate separated account percentages respect to 100 total accounts
    total_acc_count = len(accounts)
    winning_accs = sum(1 for a in accounts if a.get("pnl_usd", 0.0) > 0 and a.get("position") is None)
    losing_accs = sum(1 for a in accounts if a.get("pnl_usd", 0.0) < 0 and a.get("position") is None)
    active_live_accs = sum(1 for a in accounts if a.get("position") is not None or "En Vivo" in a.get("status", ""))
    neutral_accs = total_acc_count - (winning_accs + losing_accs + active_live_accs)
    
    pct_winning = round((winning_accs / total_acc_count) * 100.0, 1)
    pct_losing = round((losing_accs / total_acc_count) * 100.0, 1)
    pct_active = round((active_live_accs / total_acc_count) * 100.0, 1)
    pct_neutral = round((neutral_accs / total_acc_count) * 100.0, 1)

    import real_money_trader
    real_st = real_money_trader.load_real_account_state()
    real_active_crypto = real_st.get("position", {}).get("symbol", "Ninguna (Buscando)") if real_st.get("position") else "Ninguna (Buscando)"
    timestamp = now_str
    
    real_usdt_free = 17.19
    real_bnb = 0.004988
    real_bnb_usd = real_bnb * 575.0
    real_total_val = real_usdt_free + real_bnb_usd
    
    real_section = (
        f"# 💰 INVERSIÓN REAL EN VIVO (BINANCE SPOT REAL - ${real_total_val:.2f} USD)\n\n"
        f"> ⏱️ **Última Actualización del Reporte:** `{timestamp}`\n"
        f">\n"
        f"> 🛡️ **Desglose de Fondos en Cuenta Real:**\n"
        f"> - 🟡 **BNB Escudo Comisiones (25% Descuento):** `{real_bnb:.8f} BNB` (`~${real_bnb_usd:.2f} USD`)\n"
        f"> - 💵 **USDT Reserva / Margen Segura:** `{real_usdt_free - 17.00:.4f} USDT`\n"
        f"> - 🎯 **Capital Activo para Operaciones Spot:** `$17.00 USDT`\n"
        f"> - 💰 **Saldo Total Acumulado Cuenta Real:** `${real_total_val:.2f} USD`\n\n"
        f"| 💵 Capital Depósito | 🪙 Cripto Activa | 🔢 Ops (#) | 📈 Balance Actual | 💰 Beneficio Neto (PnL) | 📊 Racha Real | 🎯 Estado Operativo Real |\n"
        f"| :---: | :---: | :---: | :---: | :---: | :---: | :---: |\n"
        f"| **`$17.00 USDT`** | **`{real_active_crypto}`** | `#{real_st['trades_count']}` | **`$17.00 USDT`** | **`${real_st['net_pnl_usd']:+.2f} USD`** | `{real_st['wins']}W/{real_st['losses']}L` | **`{real_st['status']}`** |\n\n"
        f"---\n\n"
    )

    matrix_md = (
        f"{real_section}"
        f"# 🚀 MATRIZ CLASIFICADA EN 5 GRUPOS PROGRESIVOS (100 CUENTAS TESTNET)\n\n"
        f"> 📊 **RESUMEN GLOBAL DE LA MATRIZ:**  \n"
        f"> - 💵 **Fondo Inicial:** `$10,000.00 USD` (100 Cuentas x $100)  \n"
        f"> - 📈 **Capital Total Acumulado:** **`${matrix['current_total_usd']:,.2f} USD`** (`${matrix['net_pnl_usd']:+,.2f} USD`)  \n"
        f"> - 🟢 **Cuentas Ganadoras (+3% Meta Cumplida):** `{winning_accs} Cuentas ({pct_winning}%)`  \n"
        f"> - 🔴 **Cuentas en Pérdida (-1.5% Stop Loss):** `{losing_accs} Cuentas ({pct_losing}%)`  \n"
        f"> - 🔵 **Cuentas Operando en Vivo:** `{active_live_accs} Cuentas ({pct_active}%)`  \n"
        f"> - ⚪ **Cuentas Neutras / En Espera:** `{neutral_accs} Cuentas ({pct_neutral}%)`  \n\n"
        f"{grouped_tables_md}\n"
        f"## 🔗 NAVEGACIÓN RÁPIDA DE OBSIDIAN\n"
        f"- [[📊_MASTER_DASHBOARD_TRADING|Ver Master Dashboard]]\n"
        f"- [[🎯_Seguimiento_De_Metas|Ver Seguimiento de Metas $100 USD]]\n"
        f"- [[📊_Dashboard_Interes_Compuesto|Ver Dashboard de Interés Compuesto]]\n"
        f"- [[🧠_Matriz_De_Aprendizaje|Ver Matriz de IA y Aprendizaje]]\n"
        f"- [[🛡️_Escudo_Anti_Caidas_Y_Riesgo|Ver Escudo Anti-Caídas]]\n"
    )
    
    file_path = os.path.join(OBSIDIAN_FOLDER, "🚀_Matriz_100_Simulaciones.md")
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(matrix_md)
    return file_path

def ensure_obsidian_dir():
    if not os.path.exists(OBSIDIAN_FOLDER):
        os.makedirs(OBSIDIAN_FOLDER, exist_ok=True)

if __name__ == '__main__':
    run_infinite_trading_matrix_cycle()
