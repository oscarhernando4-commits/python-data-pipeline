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
    """Fetches top coins by 24H Volume from Binance directly (100% Free)."""
    print("Obteniendo clasificación por volumen 24H nativo de Binance...")
    try:
        ticker_res = requests.get('https://data-api.binance.vision/api/v3/ticker/24hr', timeout=10)
        tickers = ticker_res.json()
        usdt_tickers = [t for t in tickers if t['symbol'] in valid_pairs]
        usdt_tickers.sort(key=lambda x: float(x['quoteVolume']), reverse=True)
        # Take top 150 by volume
        vol_symbols = [t['symbol'].replace('USDT', '') for t in usdt_tickers[:150]]
        print(f"Binance API exitosa. Se obtuvieron {len(vol_symbols)} símbolos (Volumen).")
        return vol_symbols
    except Exception as e:
        print(f"Fallo Binance 24H Volume: {e}")
        return []

def update_top_pairs():
    print(f"Fetching valid Binance USDT pairs...")
    try:
        binance_res = requests.get('https://data-api.binance.vision/api/v3/exchangeInfo', timeout=10)
        binance_res.raise_for_status()
        valid_binance_pairs = {s['symbol'] for s in binance_res.json()['symbols'] if s['status'] == 'TRADING' and s['quoteAsset'] == 'USDT'}
    except Exception as e:
        print(f"Failed to fetch Binance exchange info: {e}")
        return
        
    print(f"Fetching valid Binance Futures USDT pairs...")
    try:
        f_res = requests.get('https://fapi.binance.com/fapi/v1/exchangeInfo', timeout=10)
        f_res.raise_for_status()
        futures_pairs = {s['symbol'] for s in f_res.json()['symbols'] if s['status'] == 'TRADING' and s['quoteAsset'] == 'USDT'}
    except Exception as e:
        print(f"Failed to fetch Futures info: {e}")
        futures_pairs = set()

    cmc_symbols = get_cmc_top_coins()
    binance_vol_symbols = get_binance_top_volume_coins(valid_binance_pairs)
    
    # Merge both lists to get the ultimate list (Market Cap + High Volume)
    raw_symbols = []
    # Interleave to prioritize coins that are high on BOTH lists
    max_len = max(len(cmc_symbols), len(binance_vol_symbols))
    for i in range(max_len):
        if i < len(cmc_symbols) and cmc_symbols[i] not in raw_symbols:
            raw_symbols.append(cmc_symbols[i])
        if i < len(binance_vol_symbols) and binance_vol_symbols[i] not in raw_symbols:
            raw_symbols.append(binance_vol_symbols[i])
    
    top_100_pairs = []
    stablecoins = {"USDT", "USDC", "FDUSD", "TUSD", "BUSD", "DAI", "USDD", "USDE", "USDTUSDT", "USDCUSDT", "FDUSDUSDT"}
    mapping = {"IOTA": "IOTA"}
    
    for sym in raw_symbols:
        if sym in stablecoins:
            continue
        # Filter out weird ASCII/Chinese symbols
        if not all(ord(c) < 128 for c in sym):
            continue
            
        binance_sym = f"{mapping.get(sym, sym)}USDT"
        
        # Must exist in BOTH Spot (for Longs) and Futures (for Shorts)
        if binance_sym in valid_binance_pairs and binance_sym in futures_pairs and binance_sym not in top_100_pairs:
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

if __name__ == "__main__":
    update_top_pairs()
