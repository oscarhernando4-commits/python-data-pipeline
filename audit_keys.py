import os
import json
import urllib.request
import urllib.error
import time

print("=" * 65)
print("🔍 AUDITORÍA DE CLAVES GEMINI API — PRUEBA REAL")
print("=" * 65)

# Recolectar todas las claves disponibles
keys_to_test = []
k1 = os.getenv("GEMINI_API_KEY", "")
if k1:
    keys_to_test.append(("GEMINI_API_KEY (Key_01)", k1))

for i in range(2, 21):
    name = f"GEMINI_API_KEY_{i:02d}"
    val = os.getenv(name, "") or os.getenv(f"GEMINI_API_KEY_{i}", "")
    if val:
        keys_to_test.append((f"GEMINI_API_KEY_{i:02d} (Key_{i:02d})", val))

print(f"Total claves encontradas: {len(keys_to_test)}")
print()

MODEL = "gemini-2.0-flash-lite"
PAYLOAD = json.dumps({
    "contents": [{"parts": [{"text": "Responde solo la palabra: OPERATIVO"}]}],
    "generationConfig": {"maxOutputTokens": 10, "temperature": 0.0}
}).encode("utf-8")

results = []
for label, key in keys_to_test:
    suffix = key[-8:] if len(key) >= 8 else key
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent?key={key}"
    try:
        req = urllib.request.Request(
            url, data=PAYLOAD,
            headers={"Content-Type": "application/json"}
        )
        with urllib.request.urlopen(req, timeout=12) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            text = data["candidates"][0]["content"]["parts"][0]["text"].strip()
            print(f"  ✅ {label} | Sufijo: ...{suffix} → OPERATIVO ({text[:20]})")
            results.append((label, "OK", suffix))
    except urllib.error.HTTPError as e:
        code = e.code
        body = ""
        try:
            body = e.read().decode("utf-8")[:120]
        except Exception:
            pass
        status = "CUOTA_AGOTADA" if code == 429 else f"ERROR_{code}"
        print(f"  ❌ {label} | Sufijo: ...{suffix} → {status} ({code})")
        if body:
            print(f"     Detalle: {body[:80]}")
        results.append((label, status, suffix))
    except Exception as ex:
        print(f"  ⚠️  {label} | Sufijo: ...{suffix} → EXCEPCION: {str(ex)[:60]}")
        results.append((label, "EXCEPTION", suffix))
    time.sleep(0.8)  # Pausa para no saturar RPM durante la auditoría

print()
print("=" * 65)
ok = [r for r in results if r[1] == "OK"]
fail = [r for r in results if r[1] != "OK"]
print(f"📊 RESUMEN: {len(ok)} ✅ OPERATIVAS | {len(fail)} ❌ CON PROBLEMAS")
print("=" * 65)
if fail:
    print("⚠️  Claves con problemas:")
    for label, status, suffix in fail:
        print(f"   · {label} → {status}")
if ok:
    print("✅ Claves operativas:")
    for label, status, suffix in ok:
        print(f"   · {label}")
print("=" * 65)
