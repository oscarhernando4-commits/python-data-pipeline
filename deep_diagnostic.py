import sys
import time
import hmac
import hashlib
import urllib.parse
import requests
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

sys.stdout.reconfigure(encoding='utf-8')

import api_connector

API_KEY = api_connector.API_KEY
API_SECRET = api_connector.API_SECRET
BASE_URL = api_connector.BASE_URL
FAPI_URL = api_connector.FAPI_URL
get_proxy = api_connector.get_proxy

def deep_diagnostic():
    print("="*60)
    print("🚀 INICIANDO DIAGNÓSTICO PROFUNDO DE LA CUENTA REAL DE BINANCE 🚀")
    print("="*60)

    # 1. Check IP Configuration
    print("\n[1/5] Verificando Red e IP Pública...")
    try:
        ip_res = requests.get("https://api.ipify.org?format=json", proxies=get_proxy(), timeout=10)
        print(f"✅ IP de salida: {ip_res.json().get('ip')}")
        geo_res = requests.get(f"https://ipapi.co/{ip_res.json().get('ip')}/json/", timeout=10)
        geo = geo_res.json()
        print(f"🌍 Ubicación de la IP: {geo.get('city')}, {geo.get('country_name')}")
        if geo.get('country_name') == "United States":
            print("❌ ALERTA CRÍTICA: IP detectada en USA. Binance puede bloquear operaciones.")
        else:
            print("✅ Ubicación de red segura para operar en Binance Global.")
    except Exception as e:
        print(f"❌ Error verificando IP: {e}")

    # 2. Ping API Binance
    print("\n[2/5] Ping a los servidores de Binance...")
    try:
        ping = requests.get(f"{BASE_URL}/api/v3/ping", proxies=get_proxy(), timeout=5)
        if ping.status_code == 200:
            print("✅ Binance API Spot: ONLINE")
        else:
            print(f"❌ Binance API Spot Error: {ping.status_code}")
    except Exception as e:
        print(f"❌ Error de conexión: {e}")

    # 3. Check Account Status (Spot)
    print("\n[3/5] Verificando Estado de Cuenta Real (SPOT)...")
    try:
        timestamp = int(time.time() * 1000)
        params = {"timestamp": timestamp}
        query_string = urllib.parse.urlencode(params)
        signature = hmac.new(API_SECRET.encode("utf-8"), query_string.encode("utf-8"), hashlib.sha256).hexdigest()
        params["signature"] = signature
        headers = {"X-MBX-APIKEY": API_KEY}
        
        account_res = requests.get(f"{BASE_URL}/api/v3/account", headers=headers, params=params, proxies=get_proxy(), timeout=10)
        if account_res.status_code == 200:
            acc_data = account_res.json()
            if acc_data.get("canTrade"):
                print("✅ Permiso de Trading: ACTIVADO")
            else:
                print("❌ Permiso de Trading: BLOQUEADO POR BINANCE")
            
            balances = acc_data.get("balances", [])
            usdt_bal = next((b for b in balances if b["asset"] == "USDT"), None)
            btc_bal = next((b for b in balances if b["asset"] == "BTC"), None)
            print(f"✅ Balance USDT: {usdt_bal.get('free') if usdt_bal else '0.00'}")
            print(f"✅ Balance BTC: {btc_bal.get('free') if btc_bal else '0.00'}")
        else:
            print(f"❌ Error cargando cuenta: {account_res.status_code} - {account_res.text}")
    except Exception as e:
        print(f"❌ Error API: {e}")

    # 4. Check API Key Permissions Status (Futures)
    print("\n[4/5] Verificando Estado de Cuenta Real (FUTURES)...")
    try:
        FAPI_URL = "https://fapi.binance.com"
        timestamp = int(time.time() * 1000)
        params = {"timestamp": timestamp}
        query_string = urllib.parse.urlencode(params)
        signature = hmac.new(API_SECRET.encode("utf-8"), query_string.encode("utf-8"), hashlib.sha256).hexdigest()
        params["signature"] = signature
        headers = {"X-MBX-APIKEY": API_KEY}
        
        fut_res = requests.get(f"{FAPI_URL}/fapi/v2/account", headers=headers, params=params, proxies=get_proxy(), timeout=10)
        if fut_res.status_code == 200:
            fut_data = fut_res.json()
            print("✅ Permiso de Trading Futuros: ACTIVADO")
            print(f"✅ Balance USDT Futuros: {fut_data.get('availableBalance', '0.00')}")
        else:
            print(f"❌ Error Futuros (Código {fut_res.status_code}): {fut_res.text}")
            if "API-key format invalid" in fut_res.text or "-2015" in fut_res.text:
                print("⚠️ NOTA: Los futuros pueden estar deshabilitados o las llaves API no tienen permiso de futuros.")
    except Exception as e:
        print(f"❌ Error API Futuros: {e}")

    # 5. Check Log of recent orders to see if any failed
    print("\n[5/5] Analizando Órdenes de hoy (Bloqueadas / Rechazadas)...")
    try:
        timestamp = int(time.time() * 1000)
        params = {"symbol": "BTCUSDT", "timestamp": timestamp}
        query_string = urllib.parse.urlencode(params)
        signature = hmac.new(API_SECRET.encode("utf-8"), query_string.encode("utf-8"), hashlib.sha256).hexdigest()
        params["signature"] = signature
        
        orders_res = requests.get(f"{BASE_URL}/api/v3/allOrders", headers=headers, params=params, proxies=get_proxy(), timeout=10)
        if orders_res.status_code == 200:
            orders = orders_res.json()
            if len(orders) > 0:
                print(f"✅ Se encontraron {len(orders)} órdenes históricas de BTCUSDT.")
                recent = orders[-3:]
                for o in recent:
                    time_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(o["time"] / 1000))
                    print(f"   -> [{time_str}] {o['side']} {o['origQty']} a ${o.get('price')} | Estado: {o['status']}")
                
                rejected = [o for o in orders if o["status"] == "REJECTED" or o["status"] == "EXPIRED"]
                if len(rejected) > 0:
                    print(f"⚠️ Atención: Tienes {len(rejected)} órdenes rechazadas o expiradas históricamente.")
                else:
                    print("✅ Ninguna orden reciente ha sido RECHAZADA (No hay bloqueos de la API).")
            else:
                print("ℹ️ No hay historial de órdenes de BTCUSDT aún.")
        else:
            print(f"❌ Error cargando órdenes: {orders_res.text}")
    except Exception as e:
        print(f"❌ Error en historial de órdenes: {e}")

    print("\n" + "="*60)
    print("🎯 DIAGNÓSTICO PROFUNDO COMPLETADO")
    print("="*60)

if __name__ == "__main__":
    deep_diagnostic()
