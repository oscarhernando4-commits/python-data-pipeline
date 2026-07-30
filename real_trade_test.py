"""
PRUEBA REAL DE TRADING — 1 LONG + 1 SHORT
Verifica que ambas operaciones se ejecutan correctamente con dinero real.
"""
import sys, os, time, json, hmac, hashlib, requests
from urllib.parse import urlencode
sys.stdout.reconfigure(encoding='utf-8')
os.chdir(os.path.dirname(os.path.abspath(__file__)))
from dotenv import load_dotenv
load_dotenv()

import api_connector as rmt

print("=" * 65)
print("🔬 PRUEBA REAL: 1 LONG (SPOT) + 1 SHORT (FUTUROS)")
print("=" * 65)

# Step 0: Check balances
print("\n[PASO 0] Verificando balance antes de operar...")
ts = int(time.time() * 1000)
params = {"timestamp": ts}
qs = urlencode(params)
sig = hmac.new(rmt.API_SECRET.encode(), qs.encode(), hashlib.sha256).hexdigest()
params["signature"] = sig
headers = {"X-MBX-APIKEY": rmt.API_KEY}

spot_res = requests.get(f"{rmt.BASE_URL}/api/v3/account", headers=headers, params=params, proxies=rmt.PROXIES, timeout=10)
spot_data = spot_res.json()
usdt_spot = float(next((b['free'] for b in spot_data['balances'] if b['asset'] == 'USDT'), 0))
print(f"  USDT Spot disponible: ${usdt_spot:.2f}")

ts2 = int(time.time() * 1000)
p2 = {"timestamp": ts2}
qs2 = urlencode(p2)
sig2 = hmac.new(rmt.API_SECRET.encode(), qs2.encode(), hashlib.sha256).hexdigest()
p2["signature"] = sig2
fut_res = requests.get("https://fapi.binance.com/fapi/v2/balance", headers=headers, params=p2, proxies=rmt.PROXIES, timeout=10)
fut_usdt = float(next((b['availableBalance'] for b in fut_res.json() if b['asset'] == 'USDT'), 0))
print(f"  USDT Futuros disponible: ${fut_usdt:.2f}")

if usdt_spot < 5:
    print("  ❌ Insuficiente USDT en Spot para LONG. Abortando.")
    sys.exit(1)
if fut_usdt < 5:
    print("  ❌ Insuficiente USDT en Futuros para SHORT. Abortando.")
    sys.exit(1)

print(f"  ✅ Fondos suficientes para ambas pruebas")

# ============================================
# TEST 1: LONG — Comprar DOGEUSDT en Spot
# ============================================
LONG_SYMBOL = "DOGEUSDT"
LONG_AMOUNT = 6.0  # $6 USD

print(f"\n{'='*65}")
print(f"[TEST 1] LONG — Comprando ${LONG_AMOUNT} de {LONG_SYMBOL} en Spot...")
print(f"{'='*65}")

price_before = rmt.get_symbol_price(LONG_SYMBOL, is_futures=False)
print(f"  Precio actual: ${price_before:.6f}")

buy_result = rmt.execute_real_spot_market_buy(LONG_SYMBOL, LONG_AMOUNT)
print(f"  Resultado compra: {json.dumps(buy_result, indent=2)[:300]}")

if isinstance(buy_result, dict) and "orderId" in buy_result:
    print(f"  ✅ LONG EJECUTADO EXITOSAMENTE!")
    print(f"  Order ID: {buy_result['orderId']}")
    print(f"  Status: {buy_result.get('status')}")
    
    # Get filled qty
    filled_qty = float(buy_result.get('executedQty', 0))
    filled_cost = float(buy_result.get('cummulativeQuoteQty', 0))
    print(f"  Cantidad comprada: {filled_qty} DOGE")
    print(f"  Costo total: ${filled_cost:.2f}")
    
    # Wait 3 seconds then sell to complete the cycle
    print(f"\n  ⏳ Esperando 3 segundos antes de vender (verificar ciclo completo)...")
    time.sleep(3)
    
    price_after = rmt.get_symbol_price(LONG_SYMBOL, is_futures=False)
    print(f"  Precio después: ${price_after:.6f}")
    
    # Sell
    if price_after and price_after > 1:
        qty_str = f"{int(filled_qty)}"
    elif price_after and price_after > 0.01:
        qty_str = f"{filled_qty:.1f}"
    else:
        qty_str = f"{int(filled_qty)}"
    
    sell_params = {
        "symbol": LONG_SYMBOL,
        "side": "SELL",
        "type": "MARKET",
        "quantity": qty_str,
        "timestamp": int(time.time() * 1000)
    }
    sq = urlencode(sell_params)
    ss = hmac.new(rmt.API_SECRET.encode(), sq.encode(), hashlib.sha256).hexdigest()
    sell_params["signature"] = ss
    
    sell_res = requests.post(f"{rmt.BASE_URL}/api/v3/order", headers=headers, params=sell_params, proxies=rmt.PROXIES, timeout=10)
    sell_data = sell_res.json()
    print(f"  Resultado venta: {json.dumps(sell_data, indent=2)[:300]}")
    
    if "orderId" in sell_data:
        sell_cost = float(sell_data.get('cummulativeQuoteQty', 0))
        pnl = sell_cost - filled_cost
        print(f"  ✅ VENTA EXITOSA! Recuperado: ${sell_cost:.2f} | PnL: ${pnl:+.4f}")
    else:
        print(f"  ❌ VENTA FALLÓ: {sell_data}")
else:
    print(f"  ❌ LONG FALLÓ: {buy_result}")

# ============================================
# TEST 2: SHORT — Abrir SHORT en UNIUSDT Futuros
# ============================================
SHORT_SYMBOL = "UNIUSDT"
SHORT_AMOUNT = 6.0

print(f"\n{'='*65}")
print(f"[TEST 2] SHORT — Abriendo SHORT de ${SHORT_AMOUNT} en {SHORT_SYMBOL} Futuros...")
print(f"{'='*65}")

price_before_short = rmt.get_symbol_price(SHORT_SYMBOL, is_futures=True)
print(f"  Precio actual: ${price_before_short:.4f}")

short_result = rmt.execute_real_futures_market_short(SHORT_SYMBOL, SHORT_AMOUNT)
print(f"  Resultado SHORT: {json.dumps(short_result, indent=2)[:500]}")

if isinstance(short_result, dict) and "orderId" in short_result:
    print(f"  ✅ SHORT EJECUTADO EXITOSAMENTE!")
    print(f"  Order ID: {short_result['orderId']}")
    print(f"  Status: {short_result.get('status')}")
    
    # Verify the position exists
    time.sleep(2)
    ts3 = int(time.time() * 1000)
    p3 = {"symbol": SHORT_SYMBOL, "timestamp": ts3}
    qs3 = urlencode(p3)
    sig3 = hmac.new(rmt.API_SECRET.encode(), qs3.encode(), hashlib.sha256).hexdigest()
    p3["signature"] = sig3
    pos_res = requests.get("https://fapi.binance.com/fapi/v2/positionRisk", headers=headers, params=p3, proxies=rmt.PROXIES, timeout=10)
    positions = pos_res.json()
    active = [p for p in positions if float(p.get('positionAmt', 0)) != 0]
    
    if active:
        pos = active[0]
        print(f"  ✅ POSICIÓN SHORT VERIFICADA EN BINANCE:")
        print(f"     Symbol: {pos['symbol']}")
        print(f"     Cantidad: {pos['positionAmt']}")
        print(f"     Entry Price: ${float(pos['entryPrice']):.4f}")
        print(f"     PnL actual: ${float(pos['unRealizedProfit']):.4f}")
        
        # Now close it immediately to verify the close function works
        print(f"\n  ⏳ Cerrando SHORT para verificar cierre automático...")
        qty_to_close = abs(float(pos['positionAmt']))
        close_result = rmt.execute_real_futures_market_close(SHORT_SYMBOL, qty_to_close)
        print(f"  Resultado cierre: {json.dumps(close_result, indent=2)[:300]}")
        
        if isinstance(close_result, dict) and "orderId" in close_result:
            print(f"  ✅ SHORT CERRADO EXITOSAMENTE!")
            print(f"  Order ID: {close_result['orderId']}")
        else:
            print(f"  ❌ CIERRE FALLÓ: {close_result}")
    else:
        print(f"  ⚠️ Posición no encontrada inmediatamente (puede tardar)")
else:
    print(f"  ❌ SHORT FALLÓ: {short_result}")

# FINAL SUMMARY
print(f"\n{'='*65}")
print(f"🎯 RESUMEN DE PRUEBAS REALES")
print(f"{'='*65}")
