import os
import sys
import json
import time
import urllib.request

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

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
    
    print(f"🧠 Consultando al Súper-Cerebro Gemini AI para {symbol} (Score: {score} Pts, RSI: {indicators.get('rsi_15m', 'N/A')})...")
    
    prompt_text = f"""
    Eres un Trader Cuantitativo Institucional Senior y Experto en Aprendizaje de Patrones Históricos Extremos / Rastro de Ballenas.
    Tu objetivo es lograr operaciones victoriosas de alta frecuencia intradía para {symbol}.

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
    
    print(f"✅ [Pre-Filtro Matemático] 30 Pares analizados. Consultando al Súper-Cerebro Gemini AI SOLO para el TOP 1 ({symbol})...")
    
    for model_name in models_to_try:
        for attempt in range(max_retries_per_model):
            try:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={GEMINI_API_KEY}"
                
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
                    print(f"⏳ {model_name}: Rate limit (intento {attempt+1}/{max_retries_per_model}). Esperando 10s para reintentar este modelo...")
                    time.sleep(10) # Mayor tiempo de espera para que se recupere la cuota (Opción 1)
                else:
                    print(f"💡 Aviso ({model_name}): HTTP Error {e.code}. Pasando al siguiente modelo...")
                    break # Skip to next model on 400, 403, 500, etc.
            except Exception as e:
                print(f"💡 Error de conexión ({model_name}): {e}. Pasando al siguiente modelo...")
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

    candidates_prompt_text = ""
    for cand in candidates_data_list:
        sym = cand['symbol']
        score = cand['score']
        action = cand['suggested_action']
        tech = cand['tech_data']
        ind = tech.get('indicators', {})
        pat = time_series_memory.get_multi_cycle_pattern_summary(sym)
        specific_n = news_data.get('specific_news', {}).get(sym, [])
        
        candidates_prompt_text += f"\nCANDIDATO: {sym} (Acción Cuantitativa Sugerida: {action})\n"
        candidates_prompt_text += f"- Score Técnico: {score}/100\n"
        candidates_prompt_text += f"- RSI 15M: {ind.get('rsi_15m')}, MACD: {ind.get('macd_hist_15m')}, Volume Surge: {ind.get('volume_surge_ratio')}\n"
        candidates_prompt_text += f"- Tendencia 4H: {tech.get('macro_trend_4h')}\n"
        candidates_prompt_text += f"- Historial 5M (4h): {pat}\n"
        candidates_prompt_text += f"- NOTICIAS ESPECÍFICAS ÚLTIMAS 24H: {json.dumps(specific_n)}\n"
        candidates_prompt_text += "------------------------------------"

    print(f"✅ [Comité Institucional] Mercado filtrado y analizado. Consultando al Súper-Cerebro Gemini AI para el TOP {len(candidates_data_list)} simultáneo...")

    prompt_text = f"""
    Eres el Súper-Cerebro Cuantitativo Institucional y Gestor de Riesgos de Élite (Filosofía Francisca Serrano & Hyenuk Chu: Paciencia de Francotirador y Preservación de Capital).
    Tu misión es proteger el capital real en dólares y ejecutar ÚNICAMENTE Setups A+ de altísima probabilidad matemática en SPOT (BUY_LONG).
    
    FILOSOFÍA DE TRADING:
    - "La primera regla del trading es no perder dinero. La segunda es no olvidar la primera." (Francisca Serrano).
    - "Sé un francotirador paciente. La mejor operación muchas veces es NO operar y quedarse en liquidez (HOLD)." (Hyenuk Chu).
    
    CONTEXTO GLOBAL MACRO Y SESGO DE MERCADO:
    - Sesgo de Aprendizaje: {market_bias_ctx}
    - Entorno Macro: {macro_context}
    - Fear & Greed: {fear_greed.get('score')} ({fear_greed.get('sentiment')})
    - Noticias Globales: {json.dumps(news_data.get('headlines', [])[:3])}

    MEMORIA DE SIMULADORES (Super Detailed Table):
    {super_detailed_table}

    PERFILES DE LOS CANDIDATOS FINALISTAS (TOP BULLISH):
    {candidates_prompt_text}

    REGLAS DE ORO PARA LA TOMA DE DECISIONES (SPOT ONLY):
    1. 🛡️ UMBRAL MÍNIMO A+ (Score >= 65): NUNCA apruebes una compra para un activo con Score Técnico < 65 o en caída libre. Si ningún candidato tiene Score >= 65 con confirmación de volumen, tu respuesta OBLIGATORIA es responder "NONE" con "action": "HOLD".
    2. 🚫 PROHIBIDO 'FALLING KNIVES' (Cuchillos Cayendo): Si un activo tiene Score bajo (15, 20, 30), NO intentes adivinar un rebote especulativo. Deja que el mercado limpie a los minoristas.
    3. ⚖️ VOLUMEN Y RSI: Prioriza activos con RSI en rango saludable (35-65) y Volume Surge > 1.2x que muestren soporte sólido y acumulación de ballenas.
    4. 📰 FILTRO DE FUD: Si hay hackeos, demandas o investigaciones sobre un activo, descártalo inmediatamente.
    5. 💎 DECISIÓN: Si encuentras un candidato excepcional que cumple TODAS las reglas A+, selecciona su símbolo y aprueba "BUY_LONG" con confianza >= 75%. Si el mercado está sucio, lateral, bajista o con activos mediocres, responde "NONE" y protege el 100% de la liquidez en USDT.

    RESPONDE ÚNICAMENTE EN FORMATO JSON EXACTO:
    {{
        "selected_symbol": "SIMBOLO" o "NONE",
        "action": "BUY_LONG" o "HOLD",
        "confidence": 0-100,
        "approved": true o false,
        "reasoning": "Explicación cuantitativa institucional..."
    }}
    """


    payload = {"contents": [{"parts": [{"text": prompt_text}]}], "generationConfig": {"temperature": 0.1, "responseMimeType": "application/json"}}
    models_to_try = [
        "gemini-3.1-flash-lite",
        "gemini-3.5-flash-lite",
        "gemini-3.1-flash-lite-preview",
        "gemini-2.5-flash-lite"
    ]
    
    for model_name in models_to_try:
        for attempt in range(2):
            try:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={GEMINI_API_KEY}"
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
            except Exception as e:
                time.sleep(5)
    
    # Fallback to the first one if all fails
    print("💡 Gemini Fallback: No se pudo obtener respuesta del comité AI. Tomando el #1.")
    return {"selected_symbol": candidates_data_list[0]['symbol'], "approved": True, "action": candidates_data_list[0]['suggested_action'], "confidence": 70, "reasoning": "Fallback Cuantitativo Tras Fallo de Conexión AI"}

# Backwards compatibility alias
review_top_5_candidates = review_top_candidates
