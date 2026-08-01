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

TOTAL_CYCLES = 50       # 50 cycles * 5 minutes = 250 minutes (~4.1 hours)
SLEEP_SECONDS = 300     # 5 minutes exact interval between analysis cycles

def run_git_push_sync(cycle_num: int):
    """Safely commits and pushes updated matrix and account state to GitHub."""
    try:
        now_utc = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
        subprocess.run(["git", "config", "--global", "user.name", "antigravity-bot[bot]"], check=False)
        subprocess.run(["git", "config", "--global", "user.email", "antigravity-bot[bot]@users.noreply.github.com"], check=False)
        
        # Soft reset against remote to prevent divergence
        subprocess.run(["git", "fetch", "origin", "main"], check=False)
        subprocess.run(["git", "reset", "--soft", "origin/main"], check=False)
        subprocess.run(["git", "add", "."], check=False)
        
        msg = f"chore: live 5m sync [Cycle {cycle_num}/{TOTAL_CYCLES}] [{now_utc}]"
        subprocess.run(["git", "commit", "-m", msg], check=False)
        
        # Push with retry
        for attempt in range(3):
            res = subprocess.run(["git", "push", "origin", "main"], capture_output=True, text=True)
            if res.returncode == 0:
                print(f"✅ [Cycle {cycle_num}] Git sync pushed successfully.")
                break
            else:
                print(f"⚠️ [Cycle {cycle_num}] Push retry {attempt+1}/3: {res.stderr.strip()[:100]}")
                subprocess.run(["git", "fetch", "origin", "main"], check=False)
                subprocess.run(["git", "rebase", "origin/main"], check=False)
                time.sleep(3)
    except Exception as e:
        print(f"⚠️ [Cycle {cycle_num}] Git sync warning: {e}")

def main():
    sys.stdout.reconfigure(encoding='utf-8')
    print("=" * 70)
    print("🚀 INICIANDO RUNNER CONTINUO CUÁNTICO DE 6 HORAS (5.5H / 66 CICLOS)")
    print(f"⏱️ Intervalo: Cada 5 minutos exactos ({SLEEP_SECONDS}s)")
    print(f"🎯 Total Ciclos: {TOTAL_CYCLES} ejecuciones continuas sin colas de espera")
    print("=" * 70)
    
    import data_fetcher
    import pipeline_processor

    for cycle in range(1, TOTAL_CYCLES + 1):
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"\n[{now_str}] ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print(f"🔄 CICLO [{cycle}/{TOTAL_CYCLES}] - ESCANEO Y OPERACIÓN CUÁNTICA EN VIVO")
        print(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        
        # Step 1: Fetch pairs
        try:
            data_fetcher.fetch_top_100_pairs()
        except Exception as e:
            print(f"⚠️ Error en data_fetcher (Ciclo {cycle}): {e}")
            
        # Step 2: Run institutional quant pipeline
        try:
            pipeline_processor.run_optimized_pipeline()
        except Exception as e:
            print(f"⚠️ Error en pipeline_processor (Ciclo {cycle}): {e}")
            
        # Step 3: Push changes to GitHub
        run_git_push_sync(cycle)
        
        # Step 4: Sleep until next 5-minute cycle (except after the final cycle)
        if cycle < TOTAL_CYCLES:
            print(f"⏳ [Ciclo {cycle}] Completado. Esperando {SLEEP_SECONDS}s (5 minutos) para el siguiente ciclo...")
            time.sleep(SLEEP_SECONDS)

    print("\n🏁 [RUNNER CONTINUO FINALIZADO] Se completaron los 66 ciclos (5.5 horas).")
    print("El siguiente disparador o cron tomará el relevo automáticamente.")

if __name__ == "__main__":
    main()
