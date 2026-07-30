import os, time, hmac, hashlib, requests
from urllib.parse import urlencode

API_KEY = ""
API_SECRET = ""
BASE_URL = "https://api.binance.com"
proxy_url = os.getenv("FIXIE_URL", "")
proxies = {"http": proxy_url, "https": proxy_url} if proxy_url else None

def get_signature(params):
    query_string = urlencode(params)
    return hmac.new(API_SECRET.encode("utf-8"), query_string.encode("utf-8"), hashlib.sha256).hexdigest()

def request_binance(endpoint, method="GET", extra_params=None):
    params = {"timestamp": int(time.time() * 1000)}
    if extra_params:
        params.update(extra_params)
    params["signature"] = get_signature(params)
    headers = {"X-MBX-APIKEY": API_KEY}
    
    url = f"{BASE_URL}{endpoint}"
    try:
        if method == "GET":
            res = requests.get(url, headers=headers, params=params, proxies=proxies, timeout=10)
        return res.json()
    except Exception as e:
        return {"error": str(e)}

print("=== BALANCE ===")
acc = request_binance("/api/v3/account")
if 'balances' in acc:
    for b in acc['balances']:
        if float(b['free']) > 0 or float(b['locked']) > 0:
            print(f"{b['asset']}: Free {b['free']} | Locked {b['locked']}")
else:
    print(acc)

print("\n=== OPEN ORDERS ===")
orders = request_binance("/api/v3/openOrders")
if isinstance(orders, list):
    for o in orders:
        print(f"Order: {o['symbol']} {o['side']} {o['type']} Qty: {o['origQty']} Price: {o['price']}")
else:
    print(orders)

print("\n=== RECENT TRADES (OPUSDT, BTCUSDT) ===")
for sym in ["OPUSDT", "BTCUSDT", "XRPUSDT"]:
    trades = request_binance("/api/v3/myTrades", extra_params={"symbol": sym, "limit": 5})
    if isinstance(trades, list):
        if trades:
            print(f"\n{sym}:")
            for t in trades:
                side = "BUY" if t['isBuyer'] else "SELL"
                print(f"  {time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(t['time']/1000))} | {side} {t['qty']} @ {t['price']}")
    else:
        if 'code' in trades and trades['code'] == -1121: # Invalid symbol or no trades
            pass
        else:
            print(f"{sym} error: {trades}")
