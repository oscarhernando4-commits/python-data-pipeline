import os
import urllib.request
import json
import sys

def test_models():
    sys.stdout.reconfigure(encoding='utf-8')
    api_key = "AIzaSyDPEcjMraRyLC7o0LgjdKw65emfieZZPOM"
    if not api_key:
        print("Error: GEMINI_API_KEY no encontrada.")
        return

    models = [
        "gemini-flash-latest",
        "gemini-3.6-flash",
        "gemini-3.5-flash",
        "gemini-2.5-flash",
        "gemini-1.5-flash" # The official baseline for comparison
    ]
    
    payload = {
        "contents": [{"parts": [{"text": "Hola"}]}],
        "generationConfig": {"maxOutputTokens": 10}
    }
    
    for model in models:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
        try:
            req = urllib.request.Request(url, data=json.dumps(payload).encode('utf-8'), headers={'Content-Type': 'application/json'})
            with urllib.request.urlopen(req, timeout=10) as response:
                print(f"✅ Modelo: '{model}' -> FUNCIONA CORRECTAMENTE (Código 200)")
        except urllib.error.HTTPError as e:
            if e.code == 404:
                print(f"❌ Modelo: '{model}' -> NO EXISTE EN GOOGLE (Error 404 Not Found)")
            elif e.code == 429:
                print(f"⏳ Modelo: '{model}' -> EXISTE, PERO SIN SALDO (Error 429 Rate Limit)")
            elif e.code == 400:
                print(f"❌ Modelo: '{model}' -> ERROR DE FORMATO (Error 400 Bad Request)")
            else:
                print(f"⚠️ Modelo: '{model}' -> ERROR DESCONOCIDO (Código {e.code})")
        except Exception as e:
            print(f"⚠️ Modelo: '{model}' -> FALLO DE CONEXIÓN ({e})")

if __name__ == "__main__":
    test_models()
