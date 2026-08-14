"""
Continuous 4-Hour Cloud Quant Trading Loop
- In Local Mode: Runs every 60 seconds (1 minute exact) for 240 cycles (4.0 hours).
- In Cloud Mode: Runs every 120 seconds (2 minutes exact) for 120 cycles (4.0 hours) to conserve proxies.
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

def run_git_push_sync(cycle_num: int, total_cycles: int = 240):
    """Safely commits and pushes updated matrix and account state to GitHub."""
    try:
        now_utc = datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")
        subprocess.run(["git", "config", "--global", "user.name", "github-actions[bot]"], check=False)
        subprocess.run(["git", "config", "--global", "user.email", "github-actions[bot]@users.noreply.github.com"], check=False)
        
        gh_token = os.getenv("GITHUB_TOKEN")
        gh_repo = os.getenv("GITHUB_REPOSITORY")
        if gh_token and gh_repo:
            subprocess.run(["git", "remote", "set-url", "origin", f"https://x-access-token:{gh_token}@github.com/{gh_repo}.git"], check=False)

        # Add and commit local cycle updates first
        subprocess.run(["git", "add", "."], check=False)
        status = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True)
        if status.stdout.strip():
            msg = f"chore: live sync [Cycle {cycle_num}/{total_cycles}] [{now_utc}]"
            subprocess.run(["git", "commit", "-m", msg], check=False)
            
        # Rebase pull cleanly on committed working tree
        subprocess.run(["git", "pull", "--rebase", "-X", "ours", "origin", "main"], check=False)
        
        # Push with retry
        for attempt in range(3):
            res = subprocess.run(["git", "push", "origin", "main"], capture_output=True, text=True)
            if res.returncode == 0:
                print(f"✅ [Cycle {cycle_num}] Git sync pushed successfully.", flush=True)
                break
            else:
                print(f"⚠️ [Cycle {cycle_num}] Push retry {attempt+1}/3: {res.stderr.strip()[:100]}", flush=True)
                subprocess.run(["git", "pull", "--rebase", "-X", "ours", "origin", "main"], check=False)
                time.sleep(2)
    except Exception as e:
        print(f"⚠️ [Cycle {cycle_num}] Git sync warning: {e}", flush=True)

def main():
    sys.stdout.reconfigure(encoding='utf-8', line_buffering=True)
    
    # AUTO-CLOUD: Only force cloud mode when running inside GitHub Actions environment
    try:
        import api_connector
        if os.getenv("GITHUB_ACTIONS") == "true" or os.getenv("CI") == "true":
            api_connector.set_execution_mode("cloud")
            print("☁️ Modo NUBE activado automáticamente (GitHub Actions)", flush=True)
        else:
            current_mode = api_connector.get_execution_mode()
            print(f"🖥️ Modo actual respetado: {current_mode.upper()}", flush=True)
    except Exception as e:
        print(f"⚠️ Could not evaluate execution mode: {e}", flush=True)
    
    sleep_interval_secs, total_cycles = get_loop_interval()
    
    print("=" * 70, flush=True)
    print(f"🚀 INICIANDO RUNNER CONTINUO CUÁNTICO (4 HORAS / {total_cycles} CICLOS)", flush=True)
    print(f"⏱️ Intervalo: Cada {sleep_interval_secs} segundos exactos ({sleep_interval_secs // 60} min)", flush=True)
    print(f"🎯 Total Ciclos: {total_cycles} ejecuciones continuas sin colas de espera", flush=True)
    print("=" * 70, flush=True)
    
    import importlib
    import data_fetcher
    import pipeline_processor
    import master_dashboard_generator

    for cycle in range(1, total_cycles + 1):
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"\n[{now_str}] ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━", flush=True)
        print(f"🔄 CICLO [{cycle}/{total_cycles}] - ESCANEO Y OPERACIÓN CUÁNTICA EN VIVO", flush=True)
        print(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━", flush=True)
        
        # Hot-reload modules so any pulled git improvements take effect immediately
        try:
            import obsidian_sync
            import web_dashboard_generator
            importlib.reload(obsidian_sync)
            importlib.reload(data_fetcher)
            importlib.reload(pipeline_processor)
            importlib.reload(master_dashboard_generator)
            importlib.reload(web_dashboard_generator)
        except Exception as e:
            print(f"⚠️ Reload note: {e}", flush=True)
        
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
            
        # Step 3: Refresh Master Dashboard
        try:
            master_dashboard_generator.generate_master_dashboard()
        except Exception as e:
            print(f"⚠️ Error generando dashboards (Ciclo {cycle}): {e}", flush=True)

        # Step 4: Refresh Web Dashboard & Data Feed (dashboard.html & dashboard_data.json)
        try:
            import web_dashboard_generator
            web_dashboard_generator.generate_web_dashboard()
        except Exception as e:
            print(f"⚠️ Error generando web dashboard (Ciclo {cycle}): {e}", flush=True)

        # Step 5: Push changes to GitHub
        run_git_push_sync(cycle, total_cycles)
        
        # Step 6: Sleep until next clock boundary
        if cycle < total_cycles:
            sleep_secs = sleep_until_next_boundary(sleep_interval_secs)
            target_time = datetime.fromtimestamp(time.time() + sleep_secs).strftime("%H:%M:%S")
            print(f"⏳ [Ciclo {cycle}] Completado. Esperando {sleep_secs}s hasta la marca en punto ({target_time}) para el Ciclo {cycle+1}...", flush=True)
            time.sleep(sleep_secs)

    print(f"\n🏁 [RUNNER CONTINUO FINALIZADO] Se completaron los {total_cycles} ciclos (4 horas).", flush=True)
    print("El siguiente disparador o cron tomará el relevo automáticamente.", flush=True)

if __name__ == "__main__":
    main()
