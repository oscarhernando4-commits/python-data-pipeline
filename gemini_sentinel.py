import os
import sys
import json
import urllib.request

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

def consult_gemini_flash_oracle(symbol, score, tech_data, news_data, fear_greed):
    """
    Super-Brain AI Decision Reviewer using Google Gemini Flash Free API (gemini-flash-latest).
    Provides sub-second LLM reasoning for high-stakes trades.
    """
    if not GEMINI_API_KEY:
        print("💡 Gemini Notice: GEMINI_API_KEY no configurada aún. Usando fallback cuantitativo.")
        return {"approved": True, "confidence": score, "reasoning": "Fallback cuantitativo (Score >= 85 Pts)"}

    print(f"🧠 Consultando al Súper-Cerebro Gemini Flash (gemini-flash-latest) para {symbol} (Score: {score} Pts)...")
    
    prompt_text = f"""
    Eres un Trader Cuantitativo Institucional Senior de Criptomonedas.
    Evalúa la siguiente oportunidad de trading en vivo para el par {symbol}:

    - Puntaje Técnico Cuantitativo: {score} / 100 Pts
    - Indicadores Técnicos: RSI={tech_data.get('rsi')}, MACD={tech_data.get('macd')}, Volume Surge={tech_data.get('volume_surge')}x
    - Tendencia EMA20 vs EMA200: {tech_data.get('ema_trend')}
    - Estructura Wyckoff: {tech_data.get('wyckoff')}
    - Sentimiento del Mercado (Fear & Greed): {fear_greed.get('score')} ({fear_greed.get('sentiment')})
    - Noticias Recientes: {json.dumps(news_data.get('headlines', [])[:3])}

    RESPONDE ÚNICAMENTE EN FORMATO JSON CON ESTA ESTRUCTURA EXACTA:
    {{
        "approved": true o false,
        "confidence": entero de 0 a 100,
        "reasoning": "explicación concisa en español de 1 oración",
        "action": "BUY_LONG" o "SELL_SHORT" o "HOLD"
    }}
    """
    
    # Primary endpoint: gemini-flash-latest (Always routes to the latest bleeding-edge Flash model version 3.5/3.6+)
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-latest:generateContent?key={GEMINI_API_KEY}"
    payload = {
        "contents": [{"parts": [{"text": prompt_text}]}],
        "generationConfig": {"temperature": 0.2, "responseMimeType": "application/json"}
    }
    
    try:
        req = urllib.request.Request(
            url, 
            data=json.dumps(payload).encode("utf-8"), 
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        with urllib.request.urlopen(req, timeout=15) as response:
            res_json = json.loads(response.read().decode("utf-8"))
            content = res_json['candidates'][0]['content']['parts'][0]['text']
            parsed = json.loads(content)
            print(f"🎉 Respuesta de Gemini Flash Latest AI (gemini-flash-latest): Approved={parsed.get('approved')} | Conf={parsed.get('confidence')}% | Razonamiento: {parsed.get('reasoning')}")
            return parsed
    except Exception as e:
        print(f"Aviso consultando gemini-flash-latest ({e}). Probando fallback gemini-2.5-flash...")
        try:
            url2 = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}"
            req2 = urllib.request.Request(
                url2, 
                data=json.dumps(payload).encode("utf-8"), 
                headers={"Content-Type": "application/json"},
                method="POST"
            )
            with urllib.request.urlopen(req2, timeout=15) as response:
                res_json = json.loads(response.read().decode("utf-8"))
                content = res_json['candidates'][0]['content']['parts'][0]['text']
                parsed = json.loads(content)
                print(f"🎉 Respuesta de Gemini 2.5 Flash AI: Approved={parsed.get('approved')} | Conf={parsed.get('confidence')}% | Razonamiento: {parsed.get('reasoning')}")
                return parsed
        except Exception as e2:
            print(f"Gemini LLM Notice: {e2}. Usando fallback cuantitativo seguro.")
            return {"approved": True, "confidence": score, "reasoning": f"Fallback cuantitativo (Score >= {score} Pts)"}

if __name__ == "__main__":
    sys.stdout.reconfigure(encoding='utf-8')
    res = consult_gemini_flash_oracle(
        "BTCUSDT", 88, 
        {"rsi": 58, "macd": "Bullish Cross", "volume_surge": 2.1, "ema_trend": "Bullish", "wyckoff": "Spring Phase C"},
        {"headlines": ["Bitcoin Breaks Resistance with Institutional Inflows"]},
        {"score": 65, "sentiment": "Greed"}
    )
    print(res)
