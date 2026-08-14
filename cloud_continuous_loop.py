"""
Continuous 4-Hour Cloud Quant Trading Loop
Runs autonomously in GitHub Actions for 4.1 hours (50 cycles x 5 minutes).
Eliminates runner queue delays by keeping a single virtual machine active.
"""

import time
import os
import subprocess
import sys
from datetime import datetime

TOTAL_CYCLES = 120      # 120 cycles * 2 minutes = 240 minutes (~4.0 hours)
SLEEP_SECONDS = 120     # 2 minutes exact interval between analysis cycles

def run_git_push_sync(cycle_num: int):
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
            msg = f"chore: live 2m sync [Cycle {cycle_num}/{TOTAL_CYCLES}] [{now_utc}]"
            subprocess.run(["git", "commit", "-m", msg], check=False)
            
        # Rebase pull cleanly on committed working tree
        subprocess.run(["git", "pull", "--rebase", "-X", "ours", "origin", "main"], check=False)
        
        # Push with retry
        for attempt in range(3):
            res = subprocess.run(["git", "push", "origin", "main"], capture_output=True, text=True)
            if res.returncode == 0:
                print(f"✅ [Cycle {cycle_num}] Git sync pushed successfully.")
                break
            else:
                print(f"⚠️ [Cycle {cycle_num}] Push retry {attempt+1}/3: {res.stderr.strip()[:100]}")
                subprocess.run(["git", "pull", "--rebase", "-X", "ours", "origin", "main"], check=False)
                time.sleep(2)
    except Exception as e:
        print(f"⚠️ [Cycle {cycle_num}] Git sync warning: {e}")



def sleep_until_next_2m_boundary():
    """Calculates sleep time so every cycle aligns to clean 2-minute clock intervals (:00, :02, :04, :06...)."""
    now = time.time()
    next_boundary = ((int(now) // 120) + 1) * 120
    sleep_secs = max(10, int(next_boundary - now))
    return sleep_secs

# Alias so legacy in-memory calls automatically execute 2-minute sleep
sleep_until_next_5m_boundary = sleep_until_next_2m_boundary

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
    
    print("=" * 70, flush=True)
    print(f"🚀 INICIANDO RUNNER CONTINUO CUÁNTICO (4 HORAS / {TOTAL_CYCLES} CICLOS)", flush=True)
    print(f"⏱️ Intervalo: Cada 2 minutos exactos ({SLEEP_SECONDS}s)", flush=True)
    print(f"🎯 Total Ciclos: {TOTAL_CYCLES} ejecuciones continuas sin colas de espera", flush=True)
    print("=" * 70, flush=True)
    
    import importlib
    import data_fetcher
    import pipeline_processor
    import master_dashboard_generator

    for cycle in range(1, TOTAL_CYCLES + 1):
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"\n[{now_str}] ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━", flush=True)
        print(f"🔄 CICLO [{cycle}/{TOTAL_CYCLES}] - ESCANEO Y OPERACIÓN CUÁNTICA EN VIVO", flush=True)
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
        except Exception:
            pass
        
        # Step 1: Fetch pairs
        try:
            if hasattr(data_fetcher, 'update_top_pairs'):
                data_fetcher.update_top_pairs()
            elif hasattr(data_fetcher, 'fetch_top_100_pairs'):
                data_fetcher.fetch_top_100_pairs()
        except Exception as e:
            print(f"⚠️ Error en data_fetcher (Ciclo {cycle}): {e}", flush=True)
            
        # Step 2: Run institutional quant pipeline
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

        # Step 4: Push changes to GitHub
        run_git_push_sync(cycle)
        
        # Step 5: Sleep until next 2-minute clock boundary (except after the final cycle)
        if cycle < TOTAL_CYCLES:
            sleep_secs = sleep_until_next_2m_boundary()
            target_time = datetime.fromtimestamp(time.time() + sleep_secs).strftime("%H:%M:%S")
            print(f"⏳ [Ciclo {cycle}] Completado. Esperando {sleep_secs}s hasta la marca en punto ({target_time}) para el Ciclo {cycle+1}...", flush=True)
            time.sleep(sleep_secs)

    print(f"\n🏁 [RUNNER CONTINUO FINALIZADO] Se completaron los {TOTAL_CYCLES} ciclos (4 horas).", flush=True)
    print("El siguiente disparador o cron tomará el relevo automáticamente.", flush=True)

if __name__ == "__main__":
    main()
