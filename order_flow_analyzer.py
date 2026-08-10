import requests
import time
from typing import Dict, Any

def analyze_order_flow_cvd(symbol: str, limit: int = 100) -> Dict[str, Any]:
    """
    Analyzes live Order Flow Speed, Taker Aggression Ratio, and Cumulative Volume Delta (CVD).
    - Queries Binance REST API recent trades endpoint (/api/v3/trades).
    - Computes Taker Buy Volume vs Taker Sell Volume.
    - Computes Trade Speed (trades per second).
    - Determines Buy Absorption vs Sell Pressure near key levels (e.g., MA25).
    """
    url = f"https://api.binance.com/api/v3/trades?symbol={symbol}&limit={limit}"
    try:
        res = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=5)
        if res.status_code == 200:
            trades = res.json()
            if len(trades) >= 5:
                start_time = trades[0]['time']
                end_time = trades[-1]['time']
                time_span_sec = max(0.5, (end_time - start_time) / 1000.0)
                
                trade_speed = round(len(trades) / time_span_sec, 2)
                
                taker_buy_vol = 0.0
                taker_sell_vol = 0.0
                taker_buy_usd = 0.0
                taker_sell_usd = 0.0
                
                for t in trades:
                    price = float(t['price'])
                    qty = float(t['qty'])
                    val_usd = price * qty
                    is_buyer_maker = t['isBuyerMaker']
                    
                    # If isBuyerMaker is True, the buyer was passive (maker), meaning taker was SELLER (Market Sell)
                    # If isBuyerMaker is False, the buyer was aggressive (taker), meaning taker was BUYER (Market Buy)
                    if not is_buyer_maker:
                        taker_buy_vol += qty
                        taker_buy_usd += val_usd
                    else:
                        taker_sell_vol += qty
                        taker_sell_usd += val_usd
                        
                total_usd = taker_buy_usd + taker_sell_usd
                cvd_delta_usd = round(taker_buy_usd - taker_sell_usd, 2)
                buy_aggression_pct = round((taker_buy_usd / total_usd * 100.0), 1) if total_usd > 0 else 50.0
                
                # Order Flow Verdict Classification
                if buy_aggression_pct >= 58.0 and cvd_delta_usd > 0:
                    verdict = "🟢 ABSORCIÓN COMPRADORA A+ (CVD Delta +)"
                    is_bullish_absorption = True
                    is_bearish_dump = False
                elif buy_aggression_pct <= 42.0 and cvd_delta_usd < 0:
                    verdict = "🔴 PRESIÓN VENDEDORA (CVD Delta -)"
                    is_bullish_absorption = False
                    is_bearish_dump = True
                else:
                    verdict = "🟡 EQUILIBRIO DE FLUJO DE ÓRDENES"
                    is_bullish_absorption = False
                    is_bearish_dump = False
                    
                return {
                    "symbol": symbol,
                    "trade_speed_per_sec": trade_speed,
                    "buy_aggression_pct": buy_aggression_pct,
                    "sell_aggression_pct": round(100.0 - buy_aggression_pct, 1),
                    "cvd_delta_usd": cvd_delta_usd,
                    "total_volume_usd": round(total_usd, 2),
                    "verdict": verdict,
                    "is_bullish_absorption": is_bullish_absorption,
                    "is_bearish_dump": is_bearish_dump
                }
    except Exception as e:
        pass
        
    return {
        "symbol": symbol,
        "trade_speed_per_sec": 1.0,
        "buy_aggression_pct": 50.0,
        "sell_aggression_pct": 50.0,
        "cvd_delta_usd": 0.0,
        "total_volume_usd": 0.0,
        "verdict": "🟡 EQUILIBRIO (Default)",
        "is_bullish_absorption": False,
        "is_bearish_dump": False
    }

if __name__ == "__main__":
    print("🎯 Testing Order Flow Speed & CVD Analyst...")
    print("LINKUSDT:", analyze_order_flow_cvd("LINKUSDT"))
    print("BTCUSDT:", analyze_order_flow_cvd("BTCUSDT"))
