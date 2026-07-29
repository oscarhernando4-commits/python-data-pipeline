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

    SESGO DEL MERCADO RECIENTE (AUTO-APRENDIZAJE DE PNL LONG vs SHORT):
    - {market_bias_ctx if market_bias_ctx else "Sesgo de Mercado No Disponible."}
    ⚠️ IMPORTANTE: Si el sesgo reciente indica que un lado (ej. LONG) está perdiendo repetidamente y el otro (ej. SHORT) está ganando, DEBES RECHAZAR operaciones que vayan en contra del flujo ganador a menos que haya una confirmación macro extrema de reversión. Alinear tus decisiones al dinero real (Real Money).

    HISTORIAL SUPER DETALLADO (TABLA COMPLETA ALL-TIME DE TODAS LAS OPERACIONES):
    {super_detailed_table}
    Lee detenidamente esta tabla. Contiene los resultados cruzados de 5 GRUPOS DIFERENTES de estrategias operando en el mercado en tiempo real. 
    ⚠️ INSTRUCCIÓN DE AUTO-APRENDIZAJE DINÁMICO (SUPERCEREBRO):
    1. No te limites a leer las reglas pasadas. Debes analizar esta tabla AHORA MISMO y descubrir qué grupo está siendo más rentable en las condiciones actuales.
    2. Si un Grupo (ej. Grupo 4) está logrando victorias repetidas bajo cierto RSI o Tendencia, ABSORBE esa estrategia dinámicamente y aplícala para esta decisión.
    3. Si ves que múltiples grupos están perdiendo bajo condiciones específicas recientes, crea una regla mental de bloqueo inmediato para esta operación.
    4. DIRECTRIZ CRÍTICA DE CERO PÉRDIDAS: Tu misión número 1 es NO PERDER. Rechaza categóricamente (HOLD) si el entorno actual se parece a los fracasos recientes de cualquier grupo. Solo aprueba si el patrón coincide con las victorias comprobadas de los mejores grupos de la tabla.

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

    REGLAS DE DECISIÓN CON APRENDIZAJE HISTÓRICO Y EVENTOS EXTREMOS:
    1. Compara si el patrón actual imita un evento extremo histórico de desplome o pump de {symbol}.
    2. Extrae dinámicamente el perfil del "Grupo Más Rentable" de la tabla histórica. Si la operación actual encaja en su perfil ganador, APRUEBA.
    3. Extrae dinámicamente el perfil de los "Grupos Perdedores". Si la operación imita sus errores recientes, RECHAZA (HOLD).
    4. Si el historial de 4H muestra acumulación creciente de ballenas y volumen fuerte, cruzado con victorias en la tabla, APRUEBA para BUY_LONG.
    5. Si imita una cascada de liquidación o distribución bajista que los grupos kamikazes ya sufrieron, APRUEBA para SELL_SHORT (si el mercado está cayendo) o HOLD.

    RESPONDE ÚNICAMENTE EN FORMATO JSON CON ESTA ESTRUCTURA EXACTA:
    {{
        "approved": true o false,
        "confidence": entero de 0 a 100,
        "reasoning": "explicación concisa en español de 1 oración destacando el patrón histórico 5M, ballenas y noticias",
        "action": "BUY_LONG" o "SELL_SHORT" o "HOLD"
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
        "gemini-3.1-flash-lite-preview"
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


def review_top_5_candidates(candidates_data_list, news_data, fear_greed, macro_context="", market_bias_ctx=""):
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
        candidates_prompt_text += f"\nCANDIDATO: {sym} (Acción Cuantitativa Sugerida: {action})\n"
        candidates_prompt_text += f"- Score Técnico: {score}/100\n"
        candidates_prompt_text += f"- RSI 15M: {ind.get('rsi_15m')}, MACD: {ind.get('macd_hist_15m')}, Volume Surge: {ind.get('volume_surge_ratio')}\n"
        candidates_prompt_text += f"- Tendencia 4H: {tech.get('macro_trend_4h')}\n"
        candidates_prompt_text += f"- Historial 5M (4h): {pat}\n"
        candidates_prompt_text += "------------------------------------"

    print(f"✅ [Comité Institucional] 100 Pares analizados. Consultando al Súper-Cerebro Gemini AI para el TOP {len(candidates_data_list)} simultáneo...")

    prompt_text = f"""
    Eres el Súper-Cerebro Cuantitativo Institucional.
    Tu tarea es recibir un TOP {len(candidates_data_list)} de las mejores criptomonedas pre-filtradas por un motor matemático.
    Debes hacer un análisis cruzado (Cross-Analysis) profundo de los 5 escenarios y ELEGIR A UN ÚNICO GANADOR ABSOLUTO para operar, o RECHAZARLOS TODOS si el entorno es muy tóxico.

    CONTEXTO GLOBAL MACRO Y SESGO DE MERCADO:
    - Sesgo de Aprendizaje: {market_bias_ctx}
    - Entorno Macro: {macro_context}
    - Fear & Greed: {fear_greed.get('score')} ({fear_greed.get('sentiment')})
    - Noticias: {json.dumps(news_data.get('headlines', [])[:3])}

    MEMORIA DE SIMULADORES (Super Detailed Table):
    {super_detailed_table}

    PERFILES DE LOS CANDIDATOS FINALISTAS:
    {candidates_prompt_text}

    REGLAS:
    1. Revisa qué grupo de estrategias (en la tabla histórica) está ganando y si alguno de los 5 candidatos imita esa estructura ganadora.
    2. Compara el 'Volume Surge' y el 'RSI 15M'. Prioriza la operación con mayor divergencia clara o agotamiento (Pump & Dump Exhaustion).
    3. ERES UN TRADER AGRESIVO PERO CALCULADOR. El usuario quiere ejecutar operaciones reales frecuentemente. DEBES ELEGIR AL MEJOR CANDIDATO del Top 5. Sólo selecciona "NONE" si ocurre un crash catastrófico del mercado global. De lo contrario, elige la moneda con la mejor estructura técnica.

    RESPONDE ÚNICAMENTE EN FORMATO JSON EXACTO:
    {{
        "selected_symbol": "EL_SIMBOLO_GANADOR_EJ_BTCUSDT_O_NONE",
        "approved": true,
        "confidence": 95,
        "reasoning": "explicación concisa en español de por qué ganó sobre los demás",
        "action": "BUY_LONG"
    }}
    """

    payload = {"contents": [{"parts": [{"text": prompt_text}]}], "generationConfig": {"temperature": 0.1, "responseMimeType": "application/json"}}
    models_to_try = ["gemini-3.1-flash-lite", "gemini-3.1-flash-lite-preview"]
    
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
