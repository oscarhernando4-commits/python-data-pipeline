"""
Orderbook Liquidity Depth & Imbalance Analyzer for Binance
Calculates Bid/Ask volume ratios across top orderbook depth levels to detect whale walls,
incorporates Anti-Spoofing Concentration analysis, and Live CVD (Cumulative Volume Delta) flow.
"""

import os
import json
import requests

session = requests.Session()
session.headers.update({'User-Agent': 'Mozilla/5.0'})

def fetch_live_cvd_flow(symbol, limit=60, proxies=None):
    """
    Fetches real-time aggressive market trades (Taker Volume) via Binance aggTrades.
    Calculates Cumulative Volume Delta (CVD) to separate real buying from passive spoofing:
    - m == False: Taker Buy (Aggressive market buy hitting the ask)
    - m == True:  Taker Sell (Aggressive market sell dumping into the bid)
    """
    mirrors = [
        f"https://data-api.binance.vision/api/v3/aggTrades?symbol={symbol}&limit={limit}",
        f"https://api.binance.com/api/v3/aggTrades?symbol={symbol}&limit={limit}",
        f"https://api1.binance.com/api/v3/aggTrades?symbol={symbol}&limit={limit}"
    ]
    
    for url in mirrors:
        try:
            res = session.get(url, proxies=proxies, timeout=3)
            if res.status_code == 200:
                trades = res.json()
                if isinstance(trades, list) and len(trades) > 0:
                    buy_vols = [float(t['p']) * float(t['q']) for t in trades if not t.get('m', False)]
                    sell_vols = [float(t['p']) * float(t['q']) for t in trades if t.get('m', False)]
                    
                    buy_vol_usdt = sum(buy_vols)
                    sell_vol_usdt = sum(sell_vols)
                    total_vol = buy_vol_usdt + sell_vol_usdt
                    
                    buy_ratio = round((buy_vol_usdt / total_vol) * 100.0, 1) if total_vol > 0 else 50.0
                    delta_usdt = round(buy_vol_usdt - sell_vol_usdt, 2)
                    is_bullish_cvd = buy_ratio >= 55.0
                    
                    cvd_status = (
                        f"🟢 Inyección Taker Compradora ({buy_ratio:.1f}% Compras | Delta +${delta_usdt:,.0f})"
                        if buy_ratio >= 58.0 else (
                            f"🔴 Presión Taker Vendedora ({100.0 - buy_ratio:.1f}% Ventas | Delta -${abs(delta_usdt):,.0f})"
                            if buy_ratio <= 42.0 else f"⚪ Flujo Taker Equilibrado ({buy_ratio:.1f}%)"
                        )
                    )
                    
                    return {
                        "cvd_buy_ratio": buy_ratio,
                        "cvd_delta_usdt": delta_usdt,
                        "is_bullish_cvd": is_bullish_cvd,
                        "cvd_status": cvd_status
                    }
        except Exception:
            continue
            
    return {
        "cvd_buy_ratio": 50.0,
        "cvd_delta_usdt": 0.0,
        "is_bullish_cvd": False,
        "cvd_status": "⚪ Flujo Taker Neutral (Sin datos)"
    }

def fetch_orderbook_depth(symbol, limit=20, proxies=None):
    """
    Fetches live orderbook depth for a symbol and calculates Bid/Ask Imbalance Ratio + Anti-Spoofing + Live CVD Flow.
    Uses public multi-mirror endpoints (0 Fixie Quota).
    """
    cvd_data = fetch_live_cvd_flow(symbol, limit=60, proxies=None)
    
    mirrors = [
        f"https://data-api.binance.vision/api/v3/depth?symbol={symbol}&limit={limit}",
        f"https://api1.binance.com/api/v3/depth?symbol={symbol}&limit={limit}",
        f"https://api2.binance.com/api/v3/depth?symbol={symbol}&limit={limit}",
        f"https://api3.binance.com/api/v3/depth?symbol={symbol}&limit={limit}",
        f"https://api.binance.com/api/v3/depth?symbol={symbol}&limit={limit}"
    ]
    
    data = {}
    for url in mirrors:
        try:
            response = session.get(url, timeout=3)
            if response.status_code == 200:
                data = response.json()
                if "bids" in data and "asks" in data:
                    break
        except Exception:
            continue
        
    try:
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
        
        is_genuine_whale_wall = (bid_dominance_pct >= 62.0) and not is_spoof_risk
        
        liquidity_status = "🔥 Muro de Ballenas Genuino" if (is_genuine_whale_wall and cvd_data["is_bullish_cvd"]) else (
            "⚠️ Muro Sospechoso (Posible Spoofing)" if (bid_dominance_pct >= 62.0 and is_spoof_risk) else (
                "🔴 Presión Vendedora" if bid_dominance_pct <= 38.0 else "🔵 Liquidez Neutral"
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
            "ask_dominance_pct": round(100.0 - bid_dominance_pct, 1),
            "whale_wall_detected": is_genuine_whale_wall,
            "is_spoof_risk": is_spoof_risk,
            "top_bid_concentration": round(top_bid_concentration * 100.0, 1),
            "liquidity_status": liquidity_status,
            "cvd_buy_ratio": cvd_data["cvd_buy_ratio"],
            "cvd_delta_usdt": cvd_data["cvd_delta_usdt"],
            "is_bullish_cvd": cvd_data["is_bullish_cvd"],
            "cvd_status": cvd_data["cvd_status"]
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
            "liquidity_status": f"⚪ Neutral (Fallback: {e})",
            "cvd_buy_ratio": cvd_data["cvd_buy_ratio"],
            "cvd_delta_usdt": cvd_data["cvd_delta_usdt"],
            "is_bullish_cvd": cvd_data["is_bullish_cvd"],
            "cvd_status": cvd_data["cvd_status"]
        }

if __name__ == "__main__":
    print(fetch_orderbook_depth("BTCUSDT"))
