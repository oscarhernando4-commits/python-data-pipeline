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

if __name__ == "__main__":
    init_db()
    print("quant_intelligence.db initialized successfully.")
