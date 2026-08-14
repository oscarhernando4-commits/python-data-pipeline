import os
import sys
import json
import time
import urllib.request

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
            
    # Filter out keys in 5-minute cooldown (300 seconds)
    healthy_keys = [k for k in raw_keys if (now - _KEY_COOLDOWN.get(k, 0)) >= 300]
    
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
    """Puts a key in 5-minute cooldown blacklist when it encounters HTTP 429 Rate Limit."""
    if key and key != "":
        _KEY_COOLDOWN[key] = time.time()
        healthy = len(get_gemini_api_keys())
        print(f"🚫 Clave Gemini en pausa temporal (5 min) por Rate Limit 429. Claves saludables en pool: {healthy}")

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
    
    current_key = get_next_gemini_key()
    if not current_key and not groq_key:
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
    
    # RAG: Extract ALL-TIME Super Detailed History Table
    super_detailed_table = learning_engine.get_super_detailed_table_str(mem)
    matrix_champions = learning_engine.get_matrix_champions_summary()

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
    Eres un Trader Cuantitativo Institucional Senior y Experto en Aprendizaje de Patrones Históricos Extremos / Rastro de Ballenas.
    Tu objetivo es lograr operaciones victoriosas de alta frecuencia intradía para {symbol}.

    ANÁLISIS DE MICROESTRUCTURA DE VELAS DE 15 MINUTOS (15M - CRITERIO PRINCIPAL DE DECISIÓN):
    - {mtf_info.get('pattern_15m_summary', 'Análisis 15m activo')}
    - Rango de Volatilidad 1D: {mtf_range_1d}%
    - Calificación Multi-Temporal: {mtf_score}/100
    - Alineación por Temporalidad: 2m={mtf_alignment.get('2m')}, 5m={mtf_alignment.get('5m')}, 15m={mtf_alignment.get('15m')}, 1h={mtf_alignment.get('1h')}, 4h={mtf_alignment.get('4h')}, 1d={mtf_alignment.get('1d')}
    ⚠️ REGLA DE ORO DE VELAS DE 15M (DECISIÓN PRINCIPAL):
    1. Si el precio de 15m está por DEBAJO de MA(7) o MA(25) en 15m, RECHAZA la compra de inmediato (HOLD).
    2. Si la vela de 15m presenta mechas superiores de reversión o está sobre-extendida en la cima, RECHAZA la compra (HOLD).
    3. Exige que 5m y 15m muestren alineación alcista simultánea.
    4. REGLA DE ENTRADA TEMPRANA (INICIO DE IMPULSO): Si la Fase 15m es SOBRE_EXTENDIDO (CIMA) o la distancia respecto a MA(7) supera el +1.2%, RECHAZA la compra por llegada tardía en el techo (HOLD). APRUEBA únicamente en fase RUPTURA_FRESCA (INICIO) cuando el movimiento recién empieza.
    5. PATRÓN FLECHAS AMARILLAS (PUNTO DULCE A+): Si el activo presenta el Patrón de Flechas Amarillas (apoyo/retesteo en MA7/MA25 en 15m con mecha inferior de absorción compradora + anticipación en 5m/1h + correlación alcista de BTC/Mercado), APRUEBA CON ALTA CONVICCIÓN A+ (BUY_LONG).
    6. 🚀 PRE-PUMP DETECTADO: Si Señal Pre-Pump = True (Aceleración de Volumen > 2x + Squeeze Bollinger), APRUEBA CON ALTA PRIORIDAD.

    LECCIONES APRENDIDAS DE 99 SIMULACIONES (RAG MEMORY):
    Patrones Prohibidos (Trampas descubiertas):
    - {blocked_rules if blocked_rules else 'Sin trampas descubiertas aún.'}
    Patrones Potenciados (Victorias descubiertas):
    - {boosted_rules if boosted_rules else 'Sin victorias descubiertas aún.'}

    HISTORIAL DE LECTURAS 5M (ÚLTIMAS 4 HORAS):
    - {pattern_summary}

    BASE DE DATOS DE EVENTOS EXTREMOS HISTÓRICOS DE {symbol}:
    - {extreme_context}

    ESTADO GLOBAL DEL MERCADO (Reporte de Analista Macro Lite):
    - {macro_context if macro_context else "Contexto Macro No Disponible."}

    SESGO DEL MERCADO RECIENTE (AUTO-APRENDIZAJE DE PNL):
    - {market_bias_ctx if market_bias_ctx else "Sesgo de Mercado No Disponible."}
    ⚠️ IMPORTANTE: Si el sesgo reciente indica que el mercado está cayendo fuertemente y las compras (LONG) están perdiendo repetidamente, DEBES SER EXTREMADAMENTE SELECTIVO y solo aprobar compras si hay una confirmación técnica extrema de reversión. Alinear tus decisiones al dinero real (Real Money).

    🐋 INTELIGENCIA DE SENTIMIENTO INSTITUCIONAL DE BINANCE (Top Traders Long/Short Ratio):
    - {binance_sent_str}

    ⚡ MATRIZ DE CORRELACIÓN Y BETA DE BITCOIN:
    - {beta_str}
    ⚠️ REGLA DE RIESGO CORRELACIONAL: Si Bitcoin está débil o cayendo y {symbol} presenta una alta correlación (Rho >= 0.80), RECHAZA la compra para evitar caídas arrastradas. Prioriza activos descorrelacionados o refugio.

    🎯 ORDER FLOW SPEED & CUMULATIVE VOLUME DELTA (CVD ANALYST):
    - {of_str}
    ⚠️ REGLA DE ORDER FLOW: Si hay absorción compradora A+ (Taker Buy >= 55% y CVD Delta +), AUMENTA la confianza de la compra. Si hay presión vendedora (Taker Buy <= 42%), RECHAZA la operación.

    🏆 CUENTAS CAMPEONAS EN TIEMPO REAL (REPLICACIÓN MATRIX 100):
    {matrix_champions}
    ⚠️ DIRECTRIZ DE REPLICACIÓN DE CAMPEONES: Si los campeones actuales están ganando con Grupo 3 (Breakout por Volumen en activos de tendencia como XAUTUSDT, DODOUSDT, ALLOUSDT), REPLICA de forma prioritaria esta estrategia en Dinero Real cuando el activo presente un setup técnico alcista limpio A+.

    HISTORIAL SUPER DETALLADO (TABLA COMPLETA ALL-TIME DE TODAS LAS OPERACIONES):
    {super_detailed_table}
    Lee detenidamente esta tabla. Contiene los resultados cruzados de 5 GRUPOS DIFERENTES de estrategias operando en el mercado en tiempo real. 
    ⚠️ INSTRUCCIÓN DE AUTO-APRENDIZAJE DINÁMICO (SUPERCEREBRO):
    1. No te limites a leer las reglas pasadas. Debes analizar esta tabla AHORA MISMO y descubrir qué grupo está siendo más rentable en las condiciones actuales.
    2. Si un Grupo (ej. Grupo 4) está logrando victorias repetidas bajo cierto RSI o Tendencia, ABSORBE esa estrategia dinámicamente y aplícala para esta decisión.
    3. Si ves que múltiples grupos están perdiendo bajo condiciones específicas recientes, tómalo como precaución pero NO como bloqueo absoluto.
    4. DIRECTRIZ DE TRADER ACTIVO RENTABLE (CLÁUSULA DE FLUIDEZ): Tu misión es CAPTURAR OPORTUNIDADES REALES de ganancia. El usuario necesita entre 3-4 operaciones diarias en SPOT. NO seas excesivamente conservador ni paranoico. Si una moneda cumple con las Reglas 1 a 7 (Score >= 58, MA25 limpia, VolSurge >= 1.0x, Bids >= 48% y Order Flow positivo), DEBES APROBAR (approved: true). Solo rechaza (approved: false) si hay una caída masiva activa en Bitcoin o si TODOS los indicadores están en contra simultáneamente.

    EVALÚA LOS SIGUIENTES DATOS EN TIEMPO REAL PARA {symbol}:
    - Puntaje Técnico Cuantitativo Actual: {score} / 100 Pts
    - Calificación Multi-Temporal MTF: {mtf_score} / 100 Pts
    - RSI 15M: {mtf_info.get('rsi_structure', {}).get('rsi_15m', indicators.get('rsi_15m', 'N/A'))}
    - MACD Histograma 15M: {mtf_info.get('macd_hist_15m', indicators.get('macd_hist_15m', 0.0))} (Cruce Alcista: {mtf_info.get('is_macd_bullish_cross', False)})
    - ATR 15M: {indicators.get('atr_15m', 'N/A')}
    - Volume Surge: {mtf_info.get('vol_surge_15m', indicators.get('volume_surge', 'N/A'))}x
    - Bollinger Bands %%B 15M: {mtf_info.get('pct_b_15m', 'N/A')} (0.0=Banda Inferior/Sobreventa, 1.0=Banda Superior/Sobrecompra)
    - Candidato a Rebote por Sobreventa: {mtf_info.get('is_oversold_bounce_candidate', False)}
    - Agotamiento Alcista (Sobrecompra): {mtf_info.get('is_overbought_exhaustion', False)}
    - Señal Pre-Pump (Acumulación Explosiva): {is_pre_pump} (VolAcc: {mtf_info.get('vol_acceleration', 1.0)}x, BBSqueeze: {mtf_info.get('bb_squeeze_ratio', 1.0)})
    - Anomalía GBM Z-Score: {mtf_info.get('gbm_zscore', 0.0):.2f} (Rebote Post-Crash: {mtf_info.get('is_crash_rebound', False)})
    - Dominancia Macro Bajista: {is_macro_bear}
    ⚠️ REGLA DE REVERSIÓN A LA MEDIA: Si %B <= 0.20 y RSI < 35, es una oportunidad A+ de REBOTE - APRUEBA con alta confianza. Si %B >= 0.90, el activo está agotado - RECHAZA para proteger capital.
    - Tendencia Macro 4H: {tech_data.get('macro_trend_4h', 'N/A')}
    - Rastreador de Ballenas: {tech_data.get('whale_flow', 'Neutro (50% Compradora / 50% Vendedora)')}
    - Sentimiento del Mercado (Fear & Greed): {fear_greed.get('score')} ({fear_greed.get('sentiment')})
    - Noticias al Minuto: {json.dumps(news_data.get('headlines', [])[:4])}

    REGLAS DE DECISIÓN CON APRENDIZAJE HISTÓRICO Y EVENTOS EXTREMOS (MODO SPOT ONLY):
    1. Compara si el patrón actual imita un evento extremo histórico de desplome o pump de {symbol}.
    2. Extrae dinámicamente el perfil del "Grupo Más Rentable" de la tabla histórica. Si la operación actual encaja en su perfil ganador, APRUEBA.
    3. Extrae dinámicamente el perfil de los "Grupos Perdedores". Si la operación imita sus errores recientes, RECHAZA (HOLD).
    4. Si el historial de 4H muestra acumulación creciente de ballenas y volumen fuerte, cruzado con victorias en la tabla, APRUEBA para BUY_LONG.
    5. ESTRICTAMENTE PROHIBIDO OPERAR EN SHORT. El usuario solo opera en mercado SPOT (LONG). Si el mercado se está desplomando y no hay oportunidades de rebote, la única acción válida es HOLD.

    RESPONDE ÚNICAMENTE EN FORMATO JSON CON ESTA ESTRUCTURA EXACTA:
    {{
        "approved": true o false,
        "confidence": entero de 0 a 100,
        "reasoning": "explicación concisa en español de 1 oración",
        "action": "BUY_LONG" o "HOLD"
    }}
    """
    
    # User Requested Priority Cascade (Strongest → Fallback)
    # Each model gets 2 attempts with 5s wait on rate-limit before moving to next
    payload = {
        "contents": [{"parts": [{"text": prompt_text}]}],
        "generationConfig": {"temperature": 0.2, "responseMimeType": "application/json"}
    }
    
    # User Mandate: STRICTLY ONLY gemini-3.1-flash-lite (NO other model allowed)
    models_to_try = [
        "gemini-3.1-flash-lite"
    ]
    
    max_retries_per_model = 2
    
    keys_pool = get_gemini_api_keys()
    print(f"✅ [Pre-Filtro Matemático] 30 Pares analizados. Pool de {len(keys_pool)} Claves Gemini activas. Consultando al Súper-Cerebro Gemini AI (Flash-Lite Only) SOLO para el TOP 1 ({symbol})...")
    
    for model_name in models_to_try:
        # Start from persistent round-robin key index to balance usage across all 10 API keys
        rr_idx = _get_key_index()
        keys_rotated = [keys_pool[(i + rr_idx) % len(keys_pool)] for i in range(len(keys_pool))]
        for key in keys_rotated:
            key_label = get_key_label(key, keys_pool)
            try:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={key}"
                
                req = urllib.request.Request(url, data=json.dumps(payload).encode('utf-8'), headers={'Content-Type': 'application/json'})
                with urllib.request.urlopen(req, timeout=10) as response:
                    res_data = json.loads(response.read().decode('utf-8'))
                    
                    if "candidates" in res_data and len(res_data["candidates"]) > 0:
                        text_res = res_data["candidates"][0]["content"]["parts"][0]["text"]
                        
                        try:
                            # Clean markdown blocks if present
                            if "```json" in text_res:
                                text_res = text_res.split("```json")[1].split("```")[0]
                            elif "```" in text_res:
                                text_res = text_res.split("```")[1].split("```")[0]
                                
                            parsed_res = json.loads(text_res.strip())
                            if "approved" in parsed_res and "confidence" in parsed_res:
                                _advance_key_index(key_label)  # Track successful usage
                                return parsed_res
                        except json.JSONDecodeError:
                            return {"approved": False, "confidence": 0, "action": "HOLD", "reasoning": "Veto de Seguridad: Fallo de formato IA"}
            except urllib.error.HTTPError as e:
                if e.code == 429:
                    mark_key_in_cooldown(key)
                    continue
                else:
                    continue
            except Exception as e:
                break
                
        print(f"⏭️ Agotados intentos para {model_name}. Cambiando a modelo de respaldo...")

    print("🛡️ VETO DE SEGURIDAD: Todos los modelos de IA fuera de línea. Candado de CERO compras activado.")
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
    super_detailed_table = learning_engine.get_super_detailed_table_str(mem)

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
        
        candidates_prompt_text += f"\nCANDIDATO: {sym} (Sector: {sec} | Acción Sugerida: {action})\n"
        candidates_prompt_text += f"- Score Técnico: {score}/100 | Calificación MTF: {mtf.get('multi_tf_score', score)}/100\n"
        candidates_prompt_text += f"- RSI 15M: {ind.get('rsi_15m')}, MACD Hist 15M: {mtf.get('macd_hist_15m', ind.get('macd_hist_15m', 0.0))}, VolSurge: {ind.get('volume_surge_ratio', 1.0)}x\n"
        candidates_prompt_text += f"- 🚀 Señal Pre-Pump: {is_pre_pump} (VolAcc: {mtf.get('vol_acceleration', 1.0)}x, BBSqueeze: {mtf.get('bb_squeeze_ratio', 1.0)})\n"
        candidates_prompt_text += f"- ⛔ Riesgo Falling Knife / Dead Cat: {is_knife or is_dead_cat} (Caída 24h: {chg_24h:+.1f}%) | Macro Bearish: {is_macro_bear}\n"
        candidates_prompt_text += f"- 💥 Rebote Post-Crash / GBM Z-Score: {gbm_z:.2f} (Rebote: {mtf.get('is_crash_rebound', False)})\n"
        candidates_prompt_text += f"- Libro de Órdenes: Dominancia Bids Compradores {ob['bid_dominance_pct']}% ({ob['liquidity_status']})\n"
        candidates_prompt_text += f"- Tendencia 4H: {tech.get('macro_trend_4h')}\n"
        candidates_prompt_text += f"- Historial 5M (4h): {pat}\n"
        candidates_prompt_text += f"- NOTICIAS ESPECÍFICAS ÚLTIMAS 24H: {json.dumps(specific_n)}\n"
        candidates_prompt_text += "------------------------------------"

    print(f"✅ [Comité Institucional 7 Agentes - CEO Supreme] Mercado filtrado y analizado. Consultando al Súper-Cerebro Gemini AI para el TOP {len(candidates_data_list)} simultáneo...")

    try:
        from data_fetcher import fetch_wall_street_macro_context
        ws_data = fetch_wall_street_macro_context()
        wall_street_str = f"{ws_data.get('macro_regime')} (S&P 500 {ws_data.get('sp_change_pct'):+.2f}%)"
    except Exception:
        wall_street_str = "⚪ Wall Street Neutral"

    prompt_text = f"""
    Eres el COMITÉ INSTITUCIONAL MULTI-AGENTE CUÁNTICO 24/7 (Súper-Cerebro de Élite).
    Tu estructura está compuesta por 7 AGENTES ESPECIALIZADOS DE INTELIGENCIA ARTIFICIAL que deben deliberar y lograr consenso unánime antes de ejecutar cualquier orden real:
    
    1. 🕵️ AGENTE 1 - ANALISTA MACRO & RASTRO DE BALLENAS (Whale & Macro Sentinel):
       - Examina el sentimiento Fear & Greed ({fear_greed.get('score')} - {fear_greed.get('sentiment')}), Mercado Tradicional ({wall_street_str}), noticias globales y volumen institucional (Volume Surge > 1.2x).
    
    2. 📊 AGENTE 2 - INGENIERO TÉCNICO & PRICE ACTION (Chartist & Pattern Sniper):
       - Examina Cruce MA25/MA99, SuperTrend Verde, Rebote VWAP, MACD 15M, Señal Pre-Pump (Aceleración de Volumen > 2x) y descarta Falling Knives / Dead Cat Bounces.
    
    3. 🌊 AGENTE 3 - RASTREADOR DE PROFUNDIDAD Y LIBRO DE ÓRDENES (Orderbook & Liquidity Depth Tracker):
       - Examina el Orderbook en tiempo real (Dominancia Bids Compradores vs Asks Vendedores), muros de soporte de ballenas (Bids >= 55%) y riesgo de slippage.
    
    4. 🧩 AGENTE 4 - ANALISTA DE SECTORES Y ROTACIÓN DE CAPITAL (Sector Cluster Analyst):
       - Examina la rotación de capital institucional por sectores. Sector Dominante Actual: {sector_summary['top_sector']} (Score {sector_summary['top_sector_score']}, VolSurge {sector_summary['top_sector_vol_surge']}x).
    
    5. 🧠 AGENTE 5 - HISTORIADOR RAG & MEMORIA QUANT (Memory & Pattern Historian):
       - Compara con las 99 simulaciones pasadas ({market_bias_ctx}), patrones prohibidos/potenciados y la tabla All-Time de simulaciones.
    
    6. 🛡️ AGENTE 6 - CHIEF RISK OFFICER (Juez Supremo de Riesgo - Francisca Serrano & Hyenuk Chu):
       - Posee VETO ABSOLUTO. Regla #1: No perder dinero. Regla #2: No olvidar la regla #1. Veta absolutamente si Riesgo Falling Knife / Dead Cat = True. Exige convicción A+ (Score >= 55, Confianza >= 70%).
    
    7. 👑 AGENTE 7 - CEO & ANTI-LOSS PROFIT MAXIMIZER (Chief Executive Orchestrator):
       - LÍDER SUPREMO Y ORQUESTADOR DE RENTABILIDAD. Sintetiza las opiniones de los otros 6 agentes. Prioriza activos con Señal Pre-Pump activa y autoriza compras con alta convicción. Si el mercado es tóxico, responde "NONE".

    CONTEXTO GLOBAL MACRO Y ROTACIÓN SECTORIAL:
    - Mercado Tradicional Wall Street: {wall_street_str}
    - Sector Liderando Entrada de Capital: {sector_summary['top_sector']} ({sector_summary['all_sectors'].get(sector_summary['top_sector'], {}).get('status', '')})
    - Sesgo de Aprendizaje: {market_bias_ctx}
    - Entorno Macro Cripto: {macro_context}
    - Fear & Greed: {fear_greed.get('score')} ({fear_greed.get('sentiment')})
    - Noticias Globales: {json.dumps(news_data.get('headlines', [])[:3])}

    MEMORIA DE SIMULADORES (Super Detailed Table):
    {super_detailed_table}

    PERFILES DE LOS CANDIDATOS FINALISTAS (TOP BULLISH CON LIBRO DE ÓRDENES Y SECTOR):
    {candidates_prompt_text}

    REGLAS DE ORO PARA LA TOMA DE DECISIONES (SPOT ONLY):
    1. 🛡️ UMBRAL MÍNIMO A+ (Score >= 55): NUNCA apruebes una compra para un activo con Score Técnico < 55 o en caída libre. Si ningún candidato tiene Score >= 55 con confirmación de volumen, la respuesta OBLIGATORIA es responder "NONE" con "action": "HOLD".
    2. 🚫 PROHIBIDO 'FALLING KNIVES' Y 'DEAD CAT BOUNCES': Si un activo tiene bandera de Falling Knife o Dead Cat Bounce, VÉTALO inmediatamente.
    3. 🚀 PRIORIDAD PRE-PUMP: Si un activo tiene Señal Pre-Pump = True con Bids >= 55%, selecciónalo como candidato principal con alta convicción.
    4. 🌊 SOPORTE EN LIBRO DE ÓRDENES: Prioriza candidatos con Bids Compradores >= 55% que confirmen muros de soporte de ballenas.
    5. 🧩 ROTACIÓN SECTORIAL: Favorece activos pertenecientes a sectores con entrada masiva de capital ({sector_summary['top_sector']}).
    6. 💎 DECISIÓN DEL AGENTE 7 CEO: Si encuentras un candidato excepcional que cumple TODAS las reglas A+, selecciona su símbolo y aprueba "BUY_LONG" con confianza >= 70%. Si el mercado está sucio, lateral, bajista o con activos mediocres, responde "NONE" y protege el 100% de la liquidez en USDT.

    RESPONDE ÚNICAMENTE EN FORMATO JSON EXACTO CON ESTA ESTRUCTURA MULTI-AGENTE (7 AGENTES):
    {{
        "selected_symbol": "SIMBOLO" o "NONE",
        "action": "BUY_LONG" o "HOLD",
        "confidence": 0-100,
        "approved": true o false,
        "committee_deliberation": {{
            "agent_1_macro": "Dictamen del Analista Macro y volumen de ballenas en 1 oración...",
            "agent_2_tech": "Dictamen del Ingeniero Técnico sobre RSI, MACD, Pre-Pump y soportes en 1 oración...",
            "agent_3_orderbook": "Dictamen del Rastreador de Libro de Órdenes sobre dominancia Bids/Asks en 1 oración...",
            "agent_4_sector": "Dictamen del Analista Sectorial sobre la rotación de capital en 1 oración...",
            "agent_5_memory": "Dictamen del Historiador RAG sobre coincidencia con patrones pasados en 1 oración...",
            "agent_6_risk": "Dictamen del Chief Risk Officer sobre veto de riesgo y ratio 1:2 en 1 oración...",
            "agent_7_ceo_anti_loss": "Dictamen final del CEO & Anti-Loss Profit Maximizer (Consenso Supremo) en 1 oración..."
        }},
        "reasoning": "Resumen ejecutivo del consenso institucional..."
    }}
    """

    payload = {"contents": [{"parts": [{"text": prompt_text}]}], "generationConfig": {"temperature": 0.1, "responseMimeType": "application/json"}}
    models_to_try = [
        "gemini-3.1-flash-lite"
    ]
    
    for model_name in models_to_try:
        rr_idx = _get_key_index()
        keys_rotated = [keys_pool[(i + rr_idx) % len(keys_pool)] for i in range(len(keys_pool))]
        for key in keys_rotated:
            key_label = get_key_label(key, keys_pool)
            try:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={key}"
                req = urllib.request.Request(url, data=json.dumps(payload).encode('utf-8'), headers={'Content-Type': 'application/json'})
                with urllib.request.urlopen(req, timeout=15) as response:
                    res_data = json.loads(response.read().decode('utf-8'))
                    if "candidates" in res_data and len(res_data["candidates"]) > 0:
                        text_res = res_data["candidates"][0]["content"]["parts"][0]["text"]
                        if "```json" in text_res: text_res = text_res.split("```json")[1].split("```")[0]
                        elif "```" in text_res: text_res = text_res.split("```")[1].split("```")[0]
                        
                        parsed = json.loads(text_res.strip())
                        if "selected_symbol" in parsed:
                            _advance_key_index(key_label)  # Track successful usage
                            return parsed
            except urllib.error.HTTPError as e:
                if e.code == 429:
                    mark_key_in_cooldown(key)
                    continue
                else:
                    continue
            except Exception:
                continue  # Try next key in pool instead of aborting
    
    print("🛡️ VETO DE SEGURIDAD: Todos los modelos de IA fuera de línea. Candado de CERO compras activado.")
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
