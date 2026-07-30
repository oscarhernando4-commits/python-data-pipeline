import os
import sys
import time
import hmac
import hashlib
import requests
from urllib.parse import urlencode

API_KEY = os.getenv("BINANCE_REAL_API_KEY", "")
API_SECRET = os.getenv("BINANCE_REAL_API_SECRET", "")

BASE_URL = "https://api.binance.com"

def get_account_balances():
    timestamp = int(time.time() * 1000)
    params = {"timestamp": timestamp}
    query_string = urlencode(params)
    signature = hmac.new(API_SECRET.encode("utf-8"), query_string.encode("utf-8"), hashlib.sha256).hexdigest()
    params["signature"] = signature
    headers = {"X-MBX-APIKEY": API_KEY}
    
    url = f"{BASE_URL}/api/v3/account"
    try:
        res = requests.get(url, headers=headers, params=params, timeout=10)
        if res.status_code == 200:
            return res.json().get("balances", [])
        return []
    except Exception as e:
        print(f"Error fetching balances: {e}")
        return []

def check_and_buy_bnb_for_fees():
    balances = get_account_balances()
    bnb_bal = sum([float(b["free"]) for b in balances if b["asset"] == "BNB"])
    usdt_bal = sum([float(b["free"]) for b in balances if b["asset"] in ["USDT", "USDC"]])
    
    print(f"📊 Balances Actuales Binance Real:")
    print(f"  - BNB Libre: {bnb_bal:.6f} BNB")
    print(f"  - USDT/USDC Libre: ${usdt_bal:.2f} USD")
    
    # Get BNB Current Price
    try:
        price_res = requests.get(f"{BASE_URL}/api/v3/ticker/price?symbol=BNBUSDT", timeout=5).json()
        bnb_price = float(price_res.get("price", 600.0))
        print(f"  - Precio BNB/USDT: ${bnb_price:.2f} USD")
        
        bnb_usd_val = bnb_bal * bnb_price
        print(f"  - Valor actual de BNB en cuenta: ${bnb_usd_val:.2f} USD")
        
        if bnb_usd_val >= 0.50:
            print("✅ ¡Ya tienes suficiente BNB en tu cuenta para cubrir comisiones con el 25% de descuento!")
            return True
            
        print("💡 Procediendo a adquirir una pequeña fracción de BNB para activar el 25% de descuento en comisiones...")
        
        # Try market order for minimum allowed in Binance Spot ($5 USD or Dust Convert)
        timestamp = int(time.time() * 1000)
        params = {
            "symbol": "BNBUSDT",
            "side": "BUY",
            "type": "MARKET",
            "quoteOrderQty": "5.00", # Buying minimum $5 USD of BNB
            "timestamp": timestamp
        }
        query_string = urlencode(params)
        signature = hmac.new(API_SECRET.encode("utf-8"), query_string.encode("utf-8"), hashlib.sha256).hexdigest()
        params["signature"] = signature
        headers = {"X-MBX-APIKEY": API_KEY}
        
        url = f"{BASE_URL}/api/v3/order"
        res = requests.post(url, headers=headers, params=params, timeout=10)
        res_data = res.json()
        
        if res.status_code == 200:
            print(f"🎉 ¡ORDEN COMPRADORA DE BNB EXITOSA!")
            print(f"  - BNB Adquirido con éxito para descuento de comisiones. ID de Orden: {res_data.get('orderId')}")
            return True
        else:
            print(f"ℹ️ Respuesta Binance al comprar BNB ({res.status_code}): {res_data}")
            return False
            
    except Exception as e:
        print(f"Error procesando orden BNB: {e}")
        return False

if __name__ == "__main__":
    sys.stdout.reconfigure(encoding='utf-8')
    check_and_buy_bnb_for_fees()
