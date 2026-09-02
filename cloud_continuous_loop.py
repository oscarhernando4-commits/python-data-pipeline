"""
Continuous 4-Hour Cloud Quant Trading Loop (Live Production Edition)
- Real-Money Spot Engine with Double Bottom & Bullish RSI Divergence Detection.
- 10D Fractal Matrix (1M<=35%, 5M<=38%, 15M<=42%, 1H<=50%, 1D<=55%).
- 3-Phase Pure Trailing Architecture (F1: SL -4% Unlimited, F2: +1% Fixed, F3: >=1.6% Dynamic).
- High-frequency 1-second Micro-Heartbeat for real-money positions.
"""

import time
import os

import subprocess
import sys
from datetime import datetime

def get_loop_interval():
    """Returns (interval_seconds, total_cycles) based on local vs cloud execution mode."""
    try:
        import api_connector
        mode = api_connector.get_execution_mode()
        if mode == "local" and os.getenv("GITHUB_ACTIONS") != "true" and os.getenv("CI") != "true":
            return 60, 240  # 1 minute interval, 240 cycles (4 hours)
    except Exception:
        pass
    return 120, 120  # 2 minute interval, 120 cycles (4 hours)

def sleep_until_next_boundary(interval_secs=60):
    """Calculates sleep time so every cycle aligns to clean clock intervals (every 1 min or 2 min)."""
    now = time.time()
    next_boundary = ((int(now) // interval_secs) + 1) * interval_secs
    sleep_secs = max(5, int(next_boundary - now))
    return sleep_secs

# Aliases for backwards compatibility
sleep_until_next_1m_boundary = lambda: sleep_until_next_boundary(60)
sleep_until_next_2m_boundary = lambda: sleep_until_next_boundary(120)
sleep_until_next_5m_boundary = sleep_until_next_1m_boundary

def sleep_with_micro_heartbeat(sleep_secs: int):
    """Sleeps in 1-second intervals while running the ultra-lightweight position heartbeat."""
    import api_connector
    end_time = time.time() + sleep_secs
    tick_count = 0
    while time.time() < end_time:
        remaining = end_time - time.time()
        if remaining <= 0:
            break
        chunk = min(1.0, remaining)
        time.sleep(chunk)
        tick_count += 1
        # Run 1s ultra-fast micro-heartbeat for active position (0.001% CPU)
        try:
            hb = api_connector.quick_position_heartbeat()
            if hb and isinstance(hb, dict):
                # Imprime el pulso en vivo CADA SEGUNDO EXACTO (T+1s, T+2s, T+3s...)
                p_fmt = f"${hb['price']:.5f}" if hb['price'] < 0.05 else f"${hb['price']:.4f}"
                pnl_sign = "+" if hb['pnl_pct'] >= 0 else ""
                print(f"💓 [HEARTBEAT 1s | T+{tick_count}s] {hb['symbol']} @ {p_fmt} | PnL: {pnl_sign}{hb['pnl_pct']:.2f}% (Pico: +{hb.get('highest_pnl', 0):.2f}% | Fase {hb.get('phase', 1)})", flush=True)
            elif tick_count % 15 == 0:
                print(f"📡 [RADAR 1s | T+{tick_count}s/{sleep_secs}s] Monitoreo activo de 67 pares Top 100 CMC en espera de la siguiente señal...", flush=True)
        except Exception:
            pass

        # 🟢 MEJORA 1 — BTC RECOVERY DETECTOR (cada 30 segundos cuando NO hay posición activa)
        # Si BTC RSI cruza 42 al alza durante el sleep de 2 min, romper y escanear YA.
        # Los primeros setups del rebote de BTC son los más rentables — no esperar 2 minutos.
        if tick_count % 30 == 0:
            try:
                _btc_kl = api_connector.get_klines("BTCUSDT", "1h", 25)
                if _btc_kl and len(_btc_kl) >= 15:
                    from multi_timeframe_analyzer import calculate_rsi as _crsi
                    _btc_cls = [float(k[4]) for k in _btc_kl]
                    _btc_rsi_now = _crsi(_btc_cls)
                    _btc_px_now = _btc_cls[-1]
                    _prev_btc_rsi = getattr(sleep_with_micro_heartbeat, "_last_btc_rsi", 30.0)
                    sleep_with_micro_heartbeat._last_btc_rsi = _btc_rsi_now
                    if _btc_rsi_now >= 42.0 and _prev_btc_rsi < 42.0:
                        print(f"\n🟢 [BTC RECOVERY DETECTOR] ¡BTC RSI cruzó 42 al ALZA! ({_prev_btc_rsi:.1f} → {_btc_rsi_now:.1f}) @ ${_btc_px_now:,.0f}", flush=True)
                        print("⚡ Rompiendo sleep anticipadamente — capturando PRIMEROS SETUPS del rebote...\n", flush=True)
                        break
                    elif tick_count % 60 == 0:
                        print(f"📊 [BTC MONITOR 60s] RSI1H={_btc_rsi_now:.1f} | ${_btc_px_now:,.0f} | {'🟡 Bajista (esperando RSI>42)' if _btc_rsi_now < 42 else '🟢 Modo Normal activo'}", flush=True)
            except Exception:
                pass


def run_focused_position_guardian(max_duration_secs: int = 14400):
    """
    🎯 GUARDIÁN SNIPER DEDICADO AL 100% (Modo Cero Latencia / 1s Heartbeat):
    Cuando hay una posición real abierta en Binance Spot:
    1. Cancela los escaneos del Top 100 y consultas AI a Gemini (ahorra cuota y CPU).
    2. Dedica el 100% de la CPU al Heartbeat de 1 segundo (T+1s, T+2s, T+3s...).
    3. Vigila segundo a segundo el PnL, Trailing Stop y Wick Sniper.
    4. En cuanto la posición se cierra (Take Profit o Stop Loss), sincroniza balance en Binance
       y DEVUELVE el control instantáneamente al radar para el siguiente escaneo.
    """
    import api_connector
    print("\n" + "=" * 70, flush=True)
    print("🛡️ [MODO GUARDIÁN SNIPER 100% DEDICADO ACTIVADO]", flush=True)
    print("⚡ Escaneos de 67 pares Top 100 y Gemini AI PAUSADOS para enfocar el 100% de recursos.")
    print("💓 Monitoreo en vivo SUB-SEGUNDO (1s) para cosechar la cima o ejecutar SL.", flush=True)
    print("=" * 70 + "\n", flush=True)
    
    import threading
    def _async_git_pull():
        try:
            import os
            _env = os.environ.copy()
            _env["GIT_TERMINAL_PROMPT"] = "0"
            subprocess.run(["git", "pull", "--rebase"], check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=5, env=_env)
        except Exception:
            pass

    def _async_git_push():
        try:
            run_git_push_sync(1, 1)
        except Exception:
            pass

    start_t = time.time()
    tick = 0
    while time.time() - start_t < max_duration_secs:
        tick += 1
        time.sleep(1.0)
        
        # 🔄 Sincronización en segundo plano (0ms de bloqueo para garantizar pulso ininterrumpido cada 1s)
        if tick % 30 == 0:
            threading.Thread(target=_async_git_pull, daemon=True).start()
        
        try:
            hb = api_connector.quick_position_heartbeat()
            if not hb or not isinstance(hb, dict) or not hb.get("symbol"):
                # La posición se ha cerrado
                print(f"\n🎯 [OPERACIÓN FINALIZADA TRAS {tick}s] Salida ejecutada con éxito.", flush=True)
                print("🔄 Sincronizando billetera y reactivando Radar Cuántico de 67 Pares Top 100 CMC...\n", flush=True)
                try:
                    api_connector.diagnose_full_spot_wallet()
                except Exception:
                    pass
                break
            
            p_fmt = f"${hb['price']:.5f}" if hb['price'] < 0.05 else f"${hb['price']:.4f}"
            pnl_sign = "+" if hb['pnl_pct'] >= 0 else ""
            curr_phase = hb.get('phase', 1)
            curr_highest = hb.get('highest_pnl', 0.0)
            
            # 💓 Monitoreo en Vivo Segundo a Segundo en Tiempo Real (flush=True inmediato)
            print(f"💓 [HEARTBEAT 1s | T+{tick}s] {hb['symbol']} @ {p_fmt} | PnL: {pnl_sign}{hb['pnl_pct']:.2f}% (Pico: +{curr_highest:.2f}% | Fase {curr_phase})", flush=True)
            
            # Sincronización periódica ligera de estado a git cada 300s en hilo secundario (0ms de retraso)
            if tick % 300 == 0:
                threading.Thread(target=_async_git_push, daemon=True).start()
        except Exception as e:
            print(f"⚠️ Nota en Heartbeat Guardian: {e}", flush=True)
            time.sleep(1.0)

def run_git_push_sync(cycle_num: int, total_cycles: int = 240):
    """Safely commits and pushes state periodically to avoid CPU and disk thrashing."""
    # In local mode, only sync to GitHub every 10 cycles (10 mins) or on final cycle
    is_cloud = os.getenv("GITHUB_ACTIONS") == "true" or os.getenv("CI") == "true"
    if not is_cloud and (cycle_num % 10 != 0 and cycle_num != total_cycles and cycle_num != 1):
        return

    try:
        now_utc = datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")
        _env = os.environ.copy()
        _env["GIT_TERMINAL_PROMPT"] = "0"
        
        subprocess.run(["git", "config", "--global", "user.name", "github-actions[bot]"], check=False, timeout=5, env=_env)
        subprocess.run(["git", "config", "--global", "user.email", "github-actions[bot]@users.noreply.github.com"], check=False, timeout=5, env=_env)
        
        gh_token = os.getenv("GITHUB_TOKEN")
        gh_repo = os.getenv("GITHUB_REPOSITORY")
        if gh_token and gh_repo:
            subprocess.run(["git", "remote", "set-url", "origin", f"https://x-access-token:{gh_token}@github.com/{gh_repo}.git"], check=False, timeout=5, env=_env)

        # Export intelligence matrix from SQLite vault
        try:
            import quant_database
            quant_database.export_intelligence_matrix()
        except Exception:
            pass

        # Add and commit state files
        subprocess.run(["git", "add", "real_money_account.json", "top_100_pairs.json", "dynamic_thresholds.json", "proxy_state.json", "gemini_key_state.json", "trade_memory.json", "matrix_100_simulations.json", "intelligence_matrix.json", "quant_intelligence.db"], check=False, timeout=5, env=_env)
        status = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True, timeout=5, env=_env)
        if status.stdout.strip():
            msg = f"chore: live sync [Cycle {cycle_num}/{total_cycles}] [{now_utc}]"
            subprocess.run(["git", "commit", "-m", msg], check=False, timeout=5, env=_env)
            
        # Smooth merge preferring origin updates
        subprocess.run(["git", "pull", "--no-rebase", "-X", "theirs", "origin", "main"], capture_output=True, text=True, timeout=8, env=_env)
        
        for attempt in range(2):
            res = subprocess.run(["git", "push", "origin", "main"], capture_output=True, text=True, timeout=8, env=_env)
            if res.returncode == 0:
                print(f"✅ [Cycle {cycle_num}] Git sync pushed.", flush=True)
                break
            else:
                subprocess.run(["git", "pull", "--no-rebase", "-X", "theirs", "origin", "main"], capture_output=True, text=True, timeout=8, env=_env)
                time.sleep(1)
    except Exception as e:
        print(f"⚠️ [Cycle {cycle_num}] Git sync note: {e}", flush=True)

def main():
    sys.stdout.reconfigure(encoding='utf-8', line_buffering=True)
    
    # AUTO-CLOUD: Only force cloud mode when running inside GitHub Actions environment
    is_cloud_env = os.getenv("GITHUB_ACTIONS") == "true" or os.getenv("CI") == "true"
    try:
        import api_connector
        if is_cloud_env:
            api_connector.set_execution_mode("cloud")
            print("☁️ Modo NUBE activado automáticamente (GitHub Actions)", flush=True)
        else:
            current_mode = api_connector.get_execution_mode()
            print(f"🖥️ Modo actual respetado: {current_mode.upper()} (Ultra-Lightweight)", flush=True)
    except Exception as e:
        print(f"⚠️ Could not evaluate execution mode: {e}", flush=True)
    
    # Windows Process Priority: Set to BELOW_NORMAL to ensure user apps have 100% responsiveness
    if not is_cloud_env:
        try:
            import ctypes
            kernel32 = ctypes.windll.kernel32
            handle = kernel32.GetCurrentProcess()
            kernel32.SetPriorityClass(handle, 0x00004000)  # BELOW_NORMAL_PRIORITY_CLASS
            print("⚡ Prioridad Windows configurada en 'BELOW_NORMAL' (PC 100% silencioso y fluido)", flush=True)
        except Exception:
            pass
    
    sleep_interval_secs, total_cycles = get_loop_interval()
    
    infra_label = "☁️ Servidor de Nube de Alta Velocidad (GitHub Actions)" if is_cloud_env else "⚡ Optimización PC Local: Dashboards en Background | 10 Threads"
    print("=" * 70, flush=True)
    print(f"🚀 RUNNER CUÁNTICO ULTRA-LIGERO (4 HORAS / {total_cycles} CICLOS)", flush=True)
    print(f"⏱️ Intervalo Escáner: Cada {sleep_interval_secs}s ({sleep_interval_secs // 60} min)")
    print(f"💓 Micro-Heartbeat de Posición: Activo cada 1.0 segundo (Sub-segundo / Cero Latencia)")
    print(f"{infra_label}")
    print("=" * 70, flush=True)
    
    import importlib
    import data_fetcher
    import pipeline_processor

    cycle = 0
    while cycle < total_cycles:
        # Hot-reload modules so any pulled git improvements take effect immediately
        try:
            import api_connector
            import asset_dna_predictive_engine
            import multi_timeframe_analyzer
            import llm_router
            import data_fetcher
            import pipeline_processor
            importlib.reload(asset_dna_predictive_engine)
            importlib.reload(api_connector)
            importlib.reload(multi_timeframe_analyzer)
            importlib.reload(llm_router)
            importlib.reload(data_fetcher)
            importlib.reload(pipeline_processor)
        except Exception as e:
            print(f"⚠️ Reload note: {e}", flush=True)

        # Resetear flag de 1-trade-por-ciclo al inicio de cada nuevo ciclo
        try:
            import api_connector as _ac_reset
            _ac_reset._trade_executed_this_cycle = False
        except Exception:
            pass

        # 🎯 MODO GUARDIÁN 100% EN PRIMER PLANO: Si hay posición real abierta en Binance Spot,
        # SUSPENDER los ciclos de 2 minutos y enfocar el 100% de la consola y CPU en el Heartbeat 1s continuo
        has_active_real_pos = False
        try:
            st_check = api_connector.load_real_account_state()
            if st_check.get("position"):
                api_connector.diagnose_full_spot_wallet()
                st_check = api_connector.load_real_account_state()
                has_active_real_pos = bool(st_check.get("position"))
        except Exception:
            pass

        if has_active_real_pos:
            # Monitoreo exclusivo segundo a segundo sin interrupción de ciclos hasta la salida
            run_focused_position_guardian()
            run_git_push_sync(cycle, total_cycles)
            # Tras la salida y liberación de capital a USDT, continuar de inmediato al radar
            continue

        # 📡 MODO RADAR: Solo cuando NO hay posición activa (Buscando Entrada A+)
        cycle += 1
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"\n[{now_str}] ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━", flush=True)
        print(f"🔄 CICLO [{cycle}/{total_cycles}] - ESCANEO Y OPERACIÓN CUÁNTICA EN VIVO", flush=True)
        print(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━", flush=True)

        # Step 1: Update market universe
        try:
            if hasattr(data_fetcher, 'fetch_top_100_pairs'):
                data_fetcher.fetch_top_100_pairs()
            elif hasattr(data_fetcher, 'update_top_pairs'):
                data_fetcher.update_top_pairs()
        except Exception as e:
            print(f"⚠️ Error actualizando pares (Ciclo {cycle}): {e}", flush=True)
            
        # Step 2: Run institutional trading matrix & AI execution
        try:
            if hasattr(pipeline_processor, 'run_infinite_trading_matrix_cycle'):
                pipeline_processor.run_infinite_trading_matrix_cycle()
            elif hasattr(pipeline_processor, 'run_optimized_pipeline'):
                pipeline_processor.run_optimized_pipeline()
        except Exception as e:
            print(f"⚠️ Error en pipeline_processor (Ciclo {cycle}): {e}", flush=True)

        # Step 3: Lightweight periodic state sync to GitHub (every 10 cycles)
        run_git_push_sync(cycle, total_cycles)
        
        # Step 4: Sleep until next clock boundary with 1s radar heartbeat
        if cycle < total_cycles:
            sleep_secs = sleep_until_next_boundary(sleep_interval_secs)
            target_time = datetime.fromtimestamp(time.time() + sleep_secs).strftime("%H:%M:%S")
            print(f"⏳ [Ciclo {cycle}] Completado. Esperando {sleep_secs}s hasta la marca en punto ({target_time}) para el Ciclo {cycle+1}...", flush=True)
            sleep_with_micro_heartbeat(sleep_secs)

    print(f"\n🏁 [RUNNER CONTINUO FINALIZADO] Se completaron los {total_cycles} ciclos (4 horas).", flush=True)
    print("El siguiente disparador o cron tomará el relevo automáticamente.", flush=True)

    # 📊 MEJORA 6 — DAILY RECAP: Resumen completo al final de cada run de 4 horas
    try:
        import api_connector as _ac_recap
        from multi_timeframe_analyzer import calculate_rsi as _rsi_recap
        _st = _ac_recap.load_real_account_state()
        _bal = _st.get("current_balance_usd", 0)
        _wins = _st.get("daily_wins", 0)
        _losses = _st.get("daily_losses", 0)
        _total_ops = _wins + _losses
        _wr = (_wins / _total_ops * 100) if _total_ops > 0 else 0
        _daily_pnl = _st.get("_daily_pnl_usd", 0)
        _pos = _st.get("position")
        _btc_kl = _ac_recap.get_klines("BTCUSDT", "1h", 25)
        _btc_rsi = _rsi_recap([float(k[4]) for k in _btc_kl]) if _btc_kl else 50
        _btc_px = float(_btc_kl[-1][4]) if _btc_kl else 0
        _btc_mode = "CRASH" if _btc_rsi < 22 else ("BAJISTA" if _btc_rsi < 42 else ("NORMAL" if _btc_rsi < 55 else "ALCISTA"))
        print("\n" + "=" * 70, flush=True)
        print("📊 RESUMEN DE SESIÓN (4 HORAS)", flush=True)
        print("=" * 70, flush=True)
        print(f"  💰 Balance: ${_bal:.2f} USD", flush=True)
        print(f"  📈 Operaciones hoy: {_total_ops} ({_wins} wins / {_losses} losses) | WR: {_wr:.0f}%", flush=True)
        print(f"  💵 PnL del día: ${_daily_pnl:+.4f} USD", flush=True)
        if _pos:
            _entry = _pos.get("entry_price", 0)
            _sym_p = _pos.get("symbol", "?")
            _px_p = _ac_recap.get_symbol_price(_sym_p, is_futures=False) or _entry
            _pnl_p = ((_px_p - _entry) / _entry * 100) if _entry > 0 else 0
            print(f"  📌 Posición activa: {_sym_p} | Entrada ${_entry:.4f} | PnL {_pnl_p:+.2f}%", flush=True)
        else:
            print(f"  📌 Sin posición activa — 100% USDT protegido", flush=True)
        print(f"  🔷 BTC: ${_btc_px:,.0f} | RSI1H: {_btc_rsi:.1f} | Modo: {_btc_mode}", flush=True)
        if _btc_rsi < 42:
            print(f"  ⏳ Próxima ventana de alta operatividad: cuando BTC RSI > 42 (~${_btc_px*1.03:,.0f})", flush=True)
        else:
            print(f"  ✅ Mercado en modo normal — Siguiente sesión con máxima operatividad", flush=True)
        print("=" * 70 + "\n", flush=True)
    except Exception as _recap_err:
        print(f"⚠️ Recap error (no-blocking): {_recap_err}", flush=True)

if __name__ == "__main__":
    main()
