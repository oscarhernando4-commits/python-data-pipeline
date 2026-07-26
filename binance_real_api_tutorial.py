import os
import json
import sys
from datetime import datetime

OBSIDIAN_FOLDER = r"C:\Users\hosca\Documents\Antigravity\Obsidian\01_PROYECTOS\BINANCE_QUANT_TRADING"

def ensure_obsidian_dir():
    if not os.path.exists(OBSIDIAN_FOLDER):
        os.makedirs(OBSIDIAN_FOLDER, exist_ok=True)

def generate_binance_real_api_tutorial_note():
    ensure_obsidian_dir()
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    content = f"""---
tags:
  - trading
  - tutorial_api_binance_real
  - permisos_y_restriccion_ip
  - binance
date: {now_str}
---

# 🔐 TUTORIAL PASO A PASO: CONFIGURACIÓN SEGURA DE API BINANCE REAL

> [!IMPORTANT] 🛡️ REGLA DE ORO DE SEGURIDAD PARA DINERO REAL
> **Última Actualización:** `{now_str}`  
> **Objetivo:** Permitir que el bot de la nube compre y venda en Binance Spot Real sin riesgo de retiro de dinero.

---

## 📋 PASO A PASO DE CONFIGURACIÓN

### 📍 Paso 1: Ingresar a la Gestión de API en Binance Real
1. Inicia sesión en tu cuenta oficial de Binance ([https://www.binance.com](https://www.binance.com)).
2. Haz clic en el ícono de tu **Perfil / Avatar** (esquina superior derecha).
3. Selecciona la opción **Gestión de API** (*API Management*).

---

### 📍 Paso 2: Crear la Nueva Clave de API
1. Haz clic en el botón amarillo **Crear API** (*Create API*).
2. Elige la opción **Generada por el sistema** (*System generated*).
3. Asigna un nombre a la clave, ej: `Bot_Quant_Real_2026`.
4. Completa la verificación de seguridad 2FA (código por correo y autenticador).

---

### 📍 Paso 3: Configuración de PERMISOS (Punto A)
1. Haz clic en **Editar restricciones** (*Edit restrictions*).
2. Marca exactamente las siguientes casillas:
   - ✅ **Lectura habilitada (*Enable Reading*):** Activada por defecto.
   - ✅ **Habilitar Trading Spot y Margin (*Enable Spot & Margin Trading*):** **MARCAR ESTA CASILLA**.
   - 🔴 **HABILITAR RETIROS (*Enable Withdrawals*): DEJAR 100% DESMARCADA (DESACTIVADA).**

> [!CAUTION] 🚨 GARANTÍA DE SEGURIDAD ABSOLUTA
> Al mantener la casilla **HABILITAR RETIROS DESACTIVADA**, es **100% IMPOSIBLE** que alguien en la nube o en internet retire fondos de tu cuenta. Solo se pueden comprar y vender criptomonedas Spot dentro de tu propia cuenta de Binance.

---

### 📍 Paso 4: Configuración de RESTRICCIÓN DE IP (Punto B)
1. En la sección **Restricciones de acceso IP** (*IP access restrictions*), selecciona la opción:
   - 🔘 **Sin restricción (Menos seguro) / Unrestricted (Less Secure)**.
2. **¿Por qué esta opción?**  
   Porque los servidores en la nube de GitHub Actions cambian dinámicamente de dirección IP en cada ejecución de 5 minutos.
3. **¿Es seguro?**  
   **SÍ, 100% SEGURO**, gracias a que en el Paso 3 desactivamos la opción de **RETIROS**.

---

### 📍 Paso 5: Copiar y Guardar las Claves
1. Copia tu **API Key** y tu **Secret Key**.
2. Guardaremos estas llaves en tus **GitHub Secrets** (`BINANCE_REAL_API_KEY` y `BINANCE_REAL_API_SECRET`) cuando estés listo para operar con dinero real.

---

## 🔗 NAVEGACIÓN RÁPIDA
- [[📊_MASTER_DASHBOARD_TRADING|Ver Master Dashboard]]
- [[🚀_Matriz_100_Simulaciones|Ver Matriz de 100 Cuentas]]
- [[☁️_Paso_A_Paso_GitHub_Actions_Y_Sincronizacion|Ver Guía de GitHub Actions]]
- [[🛡️_Plan_Transicion_Dinero_Real_Y_Testnet|Ver Plan de Transición]]
"""

    file_path = os.path.join(OBSIDIAN_FOLDER, "🔐_Tutorial_Paso_A_Paso_API_Binance_Real.md")
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)
        
    print(f"Binance real API tutorial note created at: {file_path}")
    return file_path

if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    generate_binance_real_api_tutorial_note()
