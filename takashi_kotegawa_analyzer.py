import os
import json
import sys
from datetime import datetime

OBSIDIAN_FOLDER = r"C:\Users\hosca\Documents\Antigravity\Obsidian\01_PROYECTOS\BINANCE_QUANT_TRADING"

CRYPTO_ASSET_PROFILES = {
    # TIER 1: MEGA-CAPS (Baja volatilidad relativa, desviaciones más ajustadas)
    "BTCUSDT": {"tier": "TIER_1_MEGACAP", "ma_dev_buy": 3.5, "ma_dev_sell": 4.0, "atr_multiplier": 1.2, "category": "Líder de Mercado"},
    "ETHUSDT": {"tier": "TIER_1_MEGACAP", "ma_dev_buy": 4.0, "ma_dev_sell": 4.5, "atr_multiplier": 1.3, "category": "Líder Smart Contracts"},
    
    # TIER 2: MAJOR ALTCOINS (Volatilidad media-alta)
    "SOLUSDT": {"tier": "TIER_2_MAJORS", "ma_dev_buy": 6.0, "ma_dev_sell": 7.0, "atr_multiplier": 1.6, "category": "Layer-1 Alta Velocidad"},
    "BNBUSDT": {"tier": "TIER_2_MAJORS", "ma_dev_buy": 4.5, "ma_dev_sell": 5.5, "atr_multiplier": 1.4, "category": "Ecosistema Exchange"},
    "XRPUSDT": {"tier": "TIER_2_MAJORS", "ma_dev_buy": 6.5, "ma_dev_sell": 7.5, "atr_multiplier": 1.7, "category": "Pagos Institucionales"},
    "ADAUSDT": {"tier": "TIER_2_MAJORS", "ma_dev_buy": 5.5, "ma_dev_sell": 6.5, "atr_multiplier": 1.5, "category": "Layer-1 Académico"},
    "LINKUSDT": {"tier": "TIER_2_MAJORS", "ma_dev_buy": 5.5, "ma_dev_sell": 6.5, "atr_multiplier": 1.5, "category": "Red de Oráculos"},
    "AVAXUSDT": {"tier": "TIER_2_MAJORS", "ma_dev_buy": 6.5, "ma_dev_sell": 7.5, "atr_multiplier": 1.7, "category": "Subredes Enterprise"},
    "DOTUSDT": {"tier": "TIER_2_MAJORS", "ma_dev_buy": 6.0, "ma_dev_sell": 7.0, "atr_multiplier": 1.6, "category": "Interoperabilidad"},
    "LTCUSDT": {"tier": "TIER_2_MAJORS", "ma_dev_buy": 5.0, "ma_dev_sell": 6.0, "atr_multiplier": 1.4, "category": "Dinero Digital"},
    "UNIUSDT": {"tier": "TIER_2_MAJORS", "ma_dev_buy": 6.5, "ma_dev_sell": 7.5, "atr_multiplier": 1.7, "category": "Líder DEX DeFi"},
    
    # TIER 3: HIGH-BETA & MEMES (Alta volatilidad, requieren sobreventas extremas)
    "NEARUSDT": {"tier": "TIER_3_HIGH_BETA", "ma_dev_buy": 8.0, "ma_dev_sell": 9.5, "atr_multiplier": 2.0, "category": "IA & Sharding"},
    "DOGEUSDT": {"tier": "TIER_3_HIGH_BETA", "ma_dev_buy": 8.5, "ma_dev_sell": 10.0, "atr_multiplier": 2.2, "category": "Memecoin Principal"},
    "ATOMUSDT": {"tier": "TIER_3_HIGH_BETA", "ma_dev_buy": 7.5, "ma_dev_sell": 8.5, "atr_multiplier": 1.8, "category": "Cosmos SDK Hub"},
    "ETCUSDT": {"tier": "TIER_3_HIGH_BETA", "ma_dev_buy": 7.0, "ma_dev_sell": 8.0, "atr_multiplier": 1.7, "category": "PoW Tradicional"},
    "FILUSDT": {"tier": "TIER_3_HIGH_BETA", "ma_dev_buy": 8.5, "ma_dev_sell": 10.0, "atr_multiplier": 2.1, "category": "Almacenamiento Descentralizado"},
    "APTUSDT": {"tier": "TIER_3_HIGH_BETA", "ma_dev_buy": 8.0, "ma_dev_sell": 9.5, "atr_multiplier": 2.0, "category": "Layer-1 Move Engine"},
    "TRXUSDT": {"tier": "TIER_3_HIGH_BETA", "ma_dev_buy": 4.0, "ma_dev_sell": 5.0, "atr_multiplier": 1.3, "category": "Red de Stablecoins"},
    "ARBUSDT": {"tier": "TIER_3_HIGH_BETA", "ma_dev_buy": 8.5, "ma_dev_sell": 10.0, "atr_multiplier": 2.1, "category": "Layer-2 Optimistic"},
    "OPUSDT": {"tier": "TIER_3_HIGH_BETA", "ma_dev_buy": 8.5, "ma_dev_sell": 10.0, "atr_multiplier": 2.1, "category": "Layer-2 Superchain"}
}

def ensure_obsidian_dir():
    if not os.path.exists(OBSIDIAN_FOLDER):
        os.makedirs(OBSIDIAN_FOLDER, exist_ok=True)

def generate_takashi_kotegawa_note():
    ensure_obsidian_dir()
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    profiles_table = ""
    for sym, prof in CRYPTO_ASSET_PROFILES.items():
        profiles_table += f"| **{sym}** | `{prof['tier']}` | `{prof['category']}` | **`-{prof['ma_dev_buy']}%`** | **`+{prof['ma_dev_sell']}%`** | `{prof['atr_multiplier']}x` |\n"

    content = f"""---
tags:
  - trading
  - estrategia_takashi_kotegawa_bnf
  - yakubari_rebotes_extremos
  - perfiles_personalizados_por_cripto
  - binance
date: {now_str}
---

# 🧠 ESTRATEGIA DE TAKASHI KOTEGAWA (BNF): ADAPTACIÓN CRIPTO QUANT

> [!NOTE] 🇯🇵 DE $13,000 A MÁS DE $150 MILLONES DE DÓLARES (TAKASHI KOTEGAWA - BNF)
> **Última Actualización:** `{now_str}`  
> **Análisis del Video:** [Ver Análisis del Trader Legendario Takashi Kotegawa (BNF)](https://www.youtube.com/watch?v=Udj8ohmL7xE)  
> **Concepto Clave:** Cada activo financiero tiene su propia "personalidad" de volatilidad. NO se puede usar la misma regla para Bitcoin que para una Altcoin de alta volatilidad.

---

## 🎯 1. PRINCIPIOS FUNDAMENTALES DE TAKASHI KOTEGAWA (BNF)

1. 📏 **Desviación de Media Móvil (25 Periodos):**  
   BNF no miraba noticias ni fundamentos de empresas. Calculaba la distancia porcentual de desviación entre el precio actual y la **Media Móvil de 25 Periodos (25-MA)**.
2. 📐 **Parámetros Específicos por Tipo de Activo:**  
   - Acciones de Servicios: Esperaba caídas del **-20%** por debajo de la media.
   - Acciones Tecnológicas: Esperaba caídas del **-30%** por debajo de la media.
   - Small Caps (Pequeña Capitalización): Esperaba caídas profundas de entre **-28% y -60%**.
3. 📉 **Estrategia Yakubari (Rebote por Sobreventa Extrema en Pánico):**  
   En mercados bajistas o caídas bruscas, capturaba el rebote violento hacia la media (Mean Reversion) obteniendo retornos rápidos de **+3% a +10%**.
4. 📈 **Estrategia Shunbari (Seguimiento de Tendencia Fuera de Rangos):**  
   En tendencias alcistas sanas, compraba los retrocesos suaves a la media móvil para surfear el movimiento impulsivo.

---

## 🛡️ 2. NUESAS ADAPTACIÓN CRIPTO QUANT (PLAN ÚNICO POR CRIPTOMONEDA)

Hemos dividido las 20 criptomonedas de nuestra Matriz en **3 Niveles de Volatilidad (Tiers)** con umbrales de Desviación de Media Móvil ajustados específicamente para cada moneda:

### 📋 Matriz de Perfiles Personalizados por Criptomoneda:

| Criptomoneda | Nivel de Volatilidad | Categoría de Activo | Desviación Compra (Bajadas) | Desviación Venta (Subidas) | Multiplicador ATR |
| :--- | :---: | :--- | :---: | :---: | :---: |
{profiles_table}

---

## 📈 3. ESTRATEGIA PARA SUBIDAS Y BAJADAS (ALCISTA Y BAJISTA)

### 🟢 A) Estrategia para Mercados Alcistas / Subidas Fuertes:
- **Regla:** Comprar cuando el precio retroceda a la EMA de 25 periodos en 15m con volumen bajo (retroceso de salud) y el Score de Confluencia sea **>= 80 Puntos**.
- **Objetivo:** Trailing Stop dinámico para capturar el impulso de **+3% a +6%**.

### 🔴 B) Estrategia para Mercados Bajistas / Caídas Flash:
- **Regla:** Cuando el mercado sufra un pánico masivo y el precio se desvíe por debajo de la EMA de 25 periodos alcanzando el umbral de sobreventa extrema de su perfil (ej: `-3.5%` en BTC o `-8.5%` en NEAR), el bot ejecuta una **Compra de Rebote Violento (Yakubari Bounce)**.
- **Objetivo:** Capturar el rebote elástico hacia la media con un **Take Profit rápido garantizado de +3.0%**.

---

## 🔗 NAVEGACIÓN RÁPIDA
- [[📊_MASTER_DASHBOARD_TRADING|Ver Master Dashboard]]
- [[🚀_Matriz_100_Simulaciones|Ver Matriz de 100 Cuentas]]
- [[🧠_Estrategia_Kyle_Chisamore_Y_Wyckoff|Ver Estrategia Kyle Chisamore]]
- [[🏛️_Analisis_Historial_Y_Noticias_Cripto|Ver Análisis Histórico Profundo]]
- [[🏛️_Auditoria_Arquitectura_Ecosistema_Trading|Ver Auditoría del Ecosistema]]
"""

    file_path = os.path.join(OBSIDIAN_FOLDER, "🧠_Estrategia_Takashi_Kotegawa_BNF_Cripto.md")
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)
        
    print(f"Takashi Kotegawa strategy note created at: {file_path}")
    return file_path

if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    generate_takashi_kotegawa_note()
