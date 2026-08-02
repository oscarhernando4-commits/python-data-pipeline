import os
import json
import urllib.request
import time

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

if not GEMINI_API_KEY:
    env_path = os.path.join(os.path.dirname(__file__), ".env")
    if os.path.exists(env_path):
        try:
            with open(env_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        k, v = line.split('=', 1)
                        if k.strip() == "GEMINI_API_KEY":
                            GEMINI_API_KEY = v.strip()
        except Exception:
            pass

def get_market_macro_context(symbol_analysis_map, fear_greed, news_headlines):
    """
    Uses Gemini Lite to perform a macro scan of ALL 30 cryptos and return a global context string.
    """
    if not GEMINI_API_KEY:
        return "Macro Analyst Offline (No API Key). Mercado evaluado solo cuantitativamente."

    # Prepare rich market summary to provide deep historical context
    market_summary = []
    bullish_count = 0
    bearish_count = 0
    
    try:
        import time_series_memory
    except ImportError:
        time_series_memory = None
    
    # Sort symbols by score to only include rich history for top 5 and bottom 5 (to save tokens)
    sorted_symbols = sorted(symbol_analysis_map.items(), key=lambda x: x[1].get("score", 50), reverse=True)
    symbols_to_detail = sorted_symbols[:5] + sorted_symbols[-5:] if len(sorted_symbols) > 10 else sorted_symbols
    detailed_syms = set([s[0] for s in symbols_to_detail])
    
    for sym, data in symbol_analysis_map.items():
        score = data.get("score", 50)
        trend = data.get("tech", {}).get("macro_trend_4h", "N/A")
        if score >= 60:
            bullish_count += 1
        elif score <= 40:
            bearish_count += 1
            
        history_str = ""
        if sym in detailed_syms and time_series_memory:
            hist = time_series_memory.get_multi_cycle_pattern_summary(sym)
            if hist:
                history_str = f" | HISTORIAL: {hist}"
                
        market_summary.append(f"[{sym}] Score: {score}/100, Tendencia: {trend}{history_str}")
        
    market_text = "\n".join(market_summary)
    
    prompt_text = f"""
    Eres el "Jefe de Riesgo Macro e Inteligencia Histórica" de un fondo cuantitativo.
    Tu objetivo es leer el estado general del mercado, correlacionar la historia reciente de los pares principales y emitir un REPORTE SÚPER DETALLADO.
    
    DATOS DEL MERCADO ACTUAL:
    - Índice Fear & Greed: {fear_greed.get('score')} ({fear_greed.get('sentiment')})
    - Monedas Fuertes (Score >= 60): {bullish_count}
    - Monedas Débiles (Score <= 40): {bearish_count}
    - Noticias Recientes: {json.dumps(news_headlines[:5])}
    
    ESTADO DE LAS MONEDAS (Contexto en Tiempo Real e Historial 4H):
    {market_text}
    
    REGLAS DE ANÁLISIS SÚPER DETALLADO:
    1. Analiza profundamente si el mercado está correlacionado (¿están todas cayendo juntas o es mixto?).
    2. Usa el "HISTORIAL" de las monedas principales para identificar si estamos en fase de acumulación de ballenas, distribución o pánico institucional.
    3. Identifica riesgos sistémicos ocultos (ej. Bitcoin cae mientras altcoins suben = trampa).
    4. Escribe un análisis RICO Y DETALLADO de 2 a 3 párrafos completos que sirva como "Mapa de Guerra" para el Agente Ejecutor que operará la moneda Top 1.
    5. Termina con un Veredicto Global (Ej: "VEREDICTO: Entorno favorable solo para Shorts rápidos").
    """
    
    payload = {
        "contents": [{"parts": [{"text": prompt_text}]}],
        "generationConfig": {"temperature": 0.3, "maxOutputTokens": 600}
    }
    
    # We prioritize gemini-3.1-flash-lite for macro sweep
    lite_models = [
        "gemini-3.1-flash-lite",
        "gemini-3.1-flash-lite-preview",
        "gemini-2.0-flash-lite",
        "gemini-2.0-flash",
        "gemini-1.5-flash"
    ]
    
    print(f"🕵️ [Macro Analyst Lite] Analizando el contexto global de {len(symbol_analysis_map)} criptomonedas...")
    
    for model_name in lite_models:
        for attempt in range(2):
            try:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={GEMINI_API_KEY}"
                req = urllib.request.Request(url, data=json.dumps(payload).encode('utf-8'), headers={'Content-Type': 'application/json'})
                with urllib.request.urlopen(req, timeout=10) as response:
                    res_data = json.loads(response.read().decode('utf-8'))
                    if "candidates" in res_data and len(res_data["candidates"]) > 0:
                        text_res = res_data["candidates"][0]["content"]["parts"][0]["text"].strip()
                        print(f"📊 [Macro Contexto ({model_name})]: {text_res}")
                        return text_res
            except Exception as e:
                print(f"💡 Error conectando a {model_name} (intento {attempt+1}/2): {e}")
                time.sleep(2)
        print(f"⏭️ Agotados intentos para {model_name}. Cambiando a modelo de respaldo...")
            
    return "Macro Analyst Fallback: Alta volatilidad detectada (Modelos IA Ocupados)."
