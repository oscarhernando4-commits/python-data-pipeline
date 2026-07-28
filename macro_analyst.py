import os
import json
import urllib.request
import time

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

def get_market_macro_context(symbol_analysis_map, fear_greed, news_headlines):
    """
    Uses Gemini Lite to perform a macro scan of ALL 30 cryptos and return a global context string.
    """
    if not GEMINI_API_KEY:
        return "Macro Analyst Offline (No API Key). Mercado evaluado solo cuantitativamente."

    # Prepare compact market summary to save tokens
    market_summary = []
    bullish_count = 0
    bearish_count = 0
    
    for sym, data in symbol_analysis_map.items():
        score = data.get("score", 50)
        trend = data.get("tech", {}).get("macro_trend_4h", "N/A")
        if score >= 60:
            bullish_count += 1
        elif score <= 40:
            bearish_count += 1
            
        market_summary.append(f"{sym}: Score {score}, {trend}")
        
    market_text = "\n".join(market_summary)
    
    prompt_text = f"""
    Eres el "Macro Analista de Riesgo" de un fondo de inversión institucional.
    Tu objetivo es leer el estado general del mercado de criptomonedas y emitir un veredicto de 2 a 3 oraciones sobre el RIESGO GLOBAL.
    
    DATOS DEL MERCADO ACTUAL:
    - Índice Fear & Greed: {fear_greed.get('score')} ({fear_greed.get('sentiment')})
    - Monedas Fuertes (Score >= 60): {bullish_count}
    - Monedas Débiles (Score <= 40): {bearish_count}
    - Noticias Recientes: {json.dumps(news_headlines[:3])}
    
    ESTADO DE LAS MONEDAS (Resumen 4H):
    {market_text}
    
    REGLAS DE SALIDA:
    1. Identifica si el mercado está correlacionado al alza, a la baja, o es mixto.
    2. Identifica si hay riesgo sistémico inminente.
    3. Responde SOLAMENTE con 2 a 3 oraciones contundentes en español detallando el contexto macro, sin formato especial, directo al grano.
    """
    
    payload = {
        "contents": [{"parts": [{"text": prompt_text}]}],
        "generationConfig": {"temperature": 0.2, "maxOutputTokens": 200}
    }
    
    # We use lite for macro sweep to save standard flash quota
    model_name = "gemini-2.5-flash-lite"
    
    print(f"🕵️ [Macro Analyst Lite] Analizando el contexto global de {len(symbol_analysis_map)} criptomonedas...")
    
    for attempt in range(2):
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={GEMINI_API_KEY}"
            req = urllib.request.Request(url, data=json.dumps(payload).encode('utf-8'), headers={'Content-Type': 'application/json'})
            with urllib.request.urlopen(req, timeout=10) as response:
                res_data = json.loads(response.read().decode('utf-8'))
                if "candidates" in res_data and len(res_data["candidates"]) > 0:
                    text_res = res_data["candidates"][0]["content"]["parts"][0]["text"].strip()
                    print(f"📊 [Macro Contexto]: {text_res}")
                    return text_res
        except Exception as e:
            time.sleep(2)
            
    print("⚠️ [Macro Analyst Lite] Falló al obtener contexto. Usando fallback.")
    return "El mercado se encuentra en un estado indeterminado debido a fallos de conectividad con el oráculo macro. Precaución."
