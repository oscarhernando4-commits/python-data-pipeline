---
name: risk-management
description: Skill for calculating optimal position sizing, stop-loss, take-profit, and emergency market crash protection (Circuit Breaker).
---

# Emergency Crash Protection & Institutional Risk Management Protocol

This skill enforces 5 layers of defense to protect capital against sudden market crashes, black swan events, and high-volatility news.

## 5 Layers of Capital Defense

1. **Inviolable Hard Stop-Loss**:
   - Every order MUST be placed with an active Stop-Loss on Binance Spot.
   - Maximum risk is strictly limited to 1.5% (-$1.50 USD for $100 capital). No position is ever left unprotected.
2. **Flash Crash Circuit Breaker (`crash_shield.py`)**:
   - Monitors 15m/1h candle drops. If BTC drops > 2.5% in 1 hour, trigger **EMERGENCY_SHIELD_ACTIVATE**.
   - Halts all buying operations and converts active spot positions to USDT/USDC stablecoins.
3. **Macro Trend Shield (4H EMA 50/200)**:
   - If 4H Macro Trend is BEARISH, spot buying of altcoins is strictly PROHIBITED.
   - Preserves 100% capital in USD during crypto bear markets.
4. **Stablecoin Capital Refuge (100% USDT/USDC)**:
   - Idle capital is stored 100% in USD stablecoins (`USDT` / `USDC`) so price drops in Altcoins do NOT affect your account value.
5. **Macro News Blackout Filter**:
   - Halts new trade entries 30 minutes before and after high-impact economic news releases (FED Interest Rates, CPI Inflation reports).
