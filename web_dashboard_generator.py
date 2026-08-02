"""
Professional Web Dashboard & Real-Time Data Generator
Generates `dashboard_data.json` and `dashboard.html` for real-time browser monitoring.
Built with glassmorphism UI, HSL color tokens, micro-animations, and live 30s auto-refresh.
"""

import os
import json
from datetime import datetime

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
            
    # 3. Load top 100 pairs & matrix summary
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
    pos = account_data.get("position", {})
    
    data_payload = {
        "updated_at": now_str,
        "total_balance_usd": account_data.get("current_balance_usd", 19.90),
        "usdt_free": account_data.get("_cached_usdt_free", 0.005),
        "bnb_free": account_data.get("_cached_bnb", 0.00446),
        "status": account_data.get("status", "🟦 Buscando Entrada A+"),
        "position": {
            "symbol": pos.get("symbol", "NINGUNA"),
            "quantity": pos.get("quantity", 0.0),
            "entry_price": pos.get("entry_price", 0.0),
            "highest_price": pos.get("highest_price", pos.get("entry_price", 0.0)),
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
        }
    }
    
    # Save JSON data feed
    json_path = os.path.join(base_dir, "dashboard_data.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(data_payload, f, indent=2, ensure_ascii=False)
        
    # Generate HTML Dashboard
    html_content = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>⚡ SÚPER-CEREBRO CUÁNTICO | Dashboard de Trading 24/7</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;800&display=swap" rel="stylesheet">
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
            --text-main: #f8fafc;
            --text-muted: #94a3b8;
        }}
        * {{ margin: 0; padding: 0; box-sizing: border-box; font-family: 'Inter', sans-serif; }}
        body {{
            background: radial-gradient(circle at top right, #0f172a, #080c14 60%);
            color: var(--text-main);
            min-height: 100vh;
            padding: 2rem;
        }}
        .header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding-bottom: 1.5rem;
            border-bottom: 1px solid var(--card-border);
            margin-bottom: 2rem;
        }}
        .logo {{ display: flex; align-items: center; gap: 0.75rem; }}
        .logo-icon {{
            width: 42px; height: 42px;
            background: linear-gradient(135deg, var(--accent-cyan), var(--accent-purple));
            border-radius: 12px;
            display: grid; place-items: center; font-size: 1.5rem;
            box-shadow: 0 0 20px rgba(6, 182, 212, 0.4);
        }}
        .title h1 {{ font-size: 1.5rem; font-weight: 800; letter-spacing: -0.5px; }}
        .title p {{ font-size: 0.85rem; color: var(--text-muted); }}
        .live-badge {{
            display: inline-flex; align-items: center; gap: 0.5rem;
            background: rgba(16, 185, 129, 0.15);
            border: 1px solid rgba(16, 185, 129, 0.3);
            color: var(--accent-emerald);
            padding: 0.4rem 1rem; border-radius: 20px; font-weight: 600; font-size: 0.85rem;
        }}
        .pulse-dot {{
            width: 8px; height: 8px; background: var(--accent-emerald); border-radius: 50%;
            box-shadow: 0 0 10px var(--accent-emerald);
            animation: pulse 1.5s infinite;
        }}
        @keyframes pulse {{ 0%, 100% {{ opacity: 1; }} 50% {{ opacity: 0.3; }} }}

        .grid-metrics {{
            display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 1.5rem; margin-bottom: 2rem;
        }}
        .card {{
            background: var(--card-bg);
            border: 1px solid var(--card-border);
            backdrop-filter: blur(12px);
            border-radius: 16px; padding: 1.5rem;
            transition: transform 0.2s ease, box-shadow 0.2s ease;
        }}
        .card:hover {{ transform: translateY(-3px); box-shadow: 0 10px 30px rgba(0,0,0,0.5); }}
        .card-title {{ font-size: 0.85rem; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 0.5rem; }}
        .card-value {{ font-size: 1.8rem; font-weight: 800; color: var(--text-main); margin-bottom: 0.25rem; }}
        .card-sub {{ font-size: 0.85rem; color: var(--accent-emerald); font-weight: 600; }}

        .agents-section {{ margin-top: 2rem; }}
        .section-title {{ font-size: 1.25rem; font-weight: 700; margin-bottom: 1rem; display: flex; align-items: center; gap: 0.5rem; }}
        .agents-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(320px, 1fr)); gap: 1.25rem; }}
        .agent-card {{
            background: rgba(30, 41, 59, 0.5);
            border: 1px solid var(--card-border);
            border-radius: 14px; padding: 1.25rem;
        }}
        .agent-header {{ display: flex; align-items: center; gap: 0.75rem; margin-bottom: 0.75rem; }}
        .agent-icon {{ font-size: 1.4rem; }}
        .agent-name {{ font-weight: 700; font-size: 0.95rem; }}
        .agent-role {{ font-size: 0.75rem; color: var(--accent-cyan); text-transform: uppercase; }}
        .agent-text {{ font-size: 0.85rem; color: var(--text-muted); line-height: 1.5; }}
        .ceo-card {{
            border: 1px solid rgba(168, 85, 247, 0.4);
            background: linear-gradient(135deg, rgba(168, 85, 247, 0.1), rgba(15, 23, 42, 0.8));
            box-shadow: 0 0 25px rgba(168, 85, 247, 0.2);
        }}
        .ceo-card .agent-name {{ color: var(--accent-purple); }}

        footer {{ text-align: center; margin-top: 3rem; color: var(--text-muted); font-size: 0.8rem; padding-top: 1.5rem; border-top: 1px solid var(--card-border); }}
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
        <div class="live-badge">
            <div class="pulse-dot"></div>
            BINANCE LIVE API ACTIVE
        </div>
    </div>

    <div class="grid-metrics">
        <div class="card">
            <div class="card-title">Capital Neto Real (USD)</div>
            <div class="card-value">${data_payload['total_balance_usd']:.2f} USD</div>
            <div class="card-sub">🟢 Protegido y en Operación en Vivo</div>
        </div>
        <div class="card">
            <div class="card-title">Posición Activa en Binance</div>
            <div class="card-value">{data_payload['position']['symbol']}</div>
            <div class="card-sub">💵 Entrada: ${data_payload['position']['entry_price']:.4f} | Pico: ${data_payload['position']['highest_price']:.4f}</div>
        </div>
        <div class="card">
            <div class="card-title">Stop-Loss Adaptativo ATR</div>
            <div class="card-value">±{data_payload['position']['adaptive_sl_pct']}%</div>
            <div class="card-sub">{data_payload['position']['volatility_regime']}</div>
        </div>
        <div class="card">
            <div class="card-title">Trailing Stop ATR Status</div>
            <div class="card-value">{'🔥 ACTIVO (Persiguiendo Pico)' if data_payload['position']['trailing_active'] else '⚪ Esperando +2.0%'}</div>
            <div class="card-sub">Cacería de Súper-Tendencia Dinámica</div>
        </div>
    </div>

    <div class="agents-section">
        <div class="section-title">🏛️ DELIBERACIÓN EN TIEMPO REAL DEL COMITÉ DE 7 AGENTES IA</div>
        <div class="agents-grid">
            <div class="agent-card">
                <div class="agent-header">
                    <span class="agent-icon">🕵️</span>
                    <div>
                        <div class="agent-name">Agente 1: Whale & Macro Sentinel</div>
                        <div class="agent-role">Macro Regime & Whale Flow</div>
                    </div>
                </div>
                <div class="agent-text">{data_payload['agents']['agent_1_macro']}</div>
            </div>

            <div class="agent-card">
                <div class="agent-header">
                    <span class="agent-icon">📊</span>
                    <div>
                        <div class="agent-name">Agente 2: Technical Sniper</div>
                        <div class="agent-role">Price Action & Oscillators</div>
                    </div>
                </div>
                <div class="agent-text">{data_payload['agents']['agent_2_tech']}</div>
            </div>

            <div class="agent-card">
                <div class="agent-header">
                    <span class="agent-icon">🌊</span>
                    <div>
                        <div class="agent-name">Agente 3: Orderbook Depth Tracker</div>
                        <div class="agent-role">Liquidity Bids/Asks Imbalance</div>
                    </div>
                </div>
                <div class="agent-text">{data_payload['agents']['agent_3_orderbook']}</div>
            </div>

            <div class="agent-card">
                <div class="agent-header">
                    <span class="agent-icon">🧩</span>
                    <div>
                        <div class="agent-name">Agente 4: Sector Cluster Analyst</div>
                        <div class="agent-role">Capital Rotation & Narrative</div>
                    </div>
                </div>
                <div class="agent-text">{data_payload['agents']['agent_4_sector']}</div>
            </div>

            <div class="agent-card">
                <div class="agent-header">
                    <span class="agent-icon">🧠</span>
                    <div>
                        <div class="agent-name">Agente 5: RAG Memory Historian</div>
                        <div class="agent-role">100 Simulations History</div>
                    </div>
                </div>
                <div class="agent-text">{data_payload['agents']['agent_5_memory']}</div>
            </div>

            <div class="agent-card">
                <div class="agent-header">
                    <span class="agent-icon">🛡️</span>
                    <div>
                        <div class="agent-name">Agente 6: Chief Risk Officer</div>
                        <div class="agent-role">Capital Preservation & Veto</div>
                    </div>
                </div>
                <div class="agent-text">{data_payload['agents']['agent_6_risk']}</div>
            </div>

            <div class="agent-card ceo-card">
                <div class="agent-header">
                    <span class="agent-icon">👑</span>
                    <div>
                        <div class="agent-name">Agente 7: CEO Supreme Anti-Loss</div>
                        <div class="agent-role">Profit Maximizer & Master Decision</div>
                    </div>
                </div>
                <div class="agent-text">{data_payload['agents']['agent_7_ceo_anti_loss']}</div>
            </div>
        </div>
    </div>

    <footer>
        Última actualización del tablero: <strong>{now_str}</strong> | Súper-Cerebro Cuántico 24/7 Binance Spot Engine
    </footer>

    <script>
        // Auto-refresh every 30 seconds
        setTimeout(() => {{
            window.location.reload();
        }}, 30000);
    </script>
</body>
</html>
"""
    html_path = os.path.join(base_dir, "dashboard.html")
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html_content)
        
    print(f"📊 Dashboard Web Interactivo generado en: {html_path}")
    return html_path

if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding='utf-8')
    generate_web_dashboard()
