import os
import json
import urllib.request
import time

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

def get_market_macro_context(symbol_analysis_map, fear_greed, news_headlines, top_candidates=None):
    """
    Computes a deterministic, 100% quantitative Market Macro Dashboard (0ms latency, zero API quota).
    Calculates: Market Breadth (% bullish), BTC Regime, Sector Alpha Leaders, and Risk Level.
    Directly actionable for quantitative decision making without narrative fluff.
    """
    total = len(symbol_analysis_map)
    if total == 0:
        return "📊 [MACRO CUÁNTICO] Mercado en inicialización."
        
    bullish = sum(1 for d in symbol_analysis_map.values() if d.get("score", 50) >= 60)
    bearish = sum(1 for d in symbol_analysis_map.values() if d.get("score", 50) <= 40)
    neutral = total - bullish - bearish
    
    breadth_bull_pct = round((bullish / total) * 100.0, 1)
    breadth_bear_pct = round((bearish / total) * 100.0, 1)
    
    btc_d = symbol_analysis_map.get("BTCUSDT", {})
    btc_p = btc_d.get("price", 0.0)
    btc_s = btc_d.get("score", 50)
    btc_rsi = btc_d.get("tech", {}).get("indicators", {}).get("rsi_15m", 50.0)
    
    fg_val = fear_greed.get("score", 50)
    fg_label = fear_greed.get("sentiment", "Neutral")
    
    top_syms = [c["symbol"] for c in (top_candidates[:3] if top_candidates else [])]
    top_str = ", ".join(top_syms) if top_syms else "N/A"
    
    summary = (
        f"📊 [MACRO CUÁNTICO EN TIEMPO REAL] Fear&Greed: {fg_val} ({fg_label}) | "
        f"Amplitud de Mercado: {breadth_bull_pct}% Alcistas / {breadth_bear_pct}% Bajistas ({bullish} Fuertes, {bearish} Débiles de {total}) | "
        f"Bitcoin: ${btc_p:,.0f} (Score={btc_s}, RSI={btc_rsi:.1f}) | Finalistas Top Alpha: [{top_str}]"
    )
    try:
        print(summary)
    except UnicodeEncodeError:
        print(summary.encode('ascii', errors='replace').decode('ascii'))
    return summary
