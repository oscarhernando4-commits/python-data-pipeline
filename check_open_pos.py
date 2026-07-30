import sys, os, time, hmac, hashlib, requests
from urllib.parse import urlencode
os.chdir(r'c:\Users\hosca\Documents\Antigravity\BINANCE')
from dotenv import load_dotenv
load_dotenv()
import real_money_trader as rmt

ts = int(time.time() * 1000)
p = {'timestamp': ts}
qs = urlencode(p)
sig = hmac.new(rmt.API_SECRET.encode(), qs.encode(), hashlib.sha256).hexdigest()
p['signature'] = sig
headers = {'X-MBX-APIKEY': rmt.API_KEY}
pos_res = requests.get('https://fapi.binance.com/fapi/v2/positionRisk', headers=headers, params=p, timeout=10)
positions = [pp for pp in pos_res.json() if float(pp.get('positionAmt', 0)) != 0]

for pos in positions:
    print(f"OPEN: {pos['symbol']} Qty: {pos['positionAmt']} Entry: {pos['entryPrice']} PnL: {pos['unRealizedProfit']}")
    
if not positions:
    print("NO OPEN POSITIONS.")
