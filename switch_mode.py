"""
🔄 Cambiador de Modo de Ejecución del Bot Cuántico
====================================================
Permite alternar entre modo LOCAL (PC encendida, sin proxy) y modo NUBE (GitHub Actions, Fixie proxy).

Uso:
  python switch_mode.py local   → Modo Local (sin proxy, análisis directo desde tu PC)
  python switch_mode.py cloud   → Modo Nube (Fixie proxy, GitHub Actions)
  python switch_mode.py status  → Ver modo actual y estadísticas de proxy
"""

import sys
import os
import json
from datetime import datetime

try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

EXECUTION_MODE_FILE = os.path.join(os.path.dirname(__file__), "execution_mode.json")
PROXY_STATE_FILE = os.path.join(os.path.dirname(__file__), "proxy_state.json")

def get_mode():
    """Lee el modo de ejecución actual."""
    try:
        with open(EXECUTION_MODE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {"mode": "cloud", "switched_at": "unknown", "switched_by": "default"}

def set_mode(mode, switched_by="user_command"):
    """Cambia el modo de ejecución."""
    data = {
        "mode": mode,
        "switched_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "switched_by": switched_by
    }
    with open(EXECUTION_MODE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    return data

def show_status():
    """Muestra el estado actual del sistema."""
    mode_data = get_mode()
    mode = mode_data.get("mode", "cloud")
    
    print("\n" + "=" * 60)
    print("🤖 ESTADO DEL SISTEMA HÍBRIDO DE EJECUCIÓN")
    print("=" * 60)
    
    if mode == "local":
        print(f"  🖥️  Modo Actual: LOCAL (Conexión Directa)")
        print(f"  ✅ Proxy Fixie: NO SE CONSUME CUOTA")
        print(f"  📊 Análisis: DETALLADO (sync cada ciclo)")
    else:
        print(f"  ☁️  Modo Actual: NUBE (Fixie Proxy)")
        print(f"  🔄 Proxy Fixie: ROUND-ROBIN EQUITATIVO (10 cuentas)")
        print(f"  📊 Análisis: EFICIENTE (sync cada 30 min)")
    
    print(f"  ⏰ Último cambio: {mode_data.get('switched_at', 'N/A')}")
    print(f"  👤 Cambiado por: {mode_data.get('switched_by', 'N/A')}")
    
    # Show proxy usage stats if available
    try:
        with open(PROXY_STATE_FILE, "r", encoding="utf-8") as f:
            proxy_state = json.load(f)
        usage = proxy_state.get("usage", {})
        if usage:
            print("\n  📈 USO DE PROXIES FIXIE (Round-Robin):")
            total_usage = sum(usage.values())
            for account, count in sorted(usage.items(), key=lambda x: x[1], reverse=True):
                pct = (count / total_usage * 100) if total_usage > 0 else 0
                bar = "█" * int(pct / 5) + "░" * (20 - int(pct / 5))
                print(f"     {account:25s} {bar} {count:4d} req ({pct:.1f}%)")
            print(f"     {'TOTAL':25s} {'':20s} {total_usage:4d} req")
    except Exception:
        print("\n  📈 Sin datos de uso de proxy aún.")
    
    # Show Gemini API key usage stats
    GEMINI_KEY_STATE_FILE = os.path.join(os.path.dirname(__file__), "gemini_key_state.json")
    try:
        with open(GEMINI_KEY_STATE_FILE, "r", encoding="utf-8") as f:
            gemini_state = json.load(f)
        g_usage = gemini_state.get("usage", {})
        if g_usage:
            print("\n  🧠 USO DE CLAVES GEMINI AI (Round-Robin):")
            g_total = sum(g_usage.values())
            for key_name, count in sorted(g_usage.items(), key=lambda x: x[1], reverse=True):
                pct = (count / g_total * 100) if g_total > 0 else 0
                bar = "█" * int(pct / 5) + "░" * (20 - int(pct / 5))
                print(f"     {key_name:25s} {bar} {count:4d} calls ({pct:.1f}%)")
            print(f"     {'TOTAL':25s} {'':20s} {g_total:4d} calls")
        else:
            print("\n  🧠 Sin datos de uso de Gemini AI aún.")
    except Exception:
        print("\n  🧠 Sin datos de uso de Gemini AI aún.")
    
    print("=" * 60 + "\n")

def main():
    if len(sys.argv) < 2:
        show_status()
        print("Uso:")
        print("  python switch_mode.py local   → Cambiar a Modo Local")
        print("  python switch_mode.py cloud   → Cambiar a Modo Nube")
        print("  python switch_mode.py status  → Ver estado actual")
        return
    
    command = sys.argv[1].lower().strip()
    
    if command == "local":
        set_mode("local")
        print("\n🖥️  ═══════════════════════════════════════════════")
        print("    MODO LOCAL ACTIVADO")
        print("    ✅ Sin proxy → No consume cuota Fixie")
        print("    ✅ Análisis detallado en cada ciclo")
        print("    ✅ Wallet sync continuo (sin límite)")
        print("    ═══════════════════════════════════════════════\n")
        
    elif command == "cloud" or command == "nube":
        set_mode("cloud")
        print("\n☁️  ═══════════════════════════════════════════════")
        print("    MODO NUBE ACTIVADO")
        print("    🔄 Fixie proxy → Round-Robin equitativo")
        print("    📊 Wallet sync cada 60 min (ahorro cuota Fixie)")
        print("    🌐 GitHub Actions ejecuta automáticamente")
        print("    ═══════════════════════════════════════════════\n")
        
    elif command == "status":
        show_status()
    else:
        print(f"❌ Comando no reconocido: '{command}'")
        print("Opciones: local, cloud, nube, status")

if __name__ == "__main__":
    main()
