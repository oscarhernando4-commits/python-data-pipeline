import os
import json
from datetime import datetime

MEMORY_FILE = os.path.join(os.path.dirname(__file__), "time_series_history.json")

def load_time_series_history():
    if os.path.exists(MEMORY_FILE):
        try:
            with open(MEMORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {}

def save_time_series_history(history):
    try:
        with open(MEMORY_FILE, "w", encoding="utf-8") as f:
            json.dump(history, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"Error saving time series memory: {e}")

def record_5m_reading(symbol, price, score, rsi, macd, volume_surge, wyckoff, news_headline=None, fear_greed_score=50):
    """
    Records a 5-minute reading snapshot for a symbol, retaining the last 12 cycles (1 hour)
    to enable multi-cycle trend pattern recognition and news-correlation learning.
    """
    history = load_time_series_history()
    if symbol not in history:
        history[symbol] = []
        
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    snapshot = {
        "timestamp": now_str,
        "price": price,
        "score": score,
        "rsi": rsi,
        "macd": macd,
        "volume_surge": volume_surge,
        "wyckoff": wyckoff,
        "news_headline": news_headline,
        "fear_greed": fear_greed_score
    }
    
    history[symbol].append(snapshot)
    # Retain the last 12 snapshots (1 hour of 5m readings)
    history[symbol] = history[symbol][-12:]
    save_time_series_history(history)
    return history[symbol]

def get_multi_cycle_pattern_summary(symbol):
    """
    Analyzes the rolling 1-hour 5-minute time-series history for a symbol
    to calculate momentum acceleration, whale accumulation velocity, and news impact.
    """
    history = load_time_series_history().get(symbol, [])
    if len(history) < 2:
        return "Historial reciente insuficiente (Primeras lecturas)."
        
    first = history[0]
    last = history[-1]
    
    price_change_pct = ((last["price"] - first["price"]) / first["price"]) * 100.0
    score_trend = last["score"] - first["score"]
    avg_volume_surge = sum(s["volume_surge"] for s in history) / len(history)
    
    summary = (
        f"Historial 1h ({len(history)} ciclos 5M): Cambio Precio: {price_change_pct:+.2f}%, "
        f"Evolución Score: {score_trend:+d} Pts, Promedio Volumen: {avg_volume_surge:.1f}x. "
        f"Patrón: {'Acumulación Intensa de Ballenas' if score_trend > 10 and avg_volume_surge > 1.5 else 'Distribución o Rango'}"
    )
    return summary

if __name__ == "__main__":
    record_5m_reading("BTCUSDT", 67500.0, 88, 58.5, "Bullish Cross", 2.1, "Wyckoff Spring", "Institutional inflows surge", 65)
    print(get_multi_cycle_pattern_summary("BTCUSDT"))
