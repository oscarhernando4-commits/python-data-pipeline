import sys,json,requests,concurrent.futures
sys.stdout.reconfigure(encoding='utf-8')
pairs=json.load(open('top_100_pairs.json'))
tickers={t['symbol']:t for t in requests.get('https://api.binance.com/api/v3/ticker/24hr',timeout=10).json()}

def scan(sym):
    t=tickers.get(sym)
    if not t: return None
    try:
        p=float(t['lastPrice']); c24=float(t['priceChangePercent']); vol=float(t['quoteVolume'])
        hi=float(t['highPrice']); lo=float(t['lowPrice'])
        prox=(p-lo)/(hi-lo)*100 if hi>lo else 50
        k7=requests.get(f'https://api.binance.com/api/v3/klines?symbol={sym}&interval=1d&limit=7',timeout=5).json()
        c7=((p-float(k7[0][1]))/float(k7[0][1]))*100 if len(k7)>=7 else 0
        k1=requests.get(f'https://api.binance.com/api/v3/klines?symbol={sym}&interval=1h&limit=2',timeout=5).json()
        c1=((p-float(k1[-1][1]))/float(k1[-1][1]))*100 if len(k1)>=2 else 0
        sc=0
        if c7>10:sc+=30
        elif c7>5:sc+=20
        elif c7>3:sc+=10
        if c24>5:sc+=25
        elif c24>3:sc+=15
        elif c24>2:sc+=10
        if c1>2:sc+=20
        elif c1>1:sc+=10
        if prox>90:sc+=15
        elif prox>80:sc+=10
        return{'s':sym,'p':p,'c1':c1,'c24':c24,'c7':c7,'vol':vol,'prox':prox,'sc':sc}
    except:
        return None

with concurrent.futures.ThreadPoolExecutor(max_workers=15) as ex:
    res=[r for r in ex.map(scan, pairs[:40]) if r]

res.sort(key=lambda x:x['sc'], reverse=True)
print("=" * 75)
print("MONEDAS SOBREEXTENDIDAS - CANDIDATAS A SHORT POR CORRECCION")
print("=" * 75)
print(f"{'Moneda':<12} {'Precio':>10} {'1H':>7} {'24H':>7} {'7D':>7} {'Prox.Hi':>8} {'Score':>6}")
print("-" * 75)
for r in res[:15]:
    flag = "***" if r['sc']>=50 else " * " if r['sc']>=30 else "   "
    print(f"{flag} {r['s']:<10} ${r['p']:>9.4f} {r['c1']:>+6.2f}% {r['c24']:>+6.2f}% {r['c7']:>+6.2f}% {r['prox']:>6.1f}% {r['sc']:>5}")

uni=next((r for r in res if r['s']=='UNIUSDT'), None)
if uni:
    print(f"\nUNISWAP (UNI): 1H={uni['c1']:+.2f}% | 24H={uni['c24']:+.2f}% | 7D={uni['c7']:+.2f}% | Score={uni['sc']}/100")
