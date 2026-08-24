"""
Volume Delta Precision Engine — Sub-Second Entry/Exit Timing
Analyzes aggressive Taker Buy vs Taker Sell volume in real-time
to anticipate price moves 1-5 seconds before they happen.
isBuyerMaker=False -> Aggressive BUY (green bar) -> Bullish
isBuyerMaker=True  -> Aggressive SELL (red bar)  -> Bearish
"""
import time
import requests

_session = requests.Session()
_session.headers.update({"User-Agent": "Mozilla/5.0"})

MIRRORS = [
    "https://data-api.binance.vision/api/v3/aggTrades",
    "https://api1.binance.com/api/v3/aggTrades",
    "https://api.binance.com/api/v3/aggTrades",
]


def _fetch_recent_agg_trades(symbol: str, limit: int = 200) -> list:
    params = {"symbol": symbol, "limit": limit}
    for url in MIRRORS:
        try:
            res = _session.get(url, params=params, timeout=4)
            if res.status_code == 200:
                data = res.json()
                if isinstance(data, list) and len(data) > 0:
                    return data
        except Exception:
            continue
    return []


def get_volume_delta_signal(symbol: str, window_seconds: int = 30) -> dict:
    """
    Computes real-time Volume Delta over the last N seconds.

    Returns:
      entry_approved     -> True when aggressive buy takers dominate
      exit_signal        -> True when aggressive sell takers flood in
      strong_buy         -> True on explosive green spike (buy_ratio >= 62%)
      delta_acceleration -> How fast momentum is building (recent vs older window)
      signal_label       -> Human-readable description of flow state
    """
    trades = _fetch_recent_agg_trades(symbol, limit=200)
    if not trades:
        return _neutral_result(symbol)

    now_ms = int(time.time() * 1000)
    cutoff_ms = now_ms - (window_seconds * 1000)
    window_trades = [t for t in trades if int(t["T"]) >= cutoff_ms]
    if len(window_trades) < 3:
        window_trades = trades[-30:]

    # Split into older half and recent half to detect acceleration
    mid = max(1, len(window_trades) // 2)
    older_trades = window_trades[:mid]
    recent_trades = window_trades[mid:]

    def compute_sides(trade_list):
        buy_v = sum(float(t["p"]) * float(t["q"]) for t in trade_list if not t.get("m", True))
        sell_v = sum(float(t["p"]) * float(t["q"]) for t in trade_list if t.get("m", True))
        return buy_v, sell_v

    buy_vol, sell_vol = compute_sides(window_trades)
    buy_recent, sell_recent = compute_sides(recent_trades)
    buy_older, sell_older = compute_sides(older_trades)

    total_vol = buy_vol + sell_vol
    if total_vol < 0.01:
        return _neutral_result(symbol)

    buy_ratio = round((buy_vol / total_vol) * 100.0, 1)
    sell_ratio = round(100.0 - buy_ratio, 1)
    delta_usdt = round(buy_vol - sell_vol, 2)

    # Delta acceleration: how much stronger is recent buying vs older?
    total_recent = buy_recent + sell_recent
    total_older = buy_older + sell_older
    buy_ratio_recent = (buy_recent / total_recent * 100) if total_recent > 0 else 50.0
    buy_ratio_older = (buy_older / total_older * 100) if total_older > 0 else 50.0
    delta_acceleration = round(buy_ratio_recent - buy_ratio_older, 1)

    # ── Entry Signals ──────────────────────────────────────────────────────
    # STRONG BUY: green bars dominating >= 62% AND momentum building
    # MODERATE BUY: green bars >= 56% (entry allowed with other confirmations)
    strong_buy = buy_ratio >= 62.0 and delta_acceleration >= 0.0
    moderate_buy = buy_ratio >= 56.0
    entry_approved = strong_buy or moderate_buy

    # ── Exit Signals ───────────────────────────────────────────────────────
    # SELL WAVE: red bars >= 58% of flow, OR sudden acceleration of selling
    sell_wave = buy_ratio <= 42.0
    sell_accelerating = delta_acceleration <= -8.0
    exit_signal = sell_wave or (sell_ratio >= 55.0 and sell_accelerating)

    # ── Human label ────────────────────────────────────────────────────────
    delta_sign = "+" if delta_usdt >= 0 else ""
    accel_sign = "+" if delta_acceleration >= 0 else ""
    if buy_ratio >= 68.0:
        label = "COMPRA AGRESIVA EXPLOSIVA"
    elif strong_buy:
        label = "Flujo Comprador Fuerte"
    elif moderate_buy:
        label = "Presion Compradora Moderada"
    elif exit_signal:
        label = "OLA VENDEDORA"
    else:
        label = "Flujo Equilibrado"

    signal_label = (
        f"{label} | Buy={buy_ratio:.0f}% Sell={sell_ratio:.0f}%"
        f" | Delta={delta_sign}{delta_usdt:,.0f} USDT"
        f" | Accel={accel_sign}{delta_acceleration:.1f}%"
    )

    return {
        "symbol": symbol,
        "buy_vol_usdt": round(buy_vol, 2),
        "sell_vol_usdt": round(sell_vol, 2),
        "delta_usdt": delta_usdt,
        "buy_ratio_pct": buy_ratio,
        "sell_ratio_pct": sell_ratio,
        "delta_acceleration": delta_acceleration,
        "entry_approved": entry_approved,
        "exit_signal": exit_signal,
        "strong_buy": strong_buy,
        "sell_wave": sell_wave,
        "trade_count": len(window_trades),
        "window_seconds": window_seconds,
        "signal_label": signal_label,
    }


def _neutral_result(symbol: str) -> dict:
    return {
        "symbol": symbol,
        "buy_vol_usdt": 0.0,
        "sell_vol_usdt": 0.0,
        "delta_usdt": 0.0,
        "buy_ratio_pct": 50.0,
        "sell_ratio_pct": 50.0,
        "delta_acceleration": 0.0,
        "entry_approved": False,
        "exit_signal": False,
        "strong_buy": False,
        "sell_wave": False,
        "trade_count": 0,
        "window_seconds": 30,
        "signal_label": "Sin datos de flujo disponibles",
    }


if __name__ == "__main__":
    import sys
    sym = sys.argv[1] if len(sys.argv) > 1 else "BTCUSDT"
    r = get_volume_delta_signal(sym, window_seconds=30)
    print(f"\n=== VOLUME DELTA: {sym} (ultimos 30s) ===")
    for k, v in r.items():
        print(f"  {k}: {v}")
