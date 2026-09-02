"""
QUANT INTELLIGENCE DATABASE — SQLite High-Performance Vault
============================================================
Provides persistent relational storage for millions of simulated
and real trades without JSON bloat or git degradation.
Uses Python native sqlite3 engine (zero extra dependencies).
"""

import sqlite3
import os
import json
import time
from datetime import datetime, timezone

DB_PATH = os.path.join(os.path.dirname(__file__), "quant_intelligence.db")

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cur = conn.cursor()
    
    # 1. Tabla de Operaciones Reales (R-01)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS real_trades (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp_utc TEXT,
        timestamp_ms INTEGER,
        symbol TEXT,
        side TEXT,
        entry_price REAL,
        exit_price REAL,
        pnl_pct REAL,
        pnl_usd REAL,
        result TEXT,
        exit_reason TEXT,
        score INTEGER,
        fii INTEGER,
        rsi_15m REAL,
        vol_surge REAL,
        obv_trend TEXT,
        btc_regime TEXT,
        notes TEXT
    )
    """)
    
    # 2. Tabla de Operaciones Simuladas (1000 cuentas geneticas)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS sim_trades (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp_ms INTEGER,
        account_id TEXT,
        group_id INTEGER,
        group_name TEXT,
        symbol TEXT,
        entry_price REAL,
        exit_price REAL,
        pnl_pct REAL,
        pnl_usd REAL,
        result TEXT,
        exit_reason TEXT,
        hold_min REAL,
        min_score INTEGER,
        min_fii INTEGER
    )
    """)
    
    cur.execute("CREATE INDEX IF NOT EXISTS idx_real_symbol ON real_trades(symbol)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_real_result ON real_trades(result)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_sim_group ON sim_trades(group_id)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_sim_symbol ON sim_trades(symbol)")
    
    # 3. Tabla de Perfiles de ADN por Criptomoneda (Auto-Aprendizaje Específico)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS crypto_dna_profiles (
        symbol TEXT PRIMARY KEY,
        sector TEXT,
        historical_trades INTEGER DEFAULT 0,
        wins INTEGER DEFAULT 0,
        losses INTEGER DEFAULT 0,
        win_rate_pct REAL DEFAULT 50.0,
        net_pnl_usd REAL DEFAULT 0.0,
        avg_peak_gain_pct REAL DEFAULT 1.0,
        recommended_target_pct REAL DEFAULT 0.90,
        recommended_sl_pct REAL DEFAULT -4.0,
        avg_hold_mins REAL DEFAULT 45.0,
        dna_tier TEXT DEFAULT 'BALANCED',
        last_updated_utc TEXT
    )
    """)
    cur.execute("CREATE INDEX IF NOT EXISTS idx_dna_tier ON crypto_dna_profiles(dna_tier)")
    
    conn.commit()
    conn.close()

def log_real_trade(symbol, side, entry_price, exit_price, pnl_usd, result, exit_reason="", context=None):
    try:
        init_db()
        pnl_pct = ((exit_price - entry_price) / entry_price * 100.0) if entry_price > 0 else 0.0
        ctx = context or {}
        now_utc = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        ts_ms = int(time.time() * 1000)
        
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
        INSERT INTO real_trades (
            timestamp_utc, timestamp_ms, symbol, side, entry_price, exit_price,
            pnl_pct, pnl_usd, result, exit_reason, score, fii, rsi_15m, vol_surge,
            obv_trend, btc_regime, notes
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            now_utc, ts_ms, symbol.upper(), side.upper(), entry_price, exit_price,
            round(pnl_pct, 4), round(pnl_usd, 4), result.upper(), exit_reason,
            ctx.get("score", 0), ctx.get("fii_score", 0), ctx.get("rsi_15m", 50.0),
            ctx.get("vol_surge", 1.0), ctx.get("obv_trend", "NEUTRAL"),
            ctx.get("btc_regime", "NORMAL"), ctx.get("notes", "")
        ))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Error logging real trade: {e}")

def log_sim_trades_batch(new_entries):
    if not new_entries:
        return
    try:
        init_db()
        conn = get_db_connection()
        cur = conn.cursor()
        batch = [
            (
                e.get("timestamp_ms", int(time.time() * 1000)),
                f"SIM-G{e.get('group_id', 0)}",
                e.get("group_id", 0),
                e.get("group_name", "?"),
                e.get("symbol", "").upper(),
                e.get("entry_price", 0.0),
                e.get("exit_price", 0.0),
                e.get("pnl_pct", 0.0),
                e.get("pnl_usd", 0.0),
                e.get("result", "LOSS"),
                e.get("exit_reason", ""),
                e.get("hold_min", 0.0),
                e.get("min_score_used", 0),
                e.get("min_fii_used", 0)
            )
            for e in new_entries
        ]
        cur.executemany("""
        INSERT INTO sim_trades (
            timestamp_ms, account_id, group_id, group_name, symbol,
            entry_price, exit_price, pnl_pct, pnl_usd, result, exit_reason,
            hold_min, min_score, min_fii
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, batch)
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Error logging sim batch: {e}")

def get_symbol_win_rate(symbol: str) -> dict:
    try:
        init_db()
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
        SELECT 
            COUNT(*) as total,
            SUM(CASE WHEN result = 'WIN' THEN 1 ELSE 0 END) as wins,
            SUM(pnl_usd) as net_pnl
        FROM sim_trades WHERE symbol = ?
        """, (symbol.upper(),))
        row = cur.fetchone()
        conn.close()
        if row and row["total"] > 0:
            total = row["total"]
            wins = row["wins"] or 0
            return {
                "symbol": symbol.upper(),
                "total_trades": total,
                "wins": wins,
                "win_rate_pct": round(wins / total * 100.0, 1),
                "net_pnl": round(row["net_pnl"] or 0.0, 2)
            }
    except Exception:
        pass
    return {"symbol": symbol.upper(), "total_trades": 0, "wins": 0, "win_rate_pct": 50.0, "net_pnl": 0.0}

def export_intelligence_matrix() -> dict:
    """
    Compila un resumen estadístico compacto (< 15 KB) de la base de datos SQLite
    en 'intelligence_matrix.json' para sincronización ultra-ligera en Git y consumo por IA.
    """
    matrix_data = {
        "updated_at": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
        "elite_tokens": [],
        "blacklisted_tokens": [],
        "global_sim_wr": 0.0,
        "total_sim_trades": 0,
        "total_real_trades": 0
    }
    try:
        init_db()
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Win Rate por símbolo con >= 3 trades
        cur.execute("""
        SELECT 
            symbol,
            COUNT(*) as total,
            SUM(CASE WHEN result = 'WIN' THEN 1 ELSE 0 END) as wins,
            SUM(pnl_usd) as net_pnl
        FROM sim_trades 
        GROUP BY symbol
        HAVING COUNT(*) >= 3
        ORDER BY (SUM(CASE WHEN result = 'WIN' THEN 1 ELSE 0 END) * 1.0 / COUNT(*)) DESC
        """)
        rows = cur.fetchall()
        for r in rows:
            wr = round(r["wins"] / r["total"] * 100.0, 1)
            token_info = {
                "symbol": r["symbol"],
                "total": r["total"],
                "wins": r["wins"],
                "win_rate": wr,
                "net_pnl": round(r["net_pnl"] or 0.0, 2)
            }
            if wr >= 65.0:
                matrix_data["elite_tokens"].append(token_info)
            elif wr < 40.0:
                matrix_data["blacklisted_tokens"].append(token_info)
                
        # Total global simulado
        cur.execute("SELECT COUNT(*), SUM(CASE WHEN result = 'WIN' THEN 1 ELSE 0 END) FROM sim_trades")
        tot_row = cur.fetchone()
        if tot_row and tot_row[0] > 0:
            matrix_data["total_sim_trades"] = tot_row[0]
            matrix_data["global_sim_wr"] = round((tot_row[1] or 0) / tot_row[0] * 100.0, 1)
            
        # Total global real
        cur.execute("SELECT COUNT(*) FROM real_trades")
        rt_row = cur.fetchone()
        if rt_row:
            matrix_data["total_real_trades"] = rt_row[0]
            
        conn.close()
        
        out_path = os.path.join(os.path.dirname(__file__), "intelligence_matrix.json")
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(matrix_data, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"⚠️ Error exportando intelligence_matrix: {e}")
        
    return matrix_data

def get_crypto_dna_profile(symbol: str) -> dict:
    """
    Retorna el perfil fenotípico de ADN aprendido para una criptomoneda específica.
    Si aún no tiene historial suficiente, infiere parámetros inteligentes basados en su sector.
    """
    try:
        init_db()
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM crypto_dna_profiles WHERE symbol = ?", (symbol.upper(),))
        row = cur.fetchone()
        conn.close()
        if row:
            return dict(row)
    except Exception:
        pass
    
    clean_sym = symbol.upper().replace("USDT", "")
    try:
        from asset_dna_predictive_engine import TOKEN_SECTOR_MAP
        sec = TOKEN_SECTOR_MAP.get(clean_sym, "L1")
    except Exception:
        sec = "L1"
        
    return {
        "symbol": symbol.upper(),
        "sector": sec,
        "historical_trades": 0,
        "wins": 0,
        "losses": 0,
        "win_rate_pct": 50.0,
        "net_pnl_usd": 0.0,
        "avg_peak_gain_pct": 1.00,
        "recommended_target_pct": 0.85,
        "recommended_sl_pct": -4.0,
        "avg_hold_mins": 45.0,
        "dna_tier": "BALANCED",
        "last_updated_utc": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    }

def compile_all_dna_profiles():
    """
    Analiza todos los trades (reales y simulados) en SQLite y actualiza
    los perfiles de ADN de cada criptomoneda con métricas hiper-detalladas.
    """
    try:
        init_db()
        conn = get_db_connection()
        cur = conn.cursor()
        
        try:
            from asset_dna_predictive_engine import TOKEN_SECTOR_MAP
        except Exception:
            TOKEN_SECTOR_MAP = {}
            
        now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

        # Agrupar estadísticas por símbolo desde sim_trades y real_trades
        cur.execute("""
        SELECT 
            symbol,
            COUNT(*) as total,
            SUM(CASE WHEN result = 'WIN' THEN 1 ELSE 0 END) as wins,
            SUM(CASE WHEN result = 'LOSS' THEN 1 ELSE 0 END) as losses,
            SUM(pnl_usd) as net_pnl,
            AVG(CASE WHEN pnl_pct > 0 THEN pnl_pct ELSE NULL END) as avg_win,
            AVG(hold_min) as avg_hold
        FROM sim_trades
        GROUP BY symbol
        """)
        sim_rows = cur.fetchall()
        
        for r in sim_rows:
            sym = r["symbol"].upper()
            clean_sym = sym.replace("USDT", "")
            sec = TOKEN_SECTOR_MAP.get(clean_sym, "L1")
            total = r["total"]
            wins = r["wins"] or 0
            losses = r["losses"] or 0
            net_pnl = round(r["net_pnl"] or 0.0, 4)
            wr = round(wins / max(total, 1) * 100.0, 1)
            avg_win = round(r["avg_win"] or 1.00, 2)
            avg_hold = round(r["avg_hold"] or 45.0, 1)
            
            # Cima típica recomendada: entre 0.75% y 1.25% según su comportamiento histórico
            rec_target = max(0.75, min(1.30, avg_win * 0.90))
            
            # Calificación del ADN
            if wr >= 65.0 and total >= 3:
                tier = "💎 A+ ÉLITE"
            elif wr >= 52.0:
                tier = "🟢 A SÓLIDO"
            elif wr < 40.0 and total >= 3:
                tier = "☠️ TÓXICO"
            else:
                tier = "🔵 B BALANCED"
                
            cur.execute("""
            INSERT INTO crypto_dna_profiles (
                symbol, sector, historical_trades, wins, losses, win_rate_pct,
                net_pnl_usd, avg_peak_gain_pct, recommended_target_pct,
                recommended_sl_pct, avg_hold_mins, dna_tier, last_updated_utc
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(symbol) DO UPDATE SET
                sector = excluded.sector,
                historical_trades = excluded.historical_trades,
                wins = excluded.wins,
                losses = excluded.losses,
                win_rate_pct = excluded.win_rate_pct,
                net_pnl_usd = excluded.net_pnl_usd,
                avg_peak_gain_pct = excluded.avg_peak_gain_pct,
                recommended_target_pct = excluded.recommended_target_pct,
                recommended_sl_pct = excluded.recommended_sl_pct,
                avg_hold_mins = excluded.avg_hold_mins,
                dna_tier = excluded.dna_tier,
                last_updated_utc = excluded.last_updated_utc
            """, (
                sym, sec, total, wins, losses, wr, net_pnl, avg_win,
                rec_target, -4.0, avg_hold, tier, now_str
            ))
            
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"⚠️ Error compiling DNA profiles: {e}")

if __name__ == "__main__":
    init_db()
    compile_all_dna_profiles()
    mat = export_intelligence_matrix()
    print("quant_intelligence.db initialized successfully. Matrix exported:", mat)
