"""
🌐 MACRO MCP GATEWAY — SÚPER-CEREBRO 5.0
Gateway unificado de Inteligencia Cuádruple MCP para Trading Cuantitativo Autónomo:
1. CoinGecko MCP: Trending Coins globales y Rotación Sectorial caliente.
2. Binance Order Flow MCP: Libro de órdenes profundo y microestructura taker en tiempo real.
3. News & Black Swan MCP: Centinela de noticias con veto automático ante hacks/demandas/fud.
4. Whale Flow Pulse: Detección de aceleración anómala de volumen institucional.
"""

import time
import json
import urllib.request
import xml.etree.ElementTree as ET
from typing import Dict, Any, List

_MCP_CACHE: Dict[str, Any] = {
    "coingecko_ts": 0.0,
    "coingecko_data": {},
    "news_ts": 0.0,
    "news_data": {},
    "whale_pulse_ts": 0.0,
    "whale_pulse_data": {}
}

CRITICAL_BLACK_SWAN_KEYWORDS = [
    'hack', 'hacked', 'exploit', 'scam', 'lawsuit', 'sec', 'ban', 
    'banned', 'crackdown', 'delist', 'delisting', 'insolvent', 
    'bankruptcy', 'investigation', 'arrest', 'stolen', 'drain'
]


# ─── 1. PILAR 1: COINGECKO MCP (TRENDING & SECTOR ROTATION) ───────────────────

def get_coingecko_trending_and_sectors() -> Dict[str, Any]:
    now = time.time()
    if now - _MCP_CACHE["coingecko_ts"] < 300 and _MCP_CACHE["coingecko_data"]:
        return _MCP_CACHE["coingecko_data"]

    trending_symbols = set()
    hot_sectors = []
    
    try:
        url_trend = "https://api.coingecko.com/api/v3/search/trending"
        req = urllib.request.Request(url_trend, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
        with urllib.request.urlopen(req, timeout=4) as resp:
            data = json.loads(resp.read().decode())
            for c in data.get("coins", []):
                sym = c.get("item", {}).get("symbol", "").upper()
                if sym:
                    trending_symbols.add(sym)
                    trending_symbols.add(f"{sym}USDT")
    except Exception:
        pass

    try:
        url_cat = "https://api.coingecko.com/api/v3/coins/categories?order=market_cap_change_24h_desc"
        req = urllib.request.Request(url_cat, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
        with urllib.request.urlopen(req, timeout=4) as resp:
            cats = json.loads(resp.read().decode())
            if isinstance(cats, list):
                for cat in cats[:5]:
                    name = cat.get("name", "")
                    chg = cat.get("market_cap_change_24h", 0.0) or 0.0
                    vol = cat.get("volume_24h", 0.0) or 0.0
                    if chg > 0:
                        hot_sectors.append({"name": name, "change_24h_pct": round(chg, 2), "volume_24h": vol})
    except Exception:
        pass

    res = {
        "timestamp": now,
        "trending_symbols": list(trending_symbols),
        "hot_sectors": hot_sectors[:3],
        "top_hot_sector": hot_sectors[0]["name"] if hot_sectors else "GENERAL_ALTCOINS"
    }

    _MCP_CACHE["coingecko_ts"] = now
    _MCP_CACHE["coingecko_data"] = res
    return res


# ─── 2. PILAR 2: BINANCE ORDER FLOW MCP ───────────────────────────────────────

def get_binance_order_flow_intelligence(symbol: str) -> Dict[str, Any]:
    try:
        import api_connector
        flow = api_connector.get_realtime_order_flow_momentum(symbol)
        return {
            "symbol": symbol,
            "taker_buy_pct": flow.get("taker_buy_pct", 50.0),
            "bid_dominance_pct": flow.get("bid_dominance_pct", 50.0),
            "is_bullish_order_flow": flow.get("is_bullish_order_flow", False),
            "is_exhaustion_or_dump": flow.get("is_exhaustion_or_dump", False)
        }
    except Exception:
        return {
            "symbol": symbol,
            "taker_buy_pct": 50.0,
            "bid_dominance_pct": 50.0,
            "is_bullish_order_flow": False,
            "is_exhaustion_or_dump": False
        }


# ─── 3. PILAR 3: NEWS & BLACK SWAN MCP SENTINEL ───────────────────────────────

def get_news_and_black_swan_sentinel(symbol: str = None) -> Dict[str, Any]:
    now = time.time()
    if now - _MCP_CACHE["news_ts"] > 360 or not _MCP_CACHE["news_data"]:
        headlines = []
        alerts = []
        try:
            url = "https://cointelegraph.com/rss"
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=4) as resp:
                xml_data = resp.read()
                root = ET.fromstring(xml_data)
                for item in root.findall('.//item')[:12]:
                    title = item.find('title').text if item.find('title') is not None else ""
                    if title:
                        headlines.append(title)
                        title_lower = title.lower()
                        for kw in CRITICAL_BLACK_SWAN_KEYWORDS:
                            import re
                            if re.search(rf'\b{kw}\b', title_lower):
                                alerts.append({"keyword": kw, "headline": title})
        except Exception:
            pass

        _MCP_CACHE["news_ts"] = now
        _MCP_CACHE["news_data"] = {"headlines": headlines, "alerts": alerts}

    cached = _MCP_CACHE["news_data"]
    headlines = cached.get("headlines", [])
    alerts = cached.get("alerts", [])

    symbol_veto = False
    veto_reason = ""
    if symbol:
        clean_sym = symbol.upper().replace("USDT", "")
        for alert in alerts:
            hl = alert.get("headline", "").upper()
            if clean_sym in hl.split():
                symbol_veto = True
                veto_reason = f"🚨 VETO NOTICIA CISNE NEGRO: Alerta '{alert['keyword']}' en '{alert['headline'][:60]}...'"
                break

    return {
        "recent_headlines": headlines[:5],
        "black_swan_alerts_count": len(alerts),
        "is_black_swan_alert_active": len(alerts) > 0,
        "symbol_veto": symbol_veto,
        "veto_reason": veto_reason
    }


# ─── 4. PILAR 4: WHALE FLOW ACCELERATION PULSE ────────────────────────────────

def get_whale_volume_pulse(symbol: str) -> Dict[str, Any]:
    try:
        import api_connector
        kl_1m = api_connector.get_klines(symbol, "1m", 15)
        if kl_1m and len(kl_1m) >= 10:
            vols = [float(k[5]) for k in kl_1m]
            recent_vol = vols[-1]
            avg_vol = sum(vols[:-1]) / len(vols[:-1]) if sum(vols[:-1]) > 0 else 1.0
            surge = round(recent_vol / avg_vol, 2)
            is_whale_pump = surge >= 2.5
            return {
                "symbol": symbol,
                "surge_ratio": surge,
                "is_whale_pump": is_whale_pump,
                "whale_status": "WHALE_SURGE" if is_whale_pump else "NORMAL"
            }
    except Exception:
        pass

    return {
        "symbol": symbol,
        "surge_ratio": 1.0,
        "is_whale_pump": False,
        "whale_status": "NORMAL"
    }


# ─── 5. GATEWAY CONSOLIDADO DE INTELIGENCIA CUÁDRUPLE ─────────────────────────

def get_combined_mcp_intelligence(symbol: str = None) -> Dict[str, Any]:
    cg = get_coingecko_trending_and_sectors()
    news = get_news_and_black_swan_sentinel(symbol)
    
    order_flow = {}
    whale_pulse = {}
    if symbol:
        order_flow = get_binance_order_flow_intelligence(symbol)
        whale_pulse = get_whale_volume_pulse(symbol)

    return {
        "coingecko_trending": cg.get("trending_symbols", []),
        "top_hot_sector": cg.get("top_hot_sector", "GENERAL"),
        "hot_sectors": cg.get("hot_sectors", []),
        "news_sentinel": news,
        "order_flow": order_flow,
        "whale_pulse": whale_pulse,
        "is_symbol_trending": (symbol in cg.get("trending_symbols", [])) if symbol else False
    }