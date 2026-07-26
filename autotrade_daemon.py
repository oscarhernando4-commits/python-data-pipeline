import time
import json
import os
import sys
from datetime import datetime
import analytics
import fundamental_sentinel
import obsidian_sync
import learning_engine

SYMBOLS_TO_SCAN = ['BTCUSDT', 'ETHUSDT', 'SOLUSDT', 'NEARUSDT']
CAPITAL = 100.0

def run_automated_scan_and_trade():
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{now_str}] Starting automated 6-hour market scan...")
    
    best_opportunity = None
    highest_score = 0
    scanned_results = []

    for symbol in SYMBOLS_TO_SCAN:
        try:
            tech = analytics.analyze_institutional_grade(symbol, account_balance=CAPITAL, risk_percentage=1.5)
            fund = fundamental_sentinel.analyze_fundamental_catalysts(symbol)
            
            tech_score = tech.get("confluence_score", 50)
            fund_fng = fund.get("fear_and_greed", {}).get("score", 50)
            
            # Weighted Final Score (60% Tech + 40% Fundamental)
            final_score = round((tech_score * 0.6) + (fund_fng * 0.4), 2)
            tech["final_score"] = final_score
            
            scanned_results.append({
                "symbol": symbol,
                "score": final_score,
                "price": tech.get("current_price"),
                "recommendation": tech.get("recommendation")
            })
            
            if final_score > highest_score:
                highest_score = final_score
                best_opportunity = (tech, fund)
        except Exception as e:
            print(f"Error scanning {symbol}: {e}")

    # Sync best opportunity to Obsidian
    if best_opportunity:
        tech_data, fund_data = best_opportunity
        obsidian_sync.sync_analysis_note(tech_data, fund_data)
        
    # Sync Dashboard
    balances_simulated = [
        {"asset": "USDT (Capital $100)", "free": f"{CAPITAL:.2f}", "locked": "0.00"},
        {"asset": "BTC", "free": "0.00", "locked": "0.00"},
        {"asset": "SOL", "free": "0.00", "locked": "0.00"}
    ]
    obsidian_sync.sync_dashboard_note(
        balances_simulated, 
        market_status=f"AUTO-SCAN COMPLETED | Highest Score: {highest_score}/100", 
        active_symbol=best_opportunity[0]['symbol'] if best_opportunity else 'BTCUSDT'
    )
    
    print(f"[{now_str}] Automated scan finished. Highest score: {highest_score}/100. Obsidian updated!")
    return scanned_results

if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    run_automated_scan_and_trade()
