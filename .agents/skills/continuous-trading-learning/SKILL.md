---
name: continuous-trading-learning
description: Skill for continuous reinforcement learning, post-trade analysis, optimizing winning setups, and blocking past failure patterns.
---

# Continuous Reinforcement Learning Protocol

This skill continuously optimizes trading performance by learning from every completed trade.

## Workflow

1. **Post-Mortem Analysis (Post-Operación)**:
   - After a trade hits Stop-Loss or Take-Profit, run `python learning_engine.py`.
   - Log entry price, exit price, PnL, indicators at entry, and root cause notes.
2. **Failure Prevention (Bloqueo de Fracasos)**:
   - Identify conditions present during losing trades (e.g. false breakouts, low volume, macro divergence).
   - Add new **Anti-Loss Block Rules** to prevent entering similar setups in the future.
3. **Success Amplification (Optimización de Aciertos)**:
   - Identify indicator combinations present during winning trades.
   - Boost Confluence Scores for high-probability winning setups.
4. **Obsidian Live Matrix Sync**:
   - Sinks all learned rules, Win Rate %, PnL, and trade history directly to `🧠_Matriz_De_Aprendizaje.md` in the user's Obsidian Vault.
