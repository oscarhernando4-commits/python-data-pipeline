"""
DETECTOR DE SOBREEXTENSIÓN — Identifica monedas que subieron demasiado y están listas para corregir (SHORT).
Se ejecuta como parte del pipeline cada 5 minutos (SIN proxy, usa API pública de Binance).
"""
import requests
import json
import os
import time
from datetime import datetime

OVEREXTENSION_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "overextension_signals.json")

def detect_overextended_coins(pairs, top_n=5):
    """
    Scans a list of pairs and returns the top N overextended coins
    that are candidates for SHORT (mean reversion).
    Uses ONLY public Binance API (no proxy needed).
    """
    # 1. Bulk fetch 24H tickers (single request for ALL pairs)
    try:
        tickers_res = requests.get("https://api.binance.com/api/v3/ticker/24hr", timeout=10)
        all_tickers = {t['symbol']: t for t in tickers_res.json()}
    except:
        return []

    results = []
    for sym in pairs[:50]:  # Limit to top 50 for speed
        t = all_tickers.get(sym)
        if not t:
            continue
        try:
            price = float(t.get('lastPrice', 0))
            change_24h = float(t.get('priceChangePercent', 0))
            volume_usd = float(t.get('quoteVolume', 0))
            high_24h = float(t.get('highPrice', 0))
            low_24h = float(t.get('lowPrice', 0))
            
            if price <= 0 or volume_usd < 500000:  # Skip low volume
                continue
                
            # Proximity to 24H high (how close to ceiling)
            range_24h = high_24h - low_24h
            proximity_to_high = ((price - low_24h) / range_24h * 100) if range_24h > 0 else 50
            
            results.append({
                'symbol': sym,
                'price': price,
                'change_24h': change_24h,
                'volume_usd': volume_usd,
                'proximity_to_high': proximity_to_high,
            })
        except:
            pass

    # 2. For top movers, fetch 7D and 1H data (targeted, not all 100)
    # Sort by 24H change to find the biggest movers first
    bullish_movers = sorted([r for r in results if r['change_24h'] > 2.0], 
                           key=lambda x: x['change_24h'], reverse=True)[:15]
    
    for r in bullish_movers:
        try:
            # 7-day change
            k7 = requests.get(f"https://api.binance.com/api/v3/klines?symbol={r['symbol']}&interval=1d&limit=7", timeout=3).json()
            if len(k7) >= 7:
                r['change_7d'] = ((r['price'] - float(k7[0][1])) / float(k7[0][1])) * 100
            else:
                r['change_7d'] = 0
                
            # 1-hour change
            k1 = requests.get(f"https://api.binance.com/api/v3/klines?symbol={r['symbol']}&interval=1h&limit=2", timeout=3).json()
            if len(k1) >= 2:
                r['change_1h'] = ((r['price'] - float(k1[-1][1])) / float(k1[-1][1])) * 100
            else:
                r['change_1h'] = 0
                
            # Quick RSI from 15m candles
            k15 = requests.get(f"https://api.binance.com/api/v3/klines?symbol={r['symbol']}&interval=15m&limit=15", timeout=3).json()
            closes = [float(k[4]) for k in k15]
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
            r['change_7d'] = r.get('change_7d', 0)
            r['change_1h'] = r.get('change_1h', 0)
            r['rsi'] = r.get('rsi', 50)

    # 3. Calculate Overextension Score
    for r in bullish_movers:
        score = 0
        c7 = r.get('change_7d', 0)
        c24 = r.get('change_24h', 0)
        c1 = r.get('change_1h', 0)
        rsi = r.get('rsi', 50)
        prox = r.get('proximity_to_high', 50)
        
        # 7D momentum (biggest weight - sustained pump = biggest correction)
        if c7 > 15: score += 35
        elif c7 > 10: score += 30
        elif c7 > 5: score += 20
        elif c7 > 3: score += 10
        
        # 24H acceleration
        if c24 > 7: score += 25
        elif c24 > 5: score += 20
        elif c24 > 3: score += 15
        elif c24 > 2: score += 10
        
        # 1H exhaustion signal
        if c1 > 3: score += 20
        elif c1 > 2: score += 15
        elif c1 > 1: score += 10
        
        # RSI overbought
        if rsi > 75: score += 20
        elif rsi > 70: score += 15
        elif rsi > 65: score += 10
        
        # Near 24H high (about to hit resistance)
        if prox > 95: score += 15
        elif prox > 90: score += 10
        elif prox > 80: score += 5
        
        r['overextension_score'] = min(score, 100)

    # 4. Sort by overextension score and return top N
    bullish_movers.sort(key=lambda x: x.get('overextension_score', 0), reverse=True)
    top_signals = bullish_movers[:top_n]
    
    # 5. Save signals to file for the main pipeline to read
    signal_data = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "signals": top_signals
    }
    try:
        with open(OVEREXTENSION_FILE, 'w') as f:
            json.dump(signal_data, f, indent=2)
    except:
        pass
    
    return top_signals


def get_best_short_candidate(pairs, min_score=50):
    """Returns the single best SHORT candidate if score >= min_score, or None."""
    signals = detect_overextended_coins(pairs, top_n=3)
    if signals and signals[0].get('overextension_score', 0) >= min_score:
        best = signals[0]
        print(f"📉 SOBREEXTENSIÓN DETECTADA: {best['symbol']} Score={best['overextension_score']}/100")
        print(f"   1H={best.get('change_1h',0):+.2f}% | 24H={best['change_24h']:+.2f}% | 7D={best.get('change_7d',0):+.2f}% | RSI={best.get('rsi',50):.0f}")
        return best
    return None


if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding='utf-8')
    pairs = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "top_100_pairs.json")))
    signals = detect_overextended_coins(pairs, top_n=5)
    print(f"Top {len(signals)} overextended coins:")
    for s in signals:
        print(f"  {s['symbol']}: Score={s.get('overextension_score',0)} | 24H={s['change_24h']:+.2f}% | 7D={s.get('change_7d',0):+.2f}%")
