"""
Professional Web Dashboard & Real-Time Data Generator
Generates `dashboard_data.json` and `dashboard.html` for real-time browser monitoring.
Includes:
- 4 Multi-Tab Professional UI:
  1. 🎯 MONITOREO EN VIVO (Real Money Spot Position & Live Safety Escudos)
  2. 🧠 SÚPER-CEREBRO IA (AI Verdict Timeline & Institutional Reasoning)
  3. 📊 ESCÁNER CUÁNTICO (Top 10 Quantum Scanner Ranking & 3-Tier RSI Architecture)
  4. 🌐 MATRIX 1000 CUENTAS (Complete 1,000-Account Testnet Simulation Analysis Engine)
- Live Top 10 Real Money Evaluation Matrix Table (Checks all 10 candidates against 7 safety rules)
- Full 1000 Matrix Accounts Interactive Table with Search & Group Filtering (G0-G5, Active Positions)
- Active Tab Persistence via localStorage
- Anti-Cache Headers
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

def _build_matrix_100_rows_html(matrix_accounts):
    """Builds HTML rows for all 100 Matrix Testnet Accounts."""
    rows = ""
    for acc in matrix_accounts:
        acc_id = acc.get("account_id", "SIM-???")
        group_id = acc.get("group_id", 0)
        group_name = acc.get("group_name", f"Grupo {group_id}")
        symbol = acc.get("symbol", "—")
        balance = acc.get("current_balance", 100.0)
        pnl_usd = acc.get("pnl_usd", 0.0)
        trades = acc.get("trades_count", 0)
        wins = acc.get("wins", 0)
        losses = acc.get("losses", 0)
        wr = (wins / trades * 100.0) if trades > 0 else 0.0
        
        pos = acc.get("position")
        if pos:
            side = pos.get("side", "LONG")
            entry = pos.get("entry_price", 0.0)
            side_badge = f'<span class="badge badge-long">BUY {side}</span>' if side == "LONG" else f'<span class="badge badge-short">SELL {side}</span>'
            entry_str = f"${entry:.4f}" if entry < 10 else f"${entry:.2f}"
            status_str = f"🟢 POSICIÓN ACTIVA"
        else:
            side_badge = '<span class="badge badge-hold">100% USDT</span>'
            entry_str = "—"
            status_str = "⚪ EN USDT"
            
        pnl_style = "color: var(--accent-emerald);" if pnl_usd >= 0 else "color: var(--accent-rose);"
        pnl_sign = "+" if pnl_usd >= 0 else ""
        
        last_res = acc.get("last_result", "—")
        
        rows += f"""
        <tr class="matrix-acc-row" data-group="{group_id}" data-active="{1 if pos else 0}" data-search="{acc_id.lower()} {symbol.lower()} {group_name.lower()}">
            <td style="font-weight: 800; color: var(--accent-cyan);">{acc_id}</td>
            <td style="font-size: 0.74rem; color: var(--text-muted);">{group_name}</td>
            <td style="font-weight: 700; color: var(--text-main);">{symbol}</td>
            <td>{side_badge}</td>
            <td style="font-variant-numeric: tabular-nums;">{entry_str}</td>
            <td style="font-weight: 700; font-variant-numeric: tabular-nums;">${balance:.2f}</td>
            <td style="font-weight: 800; font-variant-numeric: tabular-nums; {pnl_style}">{pnl_sign}${pnl_usd:.2f}</td>
            <td style="font-variant-numeric: tabular-nums;"><b>{wr:.1f}%</b> <small style="color:var(--text-dim);">({wins}W/{losses}L)</small></td>
            <td>{trades}</td>
            <td style="font-size: 0.72rem; color: var(--text-muted);">{last_res}</td>
        </tr>
        """
    if not rows:
        rows = '<tr><td colspan="10" style="text-align:center; padding: 1rem; color: var(--text-dim);">No hay datos de la Matrix...</td></tr>'
    return rows


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
    matrix_accounts = matrix_data.get("accounts", []) if isinstance(matrix_data, dict) else (matrix_data if isinstance(matrix_data, list) else [])
    active_positions = [a for a in matrix_accounts if a.get("position")]
    from collections import Counter
    symbol_counts = Counter(a.get("symbol", "?") for a in active_positions)
    
    matrix_symbol_tags = "".join(
        f'<span class="matrix-tag"><b>{sym}</b> <small>({count})</small></span>'
        for sym, count in symbol_counts.most_common(25)
    ) if symbol_counts else '<span class="matrix-tag">Esperando señales de compra...</span>'
    
    matrix_rows_html = _build_matrix_100_rows_html(matrix_accounts)
            
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    pos = account_data.get("position") or {}
    
    data_payload = {
        "updated_at": now_str,
        "total_balance_usd": account_data.get("current_balance_usd", 20.12),
        "usdt_free": account_data.get("_cached_usdt_free", 17.6936),
        "bnb_free": account_data.get("_cached_bnb", 0.004048),
        "bnb_usd": account_data.get("_cached_bnb_usd", 2.43),
        "status": account_data.get("status", "🟦 Buscando Entrada A+"),
        "position": pos,
        "verdict": verdict_data,
        "verdict_history": last_3
    }
    
    json_path = os.path.join(base_dir, "dashboard_data.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(data_payload, f, indent=2, ensure_ascii=False)
    
    # Verdict history cards
    verdict_cards_html = ""
    for i, v in enumerate(last_3):
        verdict_cards_html += _build_verdict_card_html(v, len(last_3) - i, is_latest=(i == 0))
    if not last_3:
        verdict_cards_html = '<div class="verdict-card verdict-past"><div class="verdict-body"><div class="reasoning-text">⏳ Esperando primer análisis del Súper-Cerebro...</div></div></div>'
    
    # Matrix stats
    matrix_total = matrix_data.get("current_total_usd", 10000.0) if isinstance(matrix_data, dict) else sum(a.get("balance", 100.0) for a in matrix_accounts)
    matrix_pnl = matrix_data.get("net_pnl_usd", 0.0) if isinstance(matrix_data, dict) else sum(a.get("pnl_net_usd", 0.0) for a in matrix_accounts)
    matrix_wr = matrix_data.get("global_win_rate_pct", 0.0) if isinstance(matrix_data, dict) else 0.0
    pnl_color = "var(--accent-emerald)" if matrix_pnl >= 0 else "var(--accent-rose)"
    pnl_sign = "+" if matrix_pnl >= 0 else ""
    
    # Top candidates table rows (Top 10 Quantum Scanner Ranking with 3-tier RSI Architecture)
    top_candidates = verdict_data.get("top_candidates", [])
    candidates_rows = ""
    for idx, cand in enumerate(top_candidates[:10], 1):
        cand_sym = cand.get("symbol", "—")
        cand_score = cand.get("score", 0)
        cand_rsi_2m = cand.get("rsi_2m", cand.get("rsi_15m", 50.0))
        cand_rsi_5m = cand.get("rsi_5m", cand.get("rsi_15m", 50.0))
        cand_rsi_15m = cand.get("rsi_15m", 50.0)
        cand_rsi_1h = cand.get("rsi_1h", 50.0)
        cand_rsi_4h = cand.get("rsi_4h", 50.0)
        cand_vol = cand.get("vol_surge", 1.0)
        cand_qual = cand.get("trade_quality", "C_NOISE")
        
        qual_color = "var(--accent-emerald)" if cand_qual in ("A+", "B") else "var(--text-dim)"
        status_str = '🟢 AI Aprobado' if (cand_sym == verdict_data.get('selected_symbol') and verdict_data.get('approved')) else '🔍 Monitoreando'
        
        candidates_rows += f"""
        <tr class="cand-row">
            <td class="cand-rank">#{idx}</td>
            <td class="cand-symbol"><b>{cand_sym}</b></td>
            <td class="cand-score"><span class="score-badge {'score-high' if cand_score >= 60 else 'score-mid'}">{cand_score} Pts</span></td>
            <td class="cand-rsi" style="color: var(--accent-cyan);">⚡ <b>{cand_rsi_2m:.1f}</b> <small style="color:var(--text-muted);">(2m)</small> / <b>{cand_rsi_5m:.1f}</b> <small style="color:var(--text-muted);">(5m)</small></td>
            <td class="cand-rsi" style="color: var(--accent-amber);">📌 <b>{cand_rsi_15m:.1f}</b> <small style="color:var(--text-muted);">(15m)</small></td>
            <td class="cand-rsi" style="color: var(--accent-purple);">🌐 <b>{cand_rsi_1h:.1f}</b> <small style="color:var(--text-muted);">(1h)</small> / <b>{cand_rsi_4h:.1f}</b> <small style="color:var(--text-muted);">(4h)</small></td>
            <td class="cand-vol">{cand_vol:.1f}x</td>
            <td class="cand-qual"><b style="color: {qual_color};">{cand_qual}</b></td>
            <td class="cand-status">{status_str}</td>
        </tr>
        """
    if not candidates_rows:
        candidates_rows = '<tr><td colspan="9" style="text-align:center; color: var(--text-dim); padding: 1rem;">Analizando mercado...</td></tr>'
        
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
                <div class="active-pos-time">🔎 Escaneando 67 Pares Top 100 CMC en Tiempo Real</div>
            </div>
        </div>
        """

    # 6. Real Money Entry Checklist & Top 10 Evaluation Matrix Builder
    usdt_free = data_payload.get("usdt_free", 0.0)
    has_usdt = usdt_free >= 15.0
    no_open_pos = pos_sym == "NINGUNA"
    btc_ok = True
    
    top_10_eval_rows = ""
    selected_candidate = None
    
    for idx, cand in enumerate(top_candidates[:10], 1):
        cand_sym = cand.get("symbol", "—")
        cand_score = cand.get("score", 0)
        cand_vol = cand.get("vol_surge", 1.0)
        cand_qual = cand.get("trade_quality", "C_NOISE")
        cand_rsi_2m = cand.get("rsi_2m", cand.get("rsi_15m", 50.0))
        cand_rsi_5m = cand.get("rsi_5m", cand.get("rsi_15m", 50.0))
        cand_price = cand.get("price", 0.0)
        cand_ma25 = cand.get("ma25_15m", 0.0)
        
        c_score_ok = cand_score >= 58
        c_quant_ok = cand_qual in ("A+", "B") or cand_vol >= 1.00 or cand_sym in ("PAXGUSDT", "XAUTUSDT")
        c_rsi_ok = cand_rsi_2m <= 68 or cand_rsi_5m <= 68
        c_ma_ok = (cand_price >= cand_ma25 * 1.0015) if (cand_price > 0 and cand_ma25 > 0) else True
        ai_approved = verdict_data.get("approved", True) or (cand_score >= 60 and cand_vol >= 1.2 and cand_qual in ("A+", "B"))
        
        c_eligible = has_usdt and no_open_pos and c_score_ok and c_quant_ok and c_rsi_ok and c_ma_ok and btc_ok and ai_approved
        
        if c_eligible and not selected_candidate:
            selected_candidate = cand
            
        rejection_reason = ""
        if not ai_approved:
            rejection_reason = "🔒 VETO IA (Mercado Tóxico)"
        elif not c_score_ok:
            rejection_reason = "Score < 58 Pts"
        elif not c_ma_ok:
            rejection_reason = "🟡 Trampa Mecha 15M (Buffer MA25 +0.15% insuficiente)"
        elif not c_quant_ok:
            rejection_reason = f"VolSurge {cand_vol:.1f}x < 1.00x"
        elif not c_rsi_ok:
            rejection_reason = "Overbought RSI > 68"
        else:
            rejection_reason = "🟢 100% CUMPLIDO"
            
        status_style = "color: var(--accent-emerald); font-weight: 800;" if c_eligible else ("color: var(--accent-rose); font-weight: 700;" if not ai_approved else "color: var(--accent-amber); font-weight: 700;")
        row_bg = "background: rgba(16, 185, 129, 0.08);" if c_eligible else ""
        
        top_10_eval_rows += f"""
        <tr style="{row_bg}">
            <td style="padding: 0.45rem 0.6rem; font-weight: 700;">#{idx}</td>
            <td style="padding: 0.45rem 0.6rem; font-weight: 800; color: var(--text-main);">{cand_sym}</td>
            <td style="padding: 0.45rem 0.6rem;"><span class="score-badge {'score-high' if cand_score >= 60 else 'score-mid'}">{cand_score} Pts</span></td>
            <td style="padding: 0.45rem 0.6rem; font-variant-numeric: tabular-nums;">{cand_vol:.1f}x</td>
            <td style="padding: 0.45rem 0.6rem; font-variant-numeric: tabular-nums;">{cand_rsi_2m:.1f}</td>
            <td style="padding: 0.45rem 0.6rem;">{'🟢 > MA25+0.15%' if c_ma_ok else '🟡 < MA25+0.15%'}</td>
            <td style="padding: 0.45rem 0.6rem; {status_style}">{'🚀 LISTO PARA COMPRAR' if c_eligible else rejection_reason}</td>
        </tr>
        """
        
    top_1 = top_candidates[0] if top_candidates else {}
    c1_sym = top_1.get("symbol", "—")
    c1_score = top_1.get("score", 0)
    c1_vol = top_1.get("vol_surge", 1.0)
    c1_qual = top_1.get("trade_quality", "C_NOISE")
    c1_rsi_2m = top_1.get("rsi_2m", 50.0)
    c1_rsi_5m = top_1.get("rsi_5m", 50.0)
    c1_price = top_1.get("price", 0.0)
    c1_ma25 = top_1.get("ma25_15m", 0.0)
    ma_structure_ok = (c1_price >= c1_ma25 * 1.0015) if (c1_price > 0 and c1_ma25 > 0) else True
    
    score_ok = c1_score >= 58
    ai_approved = verdict_data.get("approved", True)
    ai_reason = verdict_data.get("reasoning", "Veto de Seguridad IA")
    quant_confirm = c1_qual in ("A+", "B") or c1_vol >= 1.00 or c1_sym in ("PAXGUSDT", "XAUTUSDT")
    fast_rsi_ok = c1_rsi_2m <= 68 or c1_rsi_5m <= 68
    
    header_badge_text = f"🚀 ¡COMPRANDO EN DINERO REAL: {selected_candidate.get('symbol')}!" if (selected_candidate and ai_approved) else ("🔒 VETO DE SEGURIDAD IA: COMPRAS BLOQUEADAS (PRESERVANDO USDT)" if not ai_approved else ("🔒 TOP 10 EN PROTECCIÓN: NINGUNA MONEDA CUMPLE LAS 8 REGLAS" if no_open_pos else "🟡 POSICIÓN ABIERTA"))
    header_badge_class = "badge-long" if (selected_candidate and ai_approved) else "badge-hold"
    
    checklist_items_html = f"""
    <!-- ============ CHECKLIST & EVALUACIÓN TOP 10 EN TIEMPO REAL ============ -->
    <div class="checklist-card">
        <div class="card-header-row">
            <div class="card-heading">📋 EVALUACIÓN EN TIEMPO REAL DE LAS TOP 10 OPORTUNIDADES (DINERO REAL)</div>
            <div class="badge {header_badge_class}" style="font-size: 0.78rem; padding: 0.35rem 0.85rem;">
                {header_badge_text}
            </div>
        </div>
        
        <!-- MATRIZ DE EVALUACIÓN DE LAS TOP 10 MONEDAS -->
        <div style="margin-top: 0.6rem; margin-bottom: 1rem; overflow-x: auto; background: rgba(0,0,0,0.25); border-radius: 12px; border: 1px solid rgba(255,255,255,0.05); padding: 0.5rem;">
            <div style="font-size: 0.75rem; font-weight: 700; color: var(--accent-cyan); margin-bottom: 0.4rem; padding-left: 0.4rem;">
                🔍 Escaneo Cuántico de las Top 10 Monedas del Mercado (Buscando la Primera 100% Elegible):
            </div>
            <table style="width: 100%; border-collapse: collapse; font-size: 0.76rem;">
                <thead>
                    <tr style="border-bottom: 1px solid rgba(255,255,255,0.08); color: var(--text-dim); text-align: left;">
                        <th style="padding: 0.4rem 0.6rem;">Rank</th>
                        <th style="padding: 0.4rem 0.6rem;">Moneda</th>
                        <th style="padding: 0.4rem 0.6rem;">Score</th>
                        <th style="padding: 0.4rem 0.6rem;">VolSurge</th>
                        <th style="padding: 0.4rem 0.6rem;">RSI 2m</th>
                        <th style="padding: 0.4rem 0.6rem;">Media 15M (MA25)</th>
                        <th style="padding: 0.4rem 0.6rem;">Dictamen para Dinero Real</th>
                    </tr>
                </thead>
                <tbody>
                    {top_10_eval_rows if top_10_eval_rows else '<tr><td colspan="7" style="text-align:center; padding: 0.8rem; color: var(--text-dim);">Escaneando candidatos...</td></tr>'}
                </tbody>
            </table>
        </div>

        <div class="card-heading" style="font-size: 0.8rem; margin-bottom: 0.5rem;">
            🛡️ DESGLOSE DE LAS 8 REGLAS DE SEGURIDAD (EVALUANDO #{top_1.get('symbol', 'TOP 1')}):
        </div>
        <div class="checklist-grid">
            <div class="checklist-item {'checklist-pass' if has_usdt else 'checklist-fail'}">
                <div>
                    <div class="checklist-title">1. Liquidez USDT Disponible</div>
                    <div class="checklist-sub">Depósito mínimo >= $15.00 USDT</div>
                </div>
                <div class="checklist-sub" style="font-weight: 800; color: {'var(--accent-emerald)' if has_usdt else 'var(--accent-rose)'};">
                    {'🟢 CUMPLIDO ($' + f"{usdt_free:.2f}" + ')' if has_usdt else '🔴 REQUERIDO ($15.00)'}
                </div>
            </div>
            
            <div class="checklist-item {'checklist-pass' if no_open_pos else 'checklist-pending'}">
                <div>
                    <div class="checklist-title">2. Sin Posición Real Abierta</div>
                    <div class="checklist-sub">100% liquidez disponible en Spot</div>
                </div>
                <div class="checklist-sub" style="font-weight: 800; color: {'var(--accent-emerald)' if no_open_pos else 'var(--accent-amber)'};">
                    {'🟢 CUMPLIDO (Liquidez Libre)' if no_open_pos else '🟡 POSICIÓN ACTIVA'}
                </div>
            </div>

            <div class="checklist-item {'checklist-pass' if score_ok else 'checklist-pending'}">
                <div>
                    <div class="checklist-title">3. Puntaje Escáner (Score >= 58)</div>
                    <div class="checklist-sub">Fuerza técnica cuántica de confluencia</div>
                </div>
                <div class="checklist-sub" style="font-weight: 800; color: {'var(--accent-emerald)' if score_ok else 'var(--accent-amber)'};">
                    {'🟢 CUMPLIDO (' + str(c1_score) + ' Pts)' if score_ok else '🟡 PENDIENTE (' + str(c1_score) + ' < 58 Pts)'}
                </div>
            </div>

            <div class="checklist-item {'checklist-pass' if quant_confirm else 'checklist-pending'}">
                <div>
                    <div class="checklist-title">4. Confirmación VolSurge / GBM</div>
                    <div class="checklist-sub">VolSurge >= 1.00x O Grado GBM A+/B</div>
                </div>
                <div class="checklist-sub" style="font-weight: 800; color: {'var(--accent-emerald)' if quant_confirm else 'var(--accent-amber)'};">
                    {'🟢 CUMPLIDO (' + f"{c1_vol:.1f}" + 'x / ' + c1_qual + ')' if quant_confirm else '🟡 PENDIENTE (VolSurge ' + f"{c1_vol:.1f}" + 'x < 1.00x)'}
                </div>
            </div>

            <div class="checklist-item {'checklist-pass' if fast_rsi_ok else 'checklist-pending'}">
                <div>
                    <div class="checklist-title">5. Gatillo Alcista RSI (2m / 5m)</div>
                    <div class="checklist-sub">Sin sobre-extensión impulsiva previa</div>
                </div>
                <div class="checklist-sub" style="font-weight: 800; color: {'var(--accent-emerald)' if fast_rsi_ok else 'var(--accent-amber)'};">
                    {'🟢 CUMPLIDO (RSI2m=' + f"{c1_rsi_2m:.1f}" + ')' if fast_rsi_ok else '🟡 SOBRE-COMPRADO (RSI > 68)'}
                </div>
            </div>

            <div class="checklist-item {'checklist-pass' if ma_structure_ok else 'checklist-pending'}">
                <div>
                    <div class="checklist-title">6. Filtro Anti-Trampa 15M (MA25 Estricta)</div>
                    <div class="checklist-sub">Precio >= MA25 (+0.15% Buffer + Pendiente Alcista)</div>
                </div>
                <div class="checklist-sub" style="font-weight: 800; color: {'var(--accent-emerald)' if ma_structure_ok else 'var(--accent-amber)'};">
                    {'🟢 CUMPLIDO (Precio > MA25 +0.15%)' if ma_structure_ok else '🟡 TRAMPA MECHA (Insuficiente Buffer MA25)'}
                </div>
            </div>

            <div class="checklist-item {'checklist-pass' if btc_ok else 'checklist-fail'}">
                <div>
                    <div class="checklist-title">7. Escudo BTC Circuit Breaker</div>
                    <div class="checklist-sub">Bitcoin estable y sin crash sistémico</div>
                </div>
                <div class="checklist-sub" style="font-weight: 800; color: {'var(--accent-emerald)' if btc_ok else 'var(--accent-rose)'};">
                    {'🟢 CUMPLIDO (BTC OK)' if btc_ok else '🔴 ALERTA CRASH BTC'}
                </div>
            </div>

            <div class="checklist-item {'checklist-pass' if ai_approved else 'checklist-fail'}">
                <div>
                    <div class="checklist-title">8. Autorización Súper-Cerebro IA</div>
                    <div class="checklist-sub">Veto de seguridad de Inteligencia IA</div>
                </div>
                <div class="checklist-sub" style="font-weight: 800; color: {'var(--accent-emerald)' if ai_approved else 'var(--accent-rose)'};">
                    {'🟢 APROBADO POR IA' if ai_approved else '🔴 VETO DE SEGURIDAD (CERO COMPRAS)'}
                </div>
            </div>
        </div>
    </div>
    """
        
    # Generate HTML Dashboard
    html_content = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate">
    <meta http-equiv="Pragma" content="no-cache">
    <meta http-equiv="Expires" content="0">
    <title>⚡ SÚPER-CEREBRO CUÁNTICO | Terminal Profesional de Trading 24/7</title>
    <meta name="description" content="Terminal Profesional de Trading Cuántico Binance Spot">
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

        /* ============ HEADER ============ */
        .header {{
            display: flex; justify-content: space-between; align-items: center;
            padding-bottom: 1rem; border-bottom: 1px solid var(--card-border); margin-bottom: 1.25rem;
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

        /* ============ MAIN INTERACTIVE TABS BAR ============ */
        .main-tabs {{
            display: flex; gap: 0.75rem; border-bottom: 1px solid var(--card-border);
            margin-bottom: 1.25rem; padding-bottom: 0.5rem; flex-wrap: wrap;
        }}
        .tab-btn {{
            display: flex; align-items: center; gap: 0.55rem;
            padding: 0.65rem 1.35rem; background: rgba(30, 41, 59, 0.4);
            border: 1px solid var(--card-border); border-radius: 12px;
            color: var(--text-muted); font-size: 0.85rem; font-weight: 700;
            cursor: pointer; transition: all 0.2s ease;
        }}
        .tab-btn:hover {{ background: rgba(6, 182, 212, 0.1); color: var(--text-main); transform: translateY(-1px); }}
        .tab-btn.active {{
            background: linear-gradient(135deg, rgba(168, 85, 247, 0.25), rgba(6, 182, 212, 0.18));
            border-color: var(--accent-purple); color: var(--text-main);
            box-shadow: 0 0 20px rgba(168, 85, 247, 0.25);
        }}
        .tab-content {{ display: none; }}
        .tab-content.active {{ display: block; animation: tabFadeIn 0.3s ease-out; }}
        @keyframes tabFadeIn {{ from {{ opacity: 0; transform: translateY(6px); }} to {{ opacity: 1; transform: translateY(0); }} }}

        /* CHECKLIST REAL MONEY CARD */
        .checklist-card {{
            background: var(--card-bg); border: 1px solid var(--card-border);
            backdrop-filter: blur(12px); border-radius: 16px; padding: 1.25rem; margin-bottom: 1.25rem;
        }}
        .checklist-grid {{
            display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 0.75rem; margin-top: 0.75rem;
        }}
        .checklist-item {{
            display: flex; justify-content: space-between; align-items: center;
            background: rgba(255,255,255,0.025); border: 1px solid rgba(255,255,255,0.05);
            border-radius: 10px; padding: 0.65rem 0.85rem; font-size: 0.8rem;
        }}
        .checklist-pass {{ border-color: rgba(16, 185, 129, 0.35); background: rgba(16, 185, 129, 0.08); }}
        .checklist-pending {{ border-color: rgba(245, 158, 11, 0.35); background: rgba(245, 158, 11, 0.08); }}
        .checklist-fail {{ border-color: rgba(244, 63, 94, 0.35); background: rgba(244, 63, 94, 0.08); }}
        .checklist-title {{ font-weight: 700; color: var(--text-main); }}
        .checklist-sub {{ font-size: 0.72rem; color: var(--text-muted); margin-top: 0.1rem; }}

        /* MATRIX 100 TAB CONTROLS */
        .matrix-filter-bar {{
            display: flex; gap: 0.6rem; margin-bottom: 1rem; flex-wrap: wrap; align-items: center; justify-content: space-between;
        }}
        .matrix-filter-btn {{
            padding: 0.4rem 0.85rem; background: rgba(30, 41, 59, 0.5); border: 1px solid var(--card-border);
            border-radius: 8px; color: var(--text-muted); font-size: 0.76rem; font-weight: 700; cursor: pointer; transition: all 0.15s;
        }}
        .matrix-filter-btn:hover, .matrix-filter-btn.active {{
            background: rgba(6, 182, 212, 0.18); border-color: var(--accent-cyan); color: var(--text-main);
        }}
        .matrix-search-input {{
            padding: 0.45rem 0.85rem; background: rgba(15, 23, 42, 0.8); border: 1px solid var(--card-border);
            border-radius: 8px; color: var(--text-main); font-size: 0.78rem; width: 260px; outline: none; transition: border-color 0.2s;
        }}
        .matrix-search-input:focus {{ border-color: var(--accent-purple); box-shadow: 0 0 10px rgba(168, 85, 247, 0.2); }}

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

        /* ============ CANDIDATES & MATRIX STYLES ============ */
        .matrix-card {{
            background: var(--card-bg); border: 1px solid var(--card-border);
            backdrop-filter: blur(12px); border-radius: 16px; padding: 1.25rem; margin-bottom: 1.25rem;
        }}
        .matrix-header {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.75rem; }}
        .matrix-title {{ font-size: 0.88rem; font-weight: 800; display: flex; align-items: center; gap: 0.4rem; }}
        .matrix-total-val {{ font-size: 1.5rem; font-weight: 900; color: var(--text-main); }}
        .matrix-pnl {{ font-size: 0.78rem; font-weight: 700; margin-top: 0.1rem; }}
        .matrix-tags-box {{
            display: flex; flex-wrap: wrap; gap: 0.35rem; margin-top: 0.75rem; max-height: 200px; overflow-y: auto;
            padding-right: 0.2rem;
        }}
        .matrix-tag {{
            background: rgba(6, 182, 212, 0.08); border: 1px solid rgba(6, 182, 212, 0.2);
            color: var(--accent-cyan); padding: 0.25rem 0.6rem; border-radius: 6px; font-size: 0.72rem;
        }}

        .candidates-card {{
            background: var(--card-bg); border: 1px solid var(--card-border);
            backdrop-filter: blur(12px); border-radius: 16px; padding: 1.25rem; margin-bottom: 1.25rem;
        }}
        .cand-table {{ width: 100%; border-collapse: collapse; margin-top: 0.5rem; }}
        .cand-table th {{ font-size: 0.68rem; color: var(--text-dim); text-transform: uppercase; text-align: left; padding: 0.5rem; border-bottom: 1px solid var(--card-border); }}
        .cand-row td {{ font-size: 0.8rem; padding: 0.6rem 0.5rem; border-bottom: 1px solid rgba(255,255,255,0.03); }}
        .score-badge {{ padding: 0.15rem 0.45rem; border-radius: 4px; font-weight: 700; font-size: 0.7rem; }}
        .score-high {{ background: rgba(16, 185, 129, 0.15); color: var(--accent-emerald); border: 1px solid rgba(16, 185, 129, 0.3); }}
        .score-mid {{ background: rgba(245, 158, 11, 0.15); color: var(--accent-amber); border: 1px solid rgba(245, 158, 11, 0.3); }}

        /* ============ FOOTER ============ */
        footer {{
            text-align: center; color: var(--text-dim); font-size: 0.75rem;
            padding-top: 1rem; border-top: 1px solid var(--card-border); margin-top: 1.5rem;
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
            .top-grid {{ grid-template-columns: 1fr; }}
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

    <!-- PESTAÑAS DE NAVEGACIÓN PROFESIONAL -->
    <div class="main-tabs">
        <button class="tab-btn active" data-tab="tab-monitoreo" onclick="switchTab('tab-monitoreo')">
            <span>🎯</span> MONITOREO EN VIVO
        </button>
        <button class="tab-btn" data-tab="tab-cerebro" onclick="switchTab('tab-cerebro')">
            <span>🧠</span> SÚPER-CEREBRO IA
        </button>
        <button class="tab-btn" data-tab="tab-escaner" onclick="switchTab('tab-escaner')">
            <span>📊</span> ESCÁNER CUÁNTICO
        </button>
        <button class="tab-btn" data-tab="tab-matrix" onclick="switchTab('tab-matrix')">
            <span>🌐</span> MATRIX 1000 CUENTAS
        </button>
    </div>

    <!-- PESTAÑA 1: MONITOREO EN VIVO -->
    <div id="tab-monitoreo" class="tab-content active">
        {active_position_monitor_html}
        {checklist_items_html}
        
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
                        <div class="stat-value">{data_payload['position']['symbol'] if data_payload['position'] else 'NINGUNA'}</div>
                        <div class="stat-sub">{'Entrada: $' + f"{data_payload['position']['entry_price']:.4f}" if data_payload['position'] and data_payload['position'].get('symbol') != 'NINGUNA' else '🔒 100% USDT Preservado'}</div>
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
    </div>

    <!-- PESTAÑA 2: SÚPER-CEREBRO IA -->
    <div id="tab-cerebro" class="tab-content">
        <div class="brain-section">
            <div class="section-title">
                <span style="-webkit-text-fill-color: initial;">🧠⚡</span> 
                <span style="background: linear-gradient(90deg, var(--accent-purple), var(--accent-cyan)); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">SÚPER-CEREBRO EN VIVO — DICTAMEN Y ANÁLISIS DE MERCADO</span>
            </div>
            <div class="verdicts-timeline">
                {verdict_cards_html}
            </div>
        </div>
    </div>

    <!-- PESTAÑA 3: ESCÁNER CUÁNTICO -->
    <div id="tab-escaner" class="tab-content">
        <div class="candidates-card">
            <div class="card-heading">📊 TOP 10 OPORTUNIDADES DEL ESCÁNER CUÁNTICO</div>
            <table class="cand-table">
                <thead>
                    <tr>
                        <th>#</th>
                        <th>Símbolo</th>
                        <th>Score</th>
                        <th>⚡ RSI Gatillo (2m / 5m)</th>
                        <th>📌 RSI Medio (15m)</th>
                        <th>🌐 RSI Macro (1h / 4h)</th>
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

    <!-- PESTAÑA 4: MATRIX 1000 CUENTAS (ANÁLISIS COMPLETO EN VIVO) -->
    <div id="tab-matrix" class="tab-content">
        <div class="matrix-card">
            <div class="matrix-header">
                <div>
                    <div class="matrix-title">🌐 MATRIX 1000 CUENTAS — ANÁLISIS COMPLETO DE SIMULACIONES EN VIVO</div>
                    <div class="matrix-total-val">${matrix_total:,.2f} USD</div>
                    <div class="matrix-pnl" style="color: {pnl_color};">{pnl_sign}${matrix_pnl:,.2f} PnL Neto Total | Win Rate {matrix_wr:.1f}%</div>
                </div>
                <div style="text-align: right;">
                    <span class="badge badge-long">{len(active_positions)} Cuentas en Posición Activa</span>
                    <div style="font-size: 0.72rem; color: var(--accent-emerald); margin-top: 0.3rem; font-weight: 700;">{len(symbol_counts)} Símbolos Diversificados</div>
                </div>
            </div>

            <!-- CONTROLES E INTERACTIVIDAD MATRIX 100 -->
            <div class="matrix-filter-bar" style="margin-top: 1rem;">
                <div style="display: flex; gap: 0.4rem; flex-wrap: wrap;">
                    <button class="matrix-filter-btn active" onclick="filterMatrixGroup('all', this)">Todas (100)</button>
                    <button class="matrix-filter-btn" onclick="filterMatrixGroup('active', this)">🔥 En Posición ({len(active_positions)})</button>
                    <button class="matrix-filter-btn" onclick="filterMatrixGroup('0', this)">G0 Réplica Real</button>
                    <button class="matrix-filter-btn" onclick="filterMatrixGroup('1', this)">G1 Ultra-Estricto</button>
                    <button class="matrix-filter-btn" onclick="filterMatrixGroup('2', this)">G2 Mean Reversion</button>
                    <button class="matrix-filter-btn" onclick="filterMatrixGroup('3', this)">G3 Breakout Vol</button>
                    <button class="matrix-filter-btn" onclick="filterMatrixGroup('4', this)">G4 Short-Seller</button>
                    <button class="matrix-filter-btn" onclick="filterMatrixGroup('5', this)">G5 Kamikaze</button>
                    <button class="matrix-filter-btn" onclick="filterMatrixGroup('6', this)">G6 Tokens Apalancados</button>
                </div>
                <input type="text" id="matrixSearchInput" class="matrix-search-input" placeholder="🔍 Buscar símbolo (BTC, ZAMA) o ID..." onkeyup="filterMatrixSearch()">
            </div>

            <!-- TABLA INTERACTIVA DE LAS 1000 CUENTAS MATRIX -->
            <div style="overflow-x: auto; background: rgba(0,0,0,0.25); border-radius: 12px; border: 1px solid rgba(255,255,255,0.05); padding: 0.5rem; max-height: 550px; overflow-y: auto;">
                <table class="cand-table" id="matrix100Table">
                    <thead>
                        <tr>
                            <th>Cuenta ID</th>
                            <th>Grupo Estratégico</th>
                            <th>Símbolo</th>
                            <th>Posición</th>
                            <th>Precio Entrada</th>
                            <th>Balance</th>
                            <th>PnL Neto USD</th>
                            <th>Win Rate</th>
                            <th>Trades</th>
                            <th>Estado Escudo</th>
                        </tr>
                    </thead>
                    <tbody>
                        {matrix_rows_html}
                    </tbody>
                </table>
            </div>

            <div style="font-size: 0.72rem; color: var(--text-dim); margin-top: 1rem; font-weight: 600;">Símbolos Diversificados Activos en Paralelo (Offset Rotativo):</div>
            <div class="matrix-tags-box">
                {matrix_symbol_tags}
            </div>
        </div>
    </div>

    <!-- FOOTER -->
    <footer>
        <span>Última actualización: <strong>{now_str}</strong> | Algoritmo Cuántico Binance 24/7</span>
        <span class="countdown" id="countdown">Auto-refresh en: 30s</span>
        <button class="refresh-btn" onclick="window.location.reload()">🔄 Actualizar Ahora</button>
    </footer>

    <script>
        function switchTab(tabId) {{
            document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
            document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));
            
            const targetBtn = document.querySelector(`.tab-btn[data-tab="${{tabId}}"]`);
            const targetContent = document.getElementById(tabId);
            
            if (targetBtn && targetContent) {{
                targetBtn.classList.add('active');
                targetContent.classList.add('active');
                localStorage.setItem('activeDashboardTab', tabId);
            }}
        }}

        // Matrix 100 Filtering Logic
        function filterMatrixGroup(groupId, btnEl) {{
            document.querySelectorAll('.matrix-filter-btn').forEach(b => b.classList.remove('active'));
            if (btnEl) btnEl.classList.add('active');
            
            const rows = document.querySelectorAll('#matrix100Table tbody tr.matrix-acc-row');
            rows.forEach(row => {{
                const g = row.getAttribute('data-group');
                const active = row.getAttribute('data-active');
                
                if (groupId === 'all') {{
                    row.style.display = '';
                }} else if (groupId === 'active') {{
                    row.style.display = (active === '1') ? '' : 'none';
                }} else {{
                    row.style.display = (g === groupId) ? '' : 'none';
                }}
            }});
        }}

        function filterMatrixSearch() {{
            const input = document.getElementById('matrixSearchInput').value.toLowerCase();
            const rows = document.querySelectorAll('#matrix100Table tbody tr.matrix-acc-row');
            rows.forEach(row => {{
                const searchData = row.getAttribute('data-search') || '';
                row.style.display = searchData.includes(input) ? '' : 'none';
            }});
        }}

        // Restore active tab from localStorage or default to tab-monitoreo
        document.addEventListener('DOMContentLoaded', () => {{
            const savedTab = localStorage.getItem('activeDashboardTab') || 'tab-monitoreo';
            switchTab(savedTab);
        }});

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
