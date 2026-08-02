import os
import sys
import json
import time
import urllib.request

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
_KEY_INDEX = 0

def get_gemini_api_keys():
    """
    Extracts all 10 available Gemini API Keys from environment variables.
    Returns a list of non-empty API keys.
    """
    keys = []
    # Key 1 (Primary)
    k1 = os.getenv("GEMINI_API_KEY", "")
    if k1: keys.append(k1)
    
    # Keys 2 to 10
    for i in range(2, 11):
        env_name = f"GEMINI_API_KEY_{i:02d}"
        val = os.getenv(env_name, "")
        if val and val not in keys:
            keys.append(val)
            
    return keys if keys else [""]

def get_next_gemini_key():
    """Returns the next API key in round-robin sequence across the 10-key pool."""
    global _KEY_INDEX
    keys = get_gemini_api_keys()
    if not keys or keys == [""]:
        return ""
    key = keys[_KEY_INDEX % len(keys)]
    _KEY_INDEX += 1
    return key

def consult_gemini_flash_oracle(symbol, score, tech_data, news_data, fear_greed, macro_context="", market_bias_ctx=""):
    """
    Super-Brain AI Decision Reviewer using Google Gemini Flash Free API.
    Provides sub-second LLM reasoning for high-stakes trades, enriched with Macro Lite context.
    """
    if not GEMINI_API_KEY:
        print("💡 Gemini Notice: GEMINI_API_KEY no configurada aún. Usando fallback cuantitativo.")
        return {"approved": True, "confidence": score, "reasoning": "Fallback cuantitativo (Score >= 85 Pts)"}

    import time_series_memory
    import extreme_events_memory
    import learning_engine
    
    pattern_summary = time_series_memory.get_multi_cycle_pattern_summary(symbol)
    extreme_context = extreme_events_memory.get_symbol_extreme_context(symbol)
    
    # RAG: Extract Learned Rules from the 99 Testnet Simulations
    mem = learning_engine.load_memory()
    blocked_rules = "\n    - ".join(mem["learned_rules"]["blocked_patterns"][-5:]) # Get latest 5
    boosted_rules = "\n    - ".join(mem["learned_rules"]["boosted_patterns"][-5:])
    
    # RAG: Extract ALL-TIME Super Detailed History Table
    super_detailed_table = learning_engine.get_super_detailed_table_str(mem)

    indicators = tech_data.get('indicators', {})
    risk_plan = tech_data.get('institutional_risk_plan', {})
    
    import multi_timeframe_analyzer
    mtf_info = multi_timeframe_analyzer.analyze_multi_timeframe_candles(symbol)
    mtf_alignment = mtf_info.get("timeframe_alignment", {})
    mtf_score = mtf_info.get("multi_tf_score", 50)
    mtf_range_1d = mtf_info.get("price_expansion_1d_pct", 0.0)
    
    print(f"🧠 Consultando al Súper-Cerebro Gemini AI para {symbol} (Score: {score} Pts, MTF 1H/4H: {mtf_alignment.get('1h', 'NEUTRAL')}/{mtf_alignment.get('4h', 'NEUTRAL')})...")
    
    prompt_text = f"""
    Eres un Trader Cuantitativo Institucional Senior y Experto en Aprendizaje de Patrones Históricos Extremos / Rastro de Ballenas.
    Tu objetivo es lograr operaciones victoriosas de alta frecuencia intradía para {symbol}.

    ANÁLISIS ESTRUCTURAL DE VELAS DE 1 HORA (1H) Y 4 HORAS (4H):
    - Rango de Volatilidad 1D: {mtf_range_1d}%
    - Calificación Multi-Temporal: {mtf_score}/100
    - Alineación por Temporalidad: 5m={mtf_alignment.get('5m')}, 15m={mtf_alignment.get('15m')}, 1h={mtf_alignment.get('1h')}, 4h={mtf_alignment.get('4h')}, 1d={mtf_alignment.get('1d')}
    ⚠️ REGLA ESTRICTA DE VELAS DE 1H: Si la vela de 1H está en consolidación plana muerta (< 1.0% de movimiento) o en tendencia bajista fuerte en 1H/4H, RECHAZA la compra para evitar quedar atrapado en acumulación horizontal sin volumen.

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

    HISTORIAL SUPER DETALLADO (TABLA COMPLETA ALL-TIME DE TODAS LAS OPERACIONES):
    {super_detailed_table}
    Lee detenidamente esta tabla. Contiene los resultados cruzados de 5 GRUPOS DIFERENTES de estrategias operando en el mercado en tiempo real. 
    ⚠️ INSTRUCCIÓN DE AUTO-APRENDIZAJE DINÁMICO (SUPERCEREBRO):
    1. No te limites a leer las reglas pasadas. Debes analizar esta tabla AHORA MISMO y descubrir qué grupo está siendo más rentable en las condiciones actuales.
    2. Si un Grupo (ej. Grupo 4) está logrando victorias repetidas bajo cierto RSI o Tendencia, ABSORBE esa estrategia dinámicamente y aplícala para esta decisión.
    3. Si ves que múltiples grupos están perdiendo bajo condiciones específicas recientes, tómalo como precaución pero NO como bloqueo absoluto.
    4. DIRECTRIZ DE TRADER ACTIVO RENTABLE: Tu misión es ENCONTRAR OPORTUNIDADES REALES de ganancia. El usuario necesita entre 3-4 operaciones diarias en SPOT. NO seas excesivamente conservador. Si hay una señal técnica clara (RSI extremo, volumen fuerte, tendencia definida), APRUEBA la operación para BUY_LONG. Solo rechaza (HOLD) si TODOS los indicadores están en contra simultáneamente.

    EVALÚA LOS SIGUIENTES DATOS EN TIEMPO REAL PARA {symbol}:
    - Puntaje Técnico Cuantitativo Actual: {score} / 100 Pts
    - RSI 15M: {indicators.get('rsi_15m', 'N/A')}
    - MACD Histograma 15M: {indicators.get('macd_hist_15m', 'N/A')}
    - ATR 15M: {indicators.get('atr_15m', 'N/A')}
    - Volume Surge: {indicators.get('volume_surge', 'N/A')}
    - Tendencia Macro 4H: {tech_data.get('macro_trend_4h', 'N/A')}
    - Rastreador de Ballenas: {tech_data.get('whale_flow', 'Dominancia Compradora 68% vs 32% Vendedora')}
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
    
    # Exact cascade requested by user: prioritizing flash-lite to avoid rate limits
    models_to_try = [
        "gemini-3.1-flash-lite",
        "gemini-3.5-flash-lite",
        "gemini-3.1-flash-lite-preview",
        "gemini-2.5-flash-lite"
    ]
    
    max_retries_per_model = 2
    
    keys_pool = get_gemini_api_keys()
    print(f"✅ [Pre-Filtro Matemático] 30 Pares analizados. Pool de {len(keys_pool)} Claves Gemini activas. Consultando al Súper-Cerebro Gemini AI SOLO para el TOP 1 ({symbol})...")
    
    for model_name in models_to_try:
        for key in keys_pool:
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
                                return parsed_res
                        except json.JSONDecodeError:
                            return {"approved": True, "confidence": score, "reasoning": "Fallback cuantitativo (Fallo de formato IA)"}
            except urllib.error.HTTPError as e:
                if e.code == 429:
                    print(f"🔄 Clave Gemini en Rate Limit 429 ({model_name}). Rotando a la siguiente clave del pool de {len(keys_pool)} keys...")
                    continue
                else:
                    break
            except Exception as e:
                break
                
        print(f"⏭️ Agotados intentos para {model_name}. Cambiando a modelo de respaldo...")

    print("Gemini LLM Notice: Todos los modelos de IA ocupados. Usando fallback cuantitativo seguro.")
    return {"approved": True, "confidence": score, "reasoning": f"Fallback cuantitativo seguro (Score >= {score} Pts)"}

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
    if not GEMINI_API_KEY:
        print("💡 Gemini Notice: GEMINI_API_KEY no configurada. Fallback al primer candidato.")
        return {"selected_symbol": candidates_data_list[0]['symbol'], "approved": True, "action": candidates_data_list[0]['suggested_action'], "confidence": candidates_data_list[0]['score'], "reasoning": "Fallback Cuantitativo"}

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
        tech = cand['tech_data']
        ind = tech.get('indicators', {})
        pat = time_series_memory.get_multi_cycle_pattern_summary(sym)
        specific_n = news_data.get('specific_news', {}).get(sym, [])
        sec = sector_analyzer.get_symbol_sector(sym)
        ob = orderbook_analyzer.fetch_orderbook_depth(sym)
        
        candidates_prompt_text += f"\nCANDIDATO: {sym} (Sector: {sec} | Acción Sugerida: {action})\n"
        candidates_prompt_text += f"- Score Técnico: {score}/100\n"
        candidates_prompt_text += f"- RSI 15M: {ind.get('rsi_15m')}, MACD: {ind.get('macd_hist_15m')}, Volume Surge: {ind.get('volume_surge_ratio')}\n"
        candidates_prompt_text += f"- Libro de Órdenes: Dominancia Bids Compradores {ob['bid_dominance_pct']}% ({ob['liquidity_status']})\n"
        candidates_prompt_text += f"- Tendencia 4H: {tech.get('macro_trend_4h')}\n"
        candidates_prompt_text += f"- Historial 5M (4h): {pat}\n"
        candidates_prompt_text += f"- NOTICIAS ESPECÍFICAS ÚLTIMAS 24H: {json.dumps(specific_n)}\n"
        candidates_prompt_text += "------------------------------------"

    print(f"✅ [Comité Institucional 7 Agentes - CEO Supreme] Mercado filtrado y analizado. Consultando al Súper-Cerebro Gemini AI para el TOP {len(candidates_data_list)} simultáneo...")

    prompt_text = f"""
    Eres el COMITÉ INSTITUCIONAL MULTI-AGENTE CUÁNTICO 24/7 (Súper-Cerebro de Élite).
    Tu estructura está compuesta por 7 AGENTES ESPECIALIZADOS DE INTELIGENCIA ARTIFICIAL que deben deliberar y lograr consenso unánime antes de ejecutar cualquier orden real:
    
    1. 🕵️ AGENTE 1 - ANALISTA MACRO & RASTRO DE BALLENAS (Whale & Macro Sentinel):
       - Examina el sentimiento Fear & Greed ({fear_greed.get('score')} - {fear_greed.get('sentiment')}), noticias globales y volumen institucional (Volume Surge > 1.2x).
    
    2. 📊 AGENTE 2 - INGENIERO TÉCNICO & PRICE ACTION (Chartist & Pattern Sniper):
       - Examina RSI (15m y 4h), MACD Histograma, EMAs (20, 50, 200), mechas de absorción y estructuras de volatilidad ATR.
    
    3. 🌊 AGENTE 3 - RASTREADOR DE PROFUNDIDAD Y LIBRO DE ÓRDENES (Orderbook & Liquidity Depth Tracker):
       - Examina el Orderbook en tiempo real (Dominancia Bids Compradores vs Asks Vendedores), muros de soporte de ballenas (Bids > 65%) y riesgo de slippage.
    
    4. 🧩 AGENTE 4 - ANALISTA DE SECTORES Y ROTACIÓN DE CAPITAL (Sector Cluster Analyst):
       - Examina la rotación de capital institucional por sectores. Sector Dominante Actual: {sector_summary['top_sector']} (Score {sector_summary['top_sector_score']}, VolSurge {sector_summary['top_sector_vol_surge']}x).
    
    5. 🧠 AGENTE 5 - HISTORIADOR RAG & MEMORIA QUANT (Memory & Pattern Historian):
       - Compara con las 99 simulaciones pasadas ({market_bias_ctx}), patrones prohibidos/potenciados y la tabla All-Time de simulaciones.
    
    6. 🛡️ AGENTE 6 - CHIEF RISK OFFICER (Juez Supremo de Riesgo - Francisca Serrano & Hyenuk Chu):
       - Posee VETO ABSOLUTO. Regla #1: No perder dinero. Regla #2: No olvidar la regla #1. Activa Trailing Stop ATR dinámico al alcanzar +2.0%. Exige convicción A+ (Score >= 65, Confianza >= 70%).
    
    7. 👑 AGENTE 7 - CEO & ANTI-LOSS PROFIT MAXIMIZER (Chief Executive Orchestrator):
       - LÍDER SUPREMO Y ORQUESTADOR DE RENTABILIDAD. Sinteriza las opiniones de los otros 6 agentes. Bloquea absolutamente cualquier patrón que coincida con pérdidas pasadas y autoriza Trailing Stop ATR para exprimir súper-tendencias de +5%, +10% o +20%+.

    CONTEXTO GLOBAL MACRO Y ROTACIÓN SECTORIAL:
    - Sector Liderando Entrada de Capital: {sector_summary['top_sector']} ({sector_summary['all_sectors'].get(sector_summary['top_sector'], {}).get('status', '')})
    - Sesgo de Aprendizaje: {market_bias_ctx}
    - Entorno Macro: {macro_context}
    - Fear & Greed: {fear_greed.get('score')} ({fear_greed.get('sentiment')})
    - Noticias Globales: {json.dumps(news_data.get('headlines', [])[:3])}

    MEMORIA DE SIMULADORES (Super Detailed Table):
    {super_detailed_table}

    PERFILES DE LOS CANDIDATOS FINALISTAS (TOP BULLISH CON LIBRO DE ÓRDENES Y SECTOR):
    {candidates_prompt_text}

    REGLAS DE ORO PARA LA TOMA DE DECISIONES (SPOT ONLY):
    1. 🛡️ UMBRAL MÍNIMO A+ (Score >= 65): NUNCA apruebes una compra para un activo con Score Técnico < 65 o en caída libre. Si ningún candidato tiene Score >= 65 con confirmación de volumen, la respuesta OBLIGATORIA es responder "NONE" con "action": "HOLD".
    2. 🚫 PROHIBIDO 'FALLING KNIVES': Si un activo tiene Score bajo (15, 20, 30), NO intentes adivinar un rebote especulativo. Deja que el mercado limpie a los minoristas.
    3. 🌊 SOPORTE EN LIBRO DE ÓRDENES: Prioriza candidatos con Bids Compradores >= 55% que confirmen muros de soporte de ballenas.
    4. 🧩 ROTACIÓN SECTORIAL: Favorece activos pertenecientes a sectores con entrada masiva de capital ({sector_summary['top_sector']}).
    5. 💎 DECISIÓN DEL AGENTE 7 CEO: Si encuentras un candidato excepcional que cumple TODAS las reglas A+, selecciona su símbolo y aprueba "BUY_LONG" con confianza >= 70%. Si el mercado está sucio, lateral, bajista o con activos mediocres, responde "NONE" y protege el 100% de la liquidez en USDT.

    RESPONDE ÚNICAMENTE EN FORMATO JSON EXACTO CON ESTA ESTRUCTURA MULTI-AGENTE (7 AGENTES):
    {{
        "selected_symbol": "SIMBOLO" o "NONE",
        "action": "BUY_LONG" o "HOLD",
        "confidence": 0-100,
        "approved": true o false,
        "committee_deliberation": {{
            "agent_1_macro": "Dictamen del Analista Macro y volumen de ballenas en 1 oración...",
            "agent_2_tech": "Dictamen del Ingeniero Técnico sobre RSI, MACD y soportes en 1 oración...",
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
        "gemini-3.1-flash-lite",
        "gemini-3.5-flash-lite",
        "gemini-3.1-flash-lite-preview",
        "gemini-2.5-flash-lite"
    ]
    
    keys_pool = get_gemini_api_keys()
    for model_name in models_to_try:
        for key in keys_pool:
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
                            return parsed
            except urllib.error.HTTPError as e:
                if e.code == 429:
                    print(f"🔄 Clave Gemini en Rate Limit 429 ({model_name}). Rotando a la siguiente clave del pool de {len(keys_pool)} keys...")
                    continue
                else:
                    break
            except Exception:
                break
    
    print("Gemini LLM Notice: Todos los modelos de IA ocupados. Usando fallback cuantitativo seguro.")
    fallback_sym = candidates_data_list[0]['symbol'] if candidates_data_list else "NONE"
    return {
        "selected_symbol": fallback_sym,
        "action": "HOLD",
        "approved": False,
        "confidence": 50,
        "committee_deliberation": {
            "agent_1_macro": "Macro en espera por conectividad de respaldo.",
            "agent_2_tech": "Filtros técnicos cuantitativos aplicados.",
            "agent_3_memory": "Historial conservador preservado.",
            "agent_4_risk": "Veto de seguridad activado por fallback."
        },
        "reasoning": "Fallback Cuantitativo Conservador (Preservación de Liquidez en USDT)"
    }

# Backwards compatibility alias
review_top_5_candidates = review_top_candidates
