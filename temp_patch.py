import os

code_to_append = """

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
        candidates_prompt_text += f"\\nCANDIDATO: {sym} (Acción Cuantitativa Sugerida: {action})\\n"
        candidates_prompt_text += f"- Score Técnico: {score}/100\\n"
        candidates_prompt_text += f"- RSI 15M: {ind.get('rsi_15m')}, MACD: {ind.get('macd_hist_15m')}, Volume Surge: {ind.get('volume_surge_ratio')}\\n"
        candidates_prompt_text += f"- Tendencia 4H: {tech.get('macro_trend_4h')}\\n"
        candidates_prompt_text += f"- Historial 5M (4h): {pat}\\n"
        candidates_prompt_text += "------------------------------------"

    print(f"✅ [Comité Institucional] 100 Pares analizados. Consultando al Súper-Cerebro Gemini AI para el TOP {len(candidates_data_list)} simultáneo...")

    prompt_text = f\"\"\"
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
    3. SELECCIONA SOLO UN SÍMBOLO GANADOR. Si ninguno es seguro frente a la volatilidad macro actual, selecciona "NONE" y approved=false.

    RESPONDE ÚNICAMENTE EN FORMATO JSON EXACTO:
    {{
        "selected_symbol": "EL_SIMBOLO_GANADOR_EJ_BTCUSDT_O_NONE",
        "approved": true,
        "confidence": 95,
        "reasoning": "explicación concisa en español de por qué ganó sobre los demás",
        "action": "BUY_LONG"
    }}
    \"\"\"

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
"""

with open('llm_router.py', 'a', encoding='utf-8') as f:
    f.write(code_to_append)
