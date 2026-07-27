import os
import sys
from datetime import datetime

OBSIDIAN_FOLDER = r"C:\Users\hosca\Documents\Antigravity\Obsidian\01_PROYECTOS\BINANCE_QUANT_TRADING"

def create_tutorial():
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    content = f"""---
tags:
  - binance
  - ip_estatica
  - nube_24_7
  - github_actions
date: {now_str}
---

# 🌐 PASO A PASO: IP ESTÁTICA PARA LA NUBE 24/7 EN BINANCE REAL

> [!IMPORTANT] 🎯 OBJETIVO PRINCIPAL
> Garantizar que la Nube de GitHub Actions se conecte a Binance Real las **24 horas del día de forma 100% autónoma con tu PC apagado**, utilizando una **IP Estática Fija** autorizada en tu cuenta de Binance.

---

## 🌐 OPCIÓN 1: WEBSHARE (100% GRATIS DE POR VIDA - PROXY IP ESTÁTICA)

### 📌 Paso 1: Obtener la IP Estática Gratuita (1 minuto)
1. Entra a **[https://www.webshare.io](https://www.webshare.io)** (o **[https://usefixie.com](https://usefixie.com)**).
2. Crea una cuenta gratuita con tu correo.
3. En el panel principal te entregará 10 Proxies con IP Estática Fija gratis.
4. Copia la URL del Proxy que luce así:  
   `http://usuario:contrasena@185.199.108.153:8080`
5. Copia la dirección IP estática (ej: `185.199.108.153`).

---

## 🌐 OPCIÓN 2: REGISTRAR LAS IPS EN BINANCE Y GITHUB SECRETS

### 📌 Paso 2: Registrar las IPs en Binance Real
1. Entra a tu cuenta de Binance -> Gestión de API:  
   👉 **[https://www.binance.com/es/my/settings/api-management](https://www.binance.com/es/my/settings/api-management)**
2. Edita la clave **`HMAC Antigravity`**.
3. En el cuadro de IPs autorizadas, pega la IP estática entregada por Webshare (ej: `185.199.108.153`).
4. Agrega también la IP de tu WiFi actual: `192.100.198.93`.
5. Guarda los cambios.

### 📌 Paso 3: Guardar el Secreto en GitHub Secrets
1. Entra a tu repositorio privado en GitHub:  
   👉 **[https://github.com/oscarhernando4-commits/binance-quant-trading/settings/secrets/actions](https://github.com/oscarhernando4-commits/binance-quant-trading/settings/secrets/actions)**
2. Haz clic en **New repository secret**.
3. Nombre: **`FIXIE_URL`**
4. Valor: Pega tu URL completa del proxy de Webshare (ej: `http://usuario:contrasena@185.199.108.153:8080`).
5. Haz clic en **Add secret**.

---

## 🚀 RESULTADO FINAL:
- GitHub Actions leerá automáticamente el secreto `FIXIE_URL`.
- **100% de las órdenes Spot reales de tu cuenta de $15.00 USDT saldrán siempre a través de la IP estática**.
- La Nube operará las 24 horas del día de forma 100% autónoma con tu computador apagado.

---

## 🔗 NAVEGACIÓN RÁPIDA
- [[📊_MASTER_DASHBOARD_TRADING|Ver Master Dashboard]]
- [[🚀_Matriz_100_Simulaciones|Ver Matriz de 100 Cuentas]]
"""
    file_path = os.path.join(OBSIDIAN_FOLDER, "🌐_Paso_A_Paso_IP_Estatica_Nube_24_7.md")
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Tutorial note updated at: {file_path}")

if __name__ == "__main__":
    sys.stdout.reconfigure(encoding='utf-8')
    create_tutorial()
