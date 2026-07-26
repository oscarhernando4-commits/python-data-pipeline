import os
import json
import sys
from datetime import datetime

OBSIDIAN_FOLDER = r"C:\Users\hosca\Documents\Antigravity\Obsidian\01_PROYECTOS\BINANCE_QUANT_TRADING"

def ensure_obsidian_dir():
    if not os.path.exists(OBSIDIAN_FOLDER):
        os.makedirs(OBSIDIAN_FOLDER, exist_ok=True)

def generate_github_actions_setup_note():
    ensure_obsidian_dir()
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    content = f"""---
tags:
  - trading
  - github_actions_setup
  - sincronizacion_local_obsidian
  - binance
date: {now_str}
---

# 🌐 PASO A PASO: GITHUB ACTIONS (NUBE 24/7) + SINCRONIZACIÓN EN TU OBSIDIAN

> [!NOTE] 💎 ARQUITECTURA HÍBRIDA PERFECTA
> **Última Actualización:** `{now_str}`  
> **Concepto:** La Nube de GitHub opera 24/7 en segundo plano mientras tu PC está apagado. Cuando enciendes tu computador, Obsidian descarga automáticamente los avances para que veas tus reportes al instante.

---

## 🏗️ MAPA DE FUNCIONAMIENTO HÍBRIDO

```
                        [ NUBE GITHUB ACTIONS (24/7) ]
                                       │
           1. Se ejecuta cada 15 minutos en la nube de GitHub
           2. Revisa precios de Binance + Noticias + Indicadores A+
           3. Ejecuta compras/ventas y actualiza los JSON de la matriz
           4. Guarda los avances en tu Repositorio Privado de GitHub
                                       │
                                       ▼
                 [ TU COMPUTADOR (CUANDO ENCIENDES TU PC) ]
                                       │
           1. Obsidian / Git sincroniza automáticamente en segundos
           2. Abre tu panel visual de Obsidian con todas las operaciones
```

---

## 📋 LOS 4 PASOS PARA DEJARLO LISTO (100% GRATIS):

### 1️⃣ Paso 1: Crear un Repositorio Privado en GitHub
- Creamos un repositorio de GitHub **PRIVADO** (nadie en internet puede ver tu código ni tus notas).

### 2️⃣ Paso 2: Guardar tus API Keys en GitHub Encrypted Secrets
- En GitHub, vamos a `Settings` -> `Secrets and variables` -> `Actions`.
- Guardamos las llaves cifradas con seguridad militar:
  - `BINANCE_API_KEY`
  - `BINANCE_API_SECRET`

### 3️⃣ Paso 3: Crear el Archivo Automatizado (`.github/workflows/trading_cron.yml`)
- Este archivo le indica a GitHub que ejecute el motor cuantitativo cada 15 minutos en la nube de forma autónoma.

### 4️⃣ Paso 4: Sincronizar en tu Obsidian al Encender tu PC
- En tu computador, usamos el plugin oficial **Obsidian Git**.
- Al encender tu PC y abrir Obsidian, descarga automáticamente en 2 segundos todas las operaciones ocurridas mientras dormías o tenías el computador apagado.

---

## 🔗 NAVEGACIÓN RÁPIDA
- [[📊_MASTER_DASHBOARD_TRADING|Ver Master Dashboard]]
- [[🚀_Matriz_100_Simulaciones|Ver Matriz de 100 Cuentas]]
- [[☁️_Opciones_Nube_24_7_Gratis_Y_Segura|Ver Opciones de Nube]]
"""

    file_path = os.path.join(OBSIDIAN_FOLDER, "☁️_Paso_A_Paso_GitHub_Actions_Y_Sincronizacion.md")
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)
        
    print(f"GitHub Actions setup guide created at: {file_path}")
    return file_path

if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    generate_github_actions_setup_note()
