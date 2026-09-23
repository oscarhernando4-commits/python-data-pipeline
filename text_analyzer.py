import os
import json
import time
from typing import Dict, Any, List

def get_market_macro_context(symbol_analysis_map: Dict[str, Any], fear_greed: Dict[str, Any], news_headlines: List[str] = None, top_candidates: List[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Quantitative Structural Macro Matrix Engine:
    1. Bitcoin Tide & Flash-Crash Shield (Tide Guard)
    2. Real Market Breadth & Institutional Absorption (OBV/FII)
    3. Sector Alpha Flow & Leadership (Hot Money Tracker)
    4. Master Regime Semaphore (GREEN / YELLOW / RED)
    
    100% Deterministic, 0ms latency, zero API token waste.
    """
    total = len(symbol_analysis_map)
    if total == 0:
        return {
            "semaphore": "🟡 CAUTELOSO",
            "is_authorized": True,
            "btc_regime": "NEUTRAL",
            "breadth_pct": 50.0,
            "leader_sector": "General",
            "summary_text": "Mercado en inicialización."
        }

    # 1. 🪙 BITCOIN TIDE & FLASH CRASH SHIELD (TRI-MODAL QUANTUM REGIME)
    btc_data = symbol_analysis_map.get("BTCUSDT", {})
    btc_price = btc_data.get("price", 0.0)
    btc_score = btc_data.get("score", 50)
    btc_tech = btc_data.get("tech", {})
    btc_mtf = btc_tech.get("mtf_analysis", {})
    btc_rsi_15m = btc_mtf.get("rsi_15m", btc_tech.get("indicators", {}).get("rsi_15m", 50.0))
    btc_cascade = btc_mtf.get("is_15m_red_cascade", False)
    
    # 🌐 ANÁLISIS MACRO BTC 1H EN VIVO: Cierra la brecha de miopía temporal
    btc_1h_pct = 0.0
    btc_below_ema21_1h = False
    btc_rsi_1h = 50.0
    try:
        import api_connector as _ac_ta
        _kl_btc_1h = _ac_ta.get_klines("BTCUSDT", "1h", 25)
        if _kl_btc_1h and len(_kl_btc_1h) >= 22:
            _c_1h_now = float(_kl_btc_1h[-1][4])
            _o_1h_now = float(_kl_btc_1h[-1][1])
            btc_1h_pct = ((_c_1h_now - _o_1h_now) / _o_1h_now) * 100.0
            _cls_1h = [float(k[4]) for k in _kl_btc_1h]
            # EMA21 1H calculation
            _ema21 = sum(_cls_1h[-21:]) / 21
            _k_e = 2 / 22
            for _p in _cls_1h[-20:]:
                _ema21 = _p * _k_e + _ema21 * (1 - _k_e)
            btc_below_ema21_1h = _c_1h_now < _ema21
            from multi_timeframe_analyzer import calculate_rsi as _crsi_ta
            btc_rsi_1h = _crsi_ta(_cls_1h)
    except Exception:
        pass

    # ═══════════════════════════════════════════════════════════════════════
    # 🎯 CLASIFICACIÓN DEL RÉGIMEN CUÁNTICO TRI-MODAL:
    # 1. 🔴 MODO CAYENDO / DUMP (BÚNKER 100% USDT): CERO compras.
    # 2. 🟡 MODO ESTABLE / RANGO (FRANCOTIRADOR SELECTIVO): Solo Suelos de Rango.
    # 3. 🟢 MODO ALCISTA / RALLY (RUNNER INSTITUCIONAL): Expansión con Trailing.
    # ═══════════════════════════════════════════════════════════════════════
    is_btc_in_dump = bool(
        btc_1h_pct <= -0.35 or
        (btc_below_ema21_1h and btc_rsi_1h < 48.0) or
        (btc_rsi_15m < 35.0 and btc_cascade) or
        (btc_score < 25 and (btc_cascade or btc_rsi_15m < 38.0))
    )
    is_btc_in_rally = bool(
        not is_btc_in_dump and
        not btc_cascade and
        (btc_1h_pct >= +0.30 or (not btc_below_ema21_1h and btc_rsi_1h >= 52.0 and btc_score >= 50))
    )

    if is_btc_in_dump:
        btc_status_label = f"🔴 CAYENDO / SANGRANDO (BTC 1H={btc_1h_pct:+.2f}% | RSI 1H={btc_rsi_1h:.1f} | Prohibido Comprar Altcoins)"
        btc_regime = "BEARISH_DUMP"
        semaphore = "🔴 DEFENSIVO (HOLD 100% USDT - BÚNKER TOTAL)"
        is_trade_authorized = False
    elif is_btc_in_rally:
        btc_status_label = f"🟢 ALCISTA / RALLY (BTC 1H={btc_1h_pct:+.2f}% | Sobre EMA21 | RSI 1H={btc_rsi_1h:.1f})"
        btc_regime = "BULLISH_SUPPORTIVE"
        semaphore = "🟢 RISK-ON (Alta Confianza Spot - Modo Runner)"
        is_trade_authorized = True
    else:
        btc_status_label = f"🟡 ESTABLE / RANGO (BTC 1H={btc_1h_pct:+.2f}% | Consolidación | Solo Suelos A+)"
        btc_regime = "CONSOLIDATING"
        semaphore = "🟡 CAUTELOSO (Francotirador de Rango - Solo Suelos A+)"
        is_trade_authorized = True

    # 2. 📊 MARKET BREADTH & INSTITUTIONAL ABSORPTION
    accumulating_count = 0
    bullish_count = 0
    bearish_count = 0
    
    for d in symbol_analysis_map.values():
        score = d.get("score", 50)
        mtf = d.get("tech", {}).get("mtf_analysis", {})
        is_obv_acc = mtf.get("is_obv_accumulating", False)
        fii = mtf.get("fii_score", 0)
        
        if score >= 60:
            bullish_count += 1
        elif score <= 40:
            bearish_count += 1
            
        if is_obv_acc or fii >= 50:
            accumulating_count += 1

    absorption_pct = round((accumulating_count / max(1, total)) * 100.0, 1)
    bullish_pct = round((bullish_count / max(1, total)) * 100.0, 1)
    
    if absorption_pct >= 45.0:
        breadth_label = f"🟢 Alta Absorción Institucional ({absorption_pct}% activos con FII >= 50)"
    elif absorption_pct >= 30.0:
        breadth_label = f"🟡 Absorción Selectiva ({absorption_pct}% activos con FII >= 50)"
    else:
        breadth_label = f"🔴 Distribución Generalizada ({absorption_pct}% absorción | Trampas activas)"
        if semaphore == "🟢 RISK-ON (Alta Confianza Spot)":
            semaphore = "🟡 CAUTELOSO (Selectivo A+)"

    # 3. 🧩 SECTOR ROTATION & HOT MONEY TRACKER
    SECTOR_MAP = {
        "DeFi / Yield": ["AAVE", "UNI", "PENDLE", "MKR", "CRV", "SNX", "COMP", "LDO", "SUSHI", "DYDX", "ENA", "SYRUP"],
        "AI & Compute": ["FET", "TAO", "GRT", "WLD", "AGIX", "NMR", "OCEAN", "KAITO"],
        "Layer 2": ["ARB", "OP", "POL", "MATIC", "STRK", "ZK", "IMX", "LRC", "HEMI"],
        "Memes / High-Beta": ["PEPE", "BOME", "DOGE", "SHIB", "FLOKI", "BONK", "WIF", "NEIRO", "MEME", "PEOPLE"],
        "L1 Leaders / Infra": ["SUI", "NEAR", "APT", "SEI", "INJ", "AVAX", "LINK", "DOT", "KAS", "ATOM", "ZRO"]
    }
    
    sector_scores = {}
    for sec_name, tokens in SECTOR_MAP.items():
        matched_scores = []
        for t in tokens:
            sym_key = f"{t}USDT"
            if sym_key in symbol_analysis_map:
                matched_scores.append(symbol_analysis_map[sym_key].get("score", 50))
        if matched_scores:
            sector_scores[sec_name] = round(sum(matched_scores) / len(matched_scores), 1)

    top_sector = max(sector_scores.items(), key=lambda x: x[1])[0] if sector_scores else "DeFi / Yield"
    top_sector_score = sector_scores.get(top_sector, 60.0)

    # 4. 🎯 TOP 3 FINALISTS IDENTIFICATION
    top_syms = [c["symbol"] for c in (top_candidates[:3] if top_candidates else [])]
    top_str = ", ".join(top_syms) if top_syms else "N/A"
    
    fg_val = fear_greed.get("score", 50) if isinstance(fear_greed, dict) else 50
    fg_label = fear_greed.get("sentiment", "Neutral") if isinstance(fear_greed, dict) else "Neutral"

    # 5. 🖥️ MILITARY-GRADE DASHBOARD PRINT
    dashboard_lines = [
        "\n🏛️ ═══════════════════════════════════════════════════════════════════",
        "📡 [MATRIZ MACRO CUÁNTICA & RÉGIMEN DE MERCADO]",
        "═══════════════════════════════════════════════════════════════════════",
        f"  🚦 Semáforo de Régimen: {semaphore}",
        f"  🪙 Guardián Bitcoin: ${btc_price:,.0f} (RSI 15M: {btc_rsi_15m:.1f} | Score: {btc_score}) -> {btc_status_label}",
        f"  📊 Amplitud de Mercado: {breadth_label} ({bullish_pct}% Fuertes de {total} analizados)",
        f"  🔥 Sector Líder Institucional: {top_sector} (Score Promedio: {top_sector_score}/100 | Prioridad Alta)",
        f"  🎯 Top 3 Líderes del Escáner (de {total} Pares Top 100 CMC): [{top_str}] | Fear & Greed: {fg_val} ({fg_label})",
        "═══════════════════════════════════════════════════════════════════════\n"
    ]
    for line in dashboard_lines:
        try:
            print(line)
        except UnicodeEncodeError:
            print(line.encode('ascii', errors='replace').decode('ascii'))

    summary_ctx = (
        f"MERCADO MACRO CUÁNTICO: Semáforo={semaphore} | BTC={btc_status_label} (${btc_price:,.0f}, RSI15M={btc_rsi_15m:.1f}) | "
        f"Amplitud={breadth_label} | Sector Líder={top_sector} ({top_sector_score} Pts) | Fear&Greed={fg_val} ({fg_label})"
    )
    
    return {
        "semaphore": semaphore,
        "is_authorized": is_trade_authorized,
        "btc_regime": btc_regime,
        "btc_price": btc_price,
        "btc_rsi_15m": btc_rsi_15m,
        "absorption_pct": absorption_pct,
        "leader_sector": top_sector,
        "leader_sector_score": top_sector_score,
        "summary_text": summary_ctx
    }
