import requests
import json
import os
from datetime import datetime

# Secreto de GitHub para mayor seguridad
CMC_API_KEY = os.getenv("CMC_API_KEY", "")

def update_top_pairs():
    print(f"[{datetime.now().isoformat()}] Fetching top cryptos from CoinMarketCap...")
    headers = {
        'Accepts': 'application/json',
        'X-CMC_PRO_API_KEY': CMC_API_KEY,
    }
    params = {
        'start': '1',
        'limit': '300', # Fetch top 300 to ensure we get at least 100 Binance pairs
        'convert': 'USD'
    }
    
    try:
        res = requests.get('https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest', headers=headers, params=params)
        res.raise_for_status()
        data = res.json()
    except Exception as e:
        print(f"Failed to fetch from CMC: {e}")
        return
        
    cmc_symbols = [coin['symbol'] for coin in data.get('data', [])]
    
    print(f"Fetching valid Binance USDT pairs...")
    try:
        binance_res = requests.get('https://api.binance.com/api/v3/exchangeInfo')
        binance_res.raise_for_status()
        binance_data = binance_res.json()
        valid_binance_pairs = {s['symbol'] for s in binance_data['symbols'] if s['status'] == 'TRADING' and s['quoteAsset'] == 'USDT'}
    except Exception as e:
        print(f"Failed to fetch Binance exchange info: {e}")
        return
        
    top_100_pairs = []
    # Special mappings for CMC -> Binance
    mapping = {
        "IOTA": "IOTA", # Sometimes MIOTA
    }
    
    # Stablecoins to exclude
    stablecoins = {"USDT", "USDC", "FDUSD", "TUSD", "BUSD", "DAI", "USDD", "USDE", "USDTUSDT", "USDCUSDT", "FDUSDUSDT"}
    
    for sym in cmc_symbols:
        if sym in stablecoins:
            continue
            
        binance_sym = f"{mapping.get(sym, sym)}USDT"
        
        # Binance has some tokens like PEPE as 1000PEPE, SHIB as 1000SHIB on futures, but on SPOT it's just PEPEUSDT and SHIBUSDT
        # The real money bot trades SPOT for LONGs and FUTURES for SHORTs.
        # It's better to stick to standard SPOT names for now, the quant analytics will handle mapping if needed.
        if binance_sym in valid_binance_pairs:
            if binance_sym not in top_100_pairs:
                top_100_pairs.append(binance_sym)
                
        if len(top_100_pairs) >= 100:
            break
            
    if len(top_100_pairs) > 0:
        with open("top_100_pairs.json", "w", encoding="utf-8") as f:
            json.dump(top_100_pairs, f, indent=4)
        print(f"Successfully saved {len(top_100_pairs)} pairs to top_100_pairs.json")
        print(f"Top 5: {top_100_pairs[:5]}")
    else:
        print("Failed to map any pairs.")

def should_update():
    import time
    if not os.path.exists("top_100_pairs.json"):
        return True
    # If file is older than 1 hora (3600 seconds) - Utilizing more of the daily limit
    if time.time() - os.path.getmtime("top_100_pairs.json") > 3600:
        return True
    return False

if __name__ == "__main__":
    if should_update():
        if CMC_API_KEY:
            update_top_pairs()
        else:
            print("CMC_API_KEY is not set. Skipping update.")
    else:
        print("top_100_pairs.json is less than 1 hour old. Skipping CMC API call to save free tier limits.")
