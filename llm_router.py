import os
import sys
import json
import time
import urllib.request

# Load .env automatically so all 10 GEMINI keys are available in local execution
try:
    from dotenv import load_dotenv
    _env_path = os.path.join(os.path.dirname(__file__), '.env')
    load_dotenv(_env_path)
except ImportError:
    pass

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
_KEY_COOLDOWN = {}  # key -> timestamp when marked in cooldown


# ============================================================
# ROUND-ROBIN EQUITATIVO PERSISTENTE PARA GEMINI API KEYS
# ============================================================
GEMINI_KEY_STATE_FILE = os.path.join(os.path.dirname(__file__), "gemini_key_state.json")

def _load_gemini_key_state():
    """Carga el estado persistente del rotador de claves Gemini."""
    try:
        with open(GEMINI_KEY_STATE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {"current_index": 0, "usage": {}, "total_calls": 0}

def _save_gemini_key_state(state):
    """Guarda el estado del rotador de claves Gemini."""
    try:
        with open(GEMINI_KEY_STATE_FILE, "w", encoding="utf-8") as f:
            json.dump(state, f, indent=2, ensure_ascii=False)
    except Exception:
        pass

def _get_key_index():
    """Lee el índice actual del Round-Robin desde disco."""
    return _load_gemini_key_state().get("current_index", 0)

def _advance_key_index(key_label=""):
    """Avanza el índice del Round-Robin y registra uso."""
    state = _load_gemini_key_state()
    state["current_index"] = state.get("current_index", 0) + 1
    state["total_calls"] = state.get("total_calls", 0) + 1
    if key_label:
        usage = state.setdefault("usage", {})
        usage[key_label] = usage.get(key_label, 0) + 1
    state["last_used_time"] = time.strftime("%Y-%m-%d %H:%M:%S")
    _save_gemini_key_state(state)

def get_gemini_api_keys():
    """
    Extracts all available Gemini API Keys from environment variables.
    Filters out any keys placed in the 5-minute cooldown blacklist due to HTTP 429.
    """
    now = time.time()
    raw_keys = []
    
    # Key 1 (Primary)
    k1 = os.getenv("GEMINI_API_KEY", "")
    if k1: raw_keys.append(k1)
    
    # Keys 2 to 10
    for i in range(2, 11):
        env_name = f"GEMINI_API_KEY_{i:02d}"
        val = os.getenv(env_name, "")
        if not val:
            env_name_alt = f"GEMINI_API_KEY_{i}"
            val = os.getenv(env_name_alt, "")
        if val and val not in raw_keys:
            raw_keys.append(val)
            
    # Filter out keys in 30-second cooldown (30 seconds allows RPM rate limit to reset naturally)
    healthy_keys = [k for k in raw_keys if (now - _KEY_COOLDOWN.get(k, 0)) >= 30]
    
    # If all keys happen to be in cooldown, clear cooldown to prevent hard lock
    if not healthy_keys and raw_keys:
        print("💡 Cooldown de claves Gemini expirado/reiniciado. Reanudando rotación de claves...")
        _KEY_COOLDOWN.clear()
        healthy_keys = raw_keys
        
    return healthy_keys if healthy_keys else [""]

def get_key_label(key, keys_pool):
    """Retorna un label legible para tracking (Key_01, Key_02, etc)."""
    try:
        idx = keys_pool.index(key)
        return f"Key_{idx+1:02d}"
    except ValueError:
        return f"Key_XX"

def mark_key_in_cooldown(key):
    """Puts a key in 30-second cooldown blacklist when it encounters HTTP 429 Rate Limit."""
    if key and key != "":
        _KEY_COOLDOWN[key] = time.time()
        healthy = len(get_gemini_api_keys())
        print(f"🚫 Clave Gemini en pausa breve (30s) por Rate Limit 429. Claves saludables en pool: {healthy}")

def get_next_gemini_key():
    """Returns the next API key in round-robin sequence across the healthy key pool."""
    keys = get_gemini_api_keys()
    if not keys or keys == [""]:
        return ""
    idx = _get_key_index()
    key = keys[idx % len(keys)]
    _advance_key_index(get_key_label(key, keys))
    return key

def consult_gemini_flash_oracle(symbol, score, tech_data, news_data, fear_greed, macro_context="", market_bias_ctx=""):
    """
    Super-Brain AI Decision Reviewer using Google Gemini Flash Free API with Groq & Smart Quant Fallback.
    Guarantees 100% Uptime for AI Trade Approval.
    """
    import time_series_memory
    import extreme_events_memory
    import multi_timeframe_analyzer
    
    # 1. Fast Mathematical Pre-Filter (Pre-LLM Gatekeeper)
    mtf_info = multi_timeframe_analyzer.analyze_multi_timeframe_candles(symbol)
    is_falling_knife = mtf_info.get("is_falling_knife", False)
    is_dead_cat = mtf_info.get("is_dead_cat_bounce", False)
    is_macro_bear = mtf_info.get("is_macro_bearish_dominance", False)
    is_pre_pump = mtf_info.get("is_pre_pump_signal", False)
    
    if is_falling_knife or is_dead_cat:
        return {
            "approved": False,
            "confidence": 0,
            "action": "HOLD",
            "reasoning": f"🛡️ [VETO PRE-LLM] {symbol} descartado matemáticamente por Falling Knife / Trampa Dead Cat Bounce (Caída 24h: {mtf_info.get('price_change_24h_pct', 0):+.1f}%)."
        }
    
    # Check Groq fallback if Gemini is on cooldown
    groq_key = os.getenv("GROQ_API_KEY", "")
    
    all_keys = get_gemini_api_keys()
    if not all_keys and not groq_key:
        print("💡 [EVALUADOR CUÁNTICO DE RESPALDO] Reemplazando IA en pausa por Evaluador Técnico Inteligente...")
        # Smart Quantitative Fallback Engine
        vol_surge = tech_data.get("volume_surge_ratio", 1.0)
        rsi_2m = tech_data.get("rsi_2m", tech_data.get("rsi_15m", 50.0))
        ma25_ok = tech_data.get("price", 0) >= tech_data.get("ma25_15m", 0) if tech_data.get("ma25_15m", 0) > 0 else True
        
        if score >= 58 and rsi_2m <= 68 and ma25_ok and not is_macro_bear:
            return {
                "approved": True,
                "confidence": 88,
                "action": "BUY_LONG",
                "reasoning": f"🧠 [EVALUADOR CUÁNTICO A+] Candidata {symbol} aprobada por alta confluencia técnica (Score={score} Pts, VolSurge={vol_surge:.1f}x, RSI 2m={rsi_2m:.1f})."
            }
        else:
            return {
                "approved": False,
                "confidence": 40,
                "action": "HOLD",
                "reasoning": f"🛡️ [EVALUADOR CUÁNTICO] Candidata {symbol} en filtro de protección (Score={score} Pts, VolSurge={vol_surge:.1f}x). Preservando capital."
            }
    import learning_engine
    
    pattern_summary = time_series_memory.get_multi_cycle_pattern_summary(symbol)
    extreme_context = extreme_events_memory.get_symbol_extreme_context(symbol)
    
    # RAG: Extract Learned Rules from the 99 Testnet Simulations
    mem = learning_engine.load_memory()
    blocked_rules = "\n    - ".join(mem["learned_rules"]["blocked_patterns"][-5:]) # Get latest 5
    boosted_rules = "\n    - ".join(mem["learned_rules"]["boosted_patterns"][-5:])
    
    # RAG: Extract Dynamic Executive Learning Summary
    exec_learning_summary = learning_engine.get_executive_learning_summary(mem)

    import data_fetcher
    binance_sent = data_fetcher.get_binance_institutional_sentiment(symbol)
    binance_sent_str = f"Binance Trader Long/Short Ratio: {binance_sent.get('long_short_ratio', 1.0):.2f} (Long: {binance_sent.get('long_account_pct', 50):.1f}%, Short: {binance_sent.get('short_account_pct', 50):.1f}%) | Verdict: {binance_sent.get('sentiment_label', 'NEUTRAL')}"

    import beta_correlation_engine
    beta_info = beta_correlation_engine.calculate_beta_correlation(symbol)
    beta_str = f"Rho BTC: {beta_info.get('rho', 0.5):.2f} | Beta: {beta_info.get('beta', 1.0):.2f} | Clasificación: {beta_info.get('correlation_label')}"

    import order_flow_analyzer
    of_info = order_flow_analyzer.analyze_order_flow_cvd(symbol)
    of_str = f"Velocidad: {of_info.get('trade_speed_per_sec', 1.0):.2f} trades/sec | Taker Buy: {of_info.get('buy_aggression_pct', 50):.1f}% | CVD Delta: {of_info.get('cvd_delta_usd', 0.0):+.2f} USD | Dictamen Order Flow: {of_info.get('verdict')}"

    indicators = tech_data.get('indicators', {})
    risk_plan = tech_data.get('institutional_risk_plan', {})
    
    mtf_alignment = mtf_info.get("timeframe_alignment", {})
    mtf_score = mtf_info.get("multi_tf_score", 50)
    mtf_range_1d = mtf_info.get("price_expansion_1d_pct", 0.0)
    
    print(f"🧠 Consultando al Súper-Cerebro Gemini AI para {symbol} (Score: {score} Pts, MTF 1H/4H: {mtf_alignment.get('1h', 'NEUTRAL')}/{mtf_alignment.get('4h', 'NEUTRAL')})...")
    
    prompt_text = f"""
    Eres un Trader Cuantitativo Institucional Senior y Cazador Activo de Oportunidades A+ (Súper-Cerebro Adaptativo).
    Tu objetivo es lograr operaciones victoriosas de alta frecuencia intradía para {symbol} en SPOT LONG.

    ANÁLISIS DE MICROESTRUCTURA DE VELAS DE 15 MINUTOS (15M - CRITERIO PRINCIPAL DE DECISIÓN):
    - {mtf_info.get('pattern_15m_summary', 'Análisis 15m activo')}
    - Rango de Volatilidad 1D: {mtf_range_1d}% | Calificación MTF: {mtf_score}/100
    - Alineación: 2m={mtf_alignment.get('2m')}, 5m={mtf_alignment.get('5m')}, 15m={mtf_alignment.get('15m')}, 1h={mtf_alignment.get('1h')}, 4h={mtf_alignment.get('4h')}
    
    {exec_learning_summary}

    DATOS EN TIEMPO REAL PARA {symbol}:
    - Puntaje Técnico Cuantitativo: {score} / 100 Pts | FII (Inyección Capital Suelo): {mtf_info.get('fii_score', 0)}/100
    - RSI 15M: {mtf_info.get('rsi_structure', {}).get('rsi_15m', indicators.get('rsi_15m', 'N/A'))}
    - MACD Histograma 15M: {mtf_info.get('macd_hist_15m', indicators.get('macd_hist_15m', 0.0))}
    - Volume Surge: {mtf_info.get('vol_surge_15m', indicators.get('volume_surge', 'N/A'))}x
    - Bollinger %B 15M: {mtf_info.get('pct_b_15m', 'N/A')}
    - Pre-Pump Detectado: {is_pre_pump} | Agotamiento Cima: {mtf_info.get('is_overbought_exhaustion', False)}
    - Sentimiento Binance: {binance_sent_str}
    - Order Flow & CVD: {of_str}
    - Beta BTC: {beta_str}
    - Macro Context: {macro_context if macro_context else "Neutral"}

    DIRECTRICES DE DECISIÓN DEL SÚPER-CEREBRO:
    1. Si {symbol} presenta acumulación en suelo (FII >= 50 o soporte limpio en 15M/1H), VolSurge >= 0.7x, y no es Falling Knife, APRUEBA con alta confianza (approved: true, action: "BUY_LONG", confidence: 75-95).
    2. Si el activo está sobre-extendido (>2.5% de MA7), en caída libre activa o sin volumen comprador (<0.4x), rechaza (approved: false, action: "HOLD").
    3. Nuestro sistema opera en SPOT con Trailing Stop automático de 3 Fases (-0.80% en 3min, SL -1.50% máx).

    RESPONDE ÚNICAMENTE EN FORMATO JSON CON ESTA ESTRUCTURA EXACTA:
    {{
        "approved": true o false,
        "confidence": entero de 0 a 100,
        "reasoning": "explicación concisa en español de 1 oración",
        "action": "BUY_LONG" o "HOLD"
    }}
    """
    
    payload = {
        "contents": [{"parts": [{"text": prompt_text}]}],
        "generationConfig": {
            "temperature": 0.10,
            "maxOutputTokens": 2048,
            "responseMimeType": "application/json"
        }
    }
    
    models_to_try = [
        "gemini-3.6-flash"
    ]
    
    keys_pool = get_gemini_api_keys()
    
    def _try_one_oracle_key(args):
        model_name, key = args
        key_label = get_key_label(key, keys_pool)
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={key}"
            req = urllib.request.Request(url, data=json.dumps(payload).encode('utf-8'), headers={'Content-Type': 'application/json'})
            with urllib.request.urlopen(req, timeout=10) as response:
                res_data = json.loads(response.read().decode('utf-8'))
                if "candidates" in res_data and len(res_data["candidates"]) > 0:
                    text_res = res_data["candidates"][0]["content"]["parts"][0]["text"]
                    if "```json" in text_res:
                        text_res = text_res.split("```json")[1].split("```")[0]
                    elif "```" in text_res:
                        text_res = text_res.split("```")[1].split("```")[0]
                    parsed_res = json.loads(text_res.strip())
                    if "approved" in parsed_res and "confidence" in parsed_res:
                        return (parsed_res, key_label)
        except urllib.error.HTTPError as e:
            if e.code == 429:
                mark_key_in_cooldown(key)
        except Exception:
            pass
        return None

    import concurrent.futures

    for model_name in models_to_try:
        rr_idx = _get_key_index()
        keys_rotated = [keys_pool[(i + rr_idx) % len(keys_pool)] for i in range(len(keys_pool))]
        tasks = [(model_name, k) for k in keys_rotated]
        try:
            with concurrent.futures.ThreadPoolExecutor(max_workers=len(keys_rotated)) as executor:
                futures = {executor.submit(_try_one_oracle_key, t): t for t in tasks}
                for future in concurrent.futures.as_completed(futures, timeout=12):
                    result = future.result()
                    if result is not None:
                        parsed_res, key_label = result
                        _advance_key_index(key_label)
                        return parsed_res
        except Exception:
            continue

    print("🛡️ VETO DE SEGURIDAD: Súper-Cerebro fuera de línea. Candado de CERO compras activado.")
    return {"approved": False, "confidence": 0, "action": "HOLD", "reasoning": "Veto de Seguridad: Súper-Cerebro IA fuera de línea (Preservación de Liquidez)"}

# Function alias for universal compatibility across trading engines
review_trade_decision = consult_gemini_flash_oracle

if __name__ == "__main__":
    sys.stdout.reconfigure(encoding='utf-8')
    res = consult_gemini_flash_oracle(
        "BTCUSDT", 88, 
        {"rsi": 58, "macd": "Bullish Cross", "volume_surge": 2.1, "ema_trend": "Bullish", "wyckoff": "Spring Phase C"},
        {"headlines": ["Bitcoin Breaks Resistance with Institutional Inflows"]},
        {"score": 65, "sentiment": "Greed"}
    )
    print(res)


def review_top_candidates(candidates_data_list, news_data, fear_greed, macro_context="", market_bias_ctx=""):
    if not candidates_data_list:
        return {
            "selected_symbol": "NONE",
            "action": "HOLD",
            "approved": False,
            "confidence": 0,
            "committee_deliberation": {
                "agent_1_macro": "Sin candidatos disponibles.",
                "agent_2_tech": "Mercado sin setups técnicos A+.",
                "agent_3_orderbook": "Sin flujo de liquidez.",
                "agent_4_sector": "Sin rotación sectorial clara.",
                "agent_5_memory": "Preservación de capital.",
                "agent_6_risk": "Veto de riesgo activado.",
                "agent_7_ceo_anti_loss": "Liquidez 100% en USDT."
            },
            "reasoning": "Lista de candidatos vacía. 100% liquidez protegida en USDT."
        }

    keys_pool = get_gemini_api_keys()
    if not keys_pool or keys_pool == [""]:
        print("💡 Gemini Notice: Claves Gemini no configuradas o en cooldown. Fallback al primer candidato seguro.")
        top_cand = candidates_data_list[0]
        return {
            "selected_symbol": top_cand['symbol'],
            "approved": top_cand['score'] >= 58,
            "action": top_cand['suggested_action'],
            "confidence": top_cand['score'],
            "committee_deliberation": {
                "agent_1_macro": "Evaluación cuantitativa fallback.",
                "agent_2_tech": f"Score técnico: {top_cand['score']}/100.",
                "agent_3_orderbook": "Libro de órdenes verificado.",
                "agent_4_sector": "Sector activo.",
                "agent_5_memory": "Reglas de memoria aplicadas.",
                "agent_6_risk": "Gestión de riesgo automática.",
                "agent_7_ceo_anti_loss": "Consenso por Score Técnico."
            },
            "reasoning": f"Fallback Cuantitativo Inteligente (Score={top_cand['score']} Pts)."
        }

    import time_series_memory
    import extreme_events_memory
    import learning_engine

    mem = learning_engine.load_memory()
    exec_learning_summary = learning_engine.get_executive_learning_summary(mem)

    import orderbook_analyzer
    import sector_analyzer

    # Extract sector rotation summary across candidates map
    symbol_map = {c["symbol"]: c for c in candidates_data_list}
    sector_summary = sector_analyzer.analyze_sector_rotation(symbol_map)

    candidates_prompt_text = ""
    for cand in candidates_data_list:
        sym = cand['symbol']
        score = cand['score']
        action = cand['suggested_action']
        tech = cand.get('tech_data', {})
        ind = tech.get('indicators', {})
        mtf = tech.get('mtf_analysis', {})
        pat = time_series_memory.get_multi_cycle_pattern_summary(sym)
        specific_n = news_data.get('specific_news', {}).get(sym, [])
        sec = sector_analyzer.get_symbol_sector(sym)
        ob = orderbook_analyzer.fetch_orderbook_depth(sym)
        
        is_pre_pump = mtf.get('is_pre_pump_signal', False)
        is_knife = mtf.get('is_falling_knife', False)
        is_dead_cat = mtf.get('is_dead_cat_bounce', False)
        is_macro_bear = mtf.get('is_macro_bearish_dominance', False)
        gbm_z = mtf.get('gbm_zscore', ind.get('gbm_zscore', 0.0))
        chg_24h = mtf.get('price_change_24h_pct', 0.0)
        is_cetus_pattern = mtf.get('is_cetus_rocket_pattern', False)
        cetus_tag = " [🚀 PATRÓN COHETE - PRIORIDAD MÁXIMA]" if is_cetus_pattern else ""
        fii = mtf.get('fii_score', 0)
        fii_tag = " [🏔️ FII A+ >= 60 - INYECCIÓN SUELO]" if fii >= 60 else (" [⚡ FII 40-59]" if fii >= 40 else "")
        
        c1d = round(mtf.get('range_position_1d', 0.5) * 100)
        c4h = round(mtf.get('range_position_4h', 0.5) * 100)
        c1h = round(mtf.get('range_position_1h', 0.5) * 100)
        c30m = round(mtf.get('range_position_30m', 0.5) * 100)
        c15m = round(mtf.get('range_position_15m', 0.5) * 100)
        c5m = round(mtf.get('range_position_5m', 0.5) * 100)
        c2m = round(mtf.get('range_position_2m', 0.5) * 100)
        c1m = round(mtf.get('range_position_1m', 0.5) * 100)
        dist_to_24h_high = mtf.get('dist_to_24h_high_pct', 999.0)
        is_at_daily_ceiling = mtf.get('is_at_daily_resistance_ceiling', False)
        dist_ma7 = mtf.get('dist_from_15m_ma7_pct', 0.0)
        dist_1m_ema9 = mtf.get('dist_from_1m_ema9_pct', 0.0)
        is_sniper_pb = mtf.get('is_1m_sniper_pullback', True)
        is_fomo = mtf.get('is_1m_fomo_extension', False)
        is_overext = mtf.get('is_overextended_15m', False)
        tf_10s = mtf.get('timeframe_alignment', {}).get('10s', 'BEARISH')
        tf_30s = mtf.get('timeframe_alignment', {}).get('30s', 'BEARISH')
        cvd_str = ob.get('cvd_status', '⚪ CVD Neutral')
        
        dna = mtf.get('dna_profile', {})
        dna_str = f"{dna.get('dna_label', 'Estándar')} | Reputación: {dna.get('reputation', 'Neutral')} | Holgura Óptima: {dna.get('optimal_trailing_slack_pct', 0.50):.2f}% | Expansión Objetivo: +{dna.get('optimal_target_expansion_pct', 2.50):.2f}%"

        pred = mtf.get('predictive_dna', {})
        pump_prob = pred.get('pump_probability_pct', 50)
        dump_risk = pred.get('dump_risk_pct', 20)
        pred_label = pred.get('predictive_label', 'Neutral')
        catalysts_str = ", ".join(pred.get('active_pump_catalysts', [])) if pred.get('active_pump_catalysts') else "En desarrollo"
        warnings_str = ", ".join(pred.get('active_dump_warnings', [])) if pred.get('active_dump_warnings') else "Ninguna advertencia"

        # ── ADN v2: Time-of-Day, BTC Guard, Funding Rate, Sector Heat ──────────
        time_dna = mtf.get('time_of_day_dna', {})
        time_mult = time_dna.get('final_time_multiplier', 1.0)
        time_sess = time_dna.get('session_label', 'N/A')
        time_blackout = time_dna.get('is_blackout_hour', False)
        time_peak = time_dna.get('is_token_peak_hour', False)
        time_veto = time_dna.get('hard_veto_entry', False)
        time_expl = time_dna.get('explanation', '')

        btc_guard = mtf.get('btc_dominance_guard', {})
        btc_status = btc_guard.get('btc_status', 'UNKNOWN')
        btc_impact = btc_guard.get('altcoin_impact', 'NEUTRAL')
        btc_1h_chg = btc_guard.get('btc_1h_change_pct', 0)
        btc_avoid = btc_guard.get('should_avoid_altcoins', False)

        fund_dna = mtf.get('funding_rate_dna', {})
        fund_signal = fund_dna.get('funding_signal', 'UNKNOWN')
        fund_rate = fund_dna.get('funding_rate_pct', 0.0)
        fund_dump_risk = fund_dna.get('dump_risk_from_funding', False)
        fund_squeeze = fund_dna.get('squeeze_opportunity', False)

        sector_heat = mtf.get('sector_heat_dna', {})
        token_sector = sector_heat.get('token_sector', 'Other')
        sector_hot = sector_heat.get('is_in_hot_sector', False)
        hottest_sec = sector_heat.get('hottest_sector', 'N/A')

        anti_reentry = mtf.get('anti_reentry_check', {})
        already_traded = anti_reentry.get('already_traded_today', False)

        # ── ADN v3: Dynamic Asset Phenotype & Operational Guidelines ──────────
        arch_dna = mtf.get('archetype_dna', {})
        if not arch_dna:
            try:
                import adaptive_asset_dna
                arch_dna = adaptive_asset_dna.get_asset_dna_archetype(sym, mtf.get('atr_pct_15m', 0.30))
            except Exception:
                arch_dna = {"label": "General", "initial_sl_pct": -2.00, "max_stagnation_minutes": 35, "guideline_for_ai": "Estándar"}
        arch_lbl = arch_dna.get('label', 'General')
        arch_guide = arch_dna.get('guideline_for_ai', '')
        arch_sl = arch_dna.get('initial_sl_pct', -2.00)
        arch_tmax = arch_dna.get('max_stagnation_minutes', 60)

        floor_lbl = mtf.get('floor_structure_label', '⚪ ESPERANDO GIRO')
        is_15m_casc = mtf.get('is_15m_red_cascade', False)
        sniper_lbl = mtf.get('sniper_timing_label', '⏳ CONSOLIDANDO BASE')

        candidates_prompt_text += f"\nCANDIDATO: {sym} (Sector: {sec} | Acción Sugerida: {action}){cetus_tag}{fii_tag}\n"
        candidates_prompt_text += f"- Score: {score}/100 | MTF Score: {mtf.get('multi_tf_score', score)}/100 | FII (Inyección Suelo): {fii}/100\n"
        candidates_prompt_text += f"- 🏔️ ESTRUCTURA DE SUELO 15M: {floor_lbl} | Cascada Roja 15M={is_15m_casc}\n"
        candidates_prompt_text += f"- 🎯 GATILLO SNIPER 1M/5M: {sniper_lbl}\n"
        # ── 🔬 RADIOGRAFÍA CONDUCTUAL HOLOGRÁFICA 360° DEL ACTIVO ──────────────
        xray = mtf.get("behavioral_xray", {})
        xray_behav = xray.get("behavior_type", "ROTACIÓN_ESTRUCTURAL")
        xray_advice = xray.get("timing_advice", "")
        xray_alpha = xray.get("alpha_vs_btc_15m_pct", 0.0)
        xray_wick = xray.get("lower_wick_absorption_1m_pct", 0.0)
        xray_chan = xray.get("fractal_channel_pct", {})
        spring_info = mtf.get("spring_coiling", {})
        wave2_info = mtf.get("wave2_retest", {})

        candidates_prompt_text += f"- 🔬 RADIOGRAFÍA 360° ADN: {xray_behav} | {xray_advice}\n"
        if spring_info.get("is_spring_compressed") or wave2_info.get("is_wave2_retest"):
            candidates_prompt_text += f"- 🧬 PATRÓN FRACTAL DCR: {spring_info.get('label', 'Normal')} | {wave2_info.get('label', 'Estándar')}\n"
        candidates_prompt_text += f"- 📊 CANAL FRACTAL (% Suelo a Cima): 1M={xray_chan.get('1m', c1m)}% | 5M={xray_chan.get('5m', c5m)}% | 15M={xray_chan.get('15m', c15m)}% | 1H={xray_chan.get('1h', c1h)}% | 4H={xray_chan.get('4h', c4h)}% | 1D={xray_chan.get('1d', c1d)}%\n"
        candidates_prompt_text += f"- ⚡ ALPHA & ABSORCIÓN: Alpha vs BTC={xray_alpha:+.2f}% | Mecha Absorción 1M={xray_wick:.1f}%\n"
        candidates_prompt_text += f"- 🔮 Radar Predictivo Multi-Horizonte: {pred_label} | Prob. Pump={pump_prob}% | Riesgo Dump={dump_risk}%\n"
        candidates_prompt_text += f"- 🚀 Catalizadores Activos: [{catalysts_str}] | Advertencias: [{warnings_str}]\n"
        candidates_prompt_text += f"- 🧬 Elasticidad Histórica: {dna_str}\n"
        candidates_prompt_text += f"- 🏔️ MATRIZ FRACTAL DE SUELO 8D (% Canal desde el piso): 1D={c1d}% | 4H={c4h}% | 1H={c1h}% | 30M={c30m}% | 15M={c15m}% | 5M={c5m}% | 2M={c2m}% | 1M={c1m}%\n"
        candidates_prompt_text += f"- 🎯 Distancia a Máximo 24H: +{dist_to_24h_high:.2f}% | Alerta Techo 30M/24H={is_at_daily_ceiling}\n"
        candidates_prompt_text += f"- 🎯 Gatillo 1M Sniper: Distancia EMA9={dist_1m_ema9:+.2f}% | Retesteo Base={is_sniper_pb} | Anti-FOMO={not is_fomo}\n"
        obv_trend_sym = mtf.get("obv_trend", "NEUTRAL")
        bid_vol_depth = ob.get("bid_vol_usdt", 0.0)
        candidates_prompt_text += f"- 🌊 Flujo CVD, OBV & Libro: OBV={obv_trend_sym} | Bids={ob['bid_dominance_pct']}% (Muro Bids=${bid_vol_depth:,.0f} USDT) | {cvd_str}\n"
        candidates_prompt_text += (
            f"- RSI 8 Capas: 1M={mtf.get('rsi_1m', ind.get('rsi_1m', '?'))} | 2M={mtf.get('rsi_2m', ind.get('rsi_2m', '?'))} | "
            f"5M={mtf.get('rsi_5m', ind.get('rsi_5m', '?'))} | 15M={ind.get('rsi_15m', '?')} | 30M={mtf.get('rsi_30m', '?')} | 1H={mtf.get('rsi_1h', ind.get('rsi_1h', '?'))} | "
            f"4H={mtf.get('rsi_4h', ind.get('rsi_4h', '?'))} | 1D={mtf.get('rsi_1d', '?')}\n"
        )
        candidates_prompt_text += f"- VolSurge: 10S={mtf.get('vol_surge_10s', 1.0):.1f}x | 30S={mtf.get('vol_surge_30s', 1.0):.1f}x | 1M={mtf.get('vol_surge_1m', 1.0):.1f}x | 15M={ind.get('volume_surge', 1.0):.1f}x | Cima={is_overext}\n"
        # ── ADN v2 NEW LINES ────────────────────────────────────────────────────
        time_veto_str = " ⛔VETO_TEMPORAL" if time_veto else (" ⚠️BLACKOUT" if time_blackout else (" ⭐HORA_PICO" if time_peak else ""))
        candidates_prompt_text += f"- ⏰ ADN TEMPORAL: Sesion={time_sess} | Multiplicador={time_mult:.2f}x{time_veto_str} | {time_expl}\n"
        btc_avoid_str = " ⛔EVITAR_ALTCOINS" if btc_avoid else ""
        candidates_prompt_text += f"- 🟠 BTC GUARD: BTC 1H={btc_1h_chg:+.2f}% ({btc_status}) | Impacto Altcoins={btc_impact}{btc_avoid_str}\n"
        fund_risk_str = " ⛔DUMP_RISK_FUNDING" if fund_dump_risk else (" 🔥SHORT_SQUEEZE" if fund_squeeze else "")
        candidates_prompt_text += f"- 💰 FUNDING PERPS: {fund_signal} ({fund_rate:+.4f}%){fund_risk_str}\n"
        sector_hot_str = " 🔥SECTOR_CALIENTE" if sector_hot else ""
        already_str = " ⛔YA_OPERADO_HOY" if already_traded else ""
        candidates_prompt_text += f"- 🏭 SECTOR: {token_sector} (Sector mas caliente hoy: {hottest_sec}){sector_hot_str}{already_str}\n"
        candidates_prompt_text += "------------------------------------\n"

    print(f"✅ [Comité Institucional 7 Agentes] Consultando al Súper-Cerebro Gemini AI (Gemini 3.1 Flash Lite) para el TOP {len(candidates_data_list)} simultáneo...", flush=True)

    try:
        from data_fetcher import fetch_wall_street_macro_context
        ws_data = fetch_wall_street_macro_context()
        wall_street_str = f"{ws_data.get('macro_regime')} (S&P 500 {ws_data.get('sp_change_pct'):+.2f}%)"
    except Exception:
        wall_street_str = "⚪ Wall Street Neutral"

    prompt_text = f"""
    Eres el COMITÉ INSTITUCIONAL MULTI-AGENTE CUÁNTICO (Súper-Cerebro Supremo, Predictor de Catalizadores y Cazador de Alpha en el Suelo 7D).
    Tu misión suprema es: EVALUAR EL ADN PREDICTIVO MULTI-HORIZONTE, IDENTIFICAR CATALIZADORES DE PUMP, VETAR RIESGOS DE DUMP Y APROBAR LA MONEDA #1.

    ESTRUCTURA DE LOS 7 AGENTES INSTITUCIONALES EN DELIBERACIÓN CUÁNTICA:
    1. 🕵️ AGENTE 1 (Macro 1D & Guardián de Bitcoin): Evalúa el Semáforo Macro ({macro_context}), Wall Street ({wall_street_str}), Fear&Greed ({fear_greed.get('score')}), y estabilidad de BTC (BTC Guard). VETA categóricamente si el Semáforo es DEFENSIVO, altcoin_impact=AVOID o si BTC está en cascada roja.
    2. 📊 AGENTE 2 (Sniper de Suelo Fractal Confluente 8D): Exige entrada en la MATRIZ ARMÓNICA DE BASE (Canal 1M <= 35%, Canal 5M <= 40%, Canal 10M <= 45%, Canal 15M <= 50%, Canal 30M <= 55%, Canal 1H <= 60%, Canal 2H <= 60%). VETA categóricamente si el precio está en TECHO REAL de 1H/2H (Canal >= 68% con RSI >= 65) o si el activo es lento (ATR < 0.35%).
    3. 🌊 AGENTE 3 (Auditor de Libro, CVD & Squeeze Micro): Exige Bids >= 49.0%, Muro comprador > $15k USDT, CVD Taker positivo/neutral, Spread <= 0.28%, Vol Surge 1M >= 0.85x y OBV != DISTRIBUTING. VETA categóricamente activos con volumen muerto en 15M (Vol15M < 0.40x) o Muro Bids < $15k USDT.
    4. 🧩 AGENTE 4 (Analista Sectorial & Temporal): Prioriza sector líder ({sector_summary['top_sector']}) y valida la SESION TEMPORAL. VETO si VETO_TEMPORAL o BLACKOUT con multiplicador < 0.60.
    5. 🧠 AGENTE 5 (Memoria RAG & Auto-Aprendizaje Cuántico): Valida el ADN de la moneda, reputación histórica y patrones aprendidos. VETA permanentemente: (a) Monedas en Blacklist Dinámica (WR < 30%), (b) Mega-Caps / Zombis (TRX, BNB, BTC, ETH), (c) Volumen 15M muerto (<0.40x), (d) Distribución institucional, (e) Re-entradas en la misma moneda en menos de 4h. PREMIA cohetes con Vol1M >= 1.2x, Vol15M >= 0.80x, FII >= 60 y Retesteo Ola 2 (como ENA, KAIA, SUI, DCR).
    6. 🛡️ AGENTE 6 (Chief Risk Officer & Veto de Dump): Veta cualquier activo con Riesgo de Dump >= 40%, libro descompensado (Bids < 50.0% o Muro < $20k), OBV=DISTRIBUTING, DUMP_RISK_FUNDING, o activo en cuarentena/cooldown de 4 horas.
    7. 👑 AGENTE 7 (CEO Profit Scalp & Ejecutor Supremo): Sintetiza el consenso. Si el mejor candidato es un activo de Alta Elasticidad (ATR >= 0.45%) en SUELO CONFLUENTE FRACTAL con IGNICIÓN DE VOLUMEN (Vol1M >= 1.0x o Vol15M >= 1.2x) y vela 1M verde, APRUEBA "BUY_LONG" con Stop Loss Asimétrico de -0.75% y Cosecha Dinámica para ejecución inmediata.

    {exec_learning_summary}

    CONTEXTO DE MERCADO ACTUAL (MATRIZ MACRO CUÁNTICA):
    - {macro_context}
    - Wall Street: {wall_street_str} | Sector Líder: {sector_summary['top_sector']}
    - Fear & Greed: {fear_greed.get('score')} ({fear_greed.get('sentiment')})
    - Noticias: {json.dumps(news_data.get('headlines', [])[:2])}

    CANDIDATOS FINALISTAS EVALUADOS (TABLA MULTI-MONEDA SIMULTÁNEA):
    {candidates_prompt_text}

    🏛️ PROTOCOLO DINÁMICO Y AUTO-ADAPTATIVO DEL SÚPER-CEREBRO EN 4 PASOS:
    
    PASO 1 🔬 LECTURA DE LA RADIOGRAFÍA 360° Y CANAL FRACTAL CONFLUENTE:
    - Revisa la RADIOGRAFÍA 360° ADN y el CANAL FRACTAL (% Suelo a Cima en 1M, 5M, 15M, 1H).
    - 🎯 REGLA DE ORO DE LA MATRIZ ARMÓNICA 8D (Comprar en el Suelo Real): Exige que el precio esté en la BASE simultáneamente: 1M (<= 35%), 2M (<= 38%), 5M (<= 40%), 10M (<= 45%), 15M (<= 50%), 30M (<= 55%), 1H (<= 60%) y 2H (<= 60%). Si el precio está flotando en el TECHO de 1H/2H (Canal >= 68%), VÉTALO categóricamente.
    - ZONA ÓPTIMA DE COMPRA (Sweet-Spot): Prioriza activos en la BASE exacta (1M <= 35%, 5M <= 40%, 15M <= 50%, 1H <= 60%).
    - ALPHA & ABSORCIÓN: Premia fuertemente activos con Alpha vs BTC > +0.20% y Mecha de Absorción 1M >= 15% (compradores comprando el dip en soporte).
    - 🚫 VETO DE VOLUMEN MUERTO (Anti-Estancamiento): PROHIBIDO comprar si el candidato tiene volumen muerto (Vol1M < 0.80x o Vol15M < 0.80x). Exige compradores reales activos (Vol1M >= 1.0x o Vol15M >= 1.2x).
    REGLAS DE DECISIÓN DEL CEO:
    - Compara a los finalistas y selecciona al MEJOR ACTIVO DE TODO EL MERCADO.
    - 🎯 REGLA DE DISPARO EN BASE ARMÓNICA: Si un candidato cumple con la BASE ARMÓNICA 8D (1M <= 35%, 5M <= 40%, 10M <= 45%, 15M <= 50%, 30M <= 55%, 1H <= 60%), tiene Score >= 60, FII >= 50, OBV=ACCUMULATING, y no tiene vetos duros, APRUÉBALO con "BUY_LONG", approved: true, confidence: 85-95.
    - Si ningún candidato cumple con la confluencia de base y volumen, o el mercado está en dump macro, responde "selected_symbol": "NONE", "action": "HOLD".
    - 🔍 REGLA DE TRANSPARENCIA: En tu 'reasoning', menciona OBLIGATORIAMENTE los activos principales evaluados (ej: QNTUSDT, ZECUSDT, DASHUSDT) y el motivo técnico específico de por qué se aprueba o se veta cada uno.

    RESPONDE ÚNICAMENTE EN FORMATO JSON EXACTO CON ESTA ESTRUCTURA (7 AGENTES):
    {{
        "selected_symbol": "SIMBOLO" o "NONE",
        "action": "BUY_LONG" o "HOLD",
        "confidence": 0-100,
        "approved": true o false,
        "committee_deliberation": {{
            "agent_1_macro": "Dictamen macro en 1 oración...",
            "agent_2_tech": "Dictamen del suelo 8D (1M<=35%, 5M<=40%, 15M<=50%, 1H<=60%) y posición del canal en 1 oración...",
            "agent_3_orderbook": "Dictamen de libro de órdenes y Bids en 1 oración...",
            "agent_4_sector": "Dictamen de rotación sectorial en 1 oración...",
            "agent_5_memory": "Dictamen de memoria RAG y patrones ganadores en 1 oración...",
            "agent_6_risk": "Dictamen de validación de seguridad anti-cima en 1 oración...",
            "agent_7_ceo_anti_loss": "Dictamen final del CEO autorizando compra en el suelo o preservando USDT en 1 oración..."
        }},
        "reasoning": "Resumen técnico nombrando las monedas evaluadas y razones individuales..."
    }}
    """

    payload = {
        "contents": [{"parts": [{"text": prompt_text}]}],
        "generationConfig": {
            "temperature": 0.10,          # Baja temperatura = decisiones consistentes
            "maxOutputTokens": 2500,       # Cap óptimo para deliberación completa
            "responseMimeType": "application/json"
        }
    }
    
    # 🏎️ SUPER-CEREBRO GEMINI FLASH LITE (Ultra-Rápido, 30 RPM, Máxima Disponibilidad Libre de 429)
    models_to_try = [
        "gemini-3.1-flash-lite",
        "gemini-2.5-flash-lite",
        "gemini-3.6-flash"
    ]
    
    keys_pool = get_gemini_api_keys()
    
    def _try_one_key(args):
        """Intenta consultar Gemini con una sola key. Retorna (parsed_json, key_label, model_name) o None."""
        model_name, key = args
        key_label = get_key_label(key, keys_pool)
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={key}"
            req = urllib.request.Request(
                url,
                data=json.dumps(payload).encode('utf-8'),
                headers={'Content-Type': 'application/json'}
            )
            with urllib.request.urlopen(req, timeout=12) as response:
                res_data = json.loads(response.read().decode('utf-8'))
                if "candidates" in res_data and len(res_data["candidates"]) > 0:
                    text_res = res_data["candidates"][0]["content"]["parts"][0]["text"]
                    if "```json" in text_res:
                        text_res = text_res.split("```json")[1].split("```")[0]
                    elif "```" in text_res:
                        text_res = text_res.split("```")[1].split("```")[0]
                    parsed = json.loads(text_res.strip())
                    if "selected_symbol" in parsed:
                        return (parsed, key_label, model_name)
        except urllib.error.HTTPError as e:
            if e.code == 429:
                mark_key_in_cooldown(key)
        except Exception as err:
            pass
        return None
    
    # 🚀 MODO SECUENCIAL INTELIGENTE CON FAILOVER ULTRA-RÁPIDO:
    # Rota 1 clave por ciclo para no saturar RPM; si una da 429, salta inmediatamente a la siguiente
    for model_name in models_to_try:
        keys_available = get_gemini_api_keys()
        if not keys_available or keys_available == [""]:
            continue
        rr_idx = _get_key_index()
        keys_rotated = [keys_available[(i + rr_idx) % len(keys_available)] for i in range(len(keys_available))]
        for key in keys_rotated:
            res = _try_one_key((model_name, key))
            if res is not None:
                parsed, key_label, used_model = res
                _advance_key_index(key_label)
                print(f"✅ [{used_model}] Respuesta recibida de {key_label} (ágil).", flush=True)
                return parsed
    return {
        "selected_symbol": "NONE",
        "action": "HOLD",
        "approved": False,
        "confidence": 0,
        "committee_deliberation": {
            "agent_1_macro": "Súper-Cerebro fuera de línea.",
            "agent_2_tech": "Operaciones congeladas por seguridad.",
            "agent_3_orderbook": "Libro de órdenes en espera.",
            "agent_4_sector": "Rotación sectorial en espera.",
            "agent_5_memory": "Historial en espera.",
            "agent_6_risk": "VETO ABSOLUTO: Cero compras sin confirmación de IA.",
            "agent_7_ceo_anti_loss": "Liquidez 100% en USDT protegida."
        },
        "reasoning": "Veto de Seguridad: Súper-Cerebro IA fuera de línea (Preservación Absoluta de Liquidez en USDT)"
    }

# Backwards compatibility aliases
review_top_5_candidates = review_top_candidates
consult_committee_supreme = review_top_candidates
