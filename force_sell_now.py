import sys
import json
import time
import hmac
import hashlib
import urllib.parse
import requests
from datetime import datetime

sys.stdout.reconfigure(encoding='utf-8')

from dotenv import load_dotenv
load_dotenv()

import api_connector

API_KEY = api_connector.API_KEY
API_SECRET = api_connector.API_SECRET
BASE_URL = api_connector.BASE_URL
PROXIES = api_connector.PROXIES

def manual_sell():
    print("Iniciando venta manual de la posición SPOT BTCUSDT LONG...")
    state = api_connector.load_real_account_state()
    pos = state.get("position")
    
    if not pos:
        print("No hay ninguna posición activa en el estado local.")
        return
        
    symbol = pos.get("symbol")
    side = pos.get("side")
    active_qty = float(pos.get("quantity"))
    entry = float(pos.get("entry_price"))
    
    if side == "LONG":
        print(f"Cerrando posición SPOT LONG de {symbol}...")
        try:
            active_current_price = api_connector.get_symbol_price(symbol, is_futures=False)
            print(f"Precio actual de mercado: {active_current_price}")
            
            # Format qty
            qty_str = f"{active_qty:.5f}"
            if symbol == "BTCUSDT":
                qty_str = f"{active_qty:.5f}"
            
            sell_params = {
                "symbol": symbol,
                "side": "SELL",
                "type": "MARKET",
                "quantity": qty_str,
                "timestamp": int(time.time() * 1000)
            }
            query_string = urllib.parse.urlencode(sell_params)
            signature = hmac.new(API_SECRET.encode("utf-8"), query_string.encode("utf-8"), hashlib.sha256).hexdigest()
            sell_params["signature"] = signature
            headers = {"X-MBX-APIKEY": API_KEY}
            
            print("Enviando orden a Binance...")
            res = requests.post(f"{BASE_URL}/api/v3/order", headers=headers, params=sell_params, proxies=PROXIES, timeout=10)
            
            if res.status_code == 200:
                print(f"✅ Venta de {symbol} ejecutada exitosamente en Binance.")
                # Update local state
                pnl_usd = (active_current_price - entry) * active_qty
                pnl_pct = ((active_current_price - entry) / entry) * 100
                
                state["current_balance_usd"] = round(state["current_balance_usd"] + pnl_usd, 2)
                state["net_pnl_usd"] = round(state["net_pnl_usd"] + pnl_usd, 2)
                state["wins"] = state.get("wins", 0) + (1 if pnl_usd > 0 else 0)
                state["losses"] = state.get("losses", 0) + (1 if pnl_usd <= 0 else 0)
                state["trades_count"] = state.get("trades_count", 0) + 1
                
                if pnl_usd > 0:
                    state["daily_wins"] = state.get("daily_wins", 0) + 1
                else:
                    state["daily_losses"] = state.get("daily_losses", 0) + 1
                    
                state["position"] = None
                state["status"] = "BUSCANDO_OPORTUNIDAD"
                state["last_trade_time"] = time.strftime("%y-%m-%d<br>%H:%M", time.localtime())
                
                api_connector.save_real_account_state(state)
                print(f"✅ Estado local actualizado. PnL: ${pnl_usd:.2f} ({pnl_pct:.2f}%)")
            else:
                print(f"❌ Falló la venta en Binance. Código: {res.status_code}")
                print(res.text)
        except Exception as e:
            print(f"❌ Error durante la venta: {e}")
    else:
        print(f"La posición es {side}, se requiere cierre de futuros.")

if __name__ == "__main__":
    manual_sell()
