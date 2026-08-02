"""
Sector Clustering & Capital Rotation Analyzer
Maps 120 cryptocurrencies into 6 core sector clusters and identifies dominant institutional capital inflows.
"""

import json

SECTOR_MAP = {
    "AI & Big Data": ["RENDERUSDT", "FETUSDT", "NEARUSDT", "TAOUSDT", "AGIXUSDT", "WLDUSDT", "ASTERUSDT", "GRTUSDT", "OCEANUSDT", "AKTUSDT"],
    "Layer 1 & Infrastructure": ["BTCUSDT", "ETHUSDT", "SOLUSDT", "BNBUSDT", "ADAUSDT", "AVAXUSDT", "SUIUSDT", "APTUSDT", "DOTUSDT", "ATOMUSDT", "TRXUSDT", "HBARUSDT", "SEIUSDT", "TONUSDT"],
    "DeFi & Exchanges": ["UNIUSDT", "AAVEUSDT", "CAKEUSDT", "INJUSDT", "RAYUSDT", "ENAUSDT", "CRVUSDT", "MKRUSDT", "SNXUSDT", "COMPUSDT", "JUPUSDT"],
    "DePIN & Storage": ["FILUSDT", "ARUSDT", "THETAUSDT", "LPTUSDT", "STORJUSDT"],
    "Real World Assets (RWA) & Precious Metals": ["XAUTUSDT", "PAXGUSDT", "ONDOUSDT", "OMUSDT", "LINKUSDT"],
    "Memes & High Volatility": ["DOGEUSDT", "SHIBUSDT", "PEPEUSDT", "BONKUSDT", "WIFUSDT", "FLOKIUSDT", "NEIROUSDT", "MEMEUSDT", "BRETTUSDT", "TURBOUSDT"]
}

def analyze_sector_rotation(analyzed_candidates_map):
    """
    Analyzes the average confluence score and volume surge for each crypto sector cluster.
    Returns the top performing sector receiving institutional capital inflows.
    """
    sector_summary = {}
    
    for sector_name, symbols in SECTOR_MAP.items():
        scores = []
        vol_surges = []
        
        for sym in symbols:
            if sym in analyzed_candidates_map:
                cand = analyzed_candidates_map[sym]
                score = cand.get("score", 50)
                vol_surge = cand.get("tech", {}).get("indicators", {}).get("volume_surge", 1.0)
                scores.append(score)
                vol_surges.append(vol_surge)
                
        avg_score = sum(scores) / len(scores) if scores else 50.0
        avg_vol_surge = sum(vol_surges) / len(vol_surges) if vol_surges else 1.0
        
        sector_summary[sector_name] = {
            "avg_score": round(avg_score, 1),
            "avg_volume_surge": round(avg_vol_surge, 2),
            "tracked_symbols_count": len(scores),
            "status": "🔥 Rotación Masiva Entrante" if avg_score >= 60 and avg_vol_surge >= 1.5 else ("🔵 Sector Estable" if avg_score >= 45 else "🔴 Sector en Distribución")
        }
        
    sorted_sectors = sorted(sector_summary.items(), key=lambda x: x[1]["avg_score"], reverse=True)
    top_sector_name, top_sector_info = sorted_sectors[0] if sorted_sectors else ("Layer 1 & Infrastructure", {"avg_score": 50.0, "avg_volume_surge": 1.0, "status": "Neutral"})
    
    return {
        "top_sector": top_sector_name,
        "top_sector_score": top_sector_info["avg_score"],
        "top_sector_vol_surge": top_sector_info["avg_volume_surge"],
        "all_sectors": sector_summary
    }

def get_symbol_sector(symbol):
    """Returns the sector name for a given cryptocurrency symbol."""
    sym_upper = symbol.upper()
    for sector_name, symbols in SECTOR_MAP.items():
        if sym_upper in symbols:
            return sector_name
    return "Altcoins Generales"

if __name__ == "__main__":
    test_data = {
        "BTCUSDT": {"score": 50, "tech": {"indicators": {"volume_surge": 1.1}}},
        "XAUTUSDT": {"score": 75, "tech": {"indicators": {"volume_surge": 2.5}}},
        "CAKEUSDT": {"score": 70, "tech": {"indicators": {"volume_surge": 3.3}}}
    }
    print(analyze_sector_rotation(test_data))
