import os
import sys

try:
    sys.stdout.reconfigure(line_buffering=True, encoding='utf-8')
except Exception:
    pass

# Auto-load .env into environment
env_path = os.path.join(os.path.dirname(__file__), ".env")
if os.path.exists(env_path):
    try:
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    k, v = line.split('=', 1)
                    if k.strip() not in os.environ:
                        os.environ[k.strip()] = v.strip()
    except Exception:
        pass

import json
import time
import analytics
import fundamental_sentinel
import learning_engine
import master_dashboard_generator
import strategy_engine
import quant_institutional
import api_connector
from datetime import datetime

def get_top_pairs():
    try:
        with open("top_100_pairs.json", "r", encoding="utf-8") as f:
            pairs = json.load(f)
            if len(pairs) >= 30:
                return pairs
    except Exception:
        pass
    
    # Fallback to the classic 30 pairs if file is missing or broken
    return [
        "BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT", "XRPUSDT", "DOGEUSDT", "ADAUSDT",
        "AVAXUSDT", "LINKUSDT", "DOTUSDT", "MATICUSDT", "LTCUSDT", "BCHUSDT", "UNIUSDT",
        "ATOMUSDT", "ETCUSDT", "XLMUSDT", "FILUSDT", "NEARUSDT", "APTUSDT", "OPUSDT",
        "ARBUSDT", "LDOUSDT", "INJUSDT", "RNDRUSDT", "TIAUSDT", "SUIUSDT", "SEIUSDT",
        "ORDIUSDT", "1000PEPEUSDT"
    ]

TOP_PAIRS = get_top_pairs()

DATA_MATRIX_FILE = os.path.join(os.path.dirname(__file__), "matrix_100_simulations.json")

def get_obsidian_path():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    obs_path = os.path.join(base_dir, "Obsidian", "01_PROYECTOS", "BINANCE_QUANT_TRADING")
    os.makedirs(obs_path, exist_ok=True)
    return obs_path

def get_obsidian_folder():
    return get_obsidian_path()

OBSIDIAN_FOLDER = get_obsidian_folder()

def get_group_info(index):
    return {
        "group_id": 0,
        "group_name": "💎 MATRIZ CUÁNTICA A+ (Condición Real)",
        "threshold_score": 55,
        "risk_pct": 1.0,
        "label": "Ecosistema Real A+ (Base 8D + FII + Vol + Trailing)"
    }


def load_live_matrix():
    now_date = datetime.now().strftime("%y-%m-%d")
    now_time = datetime.now().strftime("%H:%M")
    now_br = f"{now_date}<br>{now_time}"
    
    total_target_accounts = 1000
    
    if not os.path.exists(DATA_MATRIX_FILE):
        accounts = []
        for i in range(0, total_target_accounts):
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
            "total_fund_usd": 100000.0,
            "current_total_usd": 100000.0,
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
        
        # Expand seamlessly if fewer than 1000 accounts
        if len(accounts) < total_target_accounts:
            existing_count = len(accounts)
            for i in range(existing_count, total_target_accounts):
                assigned_pair = TOP_PAIRS[i % len(TOP_PAIRS)]
                acc_id = f"SIM-{i:03d}"
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
            data["accounts"] = accounts
            data["total_fund_usd"] = 100000.0
            data["current_total_usd"] = sum(a.get("current_balance", 100.0) for a in accounts)
            
        for i, acc in enumerate(accounts):
            # Enforce strict 67 Top 100 CMC pairs on every single account
            if acc.get("symbol") not in TOP_PAIRS:
                acc["symbol"] = TOP_PAIRS[i % len(TOP_PAIRS)]
            if acc.get("position") and acc["position"].get("symbol") not in TOP_PAIRS:
                acc["position"] = None
                acc["status"] = "BUSCANDO_OPORTUNIDAD"
                
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
    print(f"[{now_str}] 🚀 Running Screen-Optimized Matrix Cycle (1000 Accounts Genetic Engine)...")
    
    import strategy_engine
    import fundamental_sentinel
    import api_connector
    
    matrix = load_live_matrix()
    accounts = matrix["accounts"]
    
    # 🎯 MODO GUARDIÁN 100% ININTERRUMPIDO EN PRIMER PLANO:
    # Si la cuenta real tiene una posición abierta, SUSPENDER el escaneo del Top 100 y Gemini,
    # y quedarse en un bucle continuo segundo a segundo (T+1s, T+2s, T+3s...) hasta que se cierre la posición.
    real_st_pre = api_connector.load_real_account_state()
    active_pos_pre = real_st_pre.get("position")
    if active_pos_pre and active_pos_pre.get("symbol"):
        sym = active_pos_pre.get("symbol")
        print(f"\n🛡️ [SÚPER-CEREBRO EN GESTIÓN 100% EXCLUSIVA] Posición activa en {sym}.")
        print("⚡ Monitoreo ininterrumpido segundo a segundo activo hasta la salida.\n", flush=True)
        
        import time as _t, threading
        def _async_git_pull_local():
            try:
                import os, subprocess as _sp
                _env = os.environ.copy()
                _env["GIT_TERMINAL_PROMPT"] = "0"
                _sp.run(["git", "pull", "--rebase"], check=False, stdout=_sp.DEVNULL, stderr=_sp.DEVNULL, timeout=5, env=_env)
            except Exception:
                pass

        tick = 0
        while True:
            tick += 1
            _t.sleep(1.0)
            if tick % 30 == 0:
                threading.Thread(target=_async_git_pull_local, daemon=True).start()
            try:
                hb = api_connector.quick_position_heartbeat()
                if not hb or not isinstance(hb, dict) or not hb.get("symbol"):
                    print(f"\n🎯 [OPERACIÓN FINALIZADA TRAS {tick}s] Salida ejecutada con éxito.", flush=True)
                    print("🔄 Sincronizando billetera y reactivando Radar Cuántico de 67 Pares Top 100 CMC...\n", flush=True)
                    try:
                        api_connector.diagnose_full_spot_wallet()
                    except Exception:
                        pass
                    break
                
                p_fmt = f"${hb['price']:.5f}" if hb['price'] < 0.05 else f"${hb['price']:.4f}"
                pnl_sign = "+" if hb['pnl_pct'] >= 0 else ""
                curr_phase = hb.get('phase', 1)
                curr_highest = hb.get('highest_pnl', 0.0)
                
                # 💓 Monitoreo en Vivo Segundo a Segundo en Tiempo Real (flush=True inmediato)
                print(f"💓 [HEARTBEAT 1s | T+{tick}s] {hb['symbol']} @ {p_fmt} | PnL: {pnl_sign}{hb['pnl_pct']:.2f}% (Pico: +{curr_highest:.2f}% | Fase {curr_phase})", flush=True)
            except Exception:
                _t.sleep(1.0)
        # 🧬 SIMULACIONES PARALELAS — corren incluso mientras hay posición real abierta
        try:
            import simulation_engine as _sim_eng
            _matrix_check = _sim_eng.load_matrix()
            _accounts_check = _matrix_check.get("accounts", [])
            # Re-inicializar si: sin group_id O grupos colapsados (menos de 5 grupos distintos)
            from collections import Counter as _GCtr
            _gid_dist = _GCtr(a.get("group_id") for a in _accounts_check)
            _needs_reinit = (
                (_accounts_check and "group_id" not in _accounts_check[0]) or
                (len(_gid_dist) < 5)
            )
            if _needs_reinit:
                print("🧬 [SIM ENGINE] Re-inicializando matriz con 5 grupos genéticos evolutivos...")
                _sim_eng._init_fresh_matrix()
            _sim_result = _sim_eng.run_simulation_cycle({})
            if _sim_result and _sim_result.get("total_trades", 0) > 0:
                _sim_eng.print_simulation_report()
        except Exception as _sim_err:
            pass  # Non-blocking


        return

    symbol_analysis_map = {}
    # Cache fundamental sentinel ONCE per cycle (prevents 100 redundant HTTP calls)
    cached_fundamental_report = fundamental_sentinel.get_crypto_fundamental_sentinel()

    import concurrent.futures

    def analyze_symbol(s):
        try:
            import multi_timeframe_analyzer
            mtf_res = multi_timeframe_analyzer.analyze_multi_timeframe_candles(s)
            tech = analytics.analyze_institutional_grade(s, account_balance=100.0, risk_percentage=1.0)
            
            # Enrich tech with complete Multi-Timeframe Architecture
            tech["mtf_analysis"] = mtf_res
            if "indicators" not in tech:
                tech["indicators"] = {}
            tech["indicators"]["macd_hist_15m"] = mtf_res.get("macd_hist_15m", 0.0)
            tech["indicators"]["gbm_zscore"] = mtf_res.get("gbm_zscore", 0.0)
            tech["indicators"]["pct_b_15m"] = mtf_res.get("pct_b_15m", 0.5)
            tech["indicators"]["vol_surge_2m"] = mtf_res.get("vol_surge_2m", 1.0)
            tech["indicators"]["is_pre_pump_signal"] = mtf_res.get("is_pre_pump_signal", False)
            tech["indicators"]["is_falling_knife"] = mtf_res.get("is_falling_knife", False)
            tech["indicators"]["is_dead_cat_bounce"] = mtf_res.get("is_dead_cat_bounce", False)
            tech["indicators"]["is_macro_bearish_dominance"] = mtf_res.get("is_macro_bearish_dominance", False)
            
            # Blended Multi-Timeframe Confluence Score
            mtf_score = mtf_res.get("multi_tf_score", 50)
            fii_sc = mtf_res.get("fii_score", 0)
            if mtf_res.get("is_falling_knife") or mtf_res.get("is_dead_cat_bounce"):
                final_score = 0
            else:
                raw_blend = (tech.get("confluence_score", 50) * 0.25) + (mtf_score * 0.75)
                if fii_sc >= 45:
                    raw_blend = max(raw_blend, mtf_score * 0.85)
                if mtf_res.get("is_pre_pump_signal"):
                    raw_blend = min(100, raw_blend + 15)
                final_score = int(round(raw_blend))
                
            tech["confluence_score"] = final_score
            
            # Record 5M Time-Series Reading for Pattern Recognition Learning (Thread-Safe)
            try:
                import time_series_memory
                rsi_val = mtf_res.get("rsi_structure", {}).get("rsi_15m", tech.get("indicators", {}).get("rsi_15m", 50.0))
                time_series_memory.record_5m_reading(
                    symbol=s,
                    price=tech.get("current_price", 0.0),
                    score=final_score,
                    rsi=rsi_val,
                    macd="Bullish Cross" if mtf_res.get("is_macd_bullish_cross") else tech.get("indicators", {}).get("macd_signal", "Neutral"),
                    volume_surge=mtf_res.get("vol_surge_15m", tech.get("indicators", {}).get("volume_surge_ratio", 1.0)),
                    wyckoff=tech.get("indicators", {}).get("wyckoff_phase", "Sin patron"),
                    news_headline=None,
                    fear_greed_score=50
                )
            except Exception:
                pass
                
            return s, {
                "tech": tech,
                "score": final_score,
                "price": tech.get("current_price", 0.0),
                "risk": tech.get("institutional_risk_plan", {})
            }
        except Exception as e:
            print(f"Error fetching live data for {s}: {e}")
            return s, None

    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_symbol = {executor.submit(analyze_symbol, s): s for s in TOP_PAIRS}
        for future in concurrent.futures.as_completed(future_to_symbol):
            s = future_to_symbol[future]
            try:
                sym, data = future.result()
                if data:
                    symbol_analysis_map[sym] = data
            except Exception as e:
                print(f"Concurrent exception for {s}: {e}")

    # ============================================================
    # 🏛️ FILTROS INSTITUCIONALES: Browniano + Correlación + Arbitraje
    # ============================================================
    # Build closes map for correlation checking across symbols
    _arb_opportunities = []
    for sym, data in symbol_analysis_map.items():
        tech = data.get("tech", {})
        inst = tech.get("institutional_analysis", {})
        inds = tech.get("indicators", {})
        # Cache GBM verdict per symbol for the brownian filter
        data["_is_brownian_noise"] = inst.get("is_brownian_noise", True)
        data["_gbm_zscore"] = inds.get("gbm_zscore", 0.0)
        data["_trade_quality"] = inst.get("trade_quality", "C_NOISE")
        data["_ou_signal"] = inds.get("ou_signal", "NEUTRAL")
        data["_institutional_verdict"] = inst.get("verdict", "NEUTRAL")

    # For SPOT LONG trading, prioritize the highest scoring bullish assets (Hyenuk Chu / Francisca Serrano Sniper)
    bullish_candidates = []
    for sym, data in symbol_analysis_map.items():
        score = data["score"]
        action = "BUY_LONG" if score >= 55 else "HOLD"
        bullish_candidates.append({
            "symbol": sym,
            "score": score,
            "tech_data": data["tech"],
            "suggested_action": action
        })
    
    # 🏔️ RANKING POR CALIDAD GROUND-ZERO + ADN HISTÓRICO DINÁMICO
    import learning_engine
    _dyn_bl = learning_engine.get_dynamic_blacklist()
    _dyn_elite = learning_engine.get_dynamic_elite()

    def _candidate_rank_key(cand):
        sym = cand["symbol"]
        mtf = cand.get("tech_data", {}).get("mtf_analysis", {})
        fii = mtf.get("fii_score", 0)
        is_overextended = mtf.get("is_overextended_15m", False)
        is_gz = mtf.get("is_ground_zero_micro_ignition", False)
        c1h = mtf.get("range_position_1h", 0.5)
        tf_10s = mtf.get("timeframe_alignment", {}).get("10s", "BEARISH")
        tf_30s = mtf.get("timeframe_alignment", {}).get("30s", "BEARISH")
        
        rank = cand["score"]

        # 🚫 BLACKLIST DINÁMICA: Penalización severa para no desperdiciar cupos en el ranking de candidatos
        if sym in _dyn_bl:
            bl_tier = _dyn_bl[sym]["tier"]
            penalty = 300 if bl_tier == "HARD" else (200 if bl_tier == "MID" else 100)
            rank -= penalty

        # 🌟 WHITELIST ÉLITE DINÁMICA: Impulso a activos con historial comprobado (WR >= 65%)
        if sym in _dyn_elite:
            rank += 35

        # Súper-Prioridad a inyección de capital en suelo (FII >= 60)
        if fii >= 60:
            rank += 60
        elif fii >= 45:
            rank += 30
            
        # Bonus por Doble Ignición 10s + 30s en Verde
        if tf_10s == "BULLISH" and tf_30s == "BULLISH":
            rank += 30
        elif tf_10s == "BULLISH":
            rank += 15
            
        if is_gz and c1h <= 0.35:
            rank += 25
            
        # Penalización de Sangrado Activo Sub-Minuto
        if tf_10s == "BEARISH" and tf_30s == "BEARISH" and fii < 50:
            rank -= 50
        if is_overextended:
            rank -= 200  # Ninguna moneda sobre-extendida puede quitarle el puesto al piso
        return rank

    bullish_candidates.sort(key=_candidate_rank_key, reverse=True)
    top_all_candidates = bullish_candidates  # Analiza el Universo Completo de los 67 Pares Top 100 CMC
    
    import learning_engine
    bias_data = learning_engine.get_market_bias()
    bias_str = f"BIAS: {bias_data['bias']} | WinRates -> LONG: {bias_data['long_win_rate']}% vs SHORT: {bias_data['short_win_rate']}%"
    
    # Inject statistical pattern analysis into AI context
    optimal = learning_engine.get_optimal_entry_conditions()
    if optimal:
        bias_str += f"\n    ANÁLISIS ESTADÍSTICO DE {optimal['total_trades_analyzed']} TRADES:"
        if optimal.get("rsi_analysis"):
            for rsi_range, stats in optimal["rsi_analysis"].items():
                bias_str += f"\n    - RSI {rsi_range}: {stats['win_rate']}% win rate ({stats['total']} trades)"
        if optimal.get("score_analysis"):
            for score_range, stats in optimal["score_analysis"].items():
                bias_str += f"\n    - Score {score_range}: {stats['win_rate']}% win rate ({stats['total']} trades)"
        if optimal.get("trend_analysis"):
            for trend, stats in optimal["trend_analysis"].items():
                bias_str += f"\n    - Trend '{trend}': {stats['win_rate']}% win rate ({stats['total']} trades)"
    
    # Evaluate All Candidates from Top 100 CMC with Gemini Flash / Pro LLM Sentinel
    gemini_res = {}
    selected_opp = None
    import api_connector
    real_st_check = api_connector.load_real_account_state()
    has_active_real_pos = bool(real_st_check.get("position") and real_st_check.get("position", {}).get("symbol"))
    
    if has_active_real_pos:
        act_sym = real_st_check["position"].get("symbol")
        act_entry = real_st_check["position"].get("entry_price", 0)
        print(f"🛡️ [SÚPER-CEREBRO EN MODO GESTIÓN ACTIVA] Posición abierta en {act_sym} @ ${act_entry:.4f}. 100% de recursos enfocados en monitorear la salida y cosechar ganancias...")
        gemini_res = {
            "selected_symbol": "NONE",
            "action": "HOLD",
            "approved": False,
            "confidence": 100,
            "reasoning": f"Posición real activa en {act_sym}. Súper-Cerebro vigilando segundo a segundo para salida óptima."
        }
    elif top_all_candidates:
        try:
            import text_analyzer
            import llm_router
            
            macro_ctx = text_analyzer.get_market_macro_context(
                symbol_analysis_map, 
                cached_fundamental_report.get("fear_and_greed", {"score": 50, "sentiment": "Neutral"}),
                cached_fundamental_report.get("recent_headlines", []),
                top_candidates=top_all_candidates
            )
            
            # ═══════════════════════════════════════════════════════════════════
            # 🔴 GATE MACRO PROGRAMÁTICO (ANTES de gastar tokens de Gemini):
            # Bloqueo duro en Python — NO depende de obediencia del LLM.
            # ═══════════════════════════════════════════════════════════════════
            macro_is_authorized = macro_ctx.get("is_authorized", True) if isinstance(macro_ctx, dict) else True
            if not macro_is_authorized:
                print(f"🔴 [VETO MACRO PROGRAMÁTICO] Semáforo DEFENSIVO. is_authorized=False. Saltando consulta a Gemini AI. CERO operaciones.")
                import api_connector
                api_connector.evaluate_and_trade_real_money(best_symbol=None, best_score=50, current_price=0.0, is_bearish=True, candidates_list=None)
                return
            
            # BTC Guard programático
            try:
                import asset_dna_predictive_engine
                btc_guard = asset_dna_predictive_engine.get_btc_dominance_guard()
                if btc_guard.get("should_avoid_altcoins", False):
                    print(f"🔴 [VETO BTC GUARD PROGRAMÁTICO] BTC dominancia activa. should_avoid_altcoins=True. Saltando consulta a Gemini AI. CERO operaciones.")
                    import api_connector
                    api_connector.evaluate_and_trade_real_money(best_symbol=None, best_score=50, current_price=0.0, is_bearish=True, candidates_list=None)
                    return
            except Exception as e_btc_guard:
                print(f"⚠️ BTC Guard check error (non-blocking): {e_btc_guard}")

            # 🚫 BLOQUEO MACRO BTC 1H 3.0: Si BTC está en tendencia bajista clara en 1H, suspender TODOS los trades.
            # Una altcoin casi nunca puede subir +1.50% si Bitcoin está cayendo en 1H.
            try:
                from multi_timeframe_analyzer import calculate_rsi as _calc_rsi
                import api_connector as _ac_btc
                btc_1h = _ac_btc.get_klines("BTCUSDT", "1h", 25)
                if btc_1h and len(btc_1h) >= 22:
                    _btc_closes_1h = [float(k[4]) for k in btc_1h]
                    _btc_rsi_1h = _calc_rsi(_btc_closes_1h)
                    _btc_ema21_1h = sum(_btc_closes_1h[-21:]) / 21  # SMA21 seed
                    _ema_k = 2 / (21 + 1)  # BUG 7 FIX: calcular EMA21 real con suavizado exponencial
                    for _ep in _btc_closes_1h[-20:]:
                        _btc_ema21_1h = _ep * _ema_k + _btc_ema21_1h * (1 - _ema_k)
                    _btc_price_now = _btc_closes_1h[-1]
                    _btc_below_ema21 = _btc_price_now < _btc_ema21_1h
                    _btc_rsi_bearish = _btc_rsi_1h < 42.0
                    _btc_rsi_crash   = _btc_rsi_1h < 22.0  # crash nuclear extremo = bloqueo total

                    if _btc_rsi_bearish and _btc_below_ema21:
                        if _btc_rsi_crash:
                            # RSI 1H < 22 → DUMP NUCLEAR EXTREMO → bloqueo total
                            print(f"🔴 [VETO BTC MACRO 1H] CRASH NUCLEAR (RSI1H={_btc_rsi_1h:.1f}<22). CERO operaciones.")
                            import api_connector
                            api_connector.evaluate_and_trade_real_money(best_symbol=None, best_score=50, current_price=0.0, is_bearish=True, candidates_list=None)
                            return
                        else:
                            # RSI 1H entre 22-42 → MODO SELECTIVO BAJISTA
                            # Permite candidatos de alta calidad: Score ≥ 78 + FII ≥ 55
                            print(f"🟡 [BTC MACRO 1H] MODO SELECTIVO BAJISTA (RSI1H={_btc_rsi_1h:.1f}<42 | Precio ${_btc_price_now:,.0f} < EMA21=${_btc_ema21_1h:,.0f}).")
                            print(f"   Candidatos ÉLITE con Score≥78 y FII≥55 habilitados.")
                            _btc_bearish_mode = True
                    else:
                        _btc_bearish_mode = False
                        _above_str = "POR ENCIMA" if not _btc_below_ema21 else "BAJO"
                        print(f"✅ [BTC MACRO 1H] BTC en zona segura (RSI1H={_btc_rsi_1h:.1f} | Precio vs EMA21: {_above_str}). Altcoins habilitadas.")

            except Exception as e_btc_1h:
                print(f"⚠️ BTC 1H macro check error (non-blocking): {e_btc_1h}")
            
            # 🔬 EVALUACIÓN MULTI-TEMPORAL ADAPTATIVA DE LOS 67 PARES DEL TOP 100 CMC:
            valid_base_candidates = []
            proximity_candidates = []
            
            for idx, cand in enumerate(top_all_candidates, 1):
                csym = cand["symbol"]
                cdata = symbol_analysis_map.get(csym, {})
                ctech = cdata.get("tech", {})
                cmtf = ctech.get("mtf_analysis", {})
                r1m = cmtf.get("range_position_1m", 0.5) * 100 if cmtf else 50
                r2m = cmtf.get("range_position_2m", 0.5) * 100 if cmtf else 50
                r5m = cmtf.get("range_position_5m", 0.5) * 100 if cmtf else 50
                r10m = cmtf.get("range_position_10m", 0.5) * 100 if cmtf else 50
                r15m = cmtf.get("range_position_15m", 0.5) * 100 if cmtf else 50
                r30m = cmtf.get("range_position_30m", 0.5) * 100 if cmtf else 50
                r1h = cmtf.get("range_position_1h", 0.5) * 100 if cmtf else 50
                r2h = cmtf.get("range_position_2h", 0.5) * 100 if cmtf else 50
                r4h = cmtf.get("range_position_4h", 0.5) * 100 if cmtf else 50
                r1d = cmtf.get("range_position_1d", 0.5) * 100 if cmtf else 50
                obv_t = cmtf.get("obv_trend", "NEUTRAL") if cmtf else "NEUTRAL"
                fii_sc = cmtf.get("fii_score", 0) if cmtf else 0
                rsi_1m = cmtf.get("rsi_1m", 50.0) if cmtf else 50.0
                rsi_15m = cmtf.get("rsi_15m", ctech.get("indicators", {}).get("rsi_15m", 50.0))
                vol_1m = cmtf.get("vol_surge_1m", ctech.get("indicators", {}).get("vol_surge_1m", 1.0))
                vol_15m = cmtf.get("vol_surge_15m", ctech.get("indicators", {}).get("volume_surge_ratio", 1.0))
                
                tf_1m_up = cmtf.get("tf_1m_up", False)
                tf_2m_up = cmtf.get("tf_2m_up", False)
                is_1m_wick = cmtf.get("is_1m_lower_wick_absorption", False)
                is_vwap_rebound = cmtf.get("is_vwap_floor_rebound", False)
                is_double_bottom = cmtf.get("is_double_bottom", False)
                is_bullish_div = cmtf.get("bullish_rsi_divergence", False)
                is_liquidity_sweep = cmtf.get("is_liquidity_sweep", False)
                is_second_touch = cmtf.get("is_second_touch_sniper", False)
                is_sniper_ready = cmtf.get("is_sniper_timing_ready", False)
                is_1m_green_ign = cmtf.get("is_1m_green_ignition", False)
                has_turnaround = bool(tf_1m_up or tf_2m_up or is_1m_wick or is_vwap_rebound or is_double_bottom or is_bullish_div or is_sniper_ready or is_1m_green_ign or is_liquidity_sweep or is_second_touch)
                
                c_score = cand.get("score", 0)
                is_knife = ctech.get("indicators", {}).get("is_falling_knife", False)
                is_dead_cat = ctech.get("indicators", {}).get("is_dead_cat_bounce", False)
                
                r1m_r = round(r1m, 1)
                r2m_r = round(r2m, 1)
                r5m_r = round(r5m, 1)
                r10m_r = round(r10m, 1)
                r15m_r = round(r15m, 1)
                r30m_r = round(r30m, 1)
                r1h_r = round(r1h, 1)
                r2h_r = round(r2h, 1)
                r4h_r = round(r4h, 1)
                r1d_r = round(r1d, 1)
                
                # 🎯 MATRIZ ARMÓNICA MULTI-TEMPORAL ADAPTATIVA DINÁMICA 3.0 (1M a 1D):
                is_a_plus_floor = bool(is_double_bottom or is_bullish_div or is_second_touch or is_liquidity_sweep or fii_sc >= 55)
                max_1d_cap = 65.0 if is_a_plus_floor else 60.0
                max_4h_cap = 55.0
                max_2h_cap = 55.0
                max_1h_cap = 55.0
                max_30m_cap = 55.0 if is_a_plus_floor else 50.0
                max_15m_cap = 55.0 if is_a_plus_floor else 48.0
                max_10m_cap = 52.0 if is_a_plus_floor else 46.0
                max_5m_cap = 50.0 if is_a_plus_floor else 44.0
                max_2m_cap = 50.0 if is_a_plus_floor else 42.0
                max_1m_cap = 52.0 if is_a_plus_floor else 42.0

                diag_reasons = []
                if r1m_r > max_1m_cap: diag_reasons.append(f"1M={r1m:.0f}%>{max_1m_cap:.0f}%")
                if r2m_r > max_2m_cap: diag_reasons.append(f"2M={r2m:.0f}%>{max_2m_cap:.0f}%")
                if r5m_r > max_5m_cap: diag_reasons.append(f"5M={r5m:.0f}%>{max_5m_cap:.0f}%")
                if r10m_r > max_10m_cap: diag_reasons.append(f"10M={r10m:.0f}%>{max_10m_cap:.0f}%")
                if r15m_r > max_15m_cap: diag_reasons.append(f"15M={r15m:.0f}%>{max_15m_cap:.0f}%")
                if r30m_r > max_30m_cap: diag_reasons.append(f"30M={r30m:.0f}%>{max_30m_cap:.0f}%")
                if r1h_r > max_1h_cap: diag_reasons.append(f"1H={r1h:.0f}%>{max_1h_cap:.0f}%")
                if r2h_r > max_2h_cap: diag_reasons.append(f"2H={r2h:.0f}%>{max_2h_cap:.0f}%")
                if r4h_r > max_4h_cap: diag_reasons.append(f"4H={r4h:.0f}%>{max_4h_cap:.0f}%")
                if r1d_r > max_1d_cap: diag_reasons.append(f"1D={r1d:.0f}%>{max_1d_cap:.0f}%")

                is_hybrid_obv_valid = cmtf.get("is_hybrid_obv_valid", False)
                if obv_t == "DISTRIBUTING" and not is_hybrid_obv_valid: diag_reasons.append("OBV=DIST")
                if fii_sc < 40: diag_reasons.append(f"FII={fii_sc}<40")
                if vol_1m < 0.15: diag_reasons.append(f"Vol1M={vol_1m:.2f}x<0.15x")
                if not has_turnaround: diag_reasons.append("SinGiroVerde")

                # 🎯 SCORE MÍNIMO FRANCOTIRADOR 3.0: 75-80 puntos
                min_score_required = 75 if (is_second_touch or is_liquidity_sweep or is_bullish_div or is_double_bottom or fii_sc >= 55) else 80
                if c_score < min_score_required: diag_reasons.append(f"Score={c_score}<{min_score_required}")
                if is_knife: diag_reasons.append("Cuchillo")
                if is_dead_cat: diag_reasons.append("GatoMuerto")

                # ⚡ VOLUME DELTA PRE-FILTRO 3.0
                try:
                    import volume_delta_engine as _vde_pre
                    _vd = _vde_pre.get_volume_delta_signal(csym, window_seconds=30)
                    _vd_buy = _vd.get("buy_ratio_pct", 50.0)
                    _vd_sell_wave = _vd.get("sell_wave", False)
                    _min_buy_ratio = 35.0 if fii_sc >= 55 else 40.0
                    if _vd_sell_wave or _vd_buy < _min_buy_ratio:
                        diag_reasons.append(f"VolDelta=VENDEDOR(Buy={_vd_buy:.0f}%<{_min_buy_ratio:.0f}%,FII={fii_sc})")
                except Exception:
                    pass  # Sin datos de Volume Delta → no bloquear (no-blocking)
                
                is_truly_valid = len(diag_reasons) == 0 and not is_knife and not is_dead_cat

                # 🟡 MODO SELECTIVO BAJISTA: si BTC RSI 1H entre 22-42, filtro élite balanceado
                _bearish_mode = locals().get("_btc_bearish_mode", False)
                if is_truly_valid and _bearish_mode:
                    if c_score < 78 or fii_sc < 55:
                        is_truly_valid = False
                        diag_reasons.append(f"BAJISTA:Score{c_score}<78oFII{fii_sc}<55")
                    else:
                        import api_connector as _ac_bm
                        _bm_state = _ac_bm.load_real_account_state()
                        _bm_ops_hoy = _bm_state.get("daily_wins", 0) + _bm_state.get("daily_losses", 0)
                        if _bm_ops_hoy >= 4:
                            is_truly_valid = False
                            diag_reasons.append(f"BAJISTA:Max4ops/dia({_bm_ops_hoy} ya)")

                dbl_lbl = cmtf.get("double_bottom_label", "🟢 Giro en V")
                canales_str = f"[1M:{r1m:>2.0f}% 5M:{r5m:>2.0f}% 15M:{r15m:>2.0f}% 1H:{r1h:>2.0f}% 4H:{r4h:>2.0f}% 1D:{r1d:>2.0f}%]"

                if is_truly_valid:
                    valid_base_candidates.append(cand)
                    _bm_tag = " 🟡BAJISTA-ELITE" if _bearish_mode else ""
                    print(f"  🟢 [CANDIDATO A+ #{idx:02d}] {csym:<10} | Score: {c_score:>2} | FII: {fii_sc:>2} | {dbl_lbl} | Canales: {canales_str} -> VÁLIDO{_bm_tag}")
                else:
                    proximity_candidates.append({
                        "sym": csym,
                        "rank": idx,
                        "reasons_count": len(diag_reasons),
                        "score": c_score,
                        "fii": fii_sc,
                        "diag": ", ".join(diag_reasons[:2]),
                        "canales": canales_str
                    })

            # 📊 RESUMEN EJECUTIVO COMPACTO (Cero saturación de logs en GitHub Actions)
            if not valid_base_candidates:
                proximity_sorted = sorted(proximity_candidates, key=lambda x: (x["reasons_count"], -x["score"], -x["fii"]))
                top_prox = proximity_sorted[:3]
                prox_str = " | ".join([f"#{p['rank']} {p['sym']} ({p['diag']})" for p in top_prox])
                print(f"📊 [RADAR 67 PARES] 0 Válidos en Suelo Fractal | {len(top_all_candidates)} en Espera | Top 3 Proximidad: [{prox_str}]", flush=True)


            # 🎯 REGLA SUPREMA: Consultar a Gemini AI EXCLUSIVAMENTE para los mejores 2 a 3 finalistas élite
            if not valid_base_candidates:
                print(f"🛡️ [PRESERVACIÓN CUÁNTICA] 0 de {len(top_all_candidates)} activos en Suelo Fractal 8D Élite (1M<=35%, 5M<=38%, 15M<=42%, FII>=60, Vol>=0.35x). Manteniendo 100% liquidez en USDT.\n", flush=True)
                gemini_res = {
                    "selected_symbol": "NONE",
                    "action": "HOLD",
                    "approved": False,
                    "confidence": 98,
                    "committee_deliberation": {
                        "agent_1_macro": "Mercado sin activos en suelo fractal élite.",
                        "agent_2_tech": "Los 67 pares están fuera de la zona élite 8D (1M<=35%, 5M<=38%).",
                        "agent_3_orderbook": "Sin confluencia de volumen y FII>=60.",
                        "agent_4_sector": "Esperando rotación limpia al piso.",
                        "agent_5_memory": "Regla RAG: Prohibido comprar sin confluencia élite.",
                        "agent_6_risk": "Veto de sobreextensión activo.",
                        "agent_7_ceo_anti_loss": "100% USDT preservado en liquidez."
                    },
                    "reasoning": "Ninguno de los 67 activos cumple la confluencia élite (Base 8D estricta + FII>=60 + Vol>=0.35x). Preservando capital."
                }
                winner_sym = "NONE"
                selected_opp = None
            else:
                # Top 2 a máximo 3 finalistas
                candidates_for_gemini = valid_base_candidates[:3]
                print(f"🎯 [FINALISTAS BASE A+ ÉLITE] Se detectaron {len(valid_base_candidates)} activos en Suelo 8D Élite (Top {len(candidates_for_gemini)}: {[c['symbol'] for c in candidates_for_gemini]}). Consultando al Comité para el dictamen supremo...\n", flush=True)


                specific_news_map = {}
                for cand in candidates_for_gemini:
                    c_sym = cand["symbol"]
                    s_news = fundamental_sentinel.fetch_coin_specific_news(c_sym)
                    if s_news:
                        specific_news_map[c_sym] = s_news
                
                macro_summary = macro_ctx.get("summary_text", str(macro_ctx)) if isinstance(macro_ctx, dict) else str(macro_ctx)
                print(f"✅ [Comité Institucional 7 Agentes] Consultando al Súper-Cerebro Gemini AI (Gemini 3.1 Flash Lite) para los {len(candidates_for_gemini)} finalistas seleccionados...")
                gemini_res = llm_router.review_top_candidates(
                    candidates_data_list=candidates_for_gemini,
                    news_data={"headlines": cached_fundamental_report.get("recent_headlines", []), "specific_news": specific_news_map},
                    fear_greed=cached_fundamental_report.get("fear_and_greed", {"score": 50, "sentiment": "Neutral"}),
                    macro_context=macro_summary,
                    market_bias_ctx=bias_str
                )
                
                winner_sym = gemini_res.get("selected_symbol")
                delib = gemini_res.get("committee_deliberation", {})
                if winner_sym and winner_sym != "NONE" and winner_sym in symbol_analysis_map:
                    top_data = symbol_analysis_map[winner_sym]
                    top_side = gemini_res.get("action", "BUY_LONG")
                    selected_opp = (winner_sym, top_data, top_side)
                    
                    print(f"\n🏛️ ═══════════════════════════════════════════════════════════════════")
                    print(f"👑 [COMITÉ INSTITUCIONAL 7 AGENTES - DICTAMEN SUPREMO: {winner_sym}]")
                    print(f"═══════════════════════════════════════════════════════════════════════")
                    if delib:
                        if delib.get("agent_1_macro"): print(f"  🕵️ Agente 1 (Macro & BTC): {delib.get('agent_1_macro')}")
                        if delib.get("agent_2_tech"): print(f"  📊 Agente 2 (Suelo 8D & DNA): {delib.get('agent_2_tech')}")
                        if delib.get("agent_3_orderbook"): print(f"  🌊 Agente 3 (Libro & Bids): {delib.get('agent_3_orderbook')}")
                        if delib.get("agent_4_sector"): print(f"  🧩 Agente 4 (Sector & Tiempo): {delib.get('agent_4_sector')}")
                        if delib.get("agent_5_memory"): print(f"  🧠 Agente 5 (Memoria RAG): {delib.get('agent_5_memory')}")
                        if delib.get("agent_6_risk"): print(f"  🛡️ Agente 6 (Riesgo & Anti-Cima): {delib.get('agent_6_risk')}")
                        if delib.get("agent_7_ceo_anti_loss"): print(f"  👑 Agente 7 (CEO Scalp): {delib.get('agent_7_ceo_anti_loss')}")
                    print(f"  🎯 Dictamen Final: {top_side} | Aprobado={gemini_res.get('approved')} | Confianza={gemini_res.get('confidence')}%")
                    print(f"  💡 Consenso: {gemini_res.get('reasoning')}")
                    print(f"═══════════════════════════════════════════════════════════════════════\n")
                else:
                    ceo_verdict = delib.get("agent_7_ceo_anti_loss", gemini_res.get("reasoning", "Preservando 100% USDT"))
                    print(f"\n🏛️ ═══════════════════════════════════════════════════════════════════")
                    print(f"🛡️ [COMITÉ INSTITUCIONAL 7 AGENTES - DICTAMEN DE PROTECCIÓN: HOLD]")
                    print(f"═══════════════════════════════════════════════════════════════════════")
                    if delib:
                        if delib.get("agent_1_macro"): print(f"  🕵️ Agente 1 (Macro & BTC): {delib.get('agent_1_macro')}")
                        if delib.get("agent_2_tech"): print(f"  📊 Agente 2 (Suelo 8D & DNA): {delib.get('agent_2_tech')}")
                        if delib.get("agent_3_orderbook"): print(f"  🌊 Agente 3 (Libro & Bids): {delib.get('agent_3_orderbook')}")
                        if delib.get("agent_4_sector"): print(f"  🧩 Agente 4 (Sector & Tiempo): {delib.get('agent_4_sector')}")
                        if delib.get("agent_5_memory"): print(f"  🧠 Agente 5 (Memoria RAG): {delib.get('agent_5_memory')}")
                        if delib.get("agent_6_risk"): print(f"  🛡️ Agente 6 (Riesgo & Anti-Cima): {delib.get('agent_6_risk')}")
                        if delib.get("agent_7_ceo_anti_loss"): print(f"  👑 Agente 7 (CEO Scalp): {delib.get('agent_7_ceo_anti_loss')}")
                    print(f"  🎯 Dictamen Final: 🛡️ HOLD (100% USDT Protegido) | Confianza={gemini_res.get('confidence', 100)}%")
                    print(f"  💡 Consenso: {gemini_res.get('reasoning')}")
                    print(f"═══════════════════════════════════════════════════════════════════════\n")
            
            # Build rich top candidates metrics for dashboard persistence (3-tier RSI architecture)
            top_candidates_rich = []
            for c in top_all_candidates:
                csym = c["symbol"]
                cdata = symbol_analysis_map.get(csym, {})
                ctech = cdata.get("tech", {})
                cinds = ctech.get("indicators", {})
                cinst = ctech.get("institutional_analysis", {})
                cmtf = ctech.get("mtf_analysis", {})
                crsi = cmtf.get("rsi_structure", {})
                
                top_candidates_rich.append({
                    "symbol": csym,
                    "score": c["score"],
                    "price": cdata.get("price", 0.0),
                    "rsi_1m": crsi.get("rsi_1m", 50.0),
                    "rsi_2m": crsi.get("rsi_2m", cinds.get("rsi_15m", 50.0)),
                    "rsi_5m": crsi.get("rsi_5m", cinds.get("rsi_15m", 50.0)),
                    "rsi_15m": crsi.get("rsi_15m", cinds.get("rsi_15m", 50.0)),
                    "rsi_1h": crsi.get("rsi_1h", 50.0),
                    "fii_score": cmtf.get("fii_score", 0),
                    "vol_surge_1m": cmtf.get("vol_surge_1m", 1.0),
                    "vol_surge": cinds.get("volume_surge_ratio", 1.0),
                    "trade_quality": cinst.get("trade_quality", "C_NOISE"),
                    "macro_trend": ctech.get("macro_trend_1h", ctech.get("macro_trend_4h", "NEUTRAL"))
                })

            # Persist AI Super-Brain Verdict to JSON for Dashboards and Obsidian
            try:
                verdict_data = {
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "selected_symbol": winner_sym if winner_sym else "NONE",
                    "action": gemini_res.get("action", "HOLD"),
                    "approved": gemini_res.get("approved", False),
                    "confidence": gemini_res.get("confidence", 0),
                    "reasoning": gemini_res.get("reasoning", "Análisis Cuantitativo Institucional"),
                    "top_candidates": top_candidates_rich
                }
                vpath = os.path.join(os.path.dirname(__file__), "latest_ai_verdict.json")
                with open(vpath, "w", encoding="utf-8") as vf:
                    json.dump(verdict_data, vf, indent=2, ensure_ascii=False)
            except Exception as ve:
                print(f"Error saving AI verdict: {ve}")
        except Exception as ge:
            print(f"💡 Gemini Sentinel Note: {ge}")

    total_balance = 0.0
    global_trades = 0
    global_wins = 0
    has_triggered_learned_trade = False

    for acc_idx, acc in enumerate(accounts):
        curr_bal = acc["current_balance"]
        curr_level = acc.get("current_level", 1)

        # Hard floor: clamp to 0 to prevent negative balance compounding bug
        if curr_bal < 0:
            acc["current_balance"] = 0.0
            curr_bal = 0.0
        if curr_bal <= 5.0:
            acc["status"] = "💀 Bancarrota"
            acc["position"] = None  # Force close any open position on bankrupt accounts
            total_balance += max(curr_bal, 0.0)
            continue

        position = acc.get("position", None)

        # 1. EVALUATE LIVE OPEN POSITION (EXACT REAL ACCOUNT PARITY: 6-PHASE TRAILING + 60M MICRO-SCRATCH)
        if position is not None:
            symbol = acc["symbol"]
            analysis = symbol_analysis_map.get(symbol)
            curr_price = analysis["price"] if analysis else position["entry_price"]
            
            entry_p = position["entry_price"]
            side = "LONG"
            
            # Increment holding minutes (~2 minutes per cycle)
            holding_mins = position.get("holding_minutes", 0) + 2
            position["holding_minutes"] = holding_mins
            
            highest_price = max(position.get("highest_price", entry_p), curr_price)
            position["highest_price"] = highest_price
            highest_pnl_pct = ((highest_price - entry_p) / entry_p) * 100.0
            unr_pct = ((curr_price - entry_p) / entry_p) * 100.0
                
            atr_pct = analysis.get("tech", {}).get("mtf_analysis", {}).get("atr_pct_15m", 0.30) if analysis else 0.30
            
            # 🎯 EXACT REPLICA: Adaptive Asset DNA 6-Phase Trailing Ladder
            import adaptive_asset_dna
            arch_dna = adaptive_asset_dna.get_asset_dna_archetype(symbol, atr_pct, curr_price)
            sl_pct, phase, phase_label = adaptive_asset_dna.calculate_archetype_trailing(
                archetype_dna=arch_dna,
                highest_pnl_pct=highest_pnl_pct,
                current_pnl_pct=unr_pct,
                holding_minutes=holding_mins,
                atr_pct=atr_pct
            )
                
            position["phase"] = phase
            position["phase_label"] = phase_label
            
            # Exit Conditions: Pure 3-Phase Trailing Stop (F1: SL -5% Ilimitado, F2: +1.25% Fijo, F3: >=2% Dinámico)
            should_close = unr_pct <= sl_pct


            
            invested = curr_bal * 0.20  # 20% position size per simulation trade
            bnb_fee = invested * 0.00075 * 2  # 0.075% BNB discount fee (entrada + salida = 0.15%)
            
            if should_close:
                pnl_ratio = unr_pct / 100.0
                net_pnl = round((invested * pnl_ratio) - bnb_fee, 2)
                acc["current_balance"] += net_pnl
                acc["pnl_usd"] += net_pnl
                acc["trades_count"] += 1
                acc["last_trade_time"] = now_br
                acc["position"] = None
                acc["status"] = "BUSCANDO_OPORTUNIDAD"
                
                is_win = net_pnl >= 0.0
                if is_win:
                    acc["wins"] += 1
                    acc["consecutive_losses"] = 0
                    acc["last_result"] = f"🟢 Ganó +${net_pnl:.2f} (Fase {phase})"
                    acc["current_level"] = acc.get("current_level", 1) + 1
                    res_type = "WIN"
                else:
                    acc["losses"] += 1
                    acc["consecutive_losses"] = acc.get("consecutive_losses", 0) + 1
                    acc["last_result"] = f"🔴 Perdió -${abs(net_pnl):.2f}"
                    res_type = "LOSS"
                    
                ctx = {}
                if analysis:
                    _indicators = analysis.get("tech", {}).get("indicators", {})
                    _mtf = analysis.get("tech", {}).get("mtf_analysis", {})
                    ctx = {
                        "score": analysis.get("score"),
                        "rsi_15m": _indicators.get("rsi_15m"),
                        "macro_trend_4h": analysis.get("tech", {}).get("macro_trend_4h"),
                        "fii_score": _mtf.get("fii_score", _indicators.get("fii_score", 0)),
                        "atr_pct_15m": _mtf.get("atr_pct_15m", 0.30),
                        "obv_trend": _mtf.get("obv_trend", "NEUTRAL"),
                        "vol_surge_1m": _mtf.get("vol_surge_1m", 1.0),
                        "vol_surge": _indicators.get("volume_surge_ratio", 1.0),
                        "range_position_1m": _mtf.get("range_position_1m", 0.50),
                    }
                    
                learning_engine.record_trade_outcome(
                    symbol=symbol, side="LONG", entry_price=entry_p, exit_price=curr_price,
                    pnl_usd=net_pnl, result_type=res_type,
                    notes=f"{res_type} on {symbol} (PnL: {unr_pct:+.2f}%, Net: ${net_pnl:+.2f} Fase {phase} | {phase_label})",
                    account_id=acc.get("account_id", "SIM-000"),
                    group_name="MATRIZ_SIMULADA",
                    context=ctx
                )
            else:
                acc["last_trade_time"] = position.get("open_time_br", now_br)
                phase_badge = f"⚡ Fase {phase}" if phase <= 2 else f"💎 Fase {phase}"
                acc["last_result"] = f"🔵 {phase_badge} ({unr_pct:+.2f}%)"
                acc["status"] = f"EN_OPERACION_VIVO ({symbol} LONG {unr_pct:+.1f}%)"

        # 2. DYNAMIC MARKET ROTATION: EVALUATE UNIFIED REAL ACCOUNT A+ STRATEGY
        else:
            best_action = "HOLD"
            selected_symbol = acc["symbol"]
            best_reason = ""
            best_curr_price = 0
            
            # 🔀 DISPERSIÓN DE SÍMBOLOS: Distribuye las 1000 cuentas en los 67 pares del Top 100 CMC
            _symbols_list = list(symbol_analysis_map.items())
            _account_offset = acc_idx % max(len(_symbols_list), 1)
            _rotated_symbols = _symbols_list[_account_offset:] + _symbols_list[:_account_offset]
            
            for sym, data_item in _rotated_symbols:
                eval_res = strategy_engine.evaluate_opportunity(data_item["tech"])
                if eval_res["action"] == "LONG":
                    # 🚫 ANTI-CONCENTRACIÓN: Máximo 15 cuentas simultáneas por símbolo
                    _sym_active_count = sum(1 for a in accounts if a.get("position") and a.get("symbol") == sym)
                    if _sym_active_count >= 15:
                        continue  # Símbolo ya cubierto por 15 cuentas, evaluar siguiente par
                    
                    best_action = "LONG"
                    selected_symbol = sym
                    best_reason = eval_res["reason"]
                    best_curr_price = data_item["price"]
                    break
                    
            if best_action == "LONG" and best_curr_price > 0:
                qty = round((curr_bal * 0.2) / best_curr_price, 8)
                current_hour = datetime.now().hour
                acc["symbol"] = selected_symbol
                acc["last_trade_time"] = now_br
                acc["last_result"] = "🔵 En Curso"
                acc["position"] = {
                    "side": "LONG",
                    "entry_price": best_curr_price,
                    "qty": qty,
                    "open_time": now_str,
                    "open_time_br": now_br,
                    "open_hour": current_hour,
                    "holding_minutes": 1,
                    "highest_price": best_curr_price
                }
                acc["status"] = f"EN_OPERACION_VIVO ({selected_symbol} LONG @ ${best_curr_price:.2f})"
            else:
                acc["status"] = "BUSCANDO_OPORTUNIDAD (Ecosistema Real A+)"

        total_balance += acc["current_balance"]
        global_trades += acc["trades_count"]
        global_wins += acc["wins"]

    matrix["current_total_usd"] = round(total_balance, 2)
    matrix["net_pnl_usd"] = round(total_balance - matrix.get("total_fund_usd", 100000.0), 2)
    matrix["global_win_rate_pct"] = round((global_wins / global_trades * 100.0), 2) if global_trades > 0 else 0.0


    save_live_matrix(matrix)
    
    # Execute Real Money Trading ONLY on AI Approved signals with Dynamic Scores (SYNCED WITH GRUPO 0)
    # Fixie proxy is consumed ONLY when an actual order is placed
    try:
        import api_connector
        
        dyn_t = strategy_engine.load_thresholds()
        real_long_score = dyn_t.get("group_0", {}).get("long_score", 80)
        real_short_score = dyn_t.get("group_0", {}).get("short_score", 20)
        
        is_ai_approved = gemini_res.get('approved') == True
        ai_action = gemini_res.get('action', 'HOLD')
        ai_symbol = gemini_res.get('selected_symbol', '')
        ai_confidence = gemini_res.get('confidence', 0)
        
        # Get the AI-selected opportunity data (from any of the top 5, not just #1)
        ai_opp_data = symbol_analysis_map.get(ai_symbol, {}) if ai_symbol and ai_symbol != "NONE" else {}
        ai_price = ai_opp_data.get("price", 0)
        ai_score = ai_opp_data.get("score", 50)
        
        # --- BITCOIN (BTC) MASTER REGIME & CORRELATION GATEKEEPER ---
        btc_data = symbol_analysis_map.get("BTCUSDT", {})
        btc_score = btc_data.get("score", 50)
        btc_rsi = btc_data.get("tech", {}).get("indicators", {}).get("rsi_15m", 50.0)
        btc_trend = btc_data.get("tech", {}).get("macro_trend_4h", "NEUTRAL")
        btc_price = btc_data.get("price", 0.0)
        
        # Determine BTC Health State
        # Crash state: BTC in active panic dump (Score < 30 AND RSI < 35.0)
        is_btc_crashing = btc_score < 30 and btc_rsi < 35.0
        is_btc_weak = btc_score < 30 or btc_rsi < 25.0
        is_btc_bearish = is_btc_crashing or is_btc_weak or btc_score < 25
        
        btc_status_str = f"BTC @ ${btc_price:,.2f} (Score={btc_score}, RSI={btc_rsi:.1f}, Trend={btc_trend})"
        print(f"🪙 [GUARDIÁN BITCOIN] Estado Macro: {btc_status_str}")
        
        # Check if there is a top bullish Spot opportunity across all analyzed pairs
        best_spot_long = None
        long_candidates = [c for c in bullish_candidates if c["score"] >= 58]
        if long_candidates:
            long_candidates.sort(key=lambda x: x["score"], reverse=True)
            best_spot_long = long_candidates[0]
            
        if is_ai_approved and ai_action == "BUY_LONG" and ai_symbol and ai_symbol != "NONE" and ai_price > 0:
            # Extract volume surge directly from AI opportunity data
            target_vol_surge = ai_opp_data.get("tech", {}).get("indicators", {}).get("volume_surge_ratio", 1.0)

            # PRECISION SNIPER GATE (Francisca Serrano / Hyenuk Chu)
            import multi_timeframe_analyzer
            mtf_ai = multi_timeframe_analyzer.analyze_multi_timeframe_candles(ai_symbol)
            is_fk_ai = mtf_ai.get("is_falling_knife", False)
            is_dcb_ai = mtf_ai.get("is_dead_cat_bounce", False)

            if is_fk_ai or is_dcb_ai:
                print(f"🛡️ [VETO FALLING KNIFE REAL] Compra en {ai_symbol} VETADA: Activo en caída libre o trampa Dead Cat (Caída 24h: {mtf_ai.get('price_change_24h_pct', 0):+.1f}%).")
                api_connector.evaluate_and_trade_real_money(best_symbol=None, best_score=50, current_price=0.0, is_bearish=True)
            elif ai_score < 55:
                print(f"🛡️ [ESCUDO CAPITAL REAL] Compra en {ai_symbol} bloqueada (Score {ai_score} < 55). Solo operamos Setups A+ para dinero real.")
                api_connector.evaluate_and_trade_real_money(best_symbol=None, best_score=50, current_price=0.0, is_bearish=True)
            elif is_btc_crashing and ai_symbol != "BTCUSDT":
                print(f"🛡️ [FILTRO CRASH BTC] Entrada LONG bloqueada en {ai_symbol}. Bitcoin en colapso activo ({btc_status_str}). Protegiendo capital.")
                api_connector.evaluate_and_trade_real_money(best_symbol=None, best_score=50, current_price=0.0, is_bearish=True)
            elif is_btc_weak and ai_symbol != "BTCUSDT" and not (ai_score >= 65 or target_vol_surge >= 1.8):
                print(f"🛡️ [FILTRO CORRELACIÓN BTC] Entrada en {ai_symbol} bloqueada (Score {ai_score}, VolSurge {target_vol_surge:.2f}x). Se exige Score>=65 o VolSurge>=1.8x durante BTC débil ({btc_status_str}).")
                api_connector.evaluate_and_trade_real_money(best_symbol=None, best_score=50, current_price=0.0, is_bearish=True)
            elif ai_confidence < 60:
                print(f"🛡️ [FILTRO CONFIANZA IA] Confianza de Gemini ({ai_confidence}%) menor al umbral mínimo (60%). Esperando mejor setup.")
                api_connector.evaluate_and_trade_real_money(best_symbol=None, best_score=50, current_price=0.0, is_bearish=True)
            else:
                print(f"💰 [REAL A+] Señal ALCISTA Aprobada por IA ({ai_symbol} @ {ai_score} Pts, VolSurge={target_vol_surge:.2f}x, Conf={ai_confidence}%). Evaluando cuenta real...")
                api_connector.evaluate_and_trade_real_money(
                    best_symbol=ai_symbol,
                    best_score=ai_score,
                    current_price=ai_price,
                    is_bearish=False,
                    is_learned_signal=True,
                    candidates_list=candidates_for_gemini
                )
        # CALIBRACIÓN HÍBRIDA REAL: Evaluar la Top Oportunidad del Escáner (Score >= 58) con Confirmación Cuántica (GBM A+/B o Refugio)
        elif top_all_candidates:
            top_cand = top_all_candidates[0]
            bs_sym = top_cand["symbol"]
            bs_score = top_cand["score"]
            bs_data = symbol_analysis_map.get(bs_sym, {})
            bs_price = bs_data.get("price", 0)
            bs_tech = bs_data.get("tech", {})
            bs_inst = bs_tech.get("institutional_analysis", {})
            bs_trade_qual = bs_inst.get("trade_quality", "C_NOISE")
            target_vol_surge = bs_tech.get("indicators", {}).get("volume_surge_ratio", 1.0)
            
            # Condición Híbrida Calibrada: Score >= 58 Y (GBM Calidad A+/B O VolSurge >= 1.00x O Refugio O Score >= 60)
            is_gold_refuge = bs_sym in ["PAXGUSDT", "XAUTUSDT"]
            is_quant_approved = bs_trade_qual in ("A+", "B") or target_vol_surge >= 1.00 or is_gold_refuge or bs_score >= 60
            
            import multi_timeframe_analyzer
            import beta_correlation_engine
            import order_flow_analyzer
            
            mtf_bs = multi_timeframe_analyzer.analyze_multi_timeframe_candles(bs_sym)
            is_overextended_bs = mtf_bs.get("is_overextended_15m", False)
            overextension_reason_bs = mtf_bs.get("overextension_reason", "")
            is_yellow_bs = mtf_bs.get("is_yellow_arrow_pivot", False)
            is_bounce_bs = mtf_bs.get("is_oversold_bounce_candidate", False)
            is_divergence_bs = mtf_bs.get("is_bullish_divergence", False)
            is_fk_bs = mtf_bs.get("is_falling_knife", False)
            is_dcb_bs = mtf_bs.get("is_dead_cat_bounce", False)
            
            beta_res = beta_correlation_engine.calculate_beta_correlation(bs_sym)
            of_res = order_flow_analyzer.analyze_order_flow_cvd(bs_sym)
            
            ai_veto_active = (ai_action == 'HOLD' or ai_symbol in ['NONE', '', None] or not gemini_res.get('approved', False))
            
            # 🛡️ MANDATO SUPREMO: El Comité de IA y el Semáforo Macro tienen PODER DE VETO ABSOLUTO (100% SUPREMO).
            # Si la IA vota HOLD o el Semáforo es DEFENSIVO, NINGUNA orden se ejecuta y se preserva el 100% del USDT.
            # CRITICAL FIX: Pass candidates_list=None to prevent api_connector from scanning and buying behind the AI's back
            if ai_veto_active:
                print(f"🔒 [VETO SUPREMO IA] Comité Gemini AI votó {ai_action} ({gemini_res.get('reasoning', 'Mercado no seguro')}). CERO compras ejecutadas. 100% USDT protegido.")
                api_connector.evaluate_and_trade_real_money(
                    best_symbol=None,
                    best_score=50,
                    current_price=0.0,
                    is_bearish=True,
                    candidates_list=None
                )
            elif bs_score >= 58 and is_quant_approved:
                if is_fk_bs or is_dcb_bs:
                    print(f"🛡️ [FILTRO FALLING KNIFE HÍBRIDO] Oportunidad {bs_sym} ({bs_score} Pts) BLOQUEADA: Falling Knife / Dead Cat detectado (Caída 24h: {mtf_bs.get('price_change_24h_pct', 0):+.1f}%).")
                    api_connector.evaluate_and_trade_real_money(best_symbol=None, best_score=50, current_price=0.0, is_bearish=True, candidates_list=candidates_for_gemini)
                elif is_overextended_bs:
                    print(f"🛡️ [FILTRO ANTI-CIMA 15M] Oportunidad {bs_sym} ({bs_score} Pts) BLOQUEADA: Entrada en la cima ({overextension_reason_bs}). Exige compra en el suelo.")
                    api_connector.evaluate_and_trade_real_money(best_symbol=None, best_score=50, current_price=0.0, is_bearish=True, candidates_list=candidates_for_gemini)
                elif (is_btc_crashing or is_high_btc_risk) and bs_sym not in ["BTCUSDT", "PAXGUSDT", "XAUTUSDT"]:
                    print(f"🛡️ [FILTRO CORRELACIÓN BETA BTC] Oportunidad {bs_sym} ({bs_score} Pts, Rho={beta_res.get('rho')}) bloqueada. BTC débil / Alta Correlación.")
                    api_connector.evaluate_and_trade_real_money(best_symbol=None, best_score=50, current_price=0.0, is_bearish=True, candidates_list=candidates_for_gemini)
                elif is_order_flow_dump:
                    print(f"🎯 [FILTRO ORDER FLOW CVD] Oportunidad {bs_sym} ({bs_score} Pts) bloqueada por presión vendedora a mercado (CVD Delta {of_res.get('cvd_delta_usd')} USD).")
                    api_connector.evaluate_and_trade_real_money(best_symbol=None, best_score=50, current_price=0.0, is_bearish=True, candidates_list=candidates_for_gemini)
                else:
                    arrow_lbl = " 🎯 [PATRÓN FLECHAS AMARILLAS 15M PIVOT]" if is_yellow_bs else (" 🌊 [REBOTE SOBREVENTA %B]" if is_bounce_bs else (" 📈 [DIVERGENCIA ALCISTA RSI]" if is_divergence_bs else ""))
                    print(f"💰 [REAL A+ APROBADO POR IA] Ejecutando Top Oportunidad del Escáner en Dinero Real: {bs_sym}{arrow_lbl} @ {bs_score} Pts (GBM: {bs_trade_qual}, VolSurge: {target_vol_surge:.2f}x, Rho: {beta_res.get('rho')}, OrderFlow: {of_res.get('verdict')})...")
                    api_connector.evaluate_and_trade_real_money(
                        best_symbol=bs_sym,
                        best_score=bs_score,
                        current_price=bs_price,
                        is_bearish=False,
                        is_learned_signal=True,
                        candidates_list=candidates_for_gemini
                    )

            else:
                print(f"🔒 [REAL HÍBRIDO] Top Escáner {bs_sym} ({bs_score} Pts, GBM {bs_trade_qual}) no alcanza umbral híbrido (Score>=58 y Calidad A+/B). Preservando capital.")
                api_connector.evaluate_and_trade_real_money(best_symbol=None, best_score=50, current_price=0.0, is_bearish=True, candidates_list=candidates_for_gemini)
        else:
            if ai_symbol and ai_symbol != "NONE":
                print(f"🔒 [REAL] Mercado sin setup A+ (Top={ai_symbol}, Score={ai_score}, Acción={ai_action}). Protegiendo 100% de capital en USDT.")
            else:
                print(f"🔒 [REAL] Ningún activo califica como Setup A+. Manteniendo 100% liquidez en USDT.")
            # Always run the trader to manage OPEN positions (check TP/SL), even if no new entry
            api_connector.evaluate_and_trade_real_money(
                best_symbol=None, best_score=50, current_price=0.0, is_bearish=True, candidates_list=candidates_for_gemini
            )
            
    except Exception as e_real:
        print(f"Real trader notice: {e_real}")
        
    try:
        import auto_tune_thresholds
        auto_tune_thresholds.auto_tune()
    except Exception as e_tune:
        print(f"Error auto-tuning thresholds: {e_tune}")

    # 🧬 MOTOR GENÉTICO 1000 SIMULACIONES — Alimenta el Súper-Cerebro con datos reales
    # Usa el mismo symbol_analysis_map calculado este ciclo → 0 llamadas extra a la API
    try:
        import simulation_engine as _sim_eng
        _matrix_check = _sim_eng.load_matrix()
        _accounts_check = _matrix_check.get("accounts", [])
        # Re-inicializar si: sin group_id O grupos colapsados (menos de 5 grupos distintos)
        from collections import Counter as _GCtr2
        _gid_dist2 = _GCtr2(a.get("group_id") for a in _accounts_check)
        _needs_reinit = (
            (_accounts_check and "group_id" not in _accounts_check[0]) or
            (len(_gid_dist2) < 5)
        )
        if _needs_reinit:
            print("🧬 [SIM ENGINE] Re-inicializando matriz con 5 grupos genéticos evolutivos...")
            _sim_eng._init_fresh_matrix()
        _sim_result = _sim_eng.run_simulation_cycle(symbol_analysis_map)
        if _sim_result:
            total_sim_trades = _sim_result.get("total_trades", 0)
            if total_sim_trades > 0:
                print(f"🧬 [SIM ENGINE] {total_sim_trades} trades acumulados | WR Global: {_sim_result.get('global_win_rate', 0):.1f}% | PnL Simulado: ${_sim_result.get('global_pnl_usd', 0):+.2f}")
                _sim_eng.print_simulation_report()
            _best = _sim_eng.get_best_group_params()
            if _best:
                print(f"🏆 [GRUPO LÍDER] {_best.get('name', '?')[:50]} → WR mayor detectado. Parámetros óptimos identificados.")
    except Exception as _sim_err:
        pass  # Non-blocking — nunca interrumpe el flujo real

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
        
        # Determine callout type based on performance
        callout_type = "[!NOTE]"
        if g_pnl > 5.0: callout_type = "[!TIP]"
        elif g_pnl < -2.0: callout_type = "[!WARNING]"
        
        grouped_tables_md += f"## {g_name}\n\n"
        grouped_tables_md += f"> {callout_type} 📊 **Resumen del {g_name}:**\n"
        grouped_tables_md += f"> - 💵 **Balance Total del Grupo:** `${g_bal:,.2f} USD` (`{g_pnl_str}`)\n"
        grouped_tables_md += f"> - 🎯 **Operaciones Totales:** `{g_trades}` (`{g_wins} Ganadas / {g_losses} Perdidas`)\n"
        grouped_tables_md += f"> - 📈 **Tasa de Acierto del Grupo:** `{g_wr}% Win Rate`\n\n"
        
        grouped_tables_md += f"| ID | Cripto | Ops | Racha | Última Hora | Último Resultado | Balance (PnL) | Estado |\n"
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
                status_clean = f"🛑 Pausado"
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
    
    pct_winning = round((winning_accs / total_acc_count) * 100.0, 1) if total_acc_count > 0 else 0
    pct_losing = round((losing_accs / total_acc_count) * 100.0, 1) if total_acc_count > 0 else 0
    pct_active = round((active_live_accs / total_acc_count) * 100.0, 1) if total_acc_count > 0 else 0
    pct_neutral = round((neutral_accs / total_acc_count) * 100.0, 1) if total_acc_count > 0 else 0

    real_st = {"position": None, "trades_count": 0, "net_pnl_usd": 0.0, "wins": 0, "losses": 0, "status": "No configurado", "current_balance_usd": 0.0}
    real_total_val = 0.0
    real_bnb = 0.0
    real_bnb_usd = 0.0
    real_usdt_free = 0.0
    
    try:
        import api_connector
        real_st = api_connector.load_real_account_state()
        
        # 🌐 BILLETERA EN VIVO: Sincroniza en cada ciclo de 2 minutos distribuyendo entre las 100 cuentas Fixie
        # Consumo: 7.2 req/día por cuenta (usamos solo 216 de las 500 mensuales -> 56.8% de margen libre)
        is_local_mode = api_connector.get_execution_mode() == "local"
        mode_label = "LOCAL DIRECTO" if is_local_mode else "NUBE 100-PROXIES"
        print(f"🔄 [SYNC {mode_label}] Sincronizando balance Spot desde Binance API...")
        real_st = api_connector.diagnose_full_spot_wallet()
        real_st["_last_wallet_sync_ts"] = time.time()
        api_connector.save_real_account_state(real_st)
            
        real_total_val = real_st.get("_cached_total_val", real_st.get("current_balance_usd", 0.0))
        real_usdt_free = real_st.get("_cached_usdt_free", 0.0)
        real_bnb = real_st.get("_cached_bnb", 0.0)
        real_bnb_usd = real_st.get("_cached_bnb_usd", 0.0)
    except Exception as e:
        print(f"Error cargando datos reales en matrix sync: {e}")
        # Usamos los datos guardados en state si la API falla
        real_total_val = real_st.get("current_balance_usd", 0.0)

    real_active_crypto = real_st.get("position", {}).get("symbol", "Ninguna (Buscando)") if real_st.get("position") else "Ninguna (Buscando)"
    timestamp = now_str
    
    real_section = (
        f"# 💰 INVERSIÓN REAL EN VIVO (BINANCE SPOT & FUTUROS - ${real_total_val:.2f} USD)\n\n"
        f"> [!TIP] 🏦 **ESTADO DE LA CUENTA REAL**\n"
        f"> ⏱️ **Última Actualización:** `{timestamp}`\n"
        f">\n"
        f"> 🛡️ **Desglose de Fondos en Cuenta Real:**\n"
        f"> - 🟡 **BNB Escudo Comisiones:** `{real_bnb:.8f} BNB` (`~${real_bnb_usd:.2f} USD`)\n"
        f"> - 💵 **USDT Disponible:** `{real_usdt_free:.4f} USDT`\n"
        f"> - 💰 **Saldo Total Acumulado:** `${real_total_val:.2f} USD`\n\n"
        f"| 💵 Capital | 🪙 Cripto Activa | 🔢 Ops | 📈 Balance | 💰 Beneficio (PnL) | 📊 Racha | 🎯 Estado Operativo |\n"
        f"| :---: | :---: | :---: | :---: | :---: | :---: | :---: |\n"
        f"| **`${real_total_val:.2f} USD`** | **`{real_active_crypto}`** | `#{real_st.get('trades_count', 0)}` | **`${real_st.get('current_balance_usd', 0):.2f} USD`** | **`${real_st.get('net_pnl_usd', 0):+.2f} USD`** | `{real_st.get('wins', 0)}W/{real_st.get('losses', 0)}L` | **`{real_st.get('status', 'Buscando')}`** |\n\n"
        f"---\n\n"
    )

    matrix_md = (
        f"---\n"
        f"tags:\n"
        f"  - matrix\n"
        f"  - trading\n"
        f"  - simulacion\n"
        f"aliases:\n"
        f"  - Matriz 1000 Cuentas\n"
        f"cssclasses:\n"
        f"  - matrix-report\n"
        f"date: {now_str}\n"
        f"---\n\n"
        f"{real_section}"
        f"# 🚀 MATRIZ CLASIFICADA EN 6 GRUPOS PROGRESIVOS (1000 CUENTAS TESTNET / $100,000 USD)\n\n"
        f"> [!IMPORTANT] 📊 **RESUMEN GLOBAL DE LA MATRIZ (1000 CUENTAS GENÉTICAS):**  \n"
        f"> - 💵 **Fondo Inicial:** `$100,000.00 USD` (1,000 Cuentas x $100)  \n"
        f"> - 📈 **Capital Total Acumulado:** **`${matrix['current_total_usd']:,.2f} USD`** (`${matrix['net_pnl_usd']:+,.2f} USD`)  \n"
        f"> - 🟢 **Cuentas Ganadoras (+2% Meta Cumplida):** `{winning_accs} Cuentas ({pct_winning}%)`  \n"
        f"> - 🔴 **Cuentas en Pérdida (-1.0% Stop Loss):** `{losing_accs} Cuentas ({pct_losing}%)`  \n"
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
    
    file_path = os.path.join(OBSIDIAN_FOLDER, "🚀_Matriz_1000_Simulaciones.md")
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(matrix_md)
    return file_path

def ensure_obsidian_dir():
    if not os.path.exists(OBSIDIAN_FOLDER):
        os.makedirs(OBSIDIAN_FOLDER, exist_ok=True)

# Compatibility alias for runners
run_optimized_pipeline = run_infinite_trading_matrix_cycle

if __name__ == '__main__':
    run_infinite_trading_matrix_cycle()

