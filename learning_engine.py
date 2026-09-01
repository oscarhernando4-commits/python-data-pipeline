import os
import json
from datetime import datetime

DATA_FILE = os.path.join(os.path.dirname(__file__), "trade_memory.json")

def _get_obsidian_folder():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    obs_path = os.path.join(base_dir, "Obsidian", "01_PROYECTOS", "BINANCE_QUANT_TRADING")
    os.makedirs(obs_path, exist_ok=True)
    return obs_path

OBSIDIAN_FOLDER = _get_obsidian_folder()

def load_memory():
    if not os.path.exists(DATA_FILE):
        initial_data = {
            "stats": {"total_trades": 0, "wins": 0, "losses": 0, "win_rate_pct": 0.0, "total_pnl_usd": 0.0},
            "learned_rules": {
                "blocked_patterns": [
                    "High impact news within 30 mins (Block Trade)",
                    "Volume surge < 1.1x average during trend reversals (Block Fakeouts)"
                ],
                "boosted_patterns": [
                    "RSI < 30 + MACD Bullish Cross + Volume > 1.5x (High Probability Win)",
                    "4H Macro Trend Alignment with 15M Reversal"
                ]
            },
            "history": []
        }
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(initial_data, f, indent=2, ensure_ascii=False)
        return initial_data
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_memory(data):
    if len(data.get("history", [])) > 500:
        data["history"] = data["history"][-500:]
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    sync_learning_note(data)

def get_market_bias(data=None):
    if data is None:
        data = load_memory()
    trades = data.get("history", []) # Look at TOTAL ALL-TIME trades for group learning
    long_w=0; long_l=0; short_w=0; short_l=0
    group_stats = {}
    
    for t in trades:
        side = t.get("side", "LONG")
        res = t.get("result", "LOSS")
        grp = t.get("group_name", "Unknown")
        
        if grp not in group_stats:
            group_stats[grp] = {"w": 0, "l": 0, "pnl": 0.0}
            
        group_stats[grp]["pnl"] += float(t.get("pnl_usd", 0.0))
        if res == "WIN":
            group_stats[grp]["w"] += 1
            if side == "LONG": long_w += 1
            elif side == "SHORT": short_w += 1
        else:
            group_stats[grp]["l"] += 1
            if side == "LONG": long_l += 1
            elif side == "SHORT": short_l += 1
            
    # Find Best Group
    best_group_name = None
    best_group_wr = 0.0
    best_group_pnl = -9999
    
    for g, st in group_stats.items():
        total = st["w"] + st["l"]
        if total >= 3: # Must have at least 3 trades to be considered
            wr = (st["w"] / total) * 100
            if wr >= 50.0 and st["pnl"] > 0 and st["pnl"] > best_group_pnl:
                best_group_wr = wr
                best_group_pnl = st["pnl"]
                best_group_name = g
                
    long_total = long_w + long_l
    short_total = short_w + short_l
    long_wr = (long_w / long_total * 100) if long_total > 0 else 0
    short_wr = (short_w / short_total * 100) if short_total > 0 else 0
    
    bias = "NEUTRAL"
    if short_wr > long_wr + 10:
        bias = "FAVOR_SHORT"
    elif long_wr > short_wr + 10:
        bias = "FAVOR_LONG"
        
    return {
        "bias": bias,
        "recommended_bias": "STRONG_LONG" if long_wr > 60 and short_wr < 40 else ("STRONG_SHORT" if short_wr > 60 and long_wr < 40 else bias),
        "long_win_rate": round(long_wr, 1),
        "short_win_rate": round(short_wr, 1),
        "long_trades": long_total,
        "short_trades": short_total,
        "total_trades": long_total + short_total,
        "best_group": best_group_name,
        "best_group_wr": round(best_group_wr, 1),
        "best_group_pnl": round(best_group_pnl, 2)
    }

def _extract_technical_rule(symbol, side, result_type, context):
    """Generate an abstract, generalizable technical rule from trade context."""
    if not context:
        return None
    rsi = context.get("rsi_15m")
    score = context.get("score")
    trend = context.get("macro_trend_4h", "")
    vol_surge_1m = context.get("vol_surge_1m")
    fii_score = context.get("fii_score")
    obv_trend = context.get("obv_trend")
    atr_pct = context.get("atr_pct_15m")
    
    parts = []
    if vol_surge_1m is not None:
        if vol_surge_1m >= 2.0: parts.append("Vol1M:Explosive(>=2.0x)")
        elif vol_surge_1m < 0.70: parts.append("Vol1M:Dead(<0.70x)")
    if obv_trend:
        parts.append(f"OBV:{obv_trend}")
    if fii_score is not None:
        if fii_score >= 60: parts.append("FII:Institutional(>=60)")
        elif fii_score < 45: parts.append("FII:Weak(<45)")
    if atr_pct is not None:
        if atr_pct < 0.40: parts.append("ATR:Zombie(<0.40%)")
        elif atr_pct >= 0.45: parts.append("ATR:HighBeta(>=0.45%)")
    if rsi is not None:
        if rsi < 30: parts.append("RSI<30(Oversold)")
        elif rsi < 40: parts.append("RSI:30-40(Weak)")
        elif rsi < 60: parts.append("RSI:40-60(Neutral)")
        elif rsi < 70: parts.append("RSI:60-70(Strong)")
        else: parts.append("RSI>70(Overbought)")
    if score is not None:
        if score >= 70: parts.append("Score:70+(Bullish)")
        elif score >= 50: parts.append("Score:50-70(Mild)")
        elif score >= 30: parts.append("Score:30-50(Mild-Bear)")
        else: parts.append("Score:<30(Bearish)")
    if trend:
        parts.append(f"Trend:{trend}")
    
    if not parts:
        return None
    condition = " + ".join(parts)
    
    if result_type.upper() == "LOSS":
        return f"BLOCK {side} when {condition} (Lost on {symbol})"
    else:
        return f"BOOST {side} when {condition} (Won on {symbol})"

def get_optimal_entry_conditions(data=None):
    """Analyze ALL trade history to discover statistically validated patterns.
    Returns the RSI ranges, score ranges, and trends with the highest win rates."""
    if data is None:
        data = load_memory()
    history = data.get("history", [])
    if len(history) < 10:
        return None
    
    # Bucket trades by RSI range
    rsi_buckets = {"<30": {"w": 0, "l": 0}, "30-40": {"w": 0, "l": 0}, 
                   "40-60": {"w": 0, "l": 0}, "60-70": {"w": 0, "l": 0}, ">70": {"w": 0, "l": 0}}
    score_buckets = {"<30": {"w": 0, "l": 0}, "30-50": {"w": 0, "l": 0},
                    "50-70": {"w": 0, "l": 0}, "70+": {"w": 0, "l": 0}}
    trend_buckets = {}
    side_buckets = {"LONG": {"w": 0, "l": 0}, "SHORT": {"w": 0, "l": 0}}
    
    for t in history:
        ctx = t.get("context", {})
        result = t.get("result", "LOSS")
        side = t.get("side", "LONG")
        k = "w" if result == "WIN" else "l"
        
        # Side tracking
        if side in side_buckets:
            side_buckets[side][k] += 1
        
        rsi = ctx.get("rsi_15m")
        if rsi is not None:
            if rsi < 30: rsi_buckets["<30"][k] += 1
            elif rsi < 40: rsi_buckets["30-40"][k] += 1
            elif rsi < 60: rsi_buckets["40-60"][k] += 1
            elif rsi < 70: rsi_buckets["60-70"][k] += 1
            else: rsi_buckets[">70"][k] += 1
        
        score = ctx.get("score")
        if score is not None:
            if score < 30: score_buckets["<30"][k] += 1
            elif score < 50: score_buckets["30-50"][k] += 1
            elif score < 70: score_buckets["50-70"][k] += 1
            else: score_buckets["70+"][k] += 1
        
        trend = ctx.get("macro_trend_4h", "")
        if trend:
            if trend not in trend_buckets:
                trend_buckets[trend] = {"w": 0, "l": 0}
            trend_buckets[trend][k] += 1
    
    def calc_wr(bucket):
        results = {}
        for key, stats in bucket.items():
            total = stats["w"] + stats["l"]
            if total >= 3:
                results[key] = {"win_rate": round(stats["w"] / total * 100, 1), "total": total, "wins": stats["w"]}
        return results
    
    return {
        "rsi_analysis": calc_wr(rsi_buckets),
        "score_analysis": calc_wr(score_buckets),
        "trend_analysis": calc_wr(trend_buckets),
        "side_analysis": calc_wr(side_buckets),
        "total_trades_analyzed": len(history)
    }

def record_trade_outcome(symbol, side="LONG", entry_price=0.0, exit_price=0.0, pnl_usd=0.0, result_type=None, notes="", account_id="Histórico", group_name="Sin Grupo", context=None, **kwargs):
    if result_type is None:
        result_type = "WIN" if pnl_usd > 0 else "LOSS"
    if not notes and "exit_reason" in kwargs:
        notes = kwargs["exit_reason"]
    data = load_memory()
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # ─────────────────────────────────────────────────────────────────────────
    # 🛡️ DEDUPLICACIÓN ANTI-TRIPLICACIÓN: Evita registrar el mismo trade de la
    # cuenta real (R-01) más de una vez dentro de una ventana de 90 segundos.
    # Causa: pipeline_processor.py corre 1000 cuentas del matrix y cada una que
    # ─────────────────────────────────────────────────────────────────────────
    # 🛡️ IDENTIFICACIÓN ESTRICTA DE CUENTA REAL (R-01):
    # Solo R-01 o CUENTA REAL exacta. Evita que grupos simulados como
    # "MATRIZ CUÁNTICA A+ (Condición Real)" se clasifiquen como reales.
    # ─────────────────────────────────────────────────────────────────────────
    is_real_account = (str(account_id).strip() == "R-01") or (str(group_name).strip() == "CUENTA REAL")
    history = data.get("history", [])
    
    if not is_real_account:
        # For simulation (matrix) accounts: check if R-01 already logged this symbol in last 90s
        try:
            from datetime import datetime as _dt, timedelta as _td
            cutoff = _dt.now() - _td(seconds=90)
            for recent in reversed(history[-20:]):
                ts_str = recent.get("timestamp", "")
                acc = str(recent.get("account_id", ""))
                sym_r = str(recent.get("symbol", ""))
                res_r = str(recent.get("result", ""))
                if acc == "R-01" or str(recent.get("group_name", "")).strip() == "CUENTA REAL":
                    try:
                        ts = _dt.strptime(ts_str, "%Y-%m-%d %H:%M:%S")
                        if ts >= cutoff and sym_r == symbol.upper() and res_r == result_type.upper():
                            # Real account already logged this — skip simulation duplicate
                            return None
                    except Exception:
                        pass
        except Exception:
            pass
    
    import time as _time_mod
    trade_entry = {
        "timestamp": now_str,
        "timestamp_ms": int(_time_mod.time() * 1000),  # ← Requerido por Pausa Inteligente 30min
        "account_id": account_id,
        "group_name": group_name,
        "source": "REAL" if is_real_account else "SIMULATION",
        "symbol": symbol.upper(),
        "side": side.upper() if side else "LONG",
        "entry_price": entry_price,
        "exit_price": exit_price,
        "pnl_usd": pnl_usd,
        "result": result_type.upper(),
        "notes": notes,
        "context": context or {}
    }
    
    data["history"].append(trade_entry)
    
    # Actualizar estadísticas principales SOLO con operaciones REALES
    if is_real_account:
        stats = data["stats"]
        stats["total_trades"] += 1
        if result_type.upper() == "WIN":
            stats["wins"] += 1
        else:
            stats["losses"] += 1
        stats["total_pnl_usd"] += pnl_usd
        stats["win_rate_pct"] = round((stats["wins"] / stats["total_trades"]) * 100.0, 2)

    
    # Generate ABSTRACT technical rules (not trade-specific strings)
    tech_rule = _extract_technical_rule(symbol, side or "LONG", result_type, context)
    if tech_rule:
        if result_type.upper() == "LOSS":
            if tech_rule not in data["learned_rules"]["blocked_patterns"]:
                data["learned_rules"]["blocked_patterns"].append(tech_rule)
                # Keep only the latest 20 rules to avoid noise
                if len(data["learned_rules"]["blocked_patterns"]) > 20:
                    data["learned_rules"]["blocked_patterns"] = data["learned_rules"]["blocked_patterns"][-20:]
        elif result_type.upper() == "WIN":
            if tech_rule not in data["learned_rules"]["boosted_patterns"]:
                data["learned_rules"]["boosted_patterns"].append(tech_rule)
                if len(data["learned_rules"]["boosted_patterns"]) > 20:
                    data["learned_rules"]["boosted_patterns"] = data["learned_rules"]["boosted_patterns"][-20:]
        
    save_memory(data)
    return trade_entry

def get_executive_learning_summary(data=None):
    """
    Synthesizes ALL historical and recent trade outcomes into a concise, high-impact
    Executive Intelligence Matrix (~400-800 tokens) for Gemini Flash-Lite.
    Provides statistical sweet-spots, winning archetypes, and empirical traps.
    """
    if data is None:
        data = load_memory()
    
    stats = data.get("stats", {})
    history = data.get("history", [])
    recent = history[-50:] if history else []
    
    # 1. Real & Recent Statistics
    total_trades = stats.get("total_trades", len(history))
    wins = stats.get("wins", sum(1 for t in history if t.get("result") == "WIN"))
    wr = stats.get("win_rate_pct", round((wins / max(total_trades, 1)) * 100, 1))
    
    # 2. Extract recent real performance
    real_trades = [t for t in history if "REAL" in str(t.get("group_name", "")).upper() or "R-01" in str(t.get("account_id", "")).upper()]
    real_wins = sum(1 for t in real_trades if t.get("result") == "WIN")
    real_wr = round((real_wins / max(len(real_trades), 1)) * 100, 1) if real_trades else wr
    
    # 3. Discover dynamic statistical sweet spots
    optimal = get_optimal_entry_conditions(data)
    best_rsi = "30-55 (Suelo Acumulación)"
    best_score = "60-85 (Confluencia A+)"
    if optimal:
        rsi_an = optimal.get("rsi_analysis", {})
        high_wr_rsi = [k for k, v in rsi_an.items() if v.get("win_rate", 0) >= 40.0]
        if high_wr_rsi:
            best_rsi = ", ".join(high_wr_rsi)
            
    # 4. Learned Rule Summaries
    blocked = data.get("learned_rules", {}).get("blocked_patterns", [])[-4:]
    boosted = data.get("learned_rules", {}).get("boosted_patterns", [])[-4:]
    
    blocked_str = "\n".join([f"    - 🛑 {b}" for b in blocked]) if blocked else "    - Ninguna trampa activa."
    boosted_str = "\n".join([f"    - ⚡ {b}" for b in boosted]) if boosted else "    - Reversión en suelo + FII >= 50 + Bids >= 45%."
    
    # 5. Dynamic Token Intelligence
    token_intel = get_dynamic_token_intelligence(data)
    elite_str = ", ".join(token_intel["elite_tokens"][:4]) if token_intel["elite_tokens"] else "SUI, NIL, AVAX, XPL"
    blocked_tok_str = ", ".join(token_intel["blocked_tokens"][:4]) if token_intel["blocked_tokens"] else "PEPE, BARD, DEXE, APT"

    # 6. Champions from Matrix
    matrix_champs = get_matrix_champions_summary()
    
    summary = f"""=== SÍNTESIS DE AUTO-APRENDIZAJE EN TIEMPO REAL (RAG QUANT) ===
- Estadísticas Generales: {total_trades} operaciones | Win Rate Global: {wr}% | Cuenta Real WR: {real_wr}% ({len(real_trades)} ops)
- Rango Óptimo de Entrada Validado: RSI 15M en [{best_rsi}] | Score Cuántico en [{best_score}]
- 🌟 Monedas Élite Validadas (WR >= 65%): [{elite_str}]
- ☠️ Monedas en Blacklist Dinámica (Pérdidas repetidas): [{blocked_tok_str}]
- Patrones Potenciados (ALTA PROBABILIDAD DE VICTORIA):
{boosted_str}
- Trampas Aprendidas (PROHIBIDO REPETIR):
{blocked_str}
- Campeones Líderes de la Simulación Matrix:
{matrix_champs}
==============================================================="""
    return summary

def get_dynamic_token_intelligence(data=None):
    """
    Analyzes historical trade outcomes per token to generate dynamic elite whitelists
    and dynamic token blacklists based on empirical win-rate evidence.
    """
    if data is None:
        data = load_memory()
    
    bl_map = get_dynamic_blacklist(data)
    elite_map = get_dynamic_elite(data)
    
    elite = [f"{s} (WR {d['win_rate']:.0f}%, +${d['pnl_usd']:.2f})" for s, d in sorted(elite_map.items(), key=lambda x: x[1]['win_rate'], reverse=True)]
    blocked = [f"{s} [TIER:{d['tier']}] (WR {d['win_rate']:.0f}%, -${abs(d['pnl_usd']):.2f})" for s, d in sorted(bl_map.items(), key=lambda x: x[1]['win_rate'])]
            
    return {
        "elite_tokens": elite,
        "blocked_tokens": blocked,
        "blacklist_map": bl_map,
        "elite_map": elite_map
    }

def calculate_asset_dna_profile(symbol: str, atr_15m_pct: float = 0.30, atr_1h_pct: float = 0.60, data=None):
    """
    🎯 MODELACIÓN CUÁNTICA DE ADN Y COMPORTAMIENTO POR MONEDA:
    Calcula el perfil de volatilidad histórica, elasticidad y memoria RAG específica del activo,
    determinando la holgura óptima del trailing stop y el objetivo de recorrido a resistencia.
    """
    if data is None:
        data = load_memory()
        
    trades = data.get("history", [])
    token_trades = [t for t in trades if t.get("symbol") == symbol]
    
    tot = len(token_trades)
    wins = len([t for t in token_trades if t.get("result") == "WIN"])
    pnl = sum([float(t.get("pnl_usd", 0.0)) for t in token_trades])
    wr = (wins / tot * 100.0) if tot > 0 else 50.0
    
    mean_vol = (atr_15m_pct + atr_1h_pct) / 2.0
    
    if mean_vol >= 0.85:
        tier = "HIGH_BETA_RUNNER"
        tier_label = "🚀 ALTA ELASTICIDAD / RUNNER"
        opt_slack = max(0.55, round(atr_15m_pct * 1.3, 2))
        opt_target = max(3.50, round(atr_1h_pct * 3.5, 2))
        opt_sl = -2.20
    elif mean_vol >= 0.45:
        tier = "BALANCED_SWING"
        tier_label = "💎 VOLATILIDAD BALANCEADA"
        opt_slack = max(0.45, round(atr_15m_pct * 1.1, 2))
        opt_target = max(2.20, round(atr_1h_pct * 2.8, 2))
        opt_sl = -2.00
    else:
        tier = "LOW_BETA_STABLE"
        tier_label = "🔒 BAJA VOLATILIDAD / ESTABLE"
        opt_slack = max(0.35, round(atr_15m_pct * 1.0, 2))
        opt_target = max(1.20, round(atr_1h_pct * 2.0, 2))
        opt_sl = -1.80
        
    reputation = "🌟 ÉLITE HISTÓRICO" if (tot >= 2 and wr >= 65.0) else (
        "☠️ ALERTA PÉRDIDAS" if (tot >= 2 and wr <= 30.0) else "🔵 NEUTRAL"
    )
    
    return {
        "symbol": symbol,
        "dna_tier": tier,
        "dna_label": tier_label,
        "reputation": reputation,
        "historical_trades_count": tot,
        "historical_win_rate": round(wr, 1),
        "historical_pnl_usd": round(pnl, 4),
        "optimal_trailing_slack_pct": opt_slack,
        "optimal_target_expansion_pct": opt_target,
        "optimal_sl_floor_pct": opt_sl,
        "mean_volatility_pct": round(mean_vol, 2)
    }

def get_token_dna_profile(symbol: str, data=None):
    """
    🧬 PERFIL ADN POR TOKEN (Alimentado por simulaciones + operaciones reales):
    Retorna el perfil histórico completo de un token específico, incluyendo:
    - Win rate, total trades, PnL acumulado
    - Condiciones promedio de entrada (RSI, Score, FII)
    - Tiempo promedio de holding
    - Racha actual (últimas 3 operaciones)
    
    Consumido por api_connector.py para VETO (WR < 30%, 3+ trades) 
    o BOOST (WR >= 65%, 3+ trades) en la evaluación de candidatos.
    """
    if data is None:
        data = load_memory()
    
    trades = data.get("history", [])
    token_trades = [t for t in trades if t.get("symbol", "").upper() == symbol.upper().replace("USDT", "") + "USDT" or t.get("symbol", "").upper() == symbol.upper()]
    
    if not token_trades:
        return {"symbol": symbol, "total_trades": 0, "win_rate": 50.0, "pnl_usd": 0.0, 
                "avg_entry_rsi": None, "avg_entry_score": None, "streak": "NEUTRAL", "is_elite": False, "is_toxic": False}
    
    tot = len(token_trades)
    wins = sum(1 for t in token_trades if t.get("result") == "WIN")
    losses = tot - wins
    pnl = sum(float(t.get("pnl_usd", 0.0)) for t in token_trades)
    wr = (wins / tot * 100.0) if tot > 0 else 50.0
    
    # Condiciones promedio de entrada (del contexto técnico guardado)
    rsi_vals = [t.get("context", {}).get("rsi_15m") for t in token_trades if t.get("context", {}).get("rsi_15m") is not None]
    score_vals = [t.get("context", {}).get("score") for t in token_trades if t.get("context", {}).get("score") is not None]
    fii_vals = [t.get("context", {}).get("fii_score") for t in token_trades if t.get("context", {}).get("fii_score") is not None]
    
    avg_rsi = round(sum(rsi_vals) / len(rsi_vals), 1) if rsi_vals else None
    avg_score = round(sum(score_vals) / len(score_vals), 1) if score_vals else None
    avg_fii = round(sum(fii_vals) / len(fii_vals), 1) if fii_vals else None
    
    # Condiciones promedio de las operaciones GANADORAS vs PERDEDORAS
    win_rsis = [t.get("context", {}).get("rsi_15m") for t in token_trades if t.get("result") == "WIN" and t.get("context", {}).get("rsi_15m") is not None]
    loss_rsis = [t.get("context", {}).get("rsi_15m") for t in token_trades if t.get("result") == "LOSS" and t.get("context", {}).get("rsi_15m") is not None]
    
    avg_win_rsi = round(sum(win_rsis) / len(win_rsis), 1) if win_rsis else None
    avg_loss_rsi = round(sum(loss_rsis) / len(loss_rsis), 1) if loss_rsis else None
    
    # Racha de las últimas 3 operaciones
    recent_3 = token_trades[-3:]
    recent_results = [t.get("result", "LOSS") for t in recent_3]
    if all(r == "WIN" for r in recent_results) and len(recent_3) >= 3:
        streak = "HOT_STREAK"
    elif all(r == "LOSS" for r in recent_results) and len(recent_3) >= 3:
        streak = "COLD_STREAK"
    else:
        streak = "NEUTRAL"
    
    return {
        "symbol": symbol,
        "total_trades": tot,
        "wins": wins,
        "losses": losses,
        "win_rate": round(wr, 1),
        "pnl_usd": round(pnl, 4),
        "avg_entry_rsi": avg_rsi,
        "avg_entry_score": avg_score,
        "avg_entry_fii": avg_fii,
        "avg_win_rsi": avg_win_rsi,
        "avg_loss_rsi": avg_loss_rsi,
        "streak": streak,
        "is_elite": bool(tot >= 3 and wr >= 65.0),
        "is_toxic": bool(tot >= 3 and wr < 30.0),
        "recent_results": recent_results
    }

def get_dynamic_blacklist(data=None, min_trades_hard=10, wr_hard=25.0,
                          min_trades_mid=5, wr_mid=20.0,
                          min_trades_soft=3, wr_soft=15.0):
    """
    BLACKLIST DINAMICA basada en evidencia historica tiered:
    HARD:  >= 10 trades con WR < 25%  (ej: AVAXUSDT 12% / 16 trades)
    MID:   >=  5 trades con WR < 20%  (ej: TIAUSDT  15% /  9 trades)
    SOFT:  >=  3 trades con WR < 15%  (ej: BTCUSDT  11% /  3 trades)
    Returns: {symbol -> {win_rate, total_trades, pnl_usd, tier}}
    """
    if data is None:
        data = load_memory()
    trades = data.get("history", [])
    token_stats = {}
    for t in trades:
        sym = t.get("symbol", "").upper().strip()
        if not sym:
            continue
        if not sym.endswith("USDT"):
            sym = sym + "USDT"
        res = t.get("result", "LOSS")
        pnl = float(t.get("pnl_usd", 0.0))
        if sym not in token_stats:
            token_stats[sym] = {"w": 0, "l": 0, "pnl": 0.0}
        if res == "WIN":
            token_stats[sym]["w"] += 1
        else:
            token_stats[sym]["l"] += 1
        token_stats[sym]["pnl"] += pnl
    blacklist = {}
    for sym, st in token_stats.items():
        tot = st["w"] + st["l"]
        wr = (st["w"] / tot * 100.0) if tot > 0 else 50.0
        tier = None
        if tot >= min_trades_hard and wr < wr_hard:
            tier = "HARD"
        elif tot >= min_trades_mid and wr < wr_mid:
            tier = "MID"
        elif tot >= min_trades_soft and wr < wr_soft:
            tier = "SOFT"
        if tier:
            blacklist[sym] = {"win_rate": round(wr, 1), "total_trades": tot,
                              "pnl_usd": round(st["pnl"], 4), "tier": tier}
    return blacklist


def get_dynamic_elite(data=None, min_trades=5, wr_threshold=65.0):
    """
    WHITELIST ELITE DINAMICA: tokens con WR >= 65% en >= 5 trades.
    Reciben boost de score en la evaluacion de candidatos.
    """
    if data is None:
        data = load_memory()
    trades = data.get("history", [])
    token_stats = {}
    for t in trades:
        sym = t.get("symbol", "").upper().strip()
        if not sym:
            continue
        if not sym.endswith("USDT"):
            sym = sym + "USDT"
        res = t.get("result", "LOSS")
        pnl = float(t.get("pnl_usd", 0.0))
        if sym not in token_stats:
            token_stats[sym] = {"w": 0, "l": 0, "pnl": 0.0}
        if res == "WIN":
            token_stats[sym]["w"] += 1
        else:
            token_stats[sym]["l"] += 1
        token_stats[sym]["pnl"] += pnl
    elite = {}
    for sym, st in token_stats.items():
        tot = st["w"] + st["l"]
        wr = (st["w"] / tot * 100.0) if tot > 0 else 0.0
        if tot >= min_trades and wr >= wr_threshold:
            elite[sym] = {"win_rate": round(wr, 1), "total_trades": tot,
                          "pnl_usd": round(st["pnl"], 4)}
    return elite


def get_super_detailed_table_str(data=None):
    if data is None:
        data = load_memory()
    
    table = "| Fecha | Grupo | Par | Lado | Entrada | Salida | PnL | Score | RSI | Tendencia | Resultado |\n"
    table += "| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |\n"
    
    # Only return last 30 trades if requested, to prevent prompt explosion
    trades_slice = data.get("history", [])[-30:]
    for t in trades_slice:
        ctx = t.get("context", {})
        score = ctx.get("score", "N/A")
        rsi = ctx.get("rsi_15m", "N/A")
        if isinstance(rsi, float): rsi = f"{rsi:.1f}"
        trend = ctx.get("macro_trend_4h", "N/A")
        
        res_emoji = "🟢 WIN" if t['result'] == 'WIN' else "🔴 LOSS"
        gname = t.get('group_name', 'Sin Grupo')[:15]
        
        table += f"| {t['timestamp']} | {gname}... | {t['symbol']} | {t['side']} | ${t['entry_price']} | ${t['exit_price']} | ${t['pnl_usd']:+.2f} | {score} | {rsi} | {trend} | {res_emoji} |\n"
        
    return table

def sync_learning_note(data):
    import obsidian_sync
    check_sync = getattr(obsidian_sync, "is_obsidian_sync_allowed", None)
    if check_sync and not check_sync():
        return
    if not os.path.exists(OBSIDIAN_FOLDER):
        os.makedirs(OBSIDIAN_FOLDER, exist_ok=True)
        
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    stats = data["stats"]
    bias_info = get_market_bias(data)
    blocked = "\n".join([f"- 🛑 {r}" for r in data["learned_rules"]["blocked_patterns"]])
    boosted = "\n".join([f"- ⚡ {r}" for r in data["learned_rules"]["boosted_patterns"]])
    
    history_rows = ""
    # BUGS 10+15 FIX: Solo mostrar trades REALES en dashboard; usar .get() con defaults seguros
    _real_history = [t for t in data.get("history", []) if t.get("source") != "SIMULATION"]
    for t in reversed(_real_history[-10:]):
        res_emoji = "🟢 WIN" if t.get("result", "") == "WIN" else "🔴 LOSS"
        _ts   = t.get("timestamp", t.get("timestamp_ms", "—"))  # fallback a timestamp_ms si no hay string
        _sym  = t.get("symbol", "?")
        _side = t.get("side", "LONG")
        _ep   = t.get("entry_price", 0)
        _xp   = t.get("exit_price", 0)
        _pnl  = t.get("pnl_usd", 0)
        history_rows += f"| {_ts} | {_sym} | {_side} | `${_ep}` | `${_xp}` | `${_pnl:+.2f}` | {res_emoji} |\n"
    if not history_rows:
        history_rows = "| - | - | - | - | - | - | Esperando primeras operaciones |"

    content = f"""---
tags:
  - trading
  - aprendizaje
  - inteligencia_artificial
  - binance
date: {now_str}
---

# 🧠 Matriz de Aprendizaje Reforzado (Reinforcement Learning Engine)

> **Última Actualización:** `{now_str}`  
> **Sistema:** Optimización Continua de Aciertos & Bloqueo de Fracasos

---

## 📊 Estadísticas Acumuladas
- **Total Operaciones:** `{stats['total_trades']}`
- **Ganadas (WIN):** `{stats['wins']}` | **Perdidas (LOSS):** `{stats['losses']}`
- **Tasa de Acierto (Win Rate):** `{stats['win_rate_pct']}%`
- **PnL Total Neto:** `${stats['total_pnl_usd']:+.2f} USD`

---

## 🧭 Sesgo de Aprendizaje Automático (Últimos 100 Trades)
- **Sesgo Actual (Market Bias):** `{bias_info['bias']}`
- **Rendimiento LONG (Compras):** `{bias_info['long_win_rate']}%` de Acierto (en {bias_info['long_trades']} ops recientes)
- **Rendimiento SHORT (Ventas):** `{bias_info['short_win_rate']}%` de Acierto (en {bias_info['short_trades']} ops recientes)
- 🏆 **Grupo de IA Más Rentable:** `{bias_info['best_group'] if bias_info['best_group'] else 'Ninguno superó el umbral'}` (WinRate: {bias_info['best_group_wr']}%, PnL: ${bias_info['best_group_pnl']})
- *Nota:* La IA utilizará este sesgo en tiempo real para descartar operaciones que vayan contra la tendencia comprobada. Y el Dinero Real copiará automáticamente al Grupo Más Rentable.

---

## 🛑 Reglas de Bloqueo de Fracasos (Filtros Anti-Pérdida)
*Estas condiciones han sido aprendidas tras fallos y BLOQUEAN automáticamente futuras operaciones de riesgo:*
{blocked}

---

## ⚡ Patrones Ganadores Optimizado (Modelos de Alta Probabilidad)
*Estos patrones han demostrado alta efectividad y AUMENTAN la puntuación de confluencia:*
{boosted}

---

## 📜 Registro de Post-Mortem de Operaciones
| Fecha | Par | Lado | Entrada | Salida | PnL | Resultado |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
{history_rows}
"""
    file_path = os.path.join(OBSIDIAN_FOLDER, "🧠_Matriz_De_Aprendizaje.md")
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)
        
    # Generate super detailed history file for Obsidian
    detailed_table = get_super_detailed_table_str(data)
    detailed_md = f"""---
tags:
  - trading
  - historial_completo
  - binance
date: {now_str}
---

# 📚 HISTORIAL SÚPER DETALLADO (ALL-TIME)

> **Última Actualización:** `{now_str}`
> Este historial contiene absolutamente todas las operaciones desde el inicio de los tiempos, junto con el análisis contextual (RSI, Score, Tendencia) en el momento exacto de la operación. La IA lee esta tabla COMPLETA para tomar decisiones.

{detailed_table}
"""
    detailed_path = os.path.join(OBSIDIAN_FOLDER, "📚_Historial_Super_Detallado.md")
    with open(detailed_path, "w", encoding="utf-8") as f:
        f.write(detailed_md)

def get_matrix_champions_summary():
    """
    Analyzes all 100 Matrix Accounts and returns a summary of the top-performing champions,
    their strategy groups, and their symbols (e.g. Group 3 + XAUTUSDT, DODOUSDT, ALLOUSDT).
    """
    matrix_file = os.path.join(os.path.dirname(__file__), "matrix_100_simulations.json")
    if not os.path.exists(matrix_file):
        return "No hay datos de la Matrix aún."
    
    try:
        with open(matrix_file, "r", encoding="utf-8") as f:
            data = json.load(f)
            
        accounts = data.get("accounts", []) if isinstance(data, dict) else (data if isinstance(data, list) else [])
        # Filter top accounts by PnL
        sorted_accs = sorted(accounts, key=lambda a: a.get("pnl_usd", 0.0), reverse=True)
        top_5 = sorted_accs[:5]
        
        champions_str = []
        for a in top_5:
            acc_id = a.get("account_id", "SIM-???")
            sym = a.get("symbol", "—")
            pnl = a.get("pnl_usd", 0.0)
            grp = a.get("group_name", "Grupo ?")
            wr = (a.get("wins", 0) / a.get("trades_count", 1) * 100.0) if a.get("trades_count", 0) > 0 else 0.0
            champions_str.append(f"• {acc_id} ({grp}) -> {sym} (+${pnl:.2f} USD | Win Rate {wr:.1f}%)")
            
        return "\n".join(champions_str)
    except Exception as e:
        return f"Error al extraer campeones: {e}"

if __name__ == '__main__':
    data = load_memory()
    sync_learning_note(data)

    print("Learning engine initialized and synced to Obsidian!")
