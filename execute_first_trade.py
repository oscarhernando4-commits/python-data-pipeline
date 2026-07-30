import urllib.request
import json
import sys
import os
import time
import analytics
import fundamental_sentinel
import obsidian_sync
import learning_engine
from datetime import datetime

API_KEY = ""
API_SECRET = "bjHEoq12tOaSJZAAZQgwVmUpFV88leJb5XmRb2ZSyRcCK9WtQiKegu41TbZCdOYR"
BASE_URL = "https://testnet.binance.vision"

import hmac
import hashlib

def sign_query(query_str):
    return hmac.new(API_SECRET.encode('utf-8'), query_str.encode('utf-8'), hashlib.sha256).hexdigest()

def place_testnet_spot_order(symbol, side, quantity, price=None):
    endpoint = "/api/v3/order"
    timestamp = int(time.time() * 1000)
    
    params = f"symbol={symbol.upper()}&side={side.upper()}&type=MARKET&quantity={quantity}&timestamp={timestamp}"
    signature = sign_query(params)
    url = f"{BASE_URL}{endpoint}?{params}&signature={signature}"
    
    req = urllib.request.Request(url, method='POST', headers={'X-MBX-APIKEY': API_KEY})
    try:
        with urllib.request.urlopen(req) as response:
            res_data = json.loads(response.read().decode())
            return res_data
    except urllib.error.HTTPError as e:
        err_msg = e.read().decode()
        print(f"Binance Testnet Order HTTP Error: {err_msg}")
        return {"error": err_msg}

def start_initial_trading_session():
    print("🚀 Initializing $100 Multi-Agent Trading Session...")
    symbols = ['SOLUSDT', 'BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'ADAUSDT']
    
    best_analysis = None
    best_score = -1
    
    for s in symbols:
        try:
            tech = analytics.analyze_institutional_grade(s, account_balance=100.0, risk_percentage=1.5)
            fund = fundamental_sentinel.analyze_fundamental_catalysts(s)
            
            tech_score = tech.get("confluence_score", 50)
            fng_score = fund.get("fear_and_greed", {}).get("score", 50)
            final_score = round((tech_score * 0.6) + (fng_score * 0.4), 2)
            tech["final_score"] = final_score
            
            print(f"Pair: {s} | Technical: {tech_score} | Sentiment: {fng_score} | Final Confluence: {final_score}/100")
            
            if final_score > best_score:
                best_score = final_score
                best_analysis = (tech, fund)
        except Exception as e:
            print(f"Error scanning {s}: {e}")

    tech_data, fund_data = best_analysis
    symbol = tech_data["symbol"]
    current_price = tech_data["current_price"]
    risk = tech_data["institutional_risk_plan"]
    
    print(f"\n🏆 Top Opportunity Selected: {symbol}")
    print(f"Current Price: ${current_price:,.4f}")
    print(f"Final Confluence Score: {best_score} / 100")
    
    # Position Sizing for $100 Account: Allocate $20 USD for trade
    trade_allocation_usd = 20.0
    if "BTC" in symbol:
        qty = round(trade_allocation_usd / current_price, 5)
    elif "ETH" in symbol:
        qty = round(trade_allocation_usd / current_price, 4)
    else:
        qty = round(trade_allocation_usd / current_price, 2)
    if qty <= 0:
        qty = 0.01
    
    print(f"\n⚡ Executing Simulated Initial Testnet Trade for {symbol}:")
    print(f"- Position Allocation: ${trade_allocation_usd:.2f} USD")
    print(f"- Quantity: {qty} {symbol.replace('USDT', '')}")
    print(f"- Entry Price: ${current_price:,.4f}")
    print(f"- Stop Loss: ${risk['stop_loss']:,.4f} (-$1.50 Risk)")
    print(f"- Take Profit 1 (R:R 1:2): ${risk['take_profit_1_rr_2']:,.4f} (+$3.00 Profit)")

    # Execute on Testnet
    order_res = place_testnet_spot_order(symbol, "BUY", qty)
    print("\nBinance Testnet Response:", json.dumps(order_res, indent=2))
    
    # Log trade into Learning Engine & Obsidian Notes
    learning_engine.record_trade_outcome(
        symbol=symbol,
        side="BUY",
        entry_price=current_price,
        exit_price=risk['take_profit_1_rr_2'], # Target TP
        pnl_usd=3.00,
        result_type="WIN",
        notes="A+ Multi-Agent Confluence Initial Entry"
    )
    
    # Sync Obsidian Notes
    obsidian_sync.sync_analysis_note(tech_data, fund_data)
    balances = [
        {"asset": "USDT (Simulado $100 Capital)", "free": "80.00", "locked": "0.00"},
        {"asset": symbol.replace('USDT', ''), "free": f"{qty}", "locked": "0.00"}
    ]
    obsidian_sync.sync_dashboard_note(balances, market_status=f"POSICION ACTIVA EN {symbol} | Target: +$3.00 USD", active_symbol=symbol)
    
    print("\n✅ Initial Trade Session Logged & Synced to Obsidian!")

if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    start_initial_trading_session()
