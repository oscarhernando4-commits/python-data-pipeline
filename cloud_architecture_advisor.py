import os
import json
import sys
from datetime import datetime

OBSIDIAN_FOLDER = r"C:\Users\hosca\Documents\Antigravity\Obsidian\01_PROYECTOS\BINANCE_QUANT_TRADING"

def ensure_obsidian_dir():
    if not os.path.exists(OBSIDIAN_FOLDER):
        os.makedirs(OBSIDIAN_FOLDER, exist_ok=True)

def generate_cloud_architecture_note():
    ensure_obsidian_dir()
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    content = f"""---
tags:
  - trading
  - arquitectura_nube_24_7
  - ejecucion_pc_apagado
  - binance
date: {now_str}
---

# ☁️ GUÍA DE ARQUITECTURA EN LA NUBE 24/7 (100% GRATIS Y SEGURA)

> [!NOTE] 🔒 CÓMO OPERAR 24/7 AUNQUE TU COMPUTADOR ESTÉ COMPLETAMENTE APAGADO
> **Última Actualización:** `{now_str}`  
> **Requisito:** 100% Gratuito, Sin Tarjeta Obligatoria de Pago y Cifrado de Seguridad Nivel Bancario.

---

## 🏆 LAS 2 MEJORES OPCIONES DE LA NUBE PARA TRADING AUTOMÁTICO

### 🥇 Opción 1: GitHub Actions (Cron Workflow Programado) — *RECOMENDADA POR SIMPLICIDAD*
- 💰 **Costo:** **`$0.00 USD (100% Gratis de por vida)`**
- 🛡️ **Seguridad:** Las API Keys de Binance se guardan en **GitHub Encrypted Secrets** (cifrado AES-256 de nivel militar de Microsoft/GitHub). Nadie en internet puede ver tus claves.
- ⚙️ **Cómo funciona:** GitHub ejecuta un contenedor en la nube cada 15 minutos o cada hora que revisa la API de Binance, evalúa los indicadores A+ y ejecuta las operaciones sin necesidad de tener tu PC encendido.

---

### 🥈 Opción 2: Oracle Cloud Always Free (Servidor VPS Gratis de por Vida)
- 💰 **Costo:** **`$0.00 USD (Servidor Nube Gratis de por Vida)`**
- 🛡️ **Seguridad:** Servidor virtual privado (VPS) Linux Ubuntu dedicado exclusivamente para ti.
- ⚙️ **Cómo funciona:** Un mini-servidor encendido los 365 días del año en los datacenters de Oracle que corre nuestro script silencioso en Linux.

---

## 📋 COMPARATIVA ESTRATÉGICA

| Característica | Local (Tu PC Actual) | GitHub Actions (Nube) | Oracle Cloud VPS |
| :--- | :---: | :---: | :---: |
| **¿Funciona con PC apagado?** | ❌ No | 🟢 **SÍ (24/7)** | 🟢 **SÍ (24/7)** |
| **Costo Mensual** | `$0` | **`$0 (Gratis)`** | **`$0 (Gratis de por vida)`** |
| **Seguridad de API Keys** | En tu disco `.env` | **GitHub Secrets (Cifrado militar)** | Servidor Privado |
| **Mantenimiento** | Cero | **Cero (Automático)** | Mínimo en Linux |

---

## 🔗 NAVEGACIÓN RÁPIDA
- [[📊_MASTER_DASHBOARD_TRADING|Ver Master Dashboard]]
- [[🚀_Matriz_100_Simulaciones|Ver Matriz de 100 Cuentas]]
- [[🏛️_Auditoria_Arquitectura_Ecosistema_Trading|Ver Auditoría del Ecosistema]]
- [[🛡️_Plan_Transicion_Dinero_Real_Y_Testnet|Ver Plan de Transición a Dinero Real]]
"""

    file_path = os.path.join(OBSIDIAN_FOLDER, "☁️_Opciones_Nube_24_7_Gratis_Y_Segura.md")
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)
        
    print(f"Cloud architecture guide created at: {file_path}")
    return file_path

if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    generate_cloud_architecture_note()
