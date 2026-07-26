---
name: technical-analysis
description: Skill for calculating technical indicators (RSI, MACD, EMA, Bollinger Bands, ATR) and interpreting market signals.
---

# Technical Analysis Protocol

## Indicator Interpretations

- **RSI (14)**:
  - `< 30`: Oversold signal (Potential Rebound / Buy opportunity).
  - `> 70`: Overbought signal (Potential Pullback / Sell risk).
  - `> 50`: Bullish momentum bias.
- **EMA (20 / 50 / 200)**:
  - Price > EMA20 > EMA50: Strong Uptrend.
  - Golden Cross (EMA20 crosses above EMA50): Bullish confirmation.
  - Death Cross (EMA20 crosses below EMA50): Bearish confirmation.
- **Bollinger Bands (20, 2.0)**:
  - Price touching Lower Band + RSI < 35: Rebound setup.
  - Price touching Upper Band + RSI > 65: Resistance rejection setup.
- **ATR (14)**:
  - Used to dynamically place Stop-Loss at `1.5 * ATR` away from entry.
