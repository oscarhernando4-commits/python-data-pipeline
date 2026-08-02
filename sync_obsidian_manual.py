"""
Manual Obsidian Sync Trigger Script
Executes explicit, on-demand synchronization of all Obsidian dashboards, subreports,
learning matrices, and AI verdicts when requested manually by the user.
"""

import os
import sys

def run_manual_obsidian_sync():
    os.environ["ENABLE_OBSIDIAN_AUTO_SYNC"] = "true"
    print("=" * 65)
    print("📂 INICIANDO SINCRONIZACIÓN MANUAL SOLICITADA EN OBSIDIAN...")
    print("=" * 65)
    
    try:
        import master_dashboard_generator
        master_dashboard_generator.generate_master_dashboard()
        print("  ✅ Master Dashboard generado en Obsidian")
    except Exception as e:
        print(f"  ⚠️ Error en Master Dashboard: {e}")
        
    try:
        import super_cerebro_analyzer
        super_cerebro_analyzer.generate_super_cerebro_report()
        print("  ✅ Informe Ejecutivo del Súper-Cerebro generado en Obsidian")
    except Exception as e:
        print(f"  ⚠️ Error en Súper-Cerebro Report: {e}")
        
    try:
        import learning_engine
        mem = learning_engine.load_memory()
        learning_engine.sync_learning_note(mem)
        print("  ✅ Matriz de Aprendizaje e Historial generado en Obsidian")
    except Exception as e:
        print(f"  ⚠️ Error en Matriz de Aprendizaje: {e}")
        
    print("=" * 65)
    print("🏆 SINCRONIZACIÓN MANUAL CON OBSIDIAN COMPLETADA CON ÉXITO")
    print("=" * 65)

if __name__ == "__main__":
    sys.stdout.reconfigure(encoding='utf-8')
    run_manual_obsidian_sync()
