"""
Análisis de Movimientos Atípicos - 1H, 24H, 7D
Identifica oportunidades con movimientos inusuales en las 100 criptomonedas.
"""
import sys, json, time
sys.stdout.reconfigure(encoding='utf-8')
import requests

pairs = json.load(open('top_100_pairs.json'))

print("=" * 70)
print("🔬 ANÁLISIS DE MOVIMIENTOS ATÍPICOS EN LAS TOP 100 CRIPTOMONEDAS")
print("=" * 70)

# Fetch 24h ticker data for all pairs at once (1 request, no proxy needed)
try:
    tickers_res = requests.get("https://api.binance.com/api/v3/ticker/24hr", timeout=10)
    all_tickers = {t['symbol']: t for t in tickers_res.json()}
except Exception as e:
    print(f"Error fetching tickers: {e}")
    all_tickers = {}

results = []
for sym in pairs:
    t = all_tickers.get(sym)
    if not t:
        continue
    try:
        change_24h = float(t.get('priceChangePercent', 0))
        volume_usd = float(t.get('quoteVolume', 0))
        price = float(t.get('lastPrice', 0))
        high = float(t.get('highPrice', 0))
        low = float(t.get('lowPrice', 0))
        volatility = ((high - low) / low * 100) if low > 0 else 0
        
        results.append({
            'symbol': sym,
            'price': price,
            'change_24h': change_24h,
            'volume_usd': volume_usd,
            'volatility': volatility,
            'high': high,
            'low': low
        })
    except:
        pass

# Sort by absolute change to find atypical movements
results.sort(key=lambda x: abs(x['change_24h']), reverse=True)

print(f"\n📈 TOP 10 MOVIMIENTOS MÁS FUERTES (24H):")
print(f"{'Moneda':<12} {'Precio':>10} {'Cambio 24H':>12} {'Volumen':>15} {'Volatilidad':>12}")
print("-" * 65)
for r in results[:10]:
    arrow = "🟢" if r['change_24h'] > 0 else "🔴"
    print(f"{arrow} {r['symbol']:<10} ${r['price']:>9.4f} {r['change_24h']:>+10.2f}% ${r['volume_usd']/1e6:>12.1f}M {r['volatility']:>10.2f}%")

# Find LONG opportunities (strong uptrend)
bullish = [r for r in results if r['change_24h'] >= 3.0 and r['volume_usd'] > 1e6]
bullish.sort(key=lambda x: x['change_24h'], reverse=True)
print(f"\n🟢 OPORTUNIDADES LONG (Subida ≥3% en 24H con volumen fuerte):")
if bullish:
    for r in bullish[:5]:
        print(f"  🚀 {r['symbol']}: +{r['change_24h']:.2f}% | ${r['price']:.4f} | Vol: ${r['volume_usd']/1e6:.1f}M")
else:
    print("  Ninguna moneda subió más del 3% hoy.")

# Find SHORT opportunities (strong downtrend)
bearish = [r for r in results if r['change_24h'] <= -3.0 and r['volume_usd'] > 1e6]
bearish.sort(key=lambda x: x['change_24h'])
print(f"\n🔴 OPORTUNIDADES SHORT (Caída ≥3% en 24H con volumen fuerte):")
if bearish:
    for r in bearish[:5]:
        print(f"  📉 {r['symbol']}: {r['change_24h']:.2f}% | ${r['price']:.4f} | Vol: ${r['volume_usd']/1e6:.1f}M")
else:
    print("  Ninguna moneda cayó más del 3% hoy.")

# Specifically check UNI
uni = next((r for r in results if r['symbol'] == 'UNIUSDT'), None)
if uni:
    print(f"\n🦄 ANÁLISIS ESPECÍFICO DE UNISWAP (UNI):")
    print(f"  Precio: ${uni['price']:.4f}")
    print(f"  Cambio 24H: {uni['change_24h']:+.2f}%")
    print(f"  Volatilidad: {uni['volatility']:.2f}%")
    print(f"  Volumen 24H: ${uni['volume_usd']/1e6:.1f}M")
    print(f"  Rango: ${uni['low']:.4f} - ${uni['high']:.4f}")
    if uni['change_24h'] > 5:
        print(f"  ⚡ MOVIMIENTO ATÍPICO ALCISTA - Candidato a LONG")
    elif uni['change_24h'] < -5:
        print(f"  ⚡ MOVIMIENTO ATÍPICO BAJISTA - Candidato a SHORT")

# High volatility movers (good for scalping)
volatile = [r for r in results if r['volatility'] >= 5.0 and r['volume_usd'] > 1e6]
volatile.sort(key=lambda x: x['volatility'], reverse=True)
print(f"\n⚡ MONEDAS CON ALTA VOLATILIDAD (≥5% rango diario):")
if volatile:
    for r in volatile[:5]:
        print(f"  💥 {r['symbol']}: Rango {r['volatility']:.1f}% | Cambio: {r['change_24h']:+.2f}% | Vol: ${r['volume_usd']/1e6:.1f}M")

print(f"\n{'=' * 70}")
print(f"Total monedas analizadas: {len(results)}")
print(f"{'=' * 70}")
