"""
╔══════════════════════════════════════════════════════════════════════════════╗
║          SIMULATION ENGINE 3.0 — MOTOR GENÉTICO DE AUTO-APRENDIZAJE         ║
║  1000 cuentas paralelas con los 67 mismos pares reales, 5 grupos evolutivos ║
║  Cada grupo prueba parámetros distintos y alimenta el learning_engine con   ║
║  resultados reales que el Súper-Cerebro usa para auto-adaptarse.            ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import json
import os
import time
import random
from datetime import datetime

MATRIX_FILE = os.path.join(os.path.dirname(__file__), "matrix_100_simulations.json")
MEMORY_FILE = os.path.join(os.path.dirname(__file__), "trade_memory.json")

# ─── GRUPOS GENÉTICOS: 5 grupos × 200 cuentas = 1000 simulaciones ─────────────
# Cada grupo varía: score mínimo, FII mínimo, SL, fase 2 target.
# El Súper-Cerebro aprende qué grupo gana más y adopta esos parámetros.
GENETIC_GROUPS = [
    {
        "group_id": 0,
        "group_name": "💎 ÉLITE ESTRICTO (Score≥90, FII≥70)",
        "count": 200,
        "min_score": 90,
        "min_fii": 70,
        "sl_pct": -3.50,
        "phase2_pct": 1.00,
        "phase3_pct": 1.60,
        "max_hold_min": 360,
        "description": "Máxima precisión — solo entradas con certeza casi total"
    },
    {
        "group_id": 1,
        "group_name": "🎯 FRANCOTIRADOR (Score≥85, FII≥60)",
        "count": 200,
        "min_score": 85,
        "min_fii": 60,
        "sl_pct": -4.00,
        "phase2_pct": 1.00,
        "phase3_pct": 1.60,
        "max_hold_min": 360,
        "description": "Configuración actual del sistema real"
    },
    {
        "group_id": 2,
        "group_name": "⚡ AGRESIVO RÁPIDO (Score≥75, FII≥50)",
        "count": 200,
        "min_score": 75,
        "min_fii": 50,
        "sl_pct": -3.00,
        "phase2_pct": 0.80,
        "phase3_pct": 1.20,
        "max_hold_min": 180,
        "description": "Más trades, menos espera — para mercados muy activos"
    },
    {
        "group_id": 3,
        "group_name": "🐢 PACIENCIA TOTAL (Score≥85, FII≥60, Hold Max 720min)",
        "count": 200,
        "min_score": 85,
        "min_fii": 60,
        "sl_pct": -4.00,
        "phase2_pct": 1.50,
        "phase3_pct": 2.50,
        "max_hold_min": 720,
        "description": "Metas más altas con mayor paciencia temporal"
    },
    {
        "group_id": 4,
        "group_name": "🧬 ADAPTATIVO HÍBRIDO (Score≥80, FII≥55)",
        "count": 200,
        "min_score": 80,
        "min_fii": 55,
        "sl_pct": -3.50,
        "phase2_pct": 1.20,
        "phase3_pct": 1.80,
        "max_hold_min": 480,
        "description": "Balance entre precisión y frecuencia"
    }
]


def load_matrix():
    if not os.path.exists(MATRIX_FILE):
        return _init_fresh_matrix()
    try:
        with open(MATRIX_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return _init_fresh_matrix()


def _init_fresh_matrix():
    """Inicializa la matriz con 1000 cuentas en 5 grupos genéticos."""
    accounts = []
    for grp in GENETIC_GROUPS:
        for i in range(grp["count"]):
            acct_id = f"G{grp['group_id']}-SIM-{i:03d}"
            accounts.append({
                "account_id": acct_id,
                "group_id": grp["group_id"],
                "group_name": grp["group_name"],
                "min_score": grp["min_score"],
                "min_fii": grp["min_fii"],
                "sl_pct": grp["sl_pct"],
                "phase2_pct": grp["phase2_pct"],
                "phase3_pct": grp["phase3_pct"],
                "max_hold_min": grp["max_hold_min"],
                "initial_capital": 100.0,
                "current_balance": 100.0,
                "pnl_usd": 0.0,
                "trades_count": 0,
                "wins": 0,
                "losses": 0,
                "consecutive_losses": 0,
                "last_result": "—",
                "position": None,
                "trade_history": [],
                "status": "BUSCANDO"
            })

    matrix = {
        "total_fund_usd": 100000.0,
        "current_total_usd": 100000.0,
        "net_pnl_usd": 0.0,
        "global_win_rate_pct": 0.0,
        "last_cycle_time": "",
        "accounts": accounts
    }
    _save_matrix(matrix)
    return matrix


def _save_matrix(matrix):
    try:
        with open(MATRIX_FILE, "w", encoding="utf-8") as f:
            json.dump(matrix, f, ensure_ascii=False, separators=(',', ':'))
    except Exception as e:
        print(f"⚠️ [SIM ENGINE] Error guardando matriz: {e}")


def run_simulation_cycle(symbol_analysis_map: dict):
    """
    Corre un ciclo completo de simulación para las 1000 cuentas.
    Usa symbol_analysis_map (ya calculado por pipeline) para no duplicar llamadas a API.

    Para cada cuenta:
    1. Si tiene posición abierta → evalúa SL/TP simulado con precio actual
    2. Si no tiene posición → busca entrada entre los candidatos aprobados
    3. Registra resultado en trade_history y alimenta el learning_engine
    """
    if not symbol_analysis_map:
        return

    matrix = load_matrix()
    accounts = matrix.get("accounts", [])

    # Verificar si necesitamos re-inicializar (estructura antigua sin grupos genéticos)
    if accounts and "group_id" not in accounts[0]:
        print("🧬 [SIM ENGINE] Detectada matriz antigua. Re-inicializando con 5 grupos genéticos...")
        matrix = _init_fresh_matrix()
        accounts = matrix["accounts"]

    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Pre-calcular candidatos válidos por símbolo desde el analysis_map
    candidates_by_quality = _extract_candidates(symbol_analysis_map)

    # Contadores del ciclo
    cycle_entries = 0
    cycle_exits_win = 0
    cycle_exits_loss = 0
    new_history_entries = []

    for acct in accounts:
        grp_min_score = acct.get("min_score", 85)
        grp_min_fii   = acct.get("min_fii", 60)
        grp_sl_pct    = acct.get("sl_pct", -4.00)
        grp_p2        = acct.get("phase2_pct", 1.00)
        grp_p3        = acct.get("phase3_pct", 1.60)
        grp_max_hold  = acct.get("max_hold_min", 360)
        balance       = acct.get("current_balance", 100.0)

        pos = acct.get("position")

        # ── GESTIÓN DE POSICIÓN ABIERTA ───────────────────────────────────────
        if pos and isinstance(pos, dict) and pos.get("entry_price"):
            sym = pos.get("symbol", "")
            entry = float(pos.get("entry_price", 0))
            highest = float(pos.get("highest_price", entry))
            open_time_s = float(pos.get("open_time_epoch", time.time()))
            hold_min = (time.time() - open_time_s) / 60.0

            # BUG 12 FIX: si el símbolo desaparece del map, usar entry como precio
            # pero NO hacer continue — permitir evaluación de tiempo máximo para evitar posiciones zombi
            sym_data = symbol_analysis_map.get(sym, {})
            current_price = sym_data.get("price", 0)
            if not current_price or current_price <= 0:
                # Símbolo ausente del map: evaluar solo cierre por tiempo
                if hold_min >= grp_max_hold:
                    # Cerrar posición zombi por tiempo agotado con precio de entrada (pnl=0)
                    acct["trades_count"] = acct.get("trades_count", 0) + 1
                    acct["losses"] = acct.get("losses", 0) + 1
                    acct["consecutive_losses"] = acct.get("consecutive_losses", 0) + 1
                    acct["position"] = None
                    acct["status"] = "BUSCANDO"
                continue

            pnl_pct = ((current_price - entry) / entry) * 100.0
            if current_price > highest:
                pos["highest_price"] = current_price
                highest = current_price

            highest_pnl = ((highest - entry) / entry) * 100.0

            # Trailing floor dinámico
            if highest_pnl >= grp_p3:
                retention = min(85.0, 50.0 + highest_pnl * 5.0)
                floor_pct = max(grp_p2, highest_pnl * retention / 100.0)
            elif highest_pnl >= grp_p2:
                floor_pct = grp_p2
            else:
                floor_pct = grp_sl_pct

            # Condiciones de salida
            should_exit = False
            exit_reason = ""

            if pnl_pct <= floor_pct:
                should_exit = True
                exit_reason = f"SL/Floor {floor_pct:.2f}% tocado"
            elif hold_min >= grp_max_hold and pnl_pct < grp_p2:
                should_exit = True
                exit_reason = f"Tiempo max {grp_max_hold}min agotado"

            if should_exit:
                result = "WIN" if pnl_pct > 0 else "LOSS"
                pnl_usd = (pnl_pct / 100.0) * balance
                balance = max(1.0, balance + pnl_usd)

                if result == "WIN":
                    acct["wins"] = acct.get("wins", 0) + 1
                    acct["consecutive_losses"] = 0
                    cycle_exits_win += 1
                else:
                    acct["losses"] = acct.get("losses", 0) + 1
                    acct["consecutive_losses"] = acct.get("consecutive_losses", 0) + 1
                    cycle_exits_loss += 1

                acct["trades_count"] = acct.get("trades_count", 0) + 1
                acct["current_balance"] = round(balance, 4)
                acct["pnl_usd"] = round(balance - acct.get("initial_capital", 100.0), 4)
                acct["last_result"] = result
                acct["position"] = None
                acct["status"] = "BUSCANDO"

                # Registro de historial para learning
                history_entry = {
                    "symbol": sym,
                    "group_id": acct.get("group_id", 0),
                    "group_name": acct.get("group_name", "?"),
                    "result": result,
                    "pnl_pct": round(pnl_pct, 4),
                    "pnl_usd": round(pnl_usd, 4),
                    "hold_min": round(hold_min, 1),
                    "exit_reason": exit_reason,
                    "entry_price": entry,
                    "exit_price": current_price,
                    "min_score_used": grp_min_score,
                    "min_fii_used": grp_min_fii,
                    "sl_pct_used": grp_sl_pct,
                    "timestamp_ms": int(time.time() * 1000),
                    "timestamp_str": now_str
                }

                # Limitar historial por cuenta a 50 últimas
                hist = acct.get("trade_history", [])
                hist.append(history_entry)
                acct["trade_history"] = hist[-50:]
                new_history_entries.append(history_entry)

        # ── BUSCAR NUEVA ENTRADA (sin posición) ──────────────────────────────
        elif pos is None or not isinstance(pos, dict):
            # No entrar si tiene 3+ consecutive losses (micro circuit breaker simulado)
            if acct.get("consecutive_losses", 0) >= 3:
                acct["status"] = "PAUSA_CB"
                # Reset tras 5 ciclos (10 minutos de pausa simulada)
                acct["_cb_pause_count"] = acct.get("_cb_pause_count", 0) + 1
                if acct.get("_cb_pause_count", 0) >= 5:
                    acct["consecutive_losses"] = 0
                    acct["_cb_pause_count"] = 0
                    acct["status"] = "BUSCANDO"
                continue

            # Seleccionar candidato que cumpla los parámetros del grupo
            eligible = [
                c for c in candidates_by_quality
                if c.get("score", 0) >= grp_min_score
                and c.get("fii", 0) >= grp_min_fii
                and c.get("vol_surge_1m", 0) >= 0.20
            ]

            if eligible:
                # Cada cuenta elige al candidato con mayor score que no esté ya en su historial reciente
                recent_syms = {h["symbol"] for h in acct.get("trade_history", [])[-3:]}
                best = next((c for c in eligible if c["symbol"] not in recent_syms), eligible[0])

                entry_price = best.get("price", 0)
                if entry_price and entry_price > 0:
                    acct["position"] = {
                        "symbol": best["symbol"],
                        "entry_price": entry_price,
                        "highest_price": entry_price,
                        "qty": round(balance / entry_price, 6),
                        "open_time_epoch": time.time(),
                        "open_time": now_str,
                        "entry_score": best.get("score", 0),
                        "entry_fii": best.get("fii", 0),
                    }
                    acct["status"] = f"EN_POSICION ({best['symbol']})"
                    cycle_entries += 1
            else:
                acct["status"] = "BUSCANDO"

    # ── ACTUALIZAR ESTADÍSTICAS GLOBALES ─────────────────────────────────────
    total_wins   = sum(a.get("wins", 0) for a in accounts)
    total_losses = sum(a.get("losses", 0) for a in accounts)
    total_trades = total_wins + total_losses
    total_balance = sum(a.get("current_balance", 100.0) for a in accounts)
    global_wr = round(total_wins / max(total_trades, 1) * 100, 2)
    global_pnl = round(total_balance - matrix.get("total_fund_usd", 100000.0), 2)

    matrix["current_total_usd"] = round(total_balance, 2)
    matrix["net_pnl_usd"] = global_pnl
    matrix["global_win_rate_pct"] = global_wr
    matrix["last_cycle_time"] = now_str
    matrix["accounts"] = accounts

    _save_matrix(matrix)

    # ── ALIMENTAR EL LEARNING ENGINE CON DATOS DE SIMULACIONES ───────────────
    if new_history_entries:
        _feed_learning_engine(new_history_entries)

    if total_trades > 0 or cycle_entries > 0:
        print(f"🧬 [SIM ENGINE] Ciclo completado: +{cycle_entries} entradas | "
              f"+{cycle_exits_win}W / +{cycle_exits_loss}L este ciclo | "
              f"Global: {total_wins}W/{total_losses}L ({global_wr}% WR) | "
              f"PnL global: ${global_pnl:+.2f} USD")

    return {
        "cycle_entries": cycle_entries,
        "cycle_wins": cycle_exits_win,
        "cycle_losses": cycle_exits_loss,
        "global_win_rate": global_wr,
        "global_pnl_usd": global_pnl,
        "total_trades": total_trades
    }


def _extract_candidates(symbol_analysis_map: dict) -> list:
    """Extrae candidatos válidos del analysis_map ya calculado por el pipeline."""
    candidates = []
    for sym, data in symbol_analysis_map.items():
        try:
            score = data.get("score", 0)
            price = data.get("price", 0)
            tech  = data.get("tech", {})
            mtf   = tech.get("mtf_analysis", {})
            fii   = mtf.get("fii_score", 0)
            vol1m = mtf.get("vol_surge_1m", 0)
            obv   = mtf.get("obv_trend", "NEUTRAL")
            rsi15 = mtf.get("rsi_15m", 50)
            r1m   = mtf.get("range_position_1m", 0.5) * 100
            r15m  = mtf.get("range_position_15m", 0.5) * 100

            if price and price > 0 and score >= 55:
                candidates.append({
                    "symbol": sym,
                    "score": score,
                    "price": price,
                    "fii": fii,
                    "vol_surge_1m": vol1m,
                    "obv": obv,
                    "rsi_15m": rsi15,
                    "range_1m": r1m,
                    "range_15m": r15m
                })
        except Exception:
            pass

    # Ordenar por score + FII descendente
    candidates.sort(key=lambda c: c["score"] + c["fii"] * 0.5, reverse=True)
    return candidates


def _feed_learning_engine(new_entries: list):
    """
    Alimenta el trade_memory.json con los trades simulados.
    El learning_engine ya lee de este archivo para calcular bias, blacklist, elite.
    Los trades simulados se marcan con 'source': 'SIMULATION' para diferenciarlos.
    """
    try:
        if not os.path.exists(MEMORY_FILE):
            return

        with open(MEMORY_FILE, "r", encoding="utf-8") as f:
            mem = json.load(f)

        history = mem.get("history", [])

        for entry in new_entries:
            # BUG 10 FIX: incluir TODOS los campos que learning_engine.py espera (timestamp, side, entry_price, exit_price)
            from datetime import datetime as _dt10
            _ts_str = _dt10.utcfromtimestamp(entry["timestamp_ms"] / 1000).strftime("%Y-%m-%d %H:%M:%S")
            history.append({
                "timestamp": _ts_str,               # requerido por sync_learning_note
                "timestamp_ms": entry["timestamp_ms"],
                "account_id": f"SIM-G{entry['group_id']}",
                "group_name": entry["group_name"],
                "symbol": entry["symbol"],
                "side": "LONG",                      # requerido por sync_learning_note
                "entry_price": entry["entry_price"],  # requerido por sync_learning_note
                "exit_price": entry["exit_price"],    # requerido por sync_learning_note
                "result": entry["result"],
                "pnl_pct": entry["pnl_pct"],
                "pnl_usd": entry["pnl_usd"],
                "exit_reason": entry["exit_reason"],
                "source": "SIMULATION",              # marcado para exclusión en dashboards y CB
                "min_score": entry["min_score_used"],
                "min_fii": entry["min_fii_used"],
                "hold_min": entry["hold_min"],
                "notes": entry["exit_reason"],
                "context": {}
            })

        # Mantener máximo 2000 entradas (500 reales + 1500 simuladas)
        real = [h for h in history if h.get("source") != "SIMULATION"]
        sims = [h for h in history if h.get("source") == "SIMULATION"]
        sims = sims[-1500:]  # últimas 1500 simuladas
        mem["history"] = real + sims

        # Actualizar stats globales
        wins = len([h for h in mem["history"] if h.get("result") == "WIN"])
        losses = len([h for h in mem["history"] if h.get("result") == "LOSS"])
        total = wins + losses
        mem["stats"] = {
            "total_trades": total,
            "wins": wins,
            "losses": losses,
            "win_rate_pct": round(wins / max(total, 1) * 100, 2),
            "total_pnl_usd": round(sum(h.get("pnl_usd", 0) for h in mem["history"]), 4)
        }

        with open(MEMORY_FILE, "w", encoding="utf-8") as f:
            json.dump(mem, f, ensure_ascii=False, indent=2)

    except Exception as e:
        pass  # Non-blocking


def get_best_group_params() -> dict:
    """
    Retorna los parámetros del grupo genético con mejor Win Rate (>= 10 trades).
    El Súper-Cerebro puede usar esto para auto-adaptar sus umbrales de entrada.
    """
    try:
        matrix = load_matrix()
        accounts = matrix.get("accounts", [])

        group_stats = {}
        for acct in accounts:
            gid = acct.get("group_id", 0)
            gname = acct.get("group_name", "?")
            if gid not in group_stats:
                group_stats[gid] = {
                    "name": gname,
                    "wins": 0, "losses": 0, "pnl": 0.0,
                    "min_score": acct.get("min_score", 85),
                    "min_fii": acct.get("min_fii", 60),
                    "phase2_pct": acct.get("phase2_pct", 1.0),
                }
            group_stats[gid]["wins"] += acct.get("wins", 0)
            group_stats[gid]["losses"] += acct.get("losses", 0)
            group_stats[gid]["pnl"] += acct.get("pnl_usd", 0.0)

        best = None
        best_wr = 0
        for gid, st in group_stats.items():
            total = st["wins"] + st["losses"]
            if total >= 10:
                wr = st["wins"] / total * 100
                if wr > best_wr:
                    best_wr = wr
                    best = st

        return best or {}
    except Exception:
        return {}


def print_simulation_report():
    """Imprime un resumen ejecutivo de los 5 grupos genéticos."""
    try:
        matrix = load_matrix()
        accounts = matrix.get("accounts", [])

        group_stats = {}
        for acct in accounts:
            gid = acct.get("group_id", 0)
            gname = acct.get("group_name", "?")
            if gid not in group_stats:
                group_stats[gid] = {"name": gname, "wins": 0, "losses": 0, "pnl": 0.0, "active": 0}
            group_stats[gid]["wins"] += acct.get("wins", 0)
            group_stats[gid]["losses"] += acct.get("losses", 0)
            group_stats[gid]["pnl"] += acct.get("pnl_usd", 0.0)
            if acct.get("position"):
                group_stats[gid]["active"] += 1

        print("🧬 ═══════ REPORTE GENÉTICO 5 GRUPOS ═══════")
        for gid in sorted(group_stats.keys()):
            st = group_stats[gid]
            total = st["wins"] + st["losses"]
            wr = round(st["wins"] / max(total, 1) * 100, 1)
            print(f"  G{gid} {st['name'][:40]}")
            print(f"      Trades: {total} | {st['wins']}W/{st['losses']}L | WR: {wr}% | PnL: ${st['pnl']:+.2f} | Activas: {st['active']}")
        print("═" * 50)
    except Exception as e:
        print(f"⚠️ Error reporte simulación: {e}")
