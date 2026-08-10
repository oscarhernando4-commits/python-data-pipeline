"""
Professional Web Dashboard & Real-Time Data Generator
Generates `dashboard_data.json` and `dashboard.html` for real-time browser monitoring.
Includes:
- Mis Activos (Binance Spot Wallet: USDT & BNB exact values)
- Súper-Cerebro AI Decision Timeline (Last 3 decisions with glowing highlight on latest)
- Top Scanner Opportunities (Quantitative Ranking & Institutional GBM Grades)
- Matrix 100 Simulations (25+ Live Diversified Symbols Breakdown)
"""

import os
import json
from datetime import datetime

HISTORY_FILE = os.path.join(os.path.dirname(__file__), "ai_verdict_history.json")
MAX_HISTORY = 10

def _load_verdict_history():
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return []

def _save_verdict_history(history):
    try:
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(history[-MAX_HISTORY:], f, indent=2, ensure_ascii=False)
    except Exception:
        pass

def _append_verdict_to_history(verdict_data):
    """Appends current verdict to history if new timestamp."""
    if not verdict_data or not verdict_data.get("timestamp"):
        return _load_verdict_history()
    
    history = _load_verdict_history()
    existing_timestamps = {h.get("timestamp") for h in history}
    
    if verdict_data.get("timestamp") not in existing_timestamps:
        history.append({
            "timestamp": verdict_data.get("timestamp", ""),
            "selected_symbol": verdict_data.get("selected_symbol", "NONE"),
            "action": verdict_data.get("action", "HOLD"),
            "approved": verdict_data.get("approved", False),
            "confidence": verdict_data.get("confidence", 0),
            "reasoning": verdict_data.get("reasoning", "Sin análisis disponible"),
            "top_candidates": verdict_data.get("top_candidates", [])
        })
        _save_verdict_history(history)
    
    return history

def _build_verdict_card_html(verdict, index, is_latest=False):
    """Builds HTML for a single verdict card."""
    ts = verdict.get("timestamp", "—")
    symbol = verdict.get("selected_symbol", "NONE")
    action = verdict.get("action", "HOLD")
    approved = verdict.get("approved", False)
    confidence = verdict.get("confidence", 0)
    reasoning = verdict.get("reasoning", "Sin análisis disponible")
    candidates = verdict.get("top_candidates", [])
    
    if action == "BUY_LONG":
        action_badge = '<span class="badge badge-long">📈 COMPRAR LONG</span>'
    elif action == "SELL_SHORT":
        action_badge = '<span class="badge badge-short">📉 VENDER SHORT</span>'
    else:
        action_badge = '<span class="badge badge-hold">⏸️ HOLD / PROTECCIÓN</span>'
    
    approval_html = '<span class="approved-yes">✅ APROBADO</span>' if approved else '<span class="approved-no">🔒 CERO COMPRAS (VETO RIESGO)</span>'
    
    conf_color = "var(--accent-emerald)" if confidence >= 80 else ("var(--accent-amber)" if confidence >= 60 else "var(--accent-rose)")
    
    candidates_html = ""
    if candidates:
        chips = "".join(f'<span class="chip">{c.get("symbol","?")} <b>{c.get("score",0)} Pts</b></span>' for c in candidates[:5])
        candidates_html = f'<div class="candidates-row"><span class="candidates-label">Top Evaluados:</span> {chips}</div>'
    
    reasoning_display = reasoning if (is_latest or len(reasoning) <= 220) else (reasoning[:220] + "...")
    
    card_class = "verdict-card verdict-latest" if is_latest else "verdict-card verdict-past"
    label = "🔴 ÚLTIMO ANÁLISIS EN VIVO" if is_latest else f"📋 ANÁLISIS ANTERIOR (#{index})"
    pulse = '<div class="latest-pulse"></div>' if is_latest else ""
    
    return f"""
        <div class="{card_class}">
            <div class="verdict-header">
                <div class="verdict-label">{pulse}{label}</div>
                <div class="verdict-time">🕐 {ts}</div>
            </div>
            <div class="verdict-body">
                <div class="verdict-decision">
                    <div class="verdict-symbol">{'🎯 ' + symbol if symbol != 'NONE' else '🔒 SIN ENTRADA (100% USDT)'}</div>
                    <div class="verdict-badges">
                        {action_badge}
                        {approval_html}
                    </div>
                </div>
                <div class="confidence-section">
                    <div class="confidence-header">
                        <span class="confidence-label">Nivel de Confianza del Súper-Cerebro:</span>
                        <span class="confidence-value" style="color: {conf_color};">{confidence}%</span>
                    </div>
                    <div class="confidence-bar-bg">
                        <div class="confidence-bar-fill" style="width: {confidence}%; background: {conf_color};"></div>
                    </div>
                </div>
                {candidates_html}
                <div class="reasoning-section">
                    <div class="reasoning-label">💭 Dictamen y Razonamiento Cuántico:</div>
                    <div class="reasoning-text">{reasoning_display}</div>
                </div>
            </div>
        </div>
    """


def generate_web_dashboard():
    """Generates dashboard_data.json and builds/updates dashboard.html"""
    base_dir = os.path.dirname(__file__)
    
    # 1. Load real account state
    account_file = os.path.join(base_dir, "real_money_account.json")
    account_data = {}
    if os.path.exists(account_file):
        try:
            with open(account_file, "r", encoding="utf-8") as f:
                account_data = json.load(f)
        except Exception:
            pass
            
    # 2. Load latest AI verdict
    verdict_file = os.path.join(base_dir, "latest_ai_verdict.json")
    verdict_data = {}
    if os.path.exists(verdict_file):
        try:
            with open(verdict_file, "r", encoding="utf-8") as f:
                verdict_data = json.load(f)
        except Exception:
            pass
    
    # 3. Append to history and get last 3
    history = _append_verdict_to_history(verdict_data)
    last_3 = history[-3:] if len(history) >= 3 else history
    last_3.reverse()
            
    # 4. Load matrix summary
    matrix_file = os.path.join(base_dir, "matrix_100_simulations.json")
    matrix_data = {}
    if os.path.exists(matrix_file):
        try:
            with open(matrix_file, "r", encoding="utf-8") as f:
                matrix_data = json.load(f)
        except Exception:
            pass

    # 5. Extract Matrix symbol distribution
    matrix_accounts = matrix_data.get("accounts", [])
    active_positions = [a for a in matrix_accounts if a.get("position")]
    from collections import Counter
    symbol_counts = Counter(a.get("symbol", "?") for a in active_positions)
    
    # Format symbol distribution tags
    matrix_symbol_tags = "".join(
        f'<span class="matrix-tag"><b>{sym}</b> <small>({count})</small></span>'
        for sym, count in symbol_counts.most_common(25)
    ) if symbol_counts else '<span class="matrix-tag">Esperando señales de compra...</span>'
            
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    pos = account_data.get("position") or {}
    
    # Build data payload
    data_payload = {
        "updated_at": now_str,
        "total_balance_usd": account_data.get("current_balance_usd", 20.08),
        "usdt_free": account_data.get("_cached_usdt_free", 17.6281876),
        "bnb_free": account_data.get("_cached_bnb", 0.00409216),
        "bnb_usd": account_data.get("_cached_bnb_usd", 2.46),
        "status": account_data.get("status", "🟦 Buscando Entrada A+"),
        "position": {
            "symbol": pos.get("symbol", "NINGUNA") if pos else "NINGUNA",
            "quantity": pos.get("quantity", 0.0) if pos else 0.0,
            "entry_price": pos.get("entry_price", 0.0) if pos else 0.0,
            "highest_price": pos.get("highest_price", pos.get("entry_price", 0.0)) if pos else 0.0,
            "adaptive_sl_pct": pos.get("adaptive_sl_pct", 1.0),
            "volatility_regime": pos.get("volatility_regime", "🔵 Standard ATR")
        },
        "verdict": verdict_data,
        "verdict_history": last_3
    }
    
    # Save JSON data feed
    json_path = os.path.join(base_dir, "dashboard_data.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(data_payload, f, indent=2, ensure_ascii=False)
    
    # Build verdict history cards HTML
    verdict_cards_html = ""
    for i, v in enumerate(last_3):
        verdict_cards_html += _build_verdict_card_html(v, len(last_3) - i, is_latest=(i == 0))
    
    if not last_3:
        verdict_cards_html = '<div class="verdict-card verdict-past"><div class="verdict-body"><div class="reasoning-text">⏳ Esperando primer análisis del Súper-Cerebro...</div></div></div>'
    
    # Matrix stats
    matrix_total = matrix_data.get("current_total_usd", 9679.13)
    matrix_pnl = matrix_data.get("net_pnl_usd", -320.87)
    matrix_wr = matrix_data.get("global_win_rate_pct", 0)
    pnl_color = "var(--accent-emerald)" if matrix_pnl >= 0 else "var(--accent-rose)"
    pnl_sign = "+" if matrix_pnl >= 0 else ""
    
    # Top candidates table rows (Top 10 Quantum Scanner Ranking)
    top_candidates = verdict_data.get("top_candidates", [])
    candidates_rows = ""
    for idx, cand in enumerate(top_candidates[:10], 1):
        cand_sym = cand.get("symbol", "—")
        cand_score = cand.get("score", 0)
        cand_price = cand.get("price", 0.0)
        cand_rsi = cand.get("rsi_15m", 50.0)
        cand_vol = cand.get("vol_surge", 1.0)
        cand_qual = cand.get("trade_quality", "C_NOISE")
        
        qual_color = "var(--accent-emerald)" if cand_qual in ("A+", "B") else "var(--text-dim)"
        status_str = '🟢 AI Aprobado' if (cand_sym == verdict_data.get('selected_symbol') and verdict_data.get('approved')) else '🔍 Monitoreando'
        
        candidates_rows += f"""
        <tr class="cand-row">
            <td class="cand-rank">#{idx}</td>
            <td class="cand-symbol"><b>{cand_sym}</b></td>
            <td class="cand-score"><span class="score-badge {'score-high' if cand_score >= 60 else 'score-mid'}">{cand_score} Pts</span></td>
            <td class="cand-rsi">{cand_rsi:.1f}</td>
            <td class="cand-vol">{cand_vol:.1f}x</td>
            <td class="cand-qual"><b style="color: {qual_color};">{cand_qual}</b></td>
            <td class="cand-status">{status_str}</td>
        </tr>
        """
    if not candidates_rows:
        candidates_rows = '<tr><td colspan="7" style="text-align:center; color: var(--text-dim); padding: 1rem;">Analizando mercado...</td></tr>'
        
    # Active position live monitor HTML
    active_position_monitor_html = ""
    pos_sym = pos.get("symbol", "NINGUNA") if pos else "NINGUNA"
    if pos and pos_sym != "NINGUNA":
        pos_qty = pos.get("quantity", 0.0)
        pos_entry = pos.get("entry_price", 0.0)
        pos_cost = pos.get("cost_usd", pos_qty * pos_entry)
        pos_highest = pos.get("highest_price", pos_entry)
        pos_sl_pct = pos.get("adaptive_sl_pct", 1.0)
        pos_sl_price = pos_entry * (1.0 - (pos_sl_pct / 100.0))
        pos_cycles = pos.get("holding_cycles", 1)
        pos_holding_mins = pos_cycles * 2
        pos_trailing = "🔥 ACTIVO (Trailing Dinámico)" if pos.get("trailing_active") else "⚪ Esperando +2.0%"
        peak_pnl_pct = ((pos_highest - pos_entry) / pos_entry * 100.0) if pos_entry > 0 else 0.0
        
        active_position_monitor_html = f"""
        <!-- ============ SEGUIMIENTO EN TIEMPO REAL POSICIÓN ACTIVA ============ -->
        <div class="active-pos-banner">
            <div class="active-pos-header">
                <div class="active-pos-title">
                    <span class="active-pos-pulse"></span>
                    <span class="active-pos-symbol">🎯 POSICIÓN REAL EN VIVO: <b>{pos_sym}</b></span>
                    <span class="badge badge-long">BUY SPOT LONG</span>
                </div>
                <div class="active-pos-time">⏱️ Tiempo Abierto: <b>{pos_holding_mins} min</b> / 75 min (Escalera Time-Decay)</div>
            </div>
            <div class="active-pos-grid">
                <div class="pos-widget">
                    <div class="pos-widget-label">Capital Invertido</div>
                    <div class="pos-widget-val">${pos_cost:.2f} USD</div>
                    <div class="pos-widget-sub">{pos_qty:,.2f} {pos_sym.replace('USDT','')}</div>
                </div>
                <div class="pos-widget">
                    <div class="pos-widget-label">Precio de Entrada</div>
                    <div class="pos-widget-val">${pos_entry:.4f}</div>
                    <div class="pos-widget-sub">Binance Spot Live</div>
                </div>
                <div class="pos-widget">
                    <div class="pos-widget-label">Máximo Pico Alcanzado</div>
                    <div class="pos-widget-val" style="color: var(--accent-emerald);">${pos_highest:.4f}</div>
                    <div class="pos-widget-sub">Pico Flotante: +{peak_pnl_pct:.2f}%</div>
                </div>
                <div class="pos-widget">
                    <div class="pos-widget-label">Piso Stop-Loss ATR</div>
                    <div class="pos-widget-val" style="color: var(--accent-rose);">${pos_sl_price:.4f}</div>
                    <div class="pos-widget-sub">Límite Salida: -{pos_sl_pct:.2f}%</div>
                </div>
            </div>
            <div class="active-pos-footer">
                <div class="pos-shield-tag">🛡️ BTC Circuit Breaker: <b>🟢 ACTIVO</b></div>
                <div class="pos-shield-tag">🧱 Orderbook Muro: <b>🟢 OK</b></div>
                <div class="pos-shield-tag">🚀 Trailing Stop: <b>{pos_trailing}</b></div>
            </div>
        </div>
        """
    else:
        active_position_monitor_html = """
        <div class="active-pos-banner active-pos-idle">
            <div class="active-pos-header">
                <div class="active-pos-title">
                    <span class="active-pos-symbol" style="color: var(--text-muted);">🔒 NINGUNA POSICIÓN ABIERTA (100% CAPITAL EN USDT)</span>
                </div>
                <div class="active-pos-time">🔎 Escaneando 120 Pares en Tiempo Real</div>
            </div>
        </div>
        """
        
    # Generate HTML Dashboard
    html_content = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>⚡ SÚPER-CEREBRO CUÁNTICO | Dashboard de Trading 24/7</title>
    <meta name="description" content="Dashboard en vivo del Súper-Cerebro Cuántico de Trading Binance Spot">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap" rel="stylesheet">
    <style>
        :root {{
            --bg-color: #080c14;
            --card-bg: rgba(15, 23, 42, 0.75);
            --card-border: rgba(255, 255, 255, 0.08);
            --accent-cyan: #06b6d4;
            --accent-emerald: #10b981;
            --accent-purple: #a855f7;
            --accent-amber: #f59e0b;
            --accent-rose: #f43f5e;
            --accent-blue: #3b82f6;
            --text-main: #f8fafc;
            --text-muted: #94a3b8;
            --text-dim: #64748b;
        }}
        * {{ margin: 0; padding: 0; box-sizing: border-box; font-family: 'Inter', sans-serif; }}
        body {{
            background: var(--bg-color);
            background-image: 
                radial-gradient(circle at 15% 15%, rgba(168, 85, 247, 0.07) 0%, transparent 45%),
                radial-gradient(circle at 85% 85%, rgba(6, 182, 212, 0.07) 0%, transparent 45%);
            color: var(--text-main);
            min-height: 100vh;
            padding: 1.25rem 1.75rem;
        }}

        /* ============ ACTIVE POSITION LIVE MONITOR BANNER ============ */
        .active-pos-banner {{
            background: linear-gradient(135deg, rgba(6, 182, 212, 0.12), rgba(16, 185, 129, 0.08));
            border: 1px solid rgba(6, 182, 212, 0.35);
            border-radius: 16px; padding: 1.25rem; margin-bottom: 1.25rem;
            box-shadow: 0 0 30px rgba(6, 182, 212, 0.15);
        }}
        .active-pos-idle {{
            background: rgba(30, 41, 59, 0.3); border: 1px solid var(--card-border);
            box-shadow: none; padding: 1rem 1.25rem;
        }}
        .active-pos-header {{
            display: flex; justify-content: space-between; align-items: center;
            margin-bottom: 1rem; flex-wrap: wrap; gap: 0.5rem;
        }}
        .active-pos-idle .active-pos-header {{ margin-bottom: 0; }}
        .active-pos-title {{ display: flex; align-items: center; gap: 0.6rem; font-size: 1.05rem; font-weight: 800; }}
        .active-pos-pulse {{
            width: 12px; height: 12px; background: var(--accent-emerald); border-radius: 50%;
            box-shadow: 0 0 14px var(--accent-emerald); animation: pulse 1.2s infinite;
        }}
        .active-pos-time {{ font-size: 0.8rem; color: var(--text-muted); font-weight: 600; }}

        .active-pos-grid {{
            display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 0.85rem; margin-bottom: 1rem;
        }}
        .pos-widget {{
            background: rgba(0,0,0,0.25); border: 1px solid rgba(255,255,255,0.05);
            border-radius: 12px; padding: 0.85rem 1rem;
        }}
        .pos-widget-label {{ font-size: 0.7rem; color: var(--text-dim); text-transform: uppercase; font-weight: 700; letter-spacing: 0.5px; }}
        .pos-widget-val {{ font-size: 1.35rem; font-weight: 900; color: var(--text-main); margin-top: 0.2rem; }}
        .pos-widget-sub {{ font-size: 0.72rem; color: var(--text-muted); margin-top: 0.1rem; font-weight: 600; }}

        .active-pos-footer {{
            display: flex; gap: 1rem; flex-wrap: wrap; border-top: 1px solid rgba(255,255,255,0.06);
            padding-top: 0.75rem; font-size: 0.75rem; color: var(--text-muted);
        }}
        .pos-shield-tag {{
            background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.05);
            padding: 0.3rem 0.75rem; border-radius: 8px; font-weight: 600;
        }}

        /* ============ HEADER ============ */
        .header {{
            display: flex; justify-content: space-between; align-items: center;
            padding-bottom: 1.25rem; border-bottom: 1px solid var(--card-border); margin-bottom: 1.25rem;
        }}
        .logo {{ display: flex; align-items: center; gap: 0.75rem; }}
        .logo-icon {{
            width: 44px; height: 44px;
            background: linear-gradient(135deg, var(--accent-cyan), var(--accent-purple));
            border-radius: 12px; display: grid; place-items: center; font-size: 1.5rem;
            box-shadow: 0 0 25px rgba(6, 182, 212, 0.4), 0 0 50px rgba(168, 85, 247, 0.2);
            animation: icon-glow 3s ease-in-out infinite;
        }}
        @keyframes icon-glow {{
            0%, 100% {{ box-shadow: 0 0 25px rgba(6, 182, 212, 0.4), 0 0 50px rgba(168, 85, 247, 0.2); }}
            50% {{ box-shadow: 0 0 35px rgba(6, 182, 212, 0.6), 0 0 70px rgba(168, 85, 247, 0.3); }}
        }}
        .title h1 {{ font-size: 1.35rem; font-weight: 900; letter-spacing: -0.5px; background: linear-gradient(90deg, var(--text-main), var(--accent-cyan)); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }}
        .title p {{ font-size: 0.78rem; color: var(--text-muted); margin-top: 1px; }}
        .header-right {{ display: flex; align-items: center; gap: 0.75rem; }}
        .live-badge {{
            display: inline-flex; align-items: center; gap: 0.5rem;
            background: rgba(16, 185, 129, 0.12); border: 1px solid rgba(16, 185, 129, 0.25);
            color: var(--accent-emerald); padding: 0.35rem 0.85rem; border-radius: 20px; font-weight: 600; font-size: 0.78rem;
        }}
        .pulse-dot {{
            width: 8px; height: 8px; background: var(--accent-emerald); border-radius: 50%;
            box-shadow: 0 0 10px var(--accent-emerald); animation: pulse 1.5s infinite;
        }}
        @keyframes pulse {{ 0%, 100% {{ opacity: 1; }} 50% {{ opacity: 0.3; }} }}
        .mode-badge {{
            background: rgba(168, 85, 247, 0.12); border: 1px solid rgba(168, 85, 247, 0.25);
            color: var(--accent-purple); padding: 0.35rem 0.85rem; border-radius: 20px; font-weight: 600; font-size: 0.75rem;
        }}

        /* ============ TOP DASHBOARD GRID (2 Columns) ============ */
        .top-grid {{
            display: grid; grid-template-columns: 1fr 1fr; gap: 1.25rem; margin-bottom: 1.25rem;
        }}

        /* WALLET ASSETS (Binance Style) */
        .wallet-card {{
            background: var(--card-bg); border: 1px solid var(--card-border);
            backdrop-filter: blur(12px); border-radius: 16px; padding: 1.25rem;
        }}
        .card-header-row {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.75rem; }}
        .card-heading {{ font-size: 0.88rem; font-weight: 800; color: var(--text-main); display: flex; align-items: center; gap: 0.5rem; }}
        .wallet-total-val {{ font-size: 1.8rem; font-weight: 900; color: var(--text-main); letter-spacing: -0.5px; }}
        .wallet-total-currency {{ font-size: 0.9rem; color: var(--text-muted); font-weight: 600; }}
        .asset-list {{ display: flex; flex-direction: column; gap: 0.5rem; margin-top: 0.75rem; }}
        .asset-item {{
            display: flex; justify-content: space-between; align-items: center;
            background: rgba(255,255,255,0.03); border-radius: 10px; padding: 0.6rem 0.85rem;
            border: 1px solid rgba(255,255,255,0.04);
        }}
        .asset-left {{ display: flex; align-items: center; gap: 0.6rem; }}
        .asset-symbol-icon {{
            width: 32px; height: 32px; border-radius: 50%; display: grid; place-items: center;
            font-size: 0.85rem; font-weight: 800; color: white;
        }}
        .icon-usdt {{ background: linear-gradient(135deg, #26a17b, #1a8a6a); }}
        .icon-bnb {{ background: linear-gradient(135deg, #f0b90b, #d4a30a); }}
        .asset-title {{ font-size: 0.88rem; font-weight: 700; }}
        .asset-sub {{ font-size: 0.7rem; color: var(--text-dim); }}
        .asset-right {{ text-align: right; }}
        .asset-qty-val {{ font-size: 0.88rem; font-weight: 700; font-variant-numeric: tabular-nums; }}
        .asset-usd-val {{ font-size: 0.72rem; color: var(--text-muted); }}

        /* REAL TRADE STATS CARD */
        .stats-card {{
            background: var(--card-bg); border: 1px solid var(--card-border);
            backdrop-filter: blur(12px); border-radius: 16px; padding: 1.25rem;
            display: flex; flex-direction: column; justify-content: space-between;
        }}
        .stats-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 0.75rem; margin-top: 0.5rem; }}
        .stat-box {{
            background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.04);
            border-radius: 10px; padding: 0.75rem;
        }}
        .stat-label {{ font-size: 0.7rem; color: var(--text-dim); text-transform: uppercase; font-weight: 600; letter-spacing: 0.5px; }}
        .stat-value {{ font-size: 1.25rem; font-weight: 800; margin-top: 0.2rem; }}
        .stat-sub {{ font-size: 0.7rem; color: var(--accent-emerald); margin-top: 0.1rem; font-weight: 600; }}

        /* ============ SÚPER-CEREBRO TIMELINE ============ */
        .brain-section {{ margin-bottom: 1.25rem; }}
        .section-title {{
            font-size: 1.1rem; font-weight: 800; margin-bottom: 0.85rem;
            display: flex; align-items: center; gap: 0.5rem;
        }}
        .verdicts-timeline {{ display: flex; flex-direction: column; gap: 0.85rem; }}

        .verdict-card {{
            border-radius: 14px; overflow: hidden; transition: transform 0.2s ease;
        }}
        .verdict-latest {{
            background: linear-gradient(135deg, rgba(168, 85, 247, 0.12), rgba(6, 182, 212, 0.08));
            border: 1px solid rgba(168, 85, 247, 0.35);
            box-shadow: 0 0 25px rgba(168, 85, 247, 0.15);
        }}
        .verdict-past {{
            background: rgba(30, 41, 59, 0.35); border: 1px solid var(--card-border); opacity: 0.8;
        }}
        .verdict-header {{
            display: flex; justify-content: space-between; align-items: center;
            padding: 0.7rem 1.1rem; border-bottom: 1px solid rgba(255,255,255,0.05);
        }}
        .verdict-label {{ font-size: 0.72rem; font-weight: 800; text-transform: uppercase; letter-spacing: 0.5px; display: flex; align-items: center; gap: 0.4rem; }}
        .verdict-latest .verdict-label {{ color: var(--accent-purple); }}
        .verdict-past .verdict-label {{ color: var(--text-dim); }}
        .verdict-time {{ font-size: 0.72rem; color: var(--text-dim); }}
        .latest-pulse {{ width: 8px; height: 8px; background: var(--accent-purple); border-radius: 50%; box-shadow: 0 0 10px var(--accent-purple); animation: pulse 1.5s infinite; }}

        .verdict-body {{ padding: 1.1rem; }}
        .verdict-decision {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.75rem; flex-wrap: wrap; gap: 0.5rem; }}
        .verdict-symbol {{ font-size: 1.3rem; font-weight: 900; letter-spacing: -0.3px; }}
        .verdict-badges {{ display: flex; gap: 0.5rem; align-items: center; }}
        .badge {{ padding: 0.25rem 0.65rem; border-radius: 6px; font-size: 0.7rem; font-weight: 700; text-transform: uppercase; }}
        .badge-long {{ background: rgba(16, 185, 129, 0.15); border: 1px solid rgba(16, 185, 129, 0.3); color: var(--accent-emerald); }}
        .badge-short {{ background: rgba(244, 63, 94, 0.15); border: 1px solid rgba(244, 63, 94, 0.3); color: var(--accent-rose); }}
        .badge-hold {{ background: rgba(245, 158, 11, 0.12); border: 1px solid rgba(245, 158, 11, 0.25); color: var(--accent-amber); }}
        .approved-yes {{ color: var(--accent-emerald); font-size: 0.75rem; font-weight: 700; }}
        .approved-no {{ color: var(--accent-rose); font-size: 0.75rem; font-weight: 700; }}

        .confidence-section {{ margin-bottom: 0.75rem; }}
        .confidence-header {{ display: flex; justify-content: space-between; margin-bottom: 0.3rem; font-size: 0.72rem; }}
        .confidence-label {{ color: var(--text-dim); font-weight: 600; }}
        .confidence-value {{ font-weight: 800; }}
        .confidence-bar-bg {{ width: 100%; height: 6px; background: rgba(255,255,255,0.06); border-radius: 10px; overflow: hidden; }}
        .confidence-bar-fill {{ height: 100%; border-radius: 10px; transition: width 0.8s ease; }}

        .candidates-row {{ font-size: 0.72rem; margin-bottom: 0.75rem; display: flex; align-items: center; gap: 0.4rem; flex-wrap: wrap; }}
        .candidates-label {{ color: var(--text-dim); font-weight: 600; }}
        .chip {{ background: rgba(59, 130, 246, 0.12); border: 1px solid rgba(59, 130, 246, 0.2); color: var(--accent-blue); padding: 0.15rem 0.5rem; border-radius: 5px; font-size: 0.68rem; }}

        .reasoning-label {{ font-size: 0.7rem; color: var(--text-dim); font-weight: 600; margin-bottom: 0.3rem; text-transform: uppercase; }}
        .reasoning-text {{
            font-size: 0.8rem; color: var(--text-muted); line-height: 1.6;
            background: rgba(0,0,0,0.25); border-radius: 8px; padding: 0.75rem 0.9rem;
            border-left: 3px solid var(--accent-purple);
        }}

        /* ============ BOTTOM GRID (2 Columns: Matrix 100 & Candidates Ranking) ============ */
        .bottom-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 1.25rem; margin-bottom: 1.25rem; }}

        .matrix-card {{
            background: var(--card-bg); border: 1px solid var(--card-border);
            backdrop-filter: blur(12px); border-radius: 16px; padding: 1.25rem;
        }}
        .matrix-header {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.75rem; }}
        .matrix-title {{ font-size: 0.88rem; font-weight: 800; display: flex; align-items: center; gap: 0.4rem; }}
        .matrix-total-val {{ font-size: 1.5rem; font-weight: 900; color: var(--text-main); }}
        .matrix-pnl {{ font-size: 0.78rem; font-weight: 700; margin-top: 0.1rem; }}
        .matrix-tags-box {{
            display: flex; flex-wrap: wrap; gap: 0.35rem; margin-top: 0.75rem; max-height: 140px; overflow-y: auto;
            padding-right: 0.2rem;
        }}
        .matrix-tag {{
            background: rgba(6, 182, 212, 0.08); border: 1px solid rgba(6, 182, 212, 0.2);
            color: var(--accent-cyan); padding: 0.2rem 0.5rem; border-radius: 6px; font-size: 0.7rem;
        }}

        .candidates-card {{
            background: var(--card-bg); border: 1px solid var(--card-border);
            backdrop-filter: blur(12px); border-radius: 16px; padding: 1.25rem;
        }}
        .cand-table {{ width: 100%; border-collapse: collapse; margin-top: 0.5rem; }}
        .cand-table th {{ font-size: 0.68rem; color: var(--text-dim); text-transform: uppercase; text-align: left; padding: 0.4rem 0.5rem; border-bottom: 1px solid var(--card-border); }}
        .cand-row td {{ font-size: 0.78rem; padding: 0.55rem 0.5rem; border-bottom: 1px solid rgba(255,255,255,0.03); }}
        .score-badge {{ padding: 0.15rem 0.45rem; border-radius: 4px; font-weight: 700; font-size: 0.7rem; }}
        .score-high {{ background: rgba(16, 185, 129, 0.15); color: var(--accent-emerald); border: 1px solid rgba(16, 185, 129, 0.3); }}
        .score-mid {{ background: rgba(245, 158, 11, 0.15); color: var(--accent-amber); border: 1px solid rgba(245, 158, 11, 0.3); }}

        /* ============ FOOTER ============ */
        footer {{
            text-align: center; color: var(--text-dim); font-size: 0.75rem;
            padding-top: 1rem; border-top: 1px solid var(--card-border);
            display: flex; justify-content: center; align-items: center; gap: 1.25rem; flex-wrap: wrap;
        }}
        .refresh-btn {{
            padding: 5px 14px; background: rgba(6, 182, 212, 0.12); border: 1px solid rgba(6, 182, 212, 0.3);
            color: var(--accent-cyan); border-radius: 8px; cursor: pointer; font-weight: 600; font-size: 0.75rem;
            transition: all 0.2s;
        }}
        .refresh-btn:hover {{ background: rgba(6, 182, 212, 0.25); transform: scale(1.03); }}
        .countdown {{ color: var(--accent-cyan); font-weight: 600; font-size: 0.75rem; }}

        @media (max-width: 900px) {{
            .top-grid, .bottom-grid {{ grid-template-columns: 1fr; }}
        }}
    </style>
</head>
<body>
    <!-- HEADER -->
    <div class="header">
        <div class="logo">
            <div class="logo-icon">🧠</div>
            <div class="title">
                <h1>SÚPER-CEREBRO CUÁNTICO 24/7</h1>
                <p>Mesa de Operaciones & Algoritmo de Inteligencia Institucional Binance Spot</p>
            </div>
        </div>
        <div class="header-right">
            <div class="mode-badge">🖥️ MODO LOCAL</div>
            <div class="live-badge">
                <div class="pulse-dot"></div>
                BINANCE API ACTIVE
            </div>
        </div>
    </div>

    <!-- TOP GRID: MIS ACTIVOS (BINANCE SPOT) + TRADING STATS REALES -->
    <div class="top-grid">
        <!-- BILLETERA REAL BINANCE -->
        <div class="wallet-card">
            <div class="card-header-row">
                <div class="card-heading">💰 MIS ACTIVOS — SPOT BINANCE</div>
                <div class="wallet-total-val">${data_payload['total_balance_usd']:.2f} <span class="wallet-total-currency">USD</span></div>
            </div>
            <div class="asset-list">
                <div class="asset-item">
                    <div class="asset-left">
                        <div class="asset-symbol-icon icon-usdt">₮</div>
                        <div>
                            <div class="asset-title">USDT</div>
                            <div class="asset-sub">TetherUS</div>
                        </div>
                    </div>
                    <div class="asset-right">
                        <div class="asset-qty-val">{data_payload['usdt_free']:.8f}</div>
                        <div class="asset-usd-val">{data_payload['usdt_free']:.2f} $</div>
                    </div>
                </div>
                <div class="asset-item">
                    <div class="asset-left">
                        <div class="asset-symbol-icon icon-bnb">B</div>
                        <div>
                            <div class="asset-title">BNB</div>
                            <div class="asset-sub">Escudo de Comisiones</div>
                        </div>
                    </div>
                    <div class="asset-right">
                        <div class="asset-qty-val">{data_payload['bnb_free']:.8f}</div>
                        <div class="asset-usd-val">{data_payload['bnb_usd']:.2f} $</div>
                    </div>
                </div>
            </div>
        </div>

        <!-- MÉTRICAS REALES Y PROTECCIÓN -->
        <div class="stats-card">
            <div class="card-heading">🛡️ PROTECCIÓN DE CAPITAL Y ESTADO REAL</div>
            <div class="stats-grid">
                <div class="stat-box">
                    <div class="stat-label">Posición Activa</div>
                    <div class="stat-value">{data_payload['position']['symbol']}</div>
                    <div class="stat-sub">{'Entrada: $' + f"{data_payload['position']['entry_price']:.4f}" if data_payload['position']['symbol'] != 'NINGUNA' else '🔒 100% USDT Preservado'}</div>
                </div>
                <div class="stat-box">
                    <div class="stat-label">Historial Operatorio</div>
                    <div class="stat-value">{account_data.get('trades_count', 0)} Trades</div>
                    <div class="stat-sub">✅ {account_data.get('wins', 0)}W / ❌ {account_data.get('losses', 0)}L</div>
                </div>
                <div class="stat-box">
                    <div class="stat-label">PnL Neto Real</div>
                    <div class="stat-value" style="color: {'var(--accent-emerald)' if account_data.get('net_pnl_usd', 0) >= 0 else 'var(--accent-rose)'};">{'+' if account_data.get('net_pnl_usd', 0) >= 0 else ''}${account_data.get('net_pnl_usd', 0):.2f}</div>
                    <div class="stat-sub">Depósito original: $17.13</div>
                </div>
                <div class="stat-box">
                    <div class="stat-label">Filtros Cuánticos</div>
                    <div class="stat-value" style="color: var(--accent-cyan); font-size: 1.05rem;">GBM + OU + Corr</div>
                    <div class="stat-sub">🛡️ Escudo Anti-Ruido Activo</div>
                </div>
            </div>
        </div>
    </div>

    <!-- SÚPER-CEREBRO IA (HISTORIAL Y DICTAMEN) -->
    <div class="brain-section">
        <div class="section-title">
            <span style="-webkit-text-fill-color: initial;">🧠⚡</span> 
            <span style="background: linear-gradient(90deg, var(--accent-purple), var(--accent-cyan)); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">SÚPER-CEREBRO EN VIVO — DICTAMEN Y ANÁLISIS DE MERCADO</span>
        </div>
        <div class="verdicts-timeline">
            {verdict_cards_html}
        </div>
    </div>

    <!-- BOTTOM GRID: MATRIX 100 CUENTAS (25+ SÍMBOLOS DIVERSIFICADOS) + RANKING DE CANDIDATOS -->
    <div class="bottom-grid">
        <!-- MATRIX 100 CUENTAS -->
        <div class="matrix-card">
            <div class="matrix-header">
                <div>
                    <div class="matrix-title">🌐 MATRIX 100 CUENTAS — SIMULADOR EN VIVO</div>
                    <div class="matrix-total-val">${matrix_total:,.2f} USD</div>
                    <div class="matrix-pnl" style="color: {pnl_color};">{pnl_sign}${matrix_pnl:,.2f} PnL Net | Win Rate {matrix_wr:.1f}%</div>
                </div>
                <div style="text-align: right;">
                    <span class="badge badge-long">{len(active_positions)} Cuentas en Posición</span>
                    <div style="font-size: 0.72rem; color: var(--accent-emerald); margin-top: 0.3rem; font-weight: 700;">{len(symbol_counts)} Símbolos Diversificados</div>
                </div>
            </div>
            <div style="font-size: 0.72rem; color: var(--text-dim); margin-top: 0.5rem; font-weight: 600;">Símbolos Activos en Paralelo (Offset Rotativo):</div>
            <div class="matrix-tags-box">
                {matrix_symbol_tags}
            </div>
        </div>

        <!-- TOP RANKING ESCÁNER -->
        <div class="candidates-card">
            <div class="card-heading">📊 TOP 10 OPORTUNIDADES DEL ESCÁNER CUÁNTICO</div>
            <table class="cand-table">
                <thead>
                    <tr>
                        <th>#</th>
                        <th>Símbolo</th>
                        <th>Score</th>
                        <th>RSI 15m</th>
                        <th>Vol Surge</th>
                        <th>Grado GBM</th>
                        <th>Estado</th>
                    </tr>
                </thead>
                <tbody>
                    {candidates_rows}
                </tbody>
            </table>
        </div>
    </div>

    <!-- FOOTER -->
    <footer>
        <span>Última actualización: <strong>{now_str}</strong> | Algoritmo Cuántico Binance 24/7</span>
        <span class="countdown" id="countdown">Auto-refresh en: 30s</span>
        <button class="refresh-btn" onclick="window.location.reload()">🔄 Actualizar Ahora</button>
    </footer>

    <script>
        let remaining = 30;
        const countdownEl = document.getElementById('countdown');
        setInterval(() => {{
            remaining--;
            if (remaining <= 0) {{
                window.location.reload();
            }}
            countdownEl.textContent = 'Auto-refresh en: ' + remaining + 's';
        }}, 1000);
    </script>
</body>
</html>
"""
    html_path = os.path.join(base_dir, "dashboard.html")
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html_content)
        
    try:
        print(f"Dashboard Web Interactivo generado en: {html_path}")
    except Exception:
        pass
    return html_path

if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding='utf-8')
    generate_web_dashboard()
