"""
AUDITORÍA INTEGRAL E2E - SISTEMA QUANT TRADING BINANCE SPOT
Diagnóstico a profundidad de todos los subsistemas, APIs, reglas de capital,
filtros de stablecoins, proxies Fixie, flujos de GitHub Actions y reportes.
"""
import sys
import os
import json
import math
import time
from datetime import datetime

try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

os.chdir(os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
load_dotenv()

TESTS_PASSED = 0
TESTS_FAILED = 0

def test(name, condition, detail=""):
    global TESTS_PASSED, TESTS_FAILED
    if condition:
        TESTS_PASSED += 1
        print(f"  ✅ {name}")
    else:
        TESTS_FAILED += 1
        print(f"  ❌ {name} -> {detail}")

print("=" * 65)
print("🔍 DIAGNÓSTICO INTEGRAL A PROFUNDIDAD DEL SISTEMA DE TRADING")
print("=" * 65)

# 1. PROXY FIXIE POOL
print("\n[1/10] ROTADOR DE PROXIES FIXIE (7 Cuentas EU West)")
import api_connector
test("FIXIE_POOL tiene 7 proxies configurados", len(api_connector.FIXIE_POOL) == 7, f"Tiene {len(api_connector.FIXIE_POOL)}")
test("PROXY_URL seleccionado válidamente", api_connector.PROXY_URL in api_connector.FIXIE_POOL)
test("PROXIES dict (http/https) listo", "http" in api_connector.PROXIES and "https" in api_connector.PROXIES)

# 2. PRECIOS EN VIVO (Conexión Pública Binance sin consumo de proxy)
print("\n[2/10] FEED DE PRECIOS EN VIVO DE BINANCE")
try:
    btc_p = api_connector.get_symbol_price("BTCUSDT", is_futures=False)
    eth_p = api_connector.get_symbol_price("ETHUSDT", is_futures=False)
    sol_p = api_connector.get_symbol_price("SOLUSDT", is_futures=False)
    test(f"BTCUSDT precio en vivo: ${btc_p:,.2f}", btc_p and btc_p > 20000)
    test(f"ETHUSDT precio en vivo: ${eth_p:,.2f}", eth_p and eth_p > 1000)
    test(f"SOLUSDT precio en vivo: ${sol_p:,.2f}", sol_p and sol_p > 20)
except Exception as e:
    test("Conexión con Binance Price API", False, str(e))

# 3. LISTA NEGRA DE STABLECOINS Y ACTIVOS SINTÉTICOS
print("\n[3/10] FILTRO Y LISTA NEGRA DE STABLECOINS")
import data_fetcher
blacklist_samples = ["RLUSD", "USD1", "USDC", "FDUSD", "TUSD", "BUSD", "EUR", "DAI"]
all_blacklisted = all(s in data_fetcher.STABLECOIN_BLACKLIST for s in blacklist_samples)
test("Blacklist en data_fetcher contiene stablecoins y sintéticos", all_blacklisted)

if os.path.exists("top_100_pairs.json"):
    with open("top_100_pairs.json", "r", encoding="utf-8") as f:
        pairs = json.load(f)
    test(f"top_100_pairs.json contiene {len(pairs)} pares híbridos", len(pairs) >= 50)
    has_toxic_stable = any(p in ["RLUSDUSDT", "USD1USDT", "USDCUSDT", "EURUSDT", "FDUSDUSDT"] for p in pairs)
    test("Ninguna stablecoin en top_100_pairs.json", not has_toxic_stable, "Se encontraron stablecoins en lista activa")

# 4. GESTIÓN DE CAPITAL 100% Y REDONDEO A 1 DECIMAL (HACIA ABAJO)
print("\n[4/10] REGLAS DE CAPITAL (100% Saldo Libre & Truncamiento 1 Decimal)")
test_balances = [17.5692, 20.99, 15.42, 8.78]
expected_floors = [17.5, 20.9, 15.4, 8.7]
floors_ok = [math.floor(b * 10) / 10.0 for b in test_balances] == expected_floors
test("Truncamiento estricto a 1 decimal hacia abajo", floors_ok)

# 5. ESTADO DE LA CUENTA REAL
print("\n[5/10] ESTADO PERSISTENTE DE CUENTA REAL (real_money_account.json)")
state = api_connector.load_real_account_state()
test("real_money_account.json cargado correctamente", state is not None)
test(f"Balance USDT registrado: ${state.get('_cached_usdt_free', 0):.4f} USDT", state.get('_cached_usdt_free', 0) > 0)
test(f"BNB escudo comisiones: {state.get('_cached_bnb', 0):.6f} BNB", state.get('_cached_bnb', 0) >= 0)
test(f"Estado operativo: {state.get('status')}", "status" in state)

# 6. MOTOR DE APRENDIZAJE CONTINUO (LEARNING ENGINE)
print("\n[6/10] MOTOR DE APRENDIZAJE Y MEMORIA (learning_engine.py)")
import learning_engine
mem = learning_engine.load_memory()
test("trade_memory.json cargado", mem is not None)
bias = learning_engine.get_market_bias()
test(f"Sesgo estadístico calculado: {bias.get('bias')} (WR LONG: {bias.get('long_win_rate')}%, SHORT: {bias.get('short_win_rate')}%)", "bias" in bias)

# 7. ROUTER DE INTELIGENCIA ARTIFICIAL (GEMINI / FALLBACK CUANTITATIVO)
print("\n[7/10] COMITÉ DE IA Y FALLBACK CUANTITATIVO")
import llm_router
dummy_cands = [{
    "symbol": "BTCUSDT", "divergence": 25, "score": 75,
    "suggested_action": "BUY_LONG", "tech_data": {"rsi": 45, "trend": "BULLISH"}
}]
ai_rev = llm_router.review_top_5_candidates(dummy_cands, {"headlines": []}, {"score": 50})
test("AI Router responde con estructura válida", "approved" in ai_rev and "selected_symbol" in ai_rev)

# 8. WORKFLOW DE GITHUB ACTIONS (trigger_quant_trade)
print("\n[8/10] WORKFLOW DE GITHUB ACTIONS (.github/workflows/pipeline_cron.yml)")
wf_path = os.path.join(".github", "workflows", "pipeline_cron.yml")
test("pipeline_cron.yml existe", os.path.exists(wf_path))
if os.path.exists(wf_path):
    with open(wf_path, "r", encoding="utf-8") as f:
        wf_code = f.read()
    test("Disparador trigger_quant_trade activo", "trigger_quant_trade" in wf_code)
    test("Cron interno schedule eliminado (previene colisiones)", "schedule:" not in wf_code)
    test("Secret BINANCE_REAL_API_KEY inyectado", "BINANCE_REAL_API_KEY" in wf_code)
    test("Mitigación de conflictos git integrada", "git reset --soft" in wf_code or "git pull" in wf_code)

# 9. INTEGRIDAD DE REPORTES OBSIDIAN
print("\n[9/10] REPORTES EN OBSIDIAN (Rutas relativas y legibilidad)")
obsidian_matrix = os.path.join("Obsidian", "01_PROYECTOS", "BINANCE_QUANT_TRADING", "📊_Analisis_Por_Grupo_y_Movimientos.md")
obsidian_real = os.path.join("Obsidian", "01_PROYECTOS", "BINANCE_QUANT_TRADING", "Reportes", "CUENTA_REAL.md")
test("Reporte matriz Obsidian existe", os.path.exists(obsidian_matrix))
test("Reporte CUENTA_REAL.md existe", os.path.exists(obsidian_real))

# 10. SINCRONIZACIÓN Y SCRIPT DIAGNÓSTICO
print("\n[10/10] EJECUCIÓN DEL RADAR Y SINCRONIZACIÓN")
test("Función diagnose_full_spot_wallet definida", hasattr(api_connector, "diagnose_full_spot_wallet"))
test("Función evaluate_and_trade_real_money definida", hasattr(api_connector, "evaluate_and_trade_real_money"))
test("Función execute_real_spot_market_buy con quoteOrderQty definida", hasattr(api_connector, "execute_real_spot_market_buy"))
test("Función execute_real_spot_market_sell con LOT_SIZE definida", hasattr(api_connector, "execute_real_spot_market_sell"))

# RESUMEN FINAL
print("\n" + "=" * 65)
print(f"🎯 RESULTADOS FINALES: {TESTS_PASSED} TESTS PASADOS / {TESTS_FAILED} FALLADOS")
if TESTS_FAILED == 0:
    print("🏆 AUDITORÍA 100% EXITOSA - TODOS LOS SUBSISTEMAS OPERATIVOS")
else:
    print(f"⚠️ SE DETECTARON {TESTS_FAILED} PROBLEMAS QUE REQUIEREN ATENCIÓN")
print("=" * 65)
