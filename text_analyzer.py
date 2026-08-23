import os
import json
import urllib.request
import time

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

def get_market_macro_context(symbol_analysis_map, fear_greed, news_headlines, top_candidates=None):
    """
    Uses Gemini Lite to perform a macro scan of ALL cryptos and return a global context string,
    fully synchronized with the Top 15 Finalists ranked by Ground-Zero confluence.
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
    
    # Use top_candidates order if provided to guarantee 100% synchronization
    if top_candidates:
        detailed_syms = set([c["symbol"] for c in top_candidates[:10]])
        top_list_text = []
        for rank_idx, c in enumerate(top_candidates[:15], 1):
            sym = c["symbol"]
            score = c.get("score", 50)
            data = symbol_analysis_map.get(sym, {})
            trend = data.get("tech", {}).get("macro_trend_4h", "N/A")
            fii = data.get("tech", {}).get("mtf_analysis", {}).get("fii_score", 0)
            vol_s = data.get("tech", {}).get("indicators", {}).get("volume_surge_ratio", 1.0)
            history_str = ""
            if time_series_memory:
                hist = time_series_memory.get_multi_cycle_pattern_summary(sym)
                if hist:
                    history_str = f" | HISTORIAL: {hist}"
            top_list_text.append(f"  #{rank_idx} [{sym}] Score: {score}/100, FII: {fii}/100, VolSurge: {vol_s:.2f}x, Tendencia 4H: {trend}{history_str}")
        candidates_section = "TOP 15 FINALISTAS DEL MERCADO (Ordenados por Confluencia Ground-Zero):\n" + "\n".join(top_list_text)
    else:
        detailed_syms = set()
        candidates_section = ""

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
        
    market_text = "\n".join(market_summary[:30])  # Sample first 30 to stay within token budget
    
    prompt_text = f"""
    Eres el "Jefe de Riesgo Macro e Inteligencia Histórica" de un fondo cuantitativo.
    Tu objetivo es leer el estado general del mercado, correlacionar la historia reciente de los pares principales y emitir un REPORTE SÚPER DETALLADO.
    
    DATOS DEL MERCADO ACTUAL:
    - Índice Fear & Greed: {fear_greed.get('score')} ({fear_greed.get('sentiment')})
    - Monedas Fuertes (Score >= 60): {bullish_count}
    - Monedas Débiles (Score <= 40): {bearish_count}
    - Noticias Recientes: {json.dumps(news_headlines[:5])}
    
    {candidates_section}
    
    ESTADO GENERAL DEL MERCADO:
    {market_text}
    
    REGLAS DE ANÁLISIS SÚPER DETALLADO:
    1. Analiza profundamente si el mercado está correlacionado (¿están todas cayendo juntas o es mixto?).
    2. Evalúa los TOP 15 FINALISTAS en su orden exacto (#1, #2, #3...) usando el historial para identificar acumulación o distribución de ballenas.
    3. Identifica riesgos sistémicos ocultos (ej. Bitcoin cae mientras altcoins suben = trampa).
    4. Escribe un análisis RICO Y DETALLADO de 2 a 3 párrafos completos que sirva como "Mapa de Guerra" para el Comité de Ejecución.
    5. Termina con un Veredicto Global (Ej: "VEREDICTO: Favorable para scalp en líderes de rotación").
    """
    
    payload = {
        "contents": [{"parts": [{"text": prompt_text}]}],
        "generationConfig": {"temperature": 0.3, "maxOutputTokens": 600}
    }
    
    import llm_router
    keys_pool = llm_router.get_gemini_api_keys()
    if not keys_pool or keys_pool == [""]:
        return "Macro Analyst Offline (No API Key). Mercado evaluado solo cuantitativamente."

    lite_models = [
        "gemini-3.1-flash-lite"
    ]
    
    print(f"🕵️ [Macro Analyst Lite] Analizando el contexto global de {len(symbol_analysis_map)} criptomonedas (Pool de {len(keys_pool)} Claves)...")
    
    for model_name in lite_models:
        rr_idx = llm_router._get_key_index()
        keys_rotated = [keys_pool[(i + rr_idx) % len(keys_pool)] for i in range(len(keys_pool))]
        for key in keys_rotated:
            key_label = llm_router.get_key_label(key, keys_pool)
            try:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={key}"
                req = urllib.request.Request(url, data=json.dumps(payload).encode('utf-8'), headers={'Content-Type': 'application/json'})
                with urllib.request.urlopen(req, timeout=10) as response:
                    res_data = json.loads(response.read().decode('utf-8'))
                    if "candidates" in res_data and len(res_data["candidates"]) > 0:
                        text_res = res_data["candidates"][0]["content"]["parts"][0]["text"].strip()
                        llm_router._advance_key_index(key_label)  # Track successful usage
                        print(f"📊 [Macro Contexto ({model_name})]: {text_res}")
                        return text_res
            except urllib.error.HTTPError as e:
                if e.code == 429:
                    llm_router.mark_key_in_cooldown(key)
                continue
            except Exception:
                continue
            
    return "Macro Analyst Fallback: Alta volatilidad detectada (Modelos IA Ocupados)."
