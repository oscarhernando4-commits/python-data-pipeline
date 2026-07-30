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
        cmc_symbols = [coin['symbol'] for coin in data.get('data', [])]
        print(f"✅ CMC API exitosa. Se obtuvieron {len(cmc_symbols)} símbolos.")
    except Exception as e:
        print(f"Fallo CMC (posible limite de cuota): {e}. Usando FALLBACK nativo de Binance...")
        cmc_symbols = [] # Lo llenaremos con Binance
        
    print(f"Fetching valid Binance USDT pairs...")
    try:
        binance_res = requests.get('https://data-api.binance.vision/api/v3/exchangeInfo')
        binance_res.raise_for_status()
        binance_data = binance_res.json()
        valid_binance_pairs = {s['symbol'] for s in binance_data['symbols'] if s['status'] == 'TRADING' and s['quoteAsset'] == 'USDT'}
        
        # Si CMC falló, usamos las monedas con más volumen de las últimas 24H en Binance
        if not cmc_symbols:
            print("Activando PLAN B: Clasificando por volumen 24H de Binance...")
            ticker_res = requests.get('https://data-api.binance.vision/api/v3/ticker/24hr')
            tickers = ticker_res.json()
            # Filtrar solo USDT y ordenar por volumen
            usdt_tickers = [t for t in tickers if t['symbol'] in valid_binance_pairs]
            usdt_tickers.sort(key=lambda x: float(x['quoteVolume']), reverse=True)
            # Tomar los top 200 para tener margen al filtrar stablecoins
            cmc_symbols = [t['symbol'].replace('USDT', '') for t in usdt_tickers[:200]]
            
    except Exception as e:
        print(f"Failed to fetch Binance data: {e}")
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
    # El Top 100 no cambia tan rápido. Actualizar cada 4 horas (14400 segundos) 
    # es perfecto y consume solo ~6 créditos al día (180 al mes vs el límite de 10,000).
    if time.time() - os.path.getmtime("top_100_pairs.json") > 14400:
        return True
    return False

if __name__ == "__main__":
    if should_update():
        if CMC_API_KEY:
            update_top_pairs()
        else:
            print("CMC_API_KEY is not set. Skipping update.")
    else:
        print("top_100_pairs.json is less than 15 minutes old. Skipping CMC API call to save free tier limits.")
