import urllib.request
import json
import sys
import os
from datetime import datetime

BASE_URL = 'https://api.binance.com'

def check_flash_crash_risk(symbol="BTCUSDT"):
    try:
        url = f"{BASE_URL}/api/v3/klines?symbol={symbol}&interval=15m&limit=5"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            klines = json.loads(response.read().decode())
            
        recent_close = float(klines[-1][4])
        prev_close = float(klines[-5][4]) # Price 1 hour ago
        drop_pct = ((recent_close - prev_close) / prev_close) * 100.0
        
        # Circuit Breaker Trigger: If BTC or ETH drops > 2.5% in 1 hour
        if drop_pct <= -2.5:
            return {
                "circuit_breaker_active": True,
                "drop_pct": round(drop_pct, 2),
                "action": "EMERGENCY_SHIELD_ACTIVATE 🛡️",
                "message": f"CRITICAL FLASH CRASH DETECTED: {symbol} dropped {drop_pct:.2f}% in 1 hour. All buying halted! HODL in USDT/USDC!"
            }
        return {
            "circuit_breaker_active": False,
            "drop_pct": round(drop_pct, 2),
            "action": "NORMAL_OPERATIONS 🟢",
            "message": "Market volatility within normal safety thresholds."
        }
    except Exception as e:
        return {"circuit_breaker_active": False, "error": str(e)}

if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    res = check_flash_crash_risk("BTCUSDT")
    print(json.dumps(res, indent=2, ensure_ascii=False))
