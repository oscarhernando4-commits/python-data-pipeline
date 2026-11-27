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
import quant_edge_engine
import api_connector
from datetime import datetime


# ═══════════════════════════════════════════════════════════════
# 🚫 BLACKLIST: Tokens con historial probado de pérdidas (WR < 50% con >= 3 trades reales)
# 📊 Basado en auditoría forense de 299 trades (Sep 2 - Nov 12, 2026)
# ═══════════════════════════════════════════════════════════════
_BLACKLISTED_TOKENS = {
    "AEROUSDT",    # 2W/3L, -$0.43
    "DASHUSDT",    # 3W/4L, -$0.33
    "ICPUSDT",     # 0W/3L, -$0.29
    "APTUSDT",     # 0W/3L, -$0.20
    "MORPHOUSDT",  # 3W/4L, -$0.19
    "UNIUSDT",     # 0W/3L, -$0.16
    "AAVEUSDT",    # 1W/3L, -$0.14
    "DOTUSDT",     # 2W/3L, -$0.12
    "SUIUSDT",     # 1W/2L, -$0.09
    "FILUSDT",     # 1W/2L, -$0.09
    "OPUSDT",      # 1W/2L, -$0.07
    "LINKUSDT",    # 2W/3L, -$0.06
    "NEARUSDT",    # 1W/3L, -$0.06
    "CAKEUSDT",    # veto por OBV flip
    "PEPEUSDT",    # flip constante, -$0.13 en una sola trade
}

# ✅ WHITELIST PREFERENTE: Tokens probados ganadores (WR >= 70% con >= 3 trades)
_WHITELIST_WINNERS = {
    "ZROUSDT",     # 11W/4L, +$0.22
    "ETHFIUSDT",   # 4W/2L, +$0.21
    "IMXUSDT",     # 4W/1L, +$0.20
    "TIAUSDT",     # 4W/0L, +$0.19
    "PENGUUSDT",   # 4W/0L, +$0.18
    "ALGOUSDT",    # 4W/1L, +$0.17
    "INJUSDT",     # 7W/2L, +$0.17
    "XLMUSDT",     # 4W/2L, +$0.14
    "TRUMPUSDT",   # 3W/1L, +$0.14
    "STXUSDT",     # 6W/0L, +$0.14
    "HBARUSDT",    # 5W/0L, +$0.13
    "QNTUSDT",     # 5W/1L, +$0.12
    "AVAXUSDT",    # 4W/1L, +$0.12
    "JUPUSDT",     # 4W/1L, +$0.09
    "FETUSDT",     # 2W/0L, +$0.08
    "POLUSDT",     # 4W/2L, +$0.06 (net positive)
    "XRPUSDT",     # proven winner
    "BNBUSDT",     # low fee asset
    "BTCUSDT",     # core asset
    "ETHUSDT",     # core asset  
    "SOLUSDT",     # core asset
    "LTCUSDT",     # proven stable
    "HYPEUSDT",    # 3W/1L
    "WLFIUSDT",    # recent winner
    "ONDOUSDT",    # recent winner
    "ENAUSDT",     # mixed but recent winner
}

_QE_1H_CACHE = getattr(sys, "_qe_1h_cache", {})
sys._qe_1h_cache = _QE_1H_CACHE

def _fetch_closed_1h_klines(symbol: str, limit: int = 600):
    """Fetch closed 1H Binance klines, cached per symbol across reloads within the current closed 1H bar."""
    import requests as _req
    global _QE_1H_CACHE
    _QE_1H_CACHE = getattr(sys, "_qe_1h_cache", {})
    sys._qe_1h_cache = _QE_1H_CACHE
    now_ms = int(time.time() * 1000)
    last_closed_open = ((now_ms // 3600000) - 1) * 3600000
    cached = _QE_1H_CACHE.get(symbol)
    if cached and cached.get("hour_open") == last_closed_open:
        return cached["ind_1h"], cached["ind_4h"]

    urls = [
        f"https://data-api.binance.vision/api/v3/klines?symbol={symbol}&interval=1h&limit={limit}",
        f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval=1h&limit={limit}",
    ]
    for url in urls:
        try:
            r = _req.get(url, timeout=8)
            if r.status_code == 200:
                raw = r.json()
                kls_1h = quant_edge_engine.parse_binance_klines(raw, only_closed=True, interval_ms=3600000, now_ms=now_ms)
                kls_4h = quant_edge_engine.resample_1h_to_4h(kls_1h, require_complete_4h=True)
                ind_1h = quant_edge_engine.build_indicators(kls_1h)
                ind_4h = quant_edge_engine.build_indicators(kls_4h)
                if ind_1h and ind_4h:
                    _QE_1H_CACHE[symbol] = {"hour_open": last_closed_open, "ind_1h": ind_1h, "ind_4h": ind_4h}
                    return ind_1h, ind_4h
        except Exception:
            continue
    return None, None


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
    try:
        import simulation_engine as _se
        gid = min(index // 200, 4)
        grp = _se.GENETIC_GROUPS[gid]
        return {
            "group_id": grp["group_id"],
            "group_name": grp["group_name"],
            "threshold_score": grp["min_score"],
            "risk_pct": 1.0,
            "label": grp["description"]
        }
    except Exception:
        return {
            "group_id": 0,
            "group_name": "💎 ÉLITE ESTRICTO (Score≥90, FII≥70)",
            "threshold_score": 90,
            "risk_pct": 1.0,
            "label": "Máxima precisión"
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
                
            # Solo asignar group_info si la cuenta no tiene group_id asignado
            if "group_id" not in acc:
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
    import learning_engine
    try:
        _pre_bl = learning_engine.get_dynamic_blacklist()
    except Exception:
        _pre_bl = {}

    def analyze_symbol(s):
        # ⚡ OPTIMIZACIÓN INSTITUCIONAL: Salta inmediatamente activos tóxicos en HARD Blacklist
        # o en CUARENTENA ANTI-REINCIDENCIA 24H (Súper-Cerebro 5.0)
        if s in _pre_bl and _pre_bl[s].get("tier") == "HARD":
            return s, None

        try:
            import quant_database as _qdb_quar
            is_quar, _ = _qdb_quar.is_symbol_in_quarantine(s)
            if is_quar:
                return s, None
        except Exception:
            pass

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
            
            # Record 5M Time-Series Reading solo para activos relevantes (Score >= 65)
            # ⚡ OPTIMIZACIÓN: Evita contención de bloqueo SQLite en 67 pares simultáneos
            if final_score >= 65:
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
    candidates_for_gemini = []
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
            # 📊 MOTOR CUÁNTICO DUAL-REGIME 1H+4H (VALIDADO 125D & 30D 1-MINUTO)
            #   - BULL (BTC 4H E21>E50 & 1H>E50/E21): RS_BREAK (Spot LONG)
            #   - TRANSITION / FLAT: DECOUPLED_LEADER (Spot LONG solo RS24>=+5%)
            #   - BEAR_CRASH (BTC 4H E21<E50 & RSI<=47): BEAR_SHORT (Futures SHORT si habilitado)
            #   Si Futures no está habilitado en el API key -> Preserva 100% USDT seguro en bear!
            # ═══════════════════════════════════════════════════════════════════
            btc_1h_ind, btc_4h_ind = _fetch_closed_1h_klines("BTCUSDT", limit=600)
            macro_qe = quant_edge_engine.detect_macro_regime(btc_1h_ind, btc_4h_ind)
            allow_short_live = api_connector.is_futures_trading_enabled()
            cd_map_real = real_st_check.get("_symbol_side_cooldown", {}) if isinstance(real_st_check, dict) else {}
            now_sec_eval = time.time()

            print(
                f"🌐 [RÉGIMEN QUANT DUAL] BTC=${macro_qe.get('btc_price', 0):,.2f} | "
                f"Régimen={macro_qe['regime']} | 4H_RSI={macro_qe.get('btc_rsi_4h', 50):.1f} | "
                f"1H_Ret={macro_qe.get('btc_1h_ret', 0):+.2f}% | Futures_SHORT={'ACTIVO' if allow_short_live else 'OFF (Spot-Only)'}",
                flush=True
            )

            qe_eligible_syms = [
                cand["symbol"] for cand in top_all_candidates
                if cand.get("symbol")
                and cand["symbol"] != "BTCUSDT"
                and cand["symbol"] not in _BLACKLISTED_TOKENS
                and not (_pre_bl.get(cand["symbol"], {}).get("tier") == "HARD")
            ]

            qe_ind_map = {}
            try:
                with concurrent.futures.ThreadPoolExecutor(max_workers=12) as qe_ex:
                    fut_map = {qe_ex.submit(_fetch_closed_1h_klines, s, 600): s for s in qe_eligible_syms}
                    for fut in concurrent.futures.as_completed(fut_map):
                        sym_k = fut_map[fut]
                        try:
                            s1h, s4h = fut.result()
                            if s1h and s4h:
                                qe_ind_map[sym_k] = (s1h, s4h)
                        except Exception:
                            pass
            except Exception as e_qef:
                print(f"⚠️ Error carga paralela velas 1H/4H: {e_qef}")

            valid_base_candidates = []
            proximity_candidates = []

            for idx, cand in enumerate(top_all_candidates, 1):
                csym = cand["symbol"]
                diag_reasons = []

                if csym == "BTCUSDT":
                    continue
                if csym in _BLACKLISTED_TOKENS:
                    diag_reasons.append(f"BLACKLIST_PROVEN_LOSER({csym})")

                if not diag_reasons:
                    s_pair = qe_ind_map.get(csym)
                    if not s_pair:
                        diag_reasons.append("SIN_VELAS_1H_4H")
                    else:
                        qe_sig = quant_edge_engine.evaluate_asset_signal(
                            symbol=csym,
                            sym_1h=s_pair[0],
                            sym_4h=s_pair[1],
                            btc_1h=btc_1h_ind,
                            btc_4h=btc_4h_ind,
                            allow_short=allow_short_live,
                            cooldown_map=cd_map_real,
                            now_sec=now_sec_eval,
                        )
                        if qe_sig is None:
                            diag_reasons.append(f"SIN_SETUP_{macro_qe['regime']}")
                        else:
                            # Cisne negro / delisting veto check
                            news_veto_msg = None
                            try:
                                import macro_mcp_gateway as _mmcp
                                _nv = _mmcp.get_news_and_black_swan_sentinel(csym)
                                if _nv.get("symbol_veto", False):
                                    news_veto_msg = _nv.get("veto_reason", "VetoNoticiaCisneNegro")
                            except Exception:
                                pass

                            if news_veto_msg:
                                diag_reasons.append(news_veto_msg)
                            else:
                                cand_enriched = dict(cand)
                                cand_enriched["score"] = qe_sig["score"]
                                cand_enriched["suggested_action"] = "SELL_SHORT" if qe_sig["side"] == "SHORT" else "BUY_LONG"
                                cand_enriched["quant_edge"] = qe_sig
                                valid_base_candidates.append(cand_enriched)
                                print(
                                    f"  🟢 [QUANT SIGNAL #{idx:02d}] {csym:<10} | {qe_sig['setup']:<16} | {qe_sig['side']:<5} | "
                                    f"Score={qe_sig['score']} | RS8={qe_sig['rs_8h_pct']:+.1f}% | Vol={qe_sig['vol_surge']:.2f}x | "
                                    f"Taker={qe_sig['taker_buy_pct']:.1f}% | SL={qe_sig['sl_pct']:.2f}% / TP=+{qe_sig['tp_pct']:.2f}%",
                                    flush=True,
                                )
                                continue

                proximity_candidates.append({
                    "sym": csym,
                    "rank": idx,
                    "reasons_count": len(diag_reasons),
                    "score": cand.get("score", 0),
                    "fii": symbol_analysis_map.get(csym, {}).get("tech", {}).get("mtf_analysis", {}).get("fii_score", 0),
                    "diag": ", ".join(diag_reasons[:2]),
                })

            valid_base_candidates.sort(key=lambda c: c.get("quant_edge", {}).get("quant_rank", 0.0), reverse=True)

            if not valid_base_candidates:
                top_prox = proximity_candidates[:3]
                prox_str = " | ".join([f"#{p['rank']} {p['sym']} ({p['diag']})" for p in top_prox])
                print(f"🛡️ [RADAR QUANT DUAL] 0 de {len(top_all_candidates)} activos cumplen entrada validada en régimen {macro_qe['regime']}. 100% USDT preservado. [{prox_str}]", flush=True)
                gemini_res = {
                    "selected_symbol": "NONE",
                    "action": "HOLD",
                    "approved": False,
                    "confidence": 98,
                    "reasoning": f"0 activos cumplen criterio cuantitativo estricto en régimen {macro_qe['regime']}. Capital 100% protegido."
                }
                winner_sym = "NONE"
                selected_opp = None
                candidates_for_gemini = []
            else:
                candidates_for_gemini = valid_base_candidates[:3]
                print(f"🎯 [FINALISTAS QUANT DUAL] {len(valid_base_candidates)} setups validados (Top {len(candidates_for_gemini)}: {[c['symbol'] for c in candidates_for_gemini]}). Consultando Comité Gemini AI...", flush=True)

                specific_news_map = {}
                for cand in candidates_for_gemini:
                    c_sym = cand["symbol"]
                    s_news = fundamental_sentinel.fetch_coin_specific_news(c_sym)
                    if s_news:
                        specific_news_map[c_sym] = s_news

                macro_summary = macro_ctx.get("summary_text", str(macro_ctx)) if isinstance(macro_ctx, dict) else str(macro_ctx)
                print(f"✅ [Comité Institucional 7 Agentes] Consultando al Súper-Cerebro Gemini AI (Gemini 3.1 Flash Lite - Pool 10 Claves) para los {len(candidates_for_gemini)} finalistas seleccionados...")
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

    # 🧬 MOTOR GENÉTICO SIMULADO (5 Grupos Evolutivos alineados Dual-Regime)
    # Ejecutado soberanamente por simulation_engine.py con symbol_analysis_map + señales quant_edge_engine
    total_balance = 10000.0
    try:
        import simulation_engine as _sim_eng
        _q_map = {}
        _m_reg = "TRANSITION"
        try:
            _m_reg = macro_qe.get("regime", "TRANSITION")
            for _vc in valid_base_candidates:
                if _vc.get("symbol") and _vc.get("quant_edge"):
                    _q_map[_vc["symbol"]] = _vc["quant_edge"]
        except Exception:
            pass
        _sim_res = _sim_eng.run_simulation_cycle(symbol_analysis_map, macro_regime=_m_reg, valid_quant_cands=_q_map)
        matrix = _sim_eng.load_matrix()
        total_balance = matrix.get("current_total_usd", 10000.0)
        sync_live_matrix_obsidian(matrix)
    except Exception as _sim_err:
        print(f"⚠️ Nota ejecución simulación: {_sim_err}")
    
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
        
        ai_opp_data = symbol_analysis_map.get(ai_symbol, {}) if ai_symbol and ai_symbol != "NONE" else {}
        ai_price = ai_opp_data.get("price", 0)
        ai_score = ai_opp_data.get("score", 50)
        ai_cand_match = next((c for c in candidates_for_gemini if c.get("symbol") == ai_symbol), None)
        if ai_cand_match:
            ai_score = ai_cand_match.get("score", ai_score)
            if not ai_price:
                ai_price = ai_cand_match.get("price", 0)
        
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
            
        if candidates_for_gemini:
            # Ruta Cuántica Dual-Regime Validada (RS_BREAK / DECOUPLED_LEADER / BEAR_SHORT)
            top_qe_cand = candidates_for_gemini[0]
            qe_meta = top_qe_cand.get("quant_edge", {})
            target_sym = ai_symbol if (is_ai_approved and ai_symbol in [c["symbol"] for c in candidates_for_gemini]) else top_qe_cand["symbol"]
            target_cand = next((c for c in candidates_for_gemini if c["symbol"] == target_sym), top_qe_cand)
            target_qe = target_cand.get("quant_edge", qe_meta)
            target_side = target_qe.get("side", "SHORT" if ai_action == "SELL_SHORT" else "LONG")
            target_px = target_qe.get("price") or ai_price or symbol_analysis_map.get(target_sym, {}).get("price", 0.0)
            target_sc = int(target_qe.get("score", target_cand.get("score", 86)))

            # Respetar veto explícito de Gemini únicamente si Gemini respondió online y detectó riesgo severo (>=75%)
            ai_offline = (gemini_res.get("confidence", 0) == 0 or "fuera de línea" in str(gemini_res.get("reasoning", "")).lower())
            explicit_ai_veto = (not is_ai_approved and ai_action == "HOLD" and not ai_offline and gemini_res.get("confidence", 0) >= 80)

            if explicit_ai_veto:
                print(f"🔒 [VETO EXPLÍCITO GEMINI] Comité vetó {target_sym} con confianza {gemini_res.get('confidence')}% ({gemini_res.get('reasoning')}). Capital preservado.")
                api_connector.evaluate_and_trade_real_money(best_symbol=None, best_score=50, current_price=0.0, is_bearish=True, candidates_list=None)
            else:
                print(
                    f"💰 [EJECUCIÓN QUANT DUAL] {target_sym} | {target_qe.get('setup', 'QUANT')} ({target_side}) @ ${target_px:.4f} | "
                    f"Score={target_sc} | IA={'APROBADA' if is_ai_approved else 'FALLBACK_QUANT'}",
                    flush=True,
                )
                api_connector.evaluate_and_trade_real_money(
                    best_symbol=target_sym,
                    best_score=target_sc,
                    current_price=target_px,
                    is_bearish=(target_side == "SHORT"),
                    is_learned_signal=bool(is_ai_approved),
                    candidates_list=candidates_for_gemini,
                )
        else:
            print("🔒 [REAL] Ningún activo cumple señal Dual-Regime validada en este ciclo. Manteniendo 100% liquidez en USDT.")
            api_connector.evaluate_and_trade_real_money(
                best_symbol=None, best_score=50, current_price=0.0, is_bearish=True, candidates_list=None
            )

    except Exception as e_real:
        print(f"Real trader notice: {e_real}")

    # 🌐 Sincronizar billetera real Spot & Futures en la nube al menos cada 20 minutos
    try:
        _st_sync = api_connector.load_real_account_state()
        _last_sync = float(_st_sync.get("_last_wallet_sync_ts", 0.0) or 0.0)
        if (time.time() - _last_sync) >= 1200.0 or _st_sync.get("_cached_usdt_free") is None:
            _st_sync = api_connector.diagnose_full_spot_wallet()
            _st_sync["_last_wallet_sync_ts"] = time.time()
            api_connector.save_real_account_state(_st_sync)
    except Exception as _sync_err:
        print(f"⚠️ Wallet periodic sync notice: {_sync_err}")

    # 🧬 REPORTE GENÉTICO Y AUTO-TUNE (Cierre único del ciclo)
    try:
        import simulation_engine as _sim_eng
        _sim_eng.print_simulation_report()
        import auto_tune_thresholds
        auto_tune_thresholds.auto_tune()
    except Exception as _sim_err:
        print(f"⚠️ Auto-tune/sim report notice: {_sim_err}")

    print(f"[{now_str}] Screen-Optimized Matrix Completed! Total Fund: ${total_balance:,.2f} USD")
    return matrix

def sync_live_matrix_obsidian(matrix):
    # ⚡ OPTIMIZACIÓN DE VELOCIDAD: En GitHub Actions / Nube no hay Obsidian instalado.
    # Saltar esta escritura pesada de 1,000 cuentas ahorra tiempo y CPU valiosos.
    if os.getenv("GITHUB_ACTIONS") == "true" or os.getenv("CI") == "true":
        return
    ensure_obsidian_dir()
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    now_date = datetime.now().strftime("%y-%m-%d")
    now_time = datetime.now().strftime("%H:%M")
    now_br = f"{now_date}<br>{now_time}"
    accounts = matrix["accounts"]
    
    # Group Accounts by group_id (0 to 4)
    groups_dict = {}
    for acc in accounts:
        g_id = acc.get("group_id", 0)
        if g_id not in groups_dict:
            groups_dict[g_id] = []
        groups_dict[g_id].append(acc)

    grouped_tables_md = ""
    
    group_titles = {
        0: "💎 GRUPO 0: Élite Estricto (Score≥90, FII≥70)",
        1: "🎯 GRUPO 1: Francotirador (Score≥85, FII≥60)",
        2: "⚡ GRUPO 2: Agresivo Rápido (Score≥75, FII≥50)",
        3: "🐢 GRUPO 3: Paciencia Total (Score≥85, FII≥60, Hold Max 720m)",
        4: "🧬 GRUPO 4: Adaptativo Híbrido (Score≥80, FII≥55)"
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

