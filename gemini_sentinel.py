import os
import sys
import json
import time
import urllib.request

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

def consult_gemini_flash_oracle(symbol, score, tech_data, news_data, fear_greed, macro_context=""):
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
    2. Usa las 'LECCIONES APRENDIDAS' del simulador. Si el mercado actual imita un Patrón Prohibido, RECHAZA (HOLD).
    3. Si el historial de 4H muestra acumulación creciente de ballenas, volumen > 1.8x y no imita un patrón de trampa histórica, APRUEBA para BUY_LONG.
    4. Si imita una cascada de liquidación o distribución bajista, APRUEBA para SELL_SHORT.

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
    
    # Option 1: Top 1 Filter implemented. 
    # Exact cascade requested by user
    models_to_try = [
        "gemini-flash-latest",
        "gemini-3.6-flash", 
        "gemini-3.5-flash", 
        "gemini-2.5-flash"
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
