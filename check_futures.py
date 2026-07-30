import json
import api_connector
import sys
import time
import hmac
import hashlib
import requests
from urllib.parse import urlencode

sys.stdout.reconfigure(encoding='utf-8')

print("=== VERIFICANDO POSICIONES ACTIVAS EN FUTUROS (CON PROXY) ===")

try:
    timestamp = int(time.time() * 1000)
    params = {"timestamp": timestamp}
    query_string = urlencode(params)
    signature = hmac.new(api_connector.API_SECRET.encode("utf-8"), query_string.encode("utf-8"), hashlib.sha256).hexdigest()
    params["signature"] = signature
    headers = {"X-MBX-APIKEY": api_connector.API_KEY}
    
    # WE MUST USE PROXY HERE OR GITHUB ACTIONS IP GETS BLOCKED!
    fapi_url = "https://fapi.binance.com"
    res = requests.get(f"{fapi_url}/fapi/v2/positionRisk", headers=headers, params=params, proxies=api_connector.PROXIES, timeout=10)
    
    positions = res.json()
    active = [p for p in positions if float(p["positionAmt"]) != 0.0]
    
    if not active:
        print("❌ No hay ninguna posición abierta en Futuros.")
        print(f"RAW RES: {json.dumps(positions[:2])}") # Print first two just to see
    else:
        print("✅ POSICIONES ACTIVAS ENCONTRADAS:")
        for p in active:
            print(f"- Símbolo: {p['symbol']}")
            print(f"- Tamaño: {p['positionAmt']} (Negativo = SHORT)")
            print(f"- Precio de Entrada: {p['entryPrice']}")
            print(f"- PnL No Realizado: {p['unRealizedProfit']} USDT")
            print(f"- Margen Aislado: {p['isolatedMargin']} USDT")
            print("-------------------------------------------------")
            
except Exception as e:
    print(f"Error: {e}")
