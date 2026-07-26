---
name: crypto-quant-trader
description: Master skill for quantitative cryptocurrency trading, fundamental catalyst modeling, news sentiment, risk management, and Binance execution.
---

# Institutional Multi-Agent Trading & Fundamental Valuation Protocol

This skill coordinates a 4-Agent Trading Desk using the `multi-agente` MCP server.

## Specialized Roles

1. **FundamentalAnalyst (Noticias, Catalizadores & Valoración)**:
   - Scans live news, upcoming product releases, mainnet upgrades, and tokenomics unlocks.
   - Evaluates the **Fear & Greed Index** and macro sentiment via `python fundamental_sentinel.py <SYMBOL>`.
   - Uses web search to research high-potential project catalysts.
2. **QuantAnalyst (Análisis Técnico & Volumen)**:
   - Runs `python analytics.py <SYMBOL> <BALANCE>` for multi-timeframe technical indicators (4H Macro + 15M Micro).
   - Verifies volume surges and technical confluence score (Must be ≥ 75 for A+ setup).
3. **RiskManager (Gestión de Riesgo & Break-Even)**:
   - Enforces max 1.5% capital risk per trade.
   - Calculates dynamic ATR Stop-Loss, Break-Even Trigger (+1R), TP1 (1:2 R:R), and TP2 (1:3.5 R:R).
4. **TraderExecutor (Ejecutador en Binance)**:
   - Checks account balances via `binance_get_account_balance`.
   - Places orders via `binance_create_spot_order`.
   - Updates task status in the Kanban board (`team_update_status`).

## Confluence Decision Rule

$$\text{Final Signal} = (\text{Fundamental Score} \times 0.4) + (\text{Technical Confluence Score} \times 0.6)$$

- Execute ONLY if **Final Score ≥ 75/100**.
- Otherwise, output **`HOLD / NO TRADE`** to protect capital.
