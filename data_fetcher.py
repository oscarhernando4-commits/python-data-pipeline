import requests
import json
import os
import time
from datetime import datetime

CMC_API_KEY = os.getenv("CMC_API_KEY", "")

def get_cmc_top_coins():
    """Fetches top coins by Market Cap from CMC. Runs every 10 mins."""
    if not CMC_API_KEY:
        return []
    
    # Check if we should use cached CMC data to save quota (every 10 mins)
    cache_file = "cmc_cache.json"
    if os.path.exists(cache_file):
        if time.time() - os.path.getmtime(cache_file) < 600:
            try:
                with open(cache_file, "r") as f:
                    return json.load(f)
            except:
                pass

    print(f"[{datetime.now().isoformat()}] Fetching top cryptos from CoinMarketCap...")
    headers = {
        'Accepts': 'application/json',
        'X-CMC_PRO_API_KEY': CMC_API_KEY,
    }
    params = {'start': '1', 'limit': '300', 'convert': 'USD'}
    
    try:
        res = requests.get('https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest', headers=headers, params=params, timeout=10)
        res.raise_for_status()
        cmc_symbols = [coin['symbol'] for coin in res.json().get('data', [])]
        print(f"CMC API exitosa. Se obtuvieron {len(cmc_symbols)} símbolos (Market Cap).")
        with open(cache_file, "w") as f:
            json.dump(cmc_symbols, f)
        return cmc_symbols
    except Exception as e:
        print(f"Fallo CMC (cuota/red): {e}")
        return []

def get_binance_top_volume_coins(valid_pairs):
    """Fetches top coins by 24H Volume from Binance directly (100% Free).
    Enforces minimum $5,000,000 USD volume to ensure deep institutional liquidity and tight spreads."""
    print("Obteniendo clasificación por volumen 24H nativo de Binance (Mínimo $5M USD)...")
    try:
        ticker_res = requests.get('https://data-api.binance.vision/api/v3/ticker/24hr', timeout=10)
        tickers = ticker_res.json()
        # Exclude coins with 24h volume < $5,000,000 USD (Ensures deep institutional liquidity & 0.02% spread)
        usdt_tickers = [t for t in tickers if t['symbol'] in valid_pairs and float(t.get('quoteVolume', 0)) >= 5000000.0]
        usdt_tickers.sort(key=lambda x: float(x['quoteVolume']), reverse=True)
        # Take top 100 by volume
        vol_symbols = [t['symbol'].replace('USDT', '') for t in usdt_tickers[:100]]
        print(f"Binance API exitosa. Se obtuvieron {len(vol_symbols)} símbolos con Volumen >= $5M USD.")
        return vol_symbols
    except Exception as e:
        print(f"Fallo Binance 24H Volume: {e}")
        return []

import multi_timeframe_analyzer

# Exhaustive Blacklist of Stablecoins, Fiat-Pegged Assets, Synthetic Collateral, and Risky/Hacked tokens
STABLECOIN_BLACKLIST = {
    "NIGHT", "NIGHTUSDT", "COMP", "COMPUSDT",
    "PAXG", "PAXGUSDT", "XAUT", "XAUTUSDT", "GRAM", "GRAMUSDT", "PORTAL", "PORTALUSDT",
    "U", "UUSDT", "USD", "USDE", "USD0", "USDS", "USDF", "USDC", "FDUSD", "TUSD", "BUSD", "DAI", "USDD", "RLUSD", "USD1",
    "EUR", "AEUR", "WBTC", "TBTC", "USDS", "USTC", "FRAX", "PYUSD", "USD0", "SNDKB", "SNDK", "USD", "EURUSDT", "AEURUSDT",
    "RLUSDUSDT", "USD1USDT", "USDCUSDT", "FDUSDUSDT", "TUSDUSDT", "BUSDUSDT", "DAIUSDT", "USDDUSDT", "USDEUSDT", "FRAXUSDT",
    "PYUSDUSDT", "WBTCUSDT", "TBTCUSDT", "EURI", "EURIOUSDT", "CRCLB", "CRCLBUSDT", "SPCXB", "SPCXBUSDT", "QQQB", "QQQBUSDT",
    "BMT", "BMTUSDT", "NOM", "NOMUSDT", "WCT", "WCTUSDT", "BERA", "BERAUSDT", "EPX", "EPXUSDT", "VANRY", "VANRYUSDT",
    "SCRT", "SCRTUSDT", "TREE", "TREEUSDT", "NXPC", "NXPCUSDT", "ALLO", "ALLOUSDT", "PLUME", "PLUMEUSDT",
    "ACE", "ACEUSDT", "MMT", "MMTUSDT", "OG", "OGUSDT", "PROS", "PROSUSDT", "KP3R", "KP3RUSDT",
    "GFT", "GFTUSDT", "OOKI", "OOKIUSDT", "AMB", "AMBUSDT", "BIFI", "BIFIUSDT", "VOXEL", "VOXELUSDT",
    "WRX", "WRXUSDT", "DOCK", "DOCKUSDT", "POLS", "POLSUSDT", "MDX", "MDXUSDT", "FIRO", "FIROUSDT",
    "NBS", "NBSUSDT", "LTO", "LTOUSDT", "FOR", "FORUSDT", "VITE", "VITEUSDT", "KEY", "KEYUSDT",
    "CREAM", "CREAMUSDT", "MBL", "MBLUSDT", "AKRO", "AKROUSDT", "UNFI", "UNFIUSDT", "WING", "WINGUSDT",
    "HARD", "HARDUSDT", "DREP", "DREPUSDT", "TROY", "TROYUSDT", "BURGER", "BURGERUSDT", "JUV", "JUVUSDT",
    "CITY", "CITYUSDT", "PSG", "PSGUSDT", "ATM", "ATMUSDT", "BAR", "BARUSDT", "ASR", "ASRUSDT", "ACM", "ACMUSDT",
    "CHIP", "CHIPUSDT", "UTK", "UTKUSDT", "BANANA", "BANANAUSDT"
}

def update_top_pairs():
    print(f"Fetching valid Binance USDT pairs...")
    try:
        binance_res = requests.get('https://data-api.binance.vision/api/v3/exchangeInfo', timeout=10)
        binance_res.raise_for_status()
        valid_binance_pairs = {s['symbol'] for s in binance_res.json()['symbols'] if s['status'] == 'TRADING' and s['quoteAsset'] == 'USDT'}
    except Exception as e:
        print(f"Failed to fetch Binance exchange info: {e}")
        return

    cmc_symbols = get_cmc_top_coins()
    binance_vol_symbols = get_binance_top_volume_coins(valid_binance_pairs)
    
    # Merge both lists to get the ultimate list (Market Cap + High Volume)
    raw_symbols = []
    max_len = max(len(cmc_symbols), len(binance_vol_symbols))
    for i in range(max_len):
        if i < len(cmc_symbols) and cmc_symbols[i] not in raw_symbols:
            raw_symbols.append(cmc_symbols[i])
        if i < len(binance_vol_symbols) and binance_vol_symbols[i] not in raw_symbols:
            raw_symbols.append(binance_vol_symbols[i])
    
    top_100_pairs = []
    mapping = {"IOTA": "IOTA"}
    
    for sym in raw_symbols:
        clean_sym = sym.upper().strip()
        if clean_sym in STABLECOIN_BLACKLIST or f"{clean_sym}USDT" in STABLECOIN_BLACKLIST:
            continue
        if multi_timeframe_analyzer.is_stablecoin(clean_sym) or multi_timeframe_analyzer.is_stablecoin(f"{clean_sym}USDT"):
            continue
        # Filter out weird ASCII/Chinese symbols
        if not all(ord(c) < 128 for c in sym):
            continue
            
        binance_sym = f"{mapping.get(sym, sym)}USDT"
        if binance_sym in STABLECOIN_BLACKLIST or multi_timeframe_analyzer.is_stablecoin(binance_sym):
            continue
        
        # Must exist in Spot
        if binance_sym in valid_binance_pairs and binance_sym not in top_100_pairs:
            top_100_pairs.append(binance_sym)
                
        if len(top_100_pairs) >= 120:  # Expanded to 120 pairs for more opportunities!
            break
            
    if len(top_100_pairs) > 0:
        with open("top_100_pairs.json", "w", encoding="utf-8") as f:
            json.dump(top_100_pairs, f, indent=4)
        print(f"Successfully saved {len(top_100_pairs)} HIBRID pairs to top_100_pairs.json")
        print(f"Top 5 Híbrido: {top_100_pairs[:5]}")
    else:
        print("Failed to map any pairs.")

def get_binance_institutional_sentiment(symbol):
    """
    Fetches Binance Official Institutional Sentiment Data:
    - Global Long/Short Trader Account Ratio
    - Top Trader Position Ratio
    Returns: {"long_account_pct": float, "short_account_pct": float, "long_short_ratio": float, "sentiment_label": str}
    """
    try:
        clean_sym = symbol.upper().strip()
        if not clean_sym.endswith("USDT"):
            clean_sym = f"{clean_sym}USDT"
        url = f"https://fapi.binance.com/futures/data/globalLongShortAccountRatio?symbol={clean_sym}&period=15m&limit=1"
        res = requests.get(url, timeout=5)
        if res.status_code == 200:
            data = res.json()
            if data and isinstance(data, list) and len(data) > 0:
                item = data[0]
                long_pct = float(item.get("longAccount", 0.5)) * 100.0
                short_pct = float(item.get("shortAccount", 0.5)) * 100.0
                ratio = float(item.get("longShortRatio", 1.0))
                
                label = "🟢 INSTITUCIONAL MUY ALCISTA (Whales Long)" if ratio >= 1.5 else ("🔴 INSTITUCIONAL BAJISTA (Whales Short)" if ratio <= 0.7 else "⚪ NEUTRAL")
                return {
                    "long_account_pct": long_pct,
                    "short_account_pct": short_pct,
                    "long_short_ratio": ratio,
                    "sentiment_label": label
                }
    except Exception:
        pass
    return {
        "long_account_pct": 50.0,
        "short_account_pct": 50.0,
        "long_short_ratio": 1.0,
        "sentiment_label": "⚪ NEUTRAL (Sin datos de futuros)"
    }

def fetch_wall_street_macro_context():
    """
    Fetches real-time Wall Street Macro Indices (S&P 500 & NASDAQ) to enhance
    the Super-Brain's market bias intelligence.
    """
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        res_nasdaq = requests.get('https://query1.finance.yahoo.com/v8/finance/chart/%5EIXIC', headers=headers, timeout=5)
        meta_nasdaq = res_nasdaq.json()['chart']['result'][0]['meta']
        nasdaq_price = meta_nasdaq['regularMarketPrice']
        nasdaq_prev = meta_nasdaq['previousClose']
        nasdaq_change_pct = round(((nasdaq_price - nasdaq_prev) / nasdaq_prev) * 100.0, 2)

        res_sp = requests.get('https://query1.finance.yahoo.com/v8/finance/chart/%5EGSPC', headers=headers, timeout=5)
        meta_sp = res_sp.json()['chart']['result'][0]['meta']
        sp_price = meta_sp['regularMarketPrice']
        sp_prev = meta_sp['previousClose']
        sp_change_pct = round(((sp_price - sp_prev) / sp_prev) * 100.0, 2)

        macro_regime = "🟢 WALL STREET ALCISTA (NASDAQ " + f"{nasdaq_change_pct:+.2f}%)" if nasdaq_change_pct > 0.3 else ("🔴 WALL STREET BAJISTA (NASDAQ " + f"{nasdaq_change_pct:+.2f}%)" if nasdaq_change_pct < -0.5 else "⚪ WALL STREET NEUTRAL (NASDAQ " + f"{nasdaq_change_pct:+.2f}%)")

        return {
            "nasdaq_change_pct": nasdaq_change_pct,
            "sp_change_pct": sp_change_pct,
            "macro_regime": macro_regime
        }
    except Exception:
        return {"nasdaq_change_pct": 0.0, "sp_change_pct": 0.0, "macro_regime": "⚪ WALL STREET NEUTRAL"}

# Compatibility aliases
fetch_top_100_pairs = update_top_pairs

if __name__ == "__main__":
    update_top_pairs()

