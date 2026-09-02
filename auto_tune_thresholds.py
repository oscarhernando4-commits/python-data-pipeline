"""
╔══════════════════════════════════════════════════════════════════════════════╗
║          AUTO-TUNE THRESHOLDS 4.0 — LAZO CERRADO DE AUTO-ADAPTACIÓN          ║
║  Conecta los resultados del Motor Genético (1000 cuentas de simulación)      ║
║  con los umbrales de la Cuenta Real (group_0 en dynamic_thresholds.json).    ║
║  Ajusta automáticamente el Score y FII requeridos según el grupo ganador.    ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import json
import os
from datetime import datetime, timezone

THRESHOLDS_FILE = os.path.join(os.path.dirname(__file__), "dynamic_thresholds.json")

def auto_tune():
    """
    Ejecuta el ciclo de auto-calibración en lazo cerrado:
    1. Lee los resultados empíricos de los 5 grupos genéticos en simulation_engine.
    2. Identifica el grupo con mejor Win Rate comprobado (mínimo 10 trades).
    3. Calibra suavemente los parámetros de 'group_0' (Cuenta Real) con guardarraíles de seguridad.
    """
    try:
        import simulation_engine as sim_eng
        best = sim_eng.get_best_group_params()
    except Exception as e:
        best = {}

    # Cargar o inicializar dynamic_thresholds.json
    t = {}
    if os.path.exists(THRESHOLDS_FILE):
        try:
            with open(THRESHOLDS_FILE, "r", encoding="utf-8") as f:
                t = json.load(f)
        except Exception:
            pass

    if "group_0" not in t:
        t["group_0"] = {
            "long_score": 82,
            "min_fii": 50,
            "max_canal_1h": 0.55,
            "max_rsi_15m": 60,
            "min_vol_surge": 0.20,
            "phase2_pct": 1.00,
            "phase3_pct": 1.60
        }

    # Estado de la cuenta real para evaluar modo defensivo
    consec_losses = 0
    daily_losses = 0
    try:
        import api_connector
        real_st = api_connector.load_real_account_state()
        consec_losses = real_st.get("_consecutive_losses", 0)
        daily_losses = real_st.get("daily_losses", 0)
    except Exception:
        pass

    now_utc = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

    # Si hay un grupo genético con >= 10 trades probados y WR >= 55%
    if best and best.get("total_trades", 0) >= 10 and best.get("win_rate_pct", 0) >= 55.0:
        cand_score = best.get("min_score", 85)
        cand_fii = best.get("min_fii", 60)
        cand_p2 = best.get("phase2_pct", 1.00)
        cand_p3 = best.get("phase3_pct", 1.60)
        wr = best.get("win_rate_pct", 0.0)
        gname = best.get("name", "Genético")

        # 🛡️ GUARDARRAÍLES DE SEGURIDAD INSTITUCIONAL:
        # Score nunca menor a 78 ni mayor a 90
        target_score = max(78, min(90, cand_score))
        # FII nunca menor a 48 ni mayor a 70
        target_fii = max(48, min(70, cand_fii))

        # Si hubo pérdidas recientes en real, elevar defensas automáticamente (+2 score, +5 FII)
        if consec_losses >= 1 or daily_losses >= 2:
            target_score = min(90, target_score + 2)
            target_fii = min(70, target_fii + 5)

        # Suavizado exponencial (50% actual + 50% target) para evitar oscilaciones bruscas
        cur_score = t["group_0"].get("long_score", 82)
        cur_fii = t["group_0"].get("min_fii", 50)
        new_score = int(round(cur_score * 0.5 + target_score * 0.5))
        new_fii = int(round(cur_fii * 0.5 + target_fii * 0.5))

        t["group_0"]["long_score"] = new_score
        t["group_0"]["min_fii"] = new_fii
        t["group_0"]["phase2_pct"] = cand_p2
        t["group_0"]["phase3_pct"] = cand_p3
        t["group_0"]["adapted_from_group"] = gname
        t["group_0"]["simulation_wr"] = wr
        t["group_0"]["last_auto_tune_utc"] = now_utc

        print(f"🧬 [AUTO-ADAPTACIÓN CUÁNTICA] Cuenta Real auto-calibrada con Grupo Líder: {gname[:35]} (WR: {wr}%) → Score Mín: {new_score} | FII Mín: {new_fii} | Meta: +{cand_p2:.2f}%", flush=True)

    else:
        # Modo por defecto seguro mientras la simulación acumula suficiente muestra
        target_score = 85 if (consec_losses >= 1 or daily_losses >= 2) else 80
        target_fii = 55 if (consec_losses >= 1 or daily_losses >= 2) else 50
        t["group_0"]["long_score"] = target_score
        t["group_0"]["min_fii"] = target_fii
        t["group_0"]["phase2_pct"] = 1.00
        t["group_0"]["phase3_pct"] = 1.60
        t["group_0"]["last_auto_tune_utc"] = now_utc

    try:
        with open(THRESHOLDS_FILE, "w", encoding="utf-8") as f:
            json.dump(t, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"⚠️ Error guardando dynamic_thresholds: {e}")

    return t

if __name__ == "__main__":
    res = auto_tune()
    print("Thresholds result:", res)
