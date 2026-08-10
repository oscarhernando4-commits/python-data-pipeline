"""
Professional Web Dashboard & Real-Time Data Generator
Generates `dashboard_data.json` and `dashboard.html` for real-time browser monitoring.
Built with glassmorphism UI, HSL color tokens, micro-animations, and live 30s auto-refresh.
Includes: Súper-Cerebro AI verdict history (last 3 analyses with reasoning).
"""

import os
import json
from datetime import datetime

HISTORY_FILE = os.path.join(os.path.dirname(__file__), "ai_verdict_history.json")
MAX_HISTORY = 10  # Keep last 10 verdicts for future use

def _load_verdict_history():
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            pass
    return []

def _save_verdict_history(history):
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history[-MAX_HISTORY:], f, indent=2, ensure_ascii=False)

def _append_verdict_to_history(verdict_data):
    """Appends the current verdict to history if it's new (different timestamp)."""
    if not verdict_data or not verdict_data.get("timestamp"):
        return _load_verdict_history()
    
    history = _load_verdict_history()
    
    # Avoid duplicates by checking timestamp
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
    """Builds HTML for a single verdict card. Latest gets special styling."""
    ts = verdict.get("timestamp", "—")
    symbol = verdict.get("selected_symbol", "NONE")
    action = verdict.get("action", "HOLD")
    approved = verdict.get("approved", False)
    confidence = verdict.get("confidence", 0)
    reasoning = verdict.get("reasoning", "Sin análisis disponible")
    candidates = verdict.get("top_candidates", [])
    
    # Action badge
    if action == "BUY_LONG":
        action_badge = '<span class="badge badge-long">📈 COMPRAR LONG</span>'
    elif action == "SELL_SHORT":
        action_badge = '<span class="badge badge-short">📉 VENDER SHORT</span>'
    else:
        action_badge = '<span class="badge badge-hold">⏸️ HOLD</span>'
    
    # Approval
    if approved:
        approval_html = '<span class="approved-yes">✅ APROBADO</span>'
    else:
        approval_html = '<span class="approved-no">🔒 NO APROBADO</span>'
    
    # Confidence bar color
    if confidence >= 80:
        conf_color = "var(--accent-emerald)"
    elif confidence >= 60:
        conf_color = "var(--accent-amber)"
    else:
        conf_color = "var(--accent-rose)"
    
    # Candidates chips
    candidates_html = ""
    if candidates:
        chips = "".join(f'<span class="chip">{c.get("symbol","?")} <b>{c.get("score",0)}</b></span>' for c in candidates[:5])
        candidates_html = f'<div class="candidates-row">{chips}</div>'
    
    # Truncate reasoning for non-latest
    reasoning_display = reasoning
    if not is_latest and len(reasoning) > 200:
        reasoning_display = reasoning[:200] + "..."
    
    card_class = "verdict-card verdict-latest" if is_latest else "verdict-card verdict-past"
    label = "🔴 EN VIVO — ÚLTIMO ANÁLISIS" if is_latest else f"📋 Análisis #{index}"
    number_badge = '<div class="latest-pulse"></div>' if is_latest else ""
    
    return f"""
        <div class="{card_class}">
            <div class="verdict-header">
                <div class="verdict-label">{number_badge}{label}</div>
                <div class="verdict-time">🕐 {ts}</div>
            </div>
            <div class="verdict-body">
                <div class="verdict-decision">
                    <div class="verdict-symbol">{'🎯 ' + symbol if symbol != 'NONE' else '🔒 NINGUNA'}</div>
                    <div class="verdict-badges">
                        {action_badge}
                        {approval_html}
                    </div>
                </div>
                <div class="confidence-section">
                    <div class="confidence-label">Confianza del Comité AI</div>
                    <div class="confidence-bar-bg">
                        <div class="confidence-bar-fill" style="width: {confidence}%; background: {conf_color};"></div>
                    </div>
                    <div class="confidence-value" style="color: {conf_color};">{confidence}%</div>
                </div>
                {candidates_html}
                <div class="reasoning-section">
                    <div class="reasoning-label">💭 Razonamiento del Súper-Cerebro:</div>
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
        except:
            pass
            
    # 2. Load latest AI verdict
    verdict_file = os.path.join(base_dir, "latest_ai_verdict.json")
    verdict_data = {}
    if os.path.exists(verdict_file):
        try:
            with open(verdict_file, "r", encoding="utf-8") as f:
                verdict_data = json.load(f)
        except:
            pass
    
    # 3. Append to history and get last 3
    history = _append_verdict_to_history(verdict_data)
    last_3 = history[-3:] if len(history) >= 3 else history
    last_3.reverse()  # Most recent first
            
    # 4. Load matrix summary
    matrix_file = os.path.join(base_dir, "matrix_100_simulations.json")
    matrix_data = {}
    if os.path.exists(matrix_file):
        try:
            with open(matrix_file, "r", encoding="utf-8") as f:
                matrix_data = json.load(f)
        except:
            pass
            
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    deliberation = verdict_data.get("committee_deliberation", {})
    pos = account_data.get("position") or {}
    
    # Build data payload
    data_payload = {
        "updated_at": now_str,
        "total_balance_usd": account_data.get("current_balance_usd", 19.90),
        "usdt_free": account_data.get("_cached_usdt_free", 0.005),
        "bnb_free": account_data.get("_cached_bnb", 0.00446),
        "status": account_data.get("status", "🟦 Buscando Entrada A+"),
        "position": {
            "symbol": pos.get("symbol", "NINGUNA") if pos else "NINGUNA",
            "quantity": pos.get("quantity", 0.0) if pos else 0.0,
            "entry_price": pos.get("entry_price", 0.0) if pos else 0.0,
            "highest_price": pos.get("highest_price", pos.get("entry_price", 0.0)) if pos else 0.0,
            "break_even": pos.get("break_even", False),
            "trailing_active": pos.get("trailing_active", False),
            "adaptive_sl_pct": pos.get("adaptive_sl_pct", 1.0),
            "volatility_regime": pos.get("volatility_regime", "🔵 Standard ATR")
        },
        "agents": {
            "agent_1_macro": deliberation.get("agent_1_macro", "Análisis de régimen macro y volumen de ballenas en vivo."),
            "agent_2_tech": deliberation.get("agent_2_tech", "Osciladores RSI, MACD, EMAs y mechas de absorción evaluadas."),
            "agent_3_orderbook": deliberation.get("agent_3_orderbook", "Rastro de liquidez del Orderbook y muros de soporte de ballenas."),
            "agent_4_sector": deliberation.get("agent_4_sector", "Evaluación de rotación de capital por cluster sectorial."),
            "agent_5_memory": deliberation.get("agent_5_memory", "Cruzamiento RAG con simulaciones históricas y patrones perdedores."),
            "agent_6_risk": deliberation.get("agent_6_risk", "Evaluación final de preservación de capital, ratio 1:2 y Trailing Stop ATR."),
            "agent_7_ceo_anti_loss": deliberation.get("agent_7_ceo_anti_loss", "Consenso del CEO Supreme Anti-Loss Profit Maximizer.")
        },
        "verdict": {
            "selected_symbol": verdict_data.get("selected_symbol", "NONE"),
            "action": verdict_data.get("action", "HOLD"),
            "confidence": verdict_data.get("confidence", 0),
            "approved": verdict_data.get("approved", False),
            "reasoning": verdict_data.get("reasoning", "El mercado se encuentra en observación defensiva.")
        },
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
    matrix_total = matrix_data.get("current_total_usd", 0)
    matrix_pnl = matrix_data.get("net_pnl_usd", 0)
    matrix_wr = matrix_data.get("global_win_rate_pct", 0)
    pnl_color = "var(--accent-emerald)" if matrix_pnl >= 0 else "var(--accent-rose)"
    pnl_sign = "+" if matrix_pnl >= 0 else ""
        
    # Generate HTML Dashboard
    html_content = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>⚡ SÚPER-CEREBRO CUÁNTICO | Dashboard de Trading 24/7</title>
    <meta name="description" content="Dashboard en vivo del Súper-Cerebro Cuántico de Trading con Comité Multi-Agente de IA">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap" rel="stylesheet">
    <style>
        :root {{
            --bg-color: #080c14;
            --bg-secondary: #0f172a;
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
                radial-gradient(circle at 20% 20%, rgba(168, 85, 247, 0.06) 0%, transparent 50%),
                radial-gradient(circle at 80% 80%, rgba(6, 182, 212, 0.06) 0%, transparent 50%);
            color: var(--text-main);
            min-height: 100vh;
            padding: 1.5rem 2rem;
        }}

        /* ============ HEADER ============ */
        .header {{
            display: flex; justify-content: space-between; align-items: center;
            padding-bottom: 1.5rem; border-bottom: 1px solid var(--card-border); margin-bottom: 1.5rem;
        }}
        .logo {{ display: flex; align-items: center; gap: 0.75rem; }}
        .logo-icon {{
            width: 48px; height: 48px;
            background: linear-gradient(135deg, var(--accent-cyan), var(--accent-purple));
            border-radius: 14px; display: grid; place-items: center; font-size: 1.6rem;
            box-shadow: 0 0 25px rgba(6, 182, 212, 0.4), 0 0 50px rgba(168, 85, 247, 0.2);
            animation: icon-glow 3s ease-in-out infinite;
        }}
        @keyframes icon-glow {{
            0%, 100% {{ box-shadow: 0 0 25px rgba(6, 182, 212, 0.4), 0 0 50px rgba(168, 85, 247, 0.2); }}
            50% {{ box-shadow: 0 0 35px rgba(6, 182, 212, 0.6), 0 0 70px rgba(168, 85, 247, 0.3); }}
        }}
        .title h1 {{ font-size: 1.4rem; font-weight: 900; letter-spacing: -0.5px; background: linear-gradient(90deg, var(--text-main), var(--accent-cyan)); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }}
        .title p {{ font-size: 0.8rem; color: var(--text-muted); margin-top: 2px; }}
        .header-right {{ display: flex; align-items: center; gap: 1rem; }}
        .live-badge {{
            display: inline-flex; align-items: center; gap: 0.5rem;
            background: rgba(16, 185, 129, 0.12); border: 1px solid rgba(16, 185, 129, 0.25);
            color: var(--accent-emerald); padding: 0.4rem 1rem; border-radius: 20px; font-weight: 600; font-size: 0.8rem;
        }}
        .pulse-dot {{
            width: 8px; height: 8px; background: var(--accent-emerald); border-radius: 50%;
            box-shadow: 0 0 10px var(--accent-emerald); animation: pulse 1.5s infinite;
        }}
        @keyframes pulse {{ 0%, 100% {{ opacity: 1; }} 50% {{ opacity: 0.3; }} }}
        .mode-badge {{
            background: rgba(168, 85, 247, 0.12); border: 1px solid rgba(168, 85, 247, 0.25);
            color: var(--accent-purple); padding: 0.4rem 0.8rem; border-radius: 20px; font-weight: 600; font-size: 0.75rem;
        }}

        /* ============ METRICS GRID ============ */
        .grid-metrics {{
            display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 1rem; margin-bottom: 1.5rem;
        }}
        .card {{
            background: var(--card-bg); border: 1px solid var(--card-border);
            backdrop-filter: blur(12px); border-radius: 16px; padding: 1.25rem;
            transition: transform 0.2s ease, box-shadow 0.2s ease;
        }}
        .card:hover {{ transform: translateY(-2px); box-shadow: 0 8px 25px rgba(0,0,0,0.4); }}
        .card-title {{ font-size: 0.72rem; color: var(--text-dim); text-transform: uppercase; letter-spacing: 0.8px; margin-bottom: 0.4rem; font-weight: 600; }}
        .card-value {{ font-size: 1.6rem; font-weight: 800; color: var(--text-main); margin-bottom: 0.15rem; }}
        .card-sub {{ font-size: 0.78rem; color: var(--accent-emerald); font-weight: 600; }}

        /* ============ SÚPER-CEREBRO SECTION ============ */
        .brain-section {{
            margin-bottom: 2rem;
        }}
        .section-title {{
            font-size: 1.15rem; font-weight: 800; margin-bottom: 1rem;
            display: flex; align-items: center; gap: 0.6rem;
            background: linear-gradient(90deg, var(--accent-purple), var(--accent-cyan));
            -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        }}
        .verdicts-timeline {{
            display: flex; flex-direction: column; gap: 1rem;
        }}

        /* Verdict Cards */
        .verdict-card {{
            border-radius: 16px; overflow: hidden;
            transition: transform 0.2s ease;
        }}
        .verdict-card:hover {{ transform: translateY(-2px); }}
        .verdict-latest {{
            background: linear-gradient(135deg, rgba(168, 85, 247, 0.12), rgba(6, 182, 212, 0.08));
            border: 1px solid rgba(168, 85, 247, 0.35);
            box-shadow: 0 0 30px rgba(168, 85, 247, 0.15), 0 0 60px rgba(6, 182, 212, 0.08);
        }}
        .verdict-past {{
            background: rgba(30, 41, 59, 0.4);
            border: 1px solid var(--card-border);
            opacity: 0.75;
        }}
        .verdict-past:hover {{ opacity: 1; }}
        .verdict-header {{
            display: flex; justify-content: space-between; align-items: center;
            padding: 0.8rem 1.25rem; border-bottom: 1px solid rgba(255,255,255,0.05);
        }}
        .verdict-label {{
            font-size: 0.75rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px;
            display: flex; align-items: center; gap: 0.5rem;
        }}
        .verdict-latest .verdict-label {{ color: var(--accent-purple); }}
        .verdict-past .verdict-label {{ color: var(--text-dim); }}
        .verdict-time {{ font-size: 0.75rem; color: var(--text-dim); font-weight: 500; }}
        .latest-pulse {{
            width: 10px; height: 10px; background: var(--accent-purple); border-radius: 50%;
            box-shadow: 0 0 12px var(--accent-purple); animation: pulse 1.5s infinite;
        }}

        .verdict-body {{ padding: 1.25rem; }}
        .verdict-decision {{
            display: flex; justify-content: space-between; align-items: center;
            margin-bottom: 1rem; flex-wrap: wrap; gap: 0.75rem;
        }}
        .verdict-symbol {{
            font-size: 1.5rem; font-weight: 900; letter-spacing: -0.5px;
        }}
        .verdict-latest .verdict-symbol {{ color: var(--text-main); }}
        .verdict-past .verdict-symbol {{ font-size: 1.15rem; color: var(--text-muted); }}
        .verdict-badges {{ display: flex; gap: 0.5rem; flex-wrap: wrap; }}
        .badge {{
            padding: 0.3rem 0.75rem; border-radius: 8px; font-size: 0.72rem; font-weight: 700;
            text-transform: uppercase; letter-spacing: 0.3px;
        }}
        .badge-long {{ background: rgba(16, 185, 129, 0.15); border: 1px solid rgba(16, 185, 129, 0.3); color: var(--accent-emerald); }}
        .badge-short {{ background: rgba(244, 63, 94, 0.15); border: 1px solid rgba(244, 63, 94, 0.3); color: var(--accent-rose); }}
        .badge-hold {{ background: rgba(245, 158, 11, 0.12); border: 1px solid rgba(245, 158, 11, 0.25); color: var(--accent-amber); }}
        .approved-yes {{ color: var(--accent-emerald); font-size: 0.78rem; font-weight: 700; }}
        .approved-no {{ color: var(--accent-rose); font-size: 0.78rem; font-weight: 700; }}

        /* Confidence bar */
        .confidence-section {{ margin-bottom: 1rem; }}
        .confidence-label {{ font-size: 0.72rem; color: var(--text-dim); text-transform: uppercase; letter-spacing: 0.5px; font-weight: 600; margin-bottom: 0.4rem; }}
        .confidence-bar-bg {{
            width: 100%; height: 8px; background: rgba(255,255,255,0.06); border-radius: 10px; overflow: hidden;
        }}
        .confidence-bar-fill {{
            height: 100%; border-radius: 10px; transition: width 1s ease;
            box-shadow: 0 0 10px currentColor;
        }}
        .confidence-value {{ font-size: 1.3rem; font-weight: 800; margin-top: 0.3rem; }}
        .verdict-past .confidence-value {{ font-size: 1rem; }}

        /* Candidates */
        .candidates-row {{ display: flex; gap: 0.4rem; flex-wrap: wrap; margin-bottom: 0.75rem; }}
        .chip {{
            background: rgba(59, 130, 246, 0.12); border: 1px solid rgba(59, 130, 246, 0.2);
            color: var(--accent-blue); padding: 0.2rem 0.6rem; border-radius: 6px;
            font-size: 0.7rem; font-weight: 600;
        }}

        /* Reasoning */
        .reasoning-section {{ }}
        .reasoning-label {{ font-size: 0.72rem; color: var(--text-dim); text-transform: uppercase; letter-spacing: 0.5px; font-weight: 600; margin-bottom: 0.4rem; }}
        .reasoning-text {{
            font-size: 0.82rem; color: var(--text-muted); line-height: 1.65;
            background: rgba(0,0,0,0.2); border-radius: 10px; padding: 0.85rem 1rem;
            border-left: 3px solid var(--accent-purple);
        }}
        .verdict-past .reasoning-text {{ border-left-color: var(--text-dim); font-size: 0.78rem; }}

        /* ============ AGENTS GRID ============ */
        .agents-section {{ margin-top: 1.5rem; }}
        .agents-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 1rem; }}
        .agent-card {{
            background: rgba(30, 41, 59, 0.4); border: 1px solid var(--card-border);
            border-radius: 14px; padding: 1rem;
        }}
        .agent-header {{ display: flex; align-items: center; gap: 0.6rem; margin-bottom: 0.5rem; }}
        .agent-icon {{ font-size: 1.2rem; }}
        .agent-name {{ font-weight: 700; font-size: 0.85rem; }}
        .agent-role {{ font-size: 0.68rem; color: var(--accent-cyan); text-transform: uppercase; letter-spacing: 0.3px; }}
        .agent-text {{ font-size: 0.78rem; color: var(--text-muted); line-height: 1.5; }}
        .ceo-card {{
            border: 1px solid rgba(168, 85, 247, 0.3);
            background: linear-gradient(135deg, rgba(168, 85, 247, 0.08), rgba(15, 23, 42, 0.7));
            box-shadow: 0 0 20px rgba(168, 85, 247, 0.12);
        }}
        .ceo-card .agent-name {{ color: var(--accent-purple); }}

        /* ============ FOOTER ============ */
        footer {{
            text-align: center; margin-top: 2rem; color: var(--text-dim); font-size: 0.75rem;
            padding-top: 1rem; border-top: 1px solid var(--card-border);
            display: flex; justify-content: center; align-items: center; gap: 1rem; flex-wrap: wrap;
        }}
        .refresh-btn {{
            padding: 6px 16px; background: rgba(6, 182, 212, 0.12); border: 1px solid rgba(6, 182, 212, 0.3);
            color: var(--accent-cyan); border-radius: 8px; cursor: pointer; font-weight: 600;
            font-size: 0.78rem; transition: all 0.2s;
        }}
        .refresh-btn:hover {{ background: rgba(6, 182, 212, 0.25); transform: scale(1.03); }}
        .countdown {{ color: var(--accent-cyan); font-weight: 600; font-size: 0.78rem; }}

        @media (max-width: 768px) {{
            body {{ padding: 1rem; }}
            .header {{ flex-direction: column; gap: 0.75rem; align-items: flex-start; }}
            .verdict-decision {{ flex-direction: column; align-items: flex-start; }}
        }}
    </style>
</head>
<body>
    <div class="header">
        <div class="logo">
            <div class="logo-icon">🧠</div>
            <div class="title">
                <h1>SÚPER-CEREBRO CUÁNTICO 24/7</h1>
                <p>Mesa de Operaciones Cuantitativas & Comité Multi-Agente de Élite</p>
            </div>
        </div>
        <div class="header-right">
            <div class="mode-badge">🖥️ LOCAL</div>
            <div class="live-badge">
                <div class="pulse-dot"></div>
                BINANCE LIVE
            </div>
        </div>
    </div>

    <div class="grid-metrics">
        <div class="card">
            <div class="card-title">Capital Neto Real</div>
            <div class="card-value">${data_payload['total_balance_usd']:.2f}</div>
            <div class="card-sub">💵 USDT en Binance Spot</div>
        </div>
        <div class="card">
            <div class="card-title">Posición Activa</div>
            <div class="card-value">{data_payload['position']['symbol']}</div>
            <div class="card-sub">💵 Entrada: ${data_payload['position']['entry_price']:.4f}</div>
        </div>
        <div class="card">
            <div class="card-title">Matrix Simulada (100 Cuentas)</div>
            <div class="card-value">${matrix_total:,.2f}</div>
            <div class="card-sub" style="color: {pnl_color};">{pnl_sign}${matrix_pnl:,.2f} PnL | WR {matrix_wr:.1f}%</div>
        </div>
        <div class="card">
            <div class="card-title">Stop-Loss / Trailing</div>
            <div class="card-value">±{data_payload['position']['adaptive_sl_pct']}%</div>
            <div class="card-sub">{data_payload['position']['volatility_regime']}</div>
        </div>
    </div>

    <!-- ============ SÚPER-CEREBRO EN VIVO ============ -->
    <div class="brain-section">
        <div class="section-title">🧠⚡ SÚPER-CEREBRO EN VIVO — ÚLTIMAS DECISIONES</div>
        <div class="verdicts-timeline">
            {verdict_cards_html}
        </div>
    </div>

    <!-- ============ COMITÉ DE 7 AGENTES ============ -->
    <div class="agents-section">
        <div class="section-title" style="background: linear-gradient(90deg, var(--accent-cyan), var(--accent-blue)); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">🏛️ COMITÉ DE 7 AGENTES IA</div>
        <div class="agents-grid">
            <div class="agent-card">
                <div class="agent-header">
                    <span class="agent-icon">🕵️</span>
                    <div>
                        <div class="agent-name">Whale & Macro Sentinel</div>
                        <div class="agent-role">Macro Regime & Whale Flow</div>
                    </div>
                </div>
                <div class="agent-text">{data_payload['agents']['agent_1_macro']}</div>
            </div>
            <div class="agent-card">
                <div class="agent-header">
                    <span class="agent-icon">📊</span>
                    <div>
                        <div class="agent-name">Technical Sniper</div>
                        <div class="agent-role">Price Action & Oscillators</div>
                    </div>
                </div>
                <div class="agent-text">{data_payload['agents']['agent_2_tech']}</div>
            </div>
            <div class="agent-card">
                <div class="agent-header">
                    <span class="agent-icon">🌊</span>
                    <div>
                        <div class="agent-name">Orderbook Depth Tracker</div>
                        <div class="agent-role">Liquidity Imbalance</div>
                    </div>
                </div>
                <div class="agent-text">{data_payload['agents']['agent_3_orderbook']}</div>
            </div>
            <div class="agent-card">
                <div class="agent-header">
                    <span class="agent-icon">🧩</span>
                    <div>
                        <div class="agent-name">Sector Cluster Analyst</div>
                        <div class="agent-role">Capital Rotation</div>
                    </div>
                </div>
                <div class="agent-text">{data_payload['agents']['agent_4_sector']}</div>
            </div>
            <div class="agent-card">
                <div class="agent-header">
                    <span class="agent-icon">🧠</span>
                    <div>
                        <div class="agent-name">RAG Memory Historian</div>
                        <div class="agent-role">100 Simulations History</div>
                    </div>
                </div>
                <div class="agent-text">{data_payload['agents']['agent_5_memory']}</div>
            </div>
            <div class="agent-card">
                <div class="agent-header">
                    <span class="agent-icon">🛡️</span>
                    <div>
                        <div class="agent-name">Chief Risk Officer</div>
                        <div class="agent-role">Capital Preservation</div>
                    </div>
                </div>
                <div class="agent-text">{data_payload['agents']['agent_6_risk']}</div>
            </div>
            <div class="agent-card ceo-card">
                <div class="agent-header">
                    <span class="agent-icon">👑</span>
                    <div>
                        <div class="agent-name">CEO Supreme Anti-Loss</div>
                        <div class="agent-role">Master Decision</div>
                    </div>
                </div>
                <div class="agent-text">{data_payload['agents']['agent_7_ceo_anti_loss']}</div>
            </div>
        </div>
    </div>

    <footer>
        <span>Última actualización: <strong>{now_str}</strong></span>
        <span class="countdown" id="countdown">Próximo ciclo en: --s</span>
        <button class="refresh-btn" onclick="window.location.reload()">🔄 Actualizar</button>
    </footer>

    <script>
        // Auto-refresh every 30 seconds
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
