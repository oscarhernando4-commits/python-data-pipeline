import urllib.request
import json
import math
import sys

BASE_URL = 'https://api.binance.com'

def fetch_klines(symbol='BTCUSDT', interval='1h', limit=100):
    url = f"{BASE_URL}/api/v3/klines?symbol={symbol.upper()}&interval={interval}&limit={limit}"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req) as response:
        data = json.loads(response.read().decode())
    
    closes = [float(k[4]) for k in data]
    highs = [float(k[2]) for k in data]
    lows = [float(k[3]) for k in data]
    volumes = [float(k[5]) for k in data]
    return closes, highs, lows, volumes

def calc_ema(values, period):
    if len(values) < period:
        return [sum(values) / len(values)] * len(values)
    k = 2 / (period + 1)
    ema = [sum(values[:period]) / period]
    for price in values[period:]:
        ema.append(price * k + ema[-1] * (1 - k))
    padding = [ema[0]] * (period - 1)
    return padding + ema

def calc_rsi(closes, period=14):
    if len(closes) < period + 1:
        return 50.0
    gains, losses = [], []
    for i in range(1, len(closes)):
        diff = closes[i] - closes[i-1]
        gains.append(diff if diff >= 0 else 0.0)
        losses.append(abs(diff) if diff < 0 else 0.0)
    
    avg_gain = sum(gains[:period]) / period
    avg_loss = sum(losses[:period]) / period
    for i in range(period, len(gains)):
        avg_gain = (avg_gain * (period - 1) + gains[i]) / period
        avg_loss = (avg_loss * (period - 1) + losses[i]) / period
    
    if avg_loss == 0:
        return 100.0
    return 100.0 - (100.0 / (1 + (avg_gain / avg_loss)))

def calc_macd(closes):
    ema12 = calc_ema(closes, 12)
    ema26 = calc_ema(closes, 26)
    macd_line = [a - b for a, b in zip(ema12, ema26)]
    signal_line = calc_ema(macd_line, 9)
    histogram = [m - s for m, s in zip(macd_line, signal_line)]
    return macd_line[-1], signal_line[-1], histogram[-1]

def calc_bollinger_bands(closes, period=20, num_std=2):
    if len(closes) < period:
        sma = sum(closes) / len(closes)
        return sma, sma, sma
    recent = closes[-period:]
    sma = sum(recent) / period
    variance = sum((x - sma) ** 2 for x in recent) / period
    std_dev = math.sqrt(variance)
    return sma + (num_std * std_dev), sma, sma - (num_std * std_dev)

def calc_atr(highs, lows, closes, period=14):
    tr_list = [
        max(highs[i] - lows[i], abs(highs[i] - closes[i-1]), abs(lows[i] - closes[i-1]))
        for i in range(1, len(closes))
    ]
    if not tr_list:
        return 0.0
    return sum(tr_list[-period:]) / min(len(tr_list), period)

def analyze_institutional_grade(symbol='BTCUSDT', account_balance=10000.0, risk_percentage=1.0):
    # Multi-timeframe fetch: 4h (Macro Trend) and 15m (Micro Trigger)
    closes_4h, highs_4h, lows_4h, _ = fetch_klines(symbol, '4h', 100)
    closes_15m, highs_15m, lows_15m, vols_15m = fetch_klines(symbol, '15m', 100)
    
    current_price = closes_15m[-1]
    
    # 1. Macro Trend (4h)
    ema50_4h = calc_ema(closes_4h, 50)[-1]
    ema200_4h = calc_ema(closes_4h, 200)[-1] if len(closes_4h) >= 200 else ema50_4h
    macro_trend = "BULLISH" if closes_4h[-1] > ema50_4h and ema50_4h > ema200_4h else (
        "BEARISH" if closes_4h[-1] < ema50_4h and ema50_4h < ema200_4h else "NEUTRAL"
    )
    
    # 2. Micro Confirmation (15m)
    rsi_15m = calc_rsi(closes_15m)
    macd_15m, macd_sig_15m, macd_hist_15m = calc_macd(closes_15m)
    bb_upper_15m, bb_mid_15m, bb_lower_15m = calc_bollinger_bands(closes_15m)
    atr_15m = calc_atr(highs_15m, lows_15m, closes_15m)
    ema20_15m = calc_ema(closes_15m, 20)[-1]
    
    # 3. Strict Volume Spike & Bollinger Squeeze Check (Kyle Chisamore Strategy)
    avg_vol_15m = sum(vols_15m[-21:-1]) / 20.0 if len(vols_15m) > 20 else vols_15m[-1]
    curr_vol = vols_15m[-1]
    volume_surge = curr_vol >= (avg_vol_15m * 1.5)
    
    # Bollinger Band Width (Squeeze Detection)
    bb_width = (bb_upper_15m - bb_lower_15m) / bb_mid_15m if bb_mid_15m > 0 else 0.1
    bb_squeeze = bb_width < 0.03  # Low volatility energy compression
    
    # Wyckoff Spring Detection (Fakeout breakdown below low followed by sharp volume recovery)
    recent_low = min(lows_15m[-10:-1]) if len(lows_15m) > 10 else lows_15m[-1]
    wyckoff_spring = (lows_15m[-1] < recent_low) and (closes_15m[-1] > recent_low) and volume_surge
    
    # Institutional Confluence Score (0 to 100)
    score = 50
    reasons = []
    
    if macro_trend == "BULLISH":
        score += 20
        reasons.append("Macro Trend (4H) is strongly BULLISH")
    elif macro_trend == "BEARISH":
        score -= 20
        reasons.append("Macro Trend (4H) is strongly BEARISH")
        
    if closes_15m[-1] > ema20_15m:
        score += 10
        reasons.append("Price above 15M EMA20")
    else:
        score -= 10
        reasons.append("Price below 15M EMA20")
        
    if rsi_15m < 32:
        score += 25
        reasons.append("15M RSI Oversold (<32) - Rebound Potential")
    elif rsi_15m > 68:
        score -= 25
        reasons.append("15M RSI Overbought (>68) - Pullback Risk")
    elif 48 <= rsi_15m <= 62 and macro_trend == "BULLISH":
        score += 15
        reasons.append("15M RSI in Healthy Bullish Expansion Zone")
        
    if macd_hist_15m > 0 and macd_hist_15m > (calc_macd(closes_15m[:-1])[2]):
        score += 15
        reasons.append("MACD Histogram expanding upwards")
    elif macd_hist_15m < 0:
        score -= 15
        reasons.append("MACD Histogram expanding downwards")
        
    if volume_surge:
        score += 15 if macro_trend == "BULLISH" else -15
        reasons.append(f"Volume Surge Approved ({round(curr_vol/avg_vol_15m, 2)}x avg)")
    else:
        score -= 10
        reasons.append(f"Low Volume Warning ({round(curr_vol/avg_vol_15m, 2)}x avg) - Anti-Fakeout Shield")

    if bb_squeeze and volume_surge:
        score += 15
        reasons.append("🔥 Kyle Chisamore Bollinger Squeeze Expansion Approved (+15 Pts)")
        
    if wyckoff_spring:
        score += 20
        reasons.append("⚡ Wyckoff Spring Institutional Recovery Approved (+20 Pts)")
        
    # High-Probability Execution Thresholds (Elevated to 80 points)
    if score >= 80:
        recommendation = "HIGH CONFLUENCE BUY 🚀 (A+ Setup)"
        action = "BUY"
    elif score <= 20:
        recommendation = "HIGH CONFLUENCE SELL 🔻 (A+ Setup)"
        action = "SELL"
    else:
        recommendation = "NO TRADE ⏸️ (Wait for A+ Confluence Setup)"
        action = "HOLD"
        
    # Risk Management & Break-Even Strategy
    risk_usd = account_balance * (risk_percentage / 100.0)
    sl_distance = max(atr_15m * 1.5, current_price * 0.008)
    
    if action == "BUY":
        stop_loss = current_price - sl_distance
        break_even_trigger = current_price + (sl_distance * 1.0) # Move SL to Entry at +1R
        take_profit_1 = current_price + (sl_distance * 2.0)     # 1:2 R:R
        take_profit_2 = current_price + (sl_distance * 3.5)     # 1:3.5 R:R
    elif action == "SELL":
        stop_loss = current_price + sl_distance
        break_even_trigger = current_price - (sl_distance * 1.0)
        take_profit_1 = current_price - (sl_distance * 2.0)
        take_profit_2 = current_price - (sl_distance * 3.5)
    else:
        stop_loss = current_price * 0.99
        break_even_trigger = current_price
        take_profit_1 = current_price * 1.02
        take_profit_2 = current_price * 1.035
        
    per_unit_risk = abs(current_price - stop_loss)
    units = (risk_usd / per_unit_risk) if per_unit_risk > 0 else 0
    
    # 7. TAKASHI KOTEGAWA (BNF) ASSET-SPECIFIC MA DEVIATION SIGNALS
    ema_25 = sum(closes_15m[-25:]) / 25 if len(closes_15m) >= 25 else ema20_15m
    ma_dev_pct = ((current_price - ema_25) / ema_25) * 100.0
    
    # Asset Specific thresholds: MegaCaps (-3.5% to -4%), Majors (-5.5% to -6.5%), High-Beta (-8%+)
    is_megacap = symbol in ['BTCUSDT', 'ETHUSDT', 'BNBUSDT']
    is_high_beta = symbol in ['NEARUSDT', 'DOGEUSDT', 'FILUSDT', 'APTUSDT', 'ARBUSDT', 'OPUSDT']
    
    dev_threshold = -3.5 if is_megacap else (-8.0 if is_high_beta else -6.0)
    
    # BNF Yakubari Extreme Oversold Bounce Signal (+15 Pts)
    bnf_yakubari_signal = ma_dev_pct <= dev_threshold and rsi_15m < 38
    if bnf_yakubari_signal:
        score += 15
        
    # BNF Shunbari Trend Continuation Pullback Signal (+10 Pts)
    ema_50 = calc_ema(closes_15m, 50)[-1]
    bnf_shunbari_signal = (abs(ma_dev_pct) <= 0.8) and (ema20_15m > ema_50) and rsi_15m >= 50
    if bnf_shunbari_signal:
        score += 10
        
    score = min(max(score, 0), 100)
    
    return {
        "symbol": symbol.upper(),
        "current_price": current_price,
        "confluence_score": score,
        "recommendation": recommendation,
        "macro_trend_4h": macro_trend,
        "reasons": reasons,
        "indicators": {
            "rsi_15m": round(rsi_15m, 2),
            "macd_hist_15m": round(macd_hist_15m, 4),
            "atr_15m": round(atr_15m, 4),
            "volume_surge": volume_surge
        },
        "institutional_risk_plan": {
            "account_balance": account_balance,
            "risk_pct": risk_percentage,
            "max_risk_usd": round(risk_usd, 2),
            "entry_price": round(current_price, 4),
            "stop_loss": round(stop_loss, 4),
            "break_even_trigger": round(break_even_trigger, 4),
            "take_profit_1_rr_2": round(take_profit_1, 4),
            "take_profit_2_rr_3_5": round(take_profit_2, 4),
            "position_size_units": round(units, 6),
            "position_size_usd": round(units * current_price, 2)
        }
    }

if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    symbol = sys.argv[1] if len(sys.argv) > 1 else 'BTCUSDT'
    bal = float(sys.argv[2]) if len(sys.argv) > 2 else 10000.0
    report = analyze_institutional_grade(symbol, bal)
    print(json.dumps(report, indent=2, ensure_ascii=False))
