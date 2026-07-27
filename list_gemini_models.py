import urllib.request
import json

key = "AIzaSyDPEcjMraRyLC7o0LgjdKw65emfieZZPOM"
url = f"https://generativelanguage.googleapis.com/v1beta/models?key={key}"

try:
    req = urllib.request.Request(url)
    with urllib.request.urlopen(req) as res:
        data = json.loads(res.read().decode())
        print("Modelos disponibles en tu API Key:")
        for m in data.get("models", []):
            if "generateContent" in m.get("supportedGenerationMethods", []):
                print(f" - {m['name']}")
except Exception as e:
    print(f"Error listando modelos: {e}")
