"""
Orderbook Liquidity Depth & Imbalance Analyzer for Binance
Calculates Bid/Ask volume ratios across top orderbook depth levels to detect whale walls,
and incorporates Anti-Spoofing Concentration analysis to filter fake liquidity walls.
"""

import os
import json
import urllib.request

def fetch_orderbook_depth(symbol, limit=20, proxies=None):
    """
    Fetches live orderbook depth for a symbol and calculates Bid/Ask Imbalance Ratio + Anti-Spoofing.
    Returns:
    - bid_volume: Total USDT volume on buy side
    - ask_volume: Total USDT volume on sell side
    - imbalance_ratio: bid_volume / (bid_volume + ask_volume)
    - bid_dominance_pct: percentage of bid dominance
    - whale_wall_detected: True if bid_dominance_pct >= 65% and not spoofed
    - is_spoof_risk: True if a single level contains > 70% of total volume
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
        
        bid_vols = [float(p) * float(q) for p, q in bids]
        ask_vols = [float(p) * float(q) for p, q in asks]
        
        bid_vol_usdt = sum(bid_vols)
        ask_vol_usdt = sum(ask_vols)
        
        total_vol = bid_vol_usdt + ask_vol_usdt
        imbalance_ratio = (bid_vol_usdt / total_vol) if total_vol > 0 else 0.5
        bid_dominance_pct = round(imbalance_ratio * 100.0, 1)
        
        # Anti-Spoofing: check if top single order is > 70% of all bids
        max_single_bid = max(bid_vols) if bid_vols else 0.0
        top_bid_concentration = (max_single_bid / bid_vol_usdt) if bid_vol_usdt > 0 else 0.0
        is_spoof_risk = top_bid_concentration > 0.70 and len(bids) >= 10
        
        is_genuine_whale_wall = (bid_dominance_pct >= 65.0) and not is_spoof_risk
        
        liquidity_status = "🔥 Muro de Ballenas Genuino" if is_genuine_whale_wall else (
            "⚠️ Muro Sospechoso (Posible Spoofing)" if (bid_dominance_pct >= 65.0 and is_spoof_risk) else (
                "🔴 Presión Vendedora" if bid_dominance_pct <= 35.0 else "🔵 Liquidez Neutral"
            )
        )
        
        return {
            "symbol": symbol,
            "top_bid": top_bid,
            "top_ask": top_ask,
            "spread_pct": spread_pct,
            "is_low_spread": is_low_spread,
            "bid_vol_usdt": round(bid_vol_usdt, 2),
            "ask_vol_usdt": round(ask_vol_usdt, 2),
            "bid_dominance_pct": bid_dominance_pct,
            "whale_wall_detected": is_genuine_whale_wall,
            "is_spoof_risk": is_spoof_risk,
            "top_bid_concentration": round(top_bid_concentration * 100.0, 1),
            "liquidity_status": liquidity_status
        }
    except Exception as e:
        return {
            "symbol": symbol,
            "bid_vol_usdt": 0.0,
            "ask_vol_usdt": 0.0,
            "bid_dominance_pct": 50.0,
            "whale_wall_detected": False,
            "is_spoof_risk": False,
            "top_bid_concentration": 0.0,
            "liquidity_status": f"⚪ Neutral (Fallback: {e})"
        }

if __name__ == "__main__":
    print(fetch_orderbook_depth("BTCUSDT"))
