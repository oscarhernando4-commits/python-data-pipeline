"""
Orderbook Liquidity Depth & Imbalance Analyzer for Binance
Calculates Bid/Ask volume ratios across top orderbook depth levels to detect whale walls.
"""

import os
import json
import urllib.request

def fetch_orderbook_depth(symbol, limit=20, proxies=None):
    """
    Fetches live orderbook depth for a symbol and calculates Bid/Ask Imbalance Ratio.
    Returns:
    - bid_volume: Total USDT volume on buy side
    - ask_volume: Total USDT volume on sell side
    - imbalance_ratio: bid_volume / (bid_volume + ask_volume)
    - bid_dominance_pct: percentage of bid dominance
    - whale_wall_detected: True if bid_dominance_pct >= 65%
    """
    url = f"https://api.binance.com/api/v3/depth?symbol={symbol}&limit={limit}"
    
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        if proxies:
            handler = urllib.request.ProxyHandler(proxies)
            opener = urllib.request.build_opener(handler)
            response = opener.open(req, timeout=5)
        else:
            response = urllib.request.urlopen(req, timeout=5)
            
        data = json.loads(response.read().decode('utf-8'))
        
        bids = data.get("bids", [])
        asks = data.get("asks", [])
        
        top_bid = float(bids[0][0]) if bids else 0.0
        top_ask = float(asks[0][0]) if asks else 0.0
        spread_pct = round(((top_ask - top_bid) / top_bid) * 100.0, 3) if top_bid > 0 else 0.0
        is_low_spread = spread_pct <= 0.25
        
        bid_vol_usdt = sum(float(p) * float(q) for p, q in bids)
        ask_vol_usdt = sum(float(p) * float(q) for p, q in asks)
        
        total_vol = bid_vol_usdt + ask_vol_usdt
        imbalance_ratio = (bid_vol_usdt / total_vol) if total_vol > 0 else 0.5
        bid_dominance_pct = round(imbalance_ratio * 100.0, 1)
        
        return {
            "symbol": symbol,
            "top_bid": top_bid,
            "top_ask": top_ask,
            "spread_pct": spread_pct,
            "is_low_spread": is_low_spread,
            "bid_vol_usdt": round(bid_vol_usdt, 2),
            "ask_vol_usdt": round(ask_vol_usdt, 2),
            "bid_dominance_pct": bid_dominance_pct,
            "whale_wall_detected": bid_dominance_pct >= 65.0,
            "liquidity_status": "🔥 Muro de Ballenas Compradoras" if bid_dominance_pct >= 65.0 else ("🔴 Presión Vendedora" if bid_dominance_pct <= 35.0 else "🔵 Liquidez Neutral")
        }
    except Exception as e:
        return {
            "symbol": symbol,
            "bid_vol_usdt": 0.0,
            "ask_vol_usdt": 0.0,
            "bid_dominance_pct": 50.0,
            "whale_wall_detected": False,
            "liquidity_status": f"⚪ Neutral (Fallback: {e})"
        }

if __name__ == "__main__":
    print(fetch_orderbook_depth("BTCUSDT"))
