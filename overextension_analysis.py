"""
ANÁLISIS DE MONEDAS SOBREEXTENDIDAS — OPORTUNIDADES SHORT POR CORRECCIÓN
Identifica monedas que subieron mucho en 1H, 24H y 7D y están listas para corregir.
"""
import sys, json, time
sys.stdout.reconfigure(encoding='utf-8')
import requests

pairs = json.load(open('top_100_pairs.json'))

print("=" * 75)
print("📉 DETECTOR DE MONEDAS SOBREEXTENDIDAS — CANDIDATAS A SHORT POR CORRECCIÓN")
print("=" * 75)

# 1. Get 24H tickers
tickers_res = requests.get("https://api.binance.com/api/v3/ticker/24hr", timeout=10)
all_tickers = {t['symbol']: t for t in tickers_res.json()}

results = []
for sym in pairs:
    t = all_tickers.get(sym)
    if not t:
        continue
    try:
        change_24h = float(t.get('priceChangePercent', 0))
        volume_usd = float(t.get('quoteVolume', 0))
        price = float(t.get('lastPrice', 0))
        high_24h = float(t.get('highPrice', 0))
        low_24h = float(t.get('lowPrice', 0))
        
        # Calculate how close to 24H HIGH (proximity to ceiling = overbought)
        range_24h = high_24h - low_24h
        proximity_to_high = ((price - low_24h) / range_24h * 100) if range_24h > 0 else 50
        
        results.append({
            'symbol': sym, 'price': price, 'change_24h': change_24h,
            'volume_usd': volume_usd, 'high_24h': high_24h, 'low_24h': low_24h,
            'proximity_to_high': proximity_to_high
        })
    except:
        pass

# 2. Get 7D change via klines (weekly candle)
print("\n🔍 Calculando cambios de 7 días y 1 hora para las TOP 100...")
for r in results:
    try:
        # 7 Day change
        klines_7d = requests.get(f"https://api.binance.com/api/v3/klines?symbol={r['symbol']}&interval=1d&limit=7", timeout=5).json()
        if len(klines_7d) >= 7:
            open_7d = float(klines_7d[0][1])
            r['change_7d'] = ((r['price'] - open_7d) / open_7d) * 100
        else:
            r['change_7d'] = 0
            
        # 1 Hour change
        klines_1h = requests.get(f"https://api.binance.com/api/v3/klines?symbol={r['symbol']}&interval=1h&limit=2", timeout=5).json()
        if len(klines_1h) >= 2:
            open_1h = float(klines_1h[-1][1])
            r['change_1h'] = ((r['price'] - open_1h) / open_1h) * 100
        else:
            r['change_1h'] = 0
            
        # RSI 15m (quick calc)
        klines_15m = requests.get(f"https://api.binance.com/api/v3/klines?symbol={r['symbol']}&interval=15m&limit=15", timeout=5).json()
        closes = [float(k[4]) for k in klines_15m]
        if len(closes) >= 15:
            gains = [max(closes[i]-closes[i-1], 0) for i in range(1, len(closes))]
            losses = [max(closes[i-1]-closes[i], 0) for i in range(1, len(closes))]
            avg_gain = sum(gains)/len(gains) if gains else 0.001
            avg_loss = sum(losses)/len(losses) if losses else 0.001
            rs = avg_gain / avg_loss if avg_loss > 0 else 100
            r['rsi'] = 100 - (100 / (1 + rs))
        else:
            r['rsi'] = 50
    except:
        r['change_7d'] = 0
        r['change_1h'] = 0
        r['rsi'] = 50

# 3. Calculate "Overextension Score" — higher = more likely to correct
for r in results:
    # Score based on: big 7D gain + big 24H gain + big 1H gain + high RSI + near 24H high
    score = 0
    if r['change_7d'] > 10: score += 30
    elif r['change_7d'] > 5: score += 20
    elif r['change_7d'] > 3: score += 10
    
    if r['change_24h'] > 5: score += 25
    elif r['change_24h'] > 3: score += 15
    elif r['change_24h'] > 2: score += 10
    
    if r['change_1h'] > 2: score += 20
    elif r['change_1h'] > 1: score += 10
    
    if r['rsi'] > 70: score += 25
    elif r['rsi'] > 60: score += 10
    
    if r['proximity_to_high'] > 90: score += 15
    elif r['proximity_to_high'] > 80: score += 10
    
    r['overextension_score'] = score

# Sort by overextension score
results.sort(key=lambda x: x['overextension_score'], reverse=True)

print(f"\n{'='*75}")
print(f"📉 TOP 15 MONEDAS SOBREEXTENDIDAS — CANDIDATAS A SHORT POR CORRECCIÓN")
print(f"{'='*75}")
print(f"{'Moneda':<12} {'Precio':>9} {'1H':>7} {'24H':>7} {'7D':>7} {'RSI':>5} {'Prox.Hi':>8} {'Score':>6}")
print("-" * 75)

for r in results[:15]:
    alert = "🔴🔴🔴" if r['overextension_score'] >= 70 else "🔴🔴" if r['overextension_score'] >= 50 else "🟡"
    print(f"{alert} {r['symbol']:<10} ${r['price']:>8.4f} {r['change_1h']:>+6.2f}% {r['change_24h']:>+6.2f}% {r['change_7d']:>+6.2f}% {r['rsi']:>5.1f} {r['proximity_to_high']:>6.1f}% {r['overextension_score']:>5}")

# Specific analysis for the most overextended
top3 = results[:3]
print(f"\n{'='*75}")
print(f"🎯 ANÁLISIS DETALLADO DE LOS 3 MEJORES CANDIDATOS A SHORT")
print(f"{'='*75}")

for r in top3:
    print(f"\n📉 {r['symbol']}:")
    print(f"   Precio actual: ${r['price']:.4f}")
    print(f"   Cambio 1H: {r['change_1h']:+.2f}% | 24H: {r['change_24h']:+.2f}% | 7D: {r['change_7d']:+.2f}%")
    print(f"   RSI 15min: {r['rsi']:.1f} {'(SOBRECOMPRADO ⚠️)' if r['rsi'] > 70 else '(Neutral)' if r['rsi'] > 40 else '(Sobrevendido)'}")
    print(f"   Proximidad al máximo 24H: {r['proximity_to_high']:.1f}%")
    print(f"   Volumen 24H: ${r['volume_usd']/1e6:.1f}M")
    print(f"   Score de Sobreextensión: {r['overextension_score']}/100")
    
    if r['overextension_score'] >= 70:
        print(f"   ➡️ VEREDICTO: 🔴 EXCELENTE candidato a SHORT — Alta probabilidad de corrección")
    elif r['overextension_score'] >= 50:
        print(f"   ➡️ VEREDICTO: 🟡 BUEN candidato a SHORT — Monitorear para entrada")
    else:
        print(f"   ➡️ VEREDICTO: ⚪ Movimiento moderado — Esperar confirmación")

# UNI specific
uni = next((r for r in results if r['symbol'] == 'UNIUSDT'), None)
if uni and uni not in top3:
    print(f"\n🦄 UNISWAP (UNI) — Análisis Específico:")
    print(f"   Precio: ${uni['price']:.4f}")
    print(f"   1H: {uni['change_1h']:+.2f}% | 24H: {uni['change_24h']:+.2f}% | 7D: {uni['change_7d']:+.2f}%")
    print(f"   RSI: {uni['rsi']:.1f} | Prox. High: {uni['proximity_to_high']:.1f}%")
    print(f"   Score Sobreextensión: {uni['overextension_score']}/100")

print(f"\n{'='*75}")
