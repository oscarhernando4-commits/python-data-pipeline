import os
import json

EXTREME_EVENTS_FILE = os.path.join(os.path.dirname(__file__), "extreme_events_db.json")

# Pre-populated Historical Extreme Volatility Reference Database for Top Cryptos
DEFAULT_EXTREME_EVENTS = {
    "BTCUSDT": {
        "max_15m_crash_pct": -12.5,
        "max_15m_pump_pct": +14.2,
        "extreme_patterns": [
            "Cascada de Liquidaciones masivas cuando RSI 15M cae de 20 y volumen supera 4.5x.",
            "Trampa de Toros Wyckoff Upthrust tras consolidación de 4 horas cerca de ATH.",
            "Rebote violento en forma de V cuando Fear & Greed cae a Miedo Extremo (<18)."
        ]
    },
    "ETHUSDT": {
        "max_15m_crash_pct": -15.8,
        "max_15m_pump_pct": +18.0,
        "extreme_patterns": [
            "Desplome por Liquidación Gas Surge cuando los Futuros sufren colateralización extrema.",
            "Rally parabólico de altcoins cuando ETH/BTC supera la EMA200 de 4H."
        ]
    },
    "BNBUSDT": {
        "max_15m_crash_pct": -10.0,
        "max_15m_pump_pct": +12.5,
        "extreme_patterns": [
            "Resiliencia extrema por utilidad de comisiones y quema trimestral de tokens.",
            "Fuerte rebote institucional cuando el precio testea la EMA200 diaria."
        ]
    },
    "SOLUSDT": {
        "max_15m_crash_pct": -22.0,
        "max_15m_pump_pct": +25.0,
        "extreme_patterns": [
            "Alta volatilidad beta: Movimientos amplificados de 2x a 3x respecto a BTC.",
            "Ruptura de rango de 4H respaldada por volumen superior a 3.8x desata squeezes."
        ]
    }
}

def load_extreme_events_db():
    if os.path.exists(EXTREME_EVENTS_FILE):
        try:
            with open(EXTREME_EVENTS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    save_extreme_events_db(DEFAULT_EXTREME_EVENTS)
    return DEFAULT_EXTREME_EVENTS

def save_extreme_events_db(data):
    try:
        with open(EXTREME_EVENTS_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"Error saving extreme events DB: {e}")

def get_symbol_extreme_context(symbol):
    """
    Retrieves the historical extreme volatility patterns and crash/pump limits for a symbol.
    """
    db = load_extreme_events_db()
    data = db.get(symbol, {
        "max_15m_crash_pct": -15.0,
        "max_15m_pump_pct": +15.0,
        "extreme_patterns": [
            "Volatilidad estándar de altcoin: Atento a cascadas de liquidación y rupturas de canal."
        ]
    })
    
    summary = (
        f"Eventos Extremos Históricos de {symbol}: "
        f"Máx Caída 15M: {data['max_15m_crash_pct']}%, Máx Pump 15M: +{data['max_15m_pump_pct']}%. "
        f"Patrones Extremos Registrados: {'; '.join(data['extreme_patterns'])}"
    )
    return summary

if __name__ == "__main__":
    print(get_symbol_extreme_context("BTCUSDT"))
