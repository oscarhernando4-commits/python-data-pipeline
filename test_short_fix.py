"""TEST 2 CORREGIDO: SHORT UNIUSDT con precision fix"""
import sys, os, time, json, hmac, hashlib, requests
from urllib.parse import urlencode
sys.stdout.reconfigure(encoding='utf-8')
os.chdir(os.path.dirname(os.path.abspath(__file__)))
from dotenv import load_dotenv
load_dotenv()
import api_connector as rmt

print("=" * 65)
print("[TEST 2] SHORT UNIUSDT — Con precision fix")
print("=" * 65)

headers = {"X-MBX-APIKEY": rmt.API_KEY}
price = rmt.get_symbol_price("UNIUSDT", is_futures=True)
print(f"Precio UNI: ${price:.4f}")
print(f"$6 / ${price:.4f} = {6/price:.2f} UNI -> int = {int(6*0.98/price)} UNI")

short_result = rmt.execute_real_futures_market_short("UNIUSDT", 6.0)
print(f"Resultado: {json.dumps(short_result, indent=2)[:500]}")

if isinstance(short_result, dict) and "orderId" in short_result:
    print(f"\n✅ SHORT ABIERTO! Order ID: {short_result['orderId']}")
    
    time.sleep(2)
    # Verify position
    ts = int(time.time() * 1000)
    p = {"symbol": "UNIUSDT", "timestamp": ts}
    qs = urlencode(p)
    sig = hmac.new(rmt.API_SECRET.encode(), qs.encode(), hashlib.sha256).hexdigest()
    p["signature"] = sig
    pos_res = requests.get("https://fapi.binance.com/fapi/v2/positionRisk", headers=headers, params=p, proxies=rmt.PROXIES, timeout=10)
    positions = [pp for pp in pos_res.json() if float(pp.get('positionAmt', 0)) != 0]
    
    if positions:
        pos = positions[0]
        print(f"✅ POSICION CONFIRMADA:")
        print(f"   Qty: {pos['positionAmt']} UNI")
        print(f"   Entry: ${float(pos['entryPrice']):.4f}")
        print(f"   PnL: ${float(pos['unRealizedProfit']):.4f}")
        
        # Close it
        print(f"\n⏳ Cerrando SHORT...")
        close = rmt.execute_real_futures_market_close("UNIUSDT", abs(float(pos['positionAmt'])))
        print(f"Cierre: {json.dumps(close, indent=2)[:300]}")
        if isinstance(close, dict) and "orderId" in close:
            print(f"✅ SHORT CERRADO! Order ID: {close['orderId']}")
        else:
            print(f"❌ Cierre falló: {close}")
    else:
        print("⚠️ Posición no encontrada")
else:
    print(f"❌ SHORT falló: {short_result}")
