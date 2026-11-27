"""Quantitative Dual-Regime Edge Engine (Validated across 125D 1H & 30D 1m Binance Klines).

Implements strictly causal multi-timeframe market regime detection, Relative Strength
Leader Breakouts (Spot LONG), Decoupled Super-Leaders (Spot LONG), Bear Breakdown
Shorts (Futures SHORT when enabled), and ATR-scaled trailing/stop/target exit logic.
"""
import math
import time
from typing import Any, Dict, List, Optional, Tuple


# Default fee rates (round-trip %):
# Spot with BNB 25% discount: 0.075% * 2 = 0.15%
# Spot without BNB: 0.10% * 2 = 0.20%
# Futures USDT-M taker: ~0.05% * 2 = 0.10% (+ small funding margin -> 0.12% conservative)
SPOT_FEE_BNB_PCT = 0.15
SPOT_FEE_STD_PCT = 0.20
FUTURES_FEE_PCT = 0.12

# Universe liquidity cap / high-slippage tokens kept out by structural liquidity & spread rules
DEFAULT_SLIPPAGE_PCT = 0.05


def parse_binance_klines(raw_klines: List[Any], only_closed: bool = True, interval_ms: int = 3600000, now_ms: Optional[int] = None) -> List[List[float]]:
    """Normalize Binance /klines array rows into [ts_open, o, h, l, c, v, qv, tb] floats."""
    if not raw_klines:
        return []
    cur_ms = int(now_ms if now_ms is not None else time.time() * 1000)
    out: List[List[float]] = []
    seen = set()
    for row in raw_klines:
        try:
            ts = int(row[0])
            if ts in seen:
                continue
            if only_closed and (ts + interval_ms - 1) > cur_ms:
                continue
            seen.add(ts)
            if len(row) >= 11:
                # Raw Binance kline: [openTime, o, h, l, c, v, closeTime, qv, n, tb_base, tb_quote, ignore]
                out.append([
                    ts, float(row[1]), float(row[2]), float(row[3]), float(row[4]),
                    float(row[5]), float(row[7]), float(row[10])
                ])
            elif len(row) >= 8:
                out.append([
                    ts, float(row[1]), float(row[2]), float(row[3]), float(row[4]),
                    float(row[5]), float(row[6]), float(row[7])
                ])
        except (TypeError, ValueError, IndexError):
            continue
    out.sort(key=lambda x: x[0])
    return out


def resample_1h_to_4h(kls_1h: List[List[float]], require_complete_4h: bool = True) -> List[List[float]]:
    """Aggregate normalized 1H candles into chronological 4H bars."""
    if not kls_1h:
        return []
    buckets: Dict[int, List[float]] = {}
    counts: Dict[int, int] = {}
    for k in kls_1h:
        ts, o, h, l, c, v, qv, tb = k
        bt = (int(ts) // 14400000) * 14400000
        if bt not in buckets:
            buckets[bt] = [bt, o, h, l, c, v, qv, tb]
            counts[bt] = 1
        else:
            b = buckets[bt]
            b[2] = max(b[2], h)
            b[3] = min(b[3], l)
            b[4] = c
            b[5] += v
            b[6] += qv
            b[7] += tb
            counts[bt] += 1
    out = []
    ordered_ts = sorted(buckets.keys())
    for idx, bt in enumerate(ordered_ts):
        # Only keep incomplete tail 4h bucket when explicitly requested
        if require_complete_4h and idx == len(ordered_ts) - 1 and counts[bt] < 4:
            continue
        out.append(buckets[bt])
    return out


def _ema(values: List[float], period: int) -> List[float]:
    if not values:
        return []
    k = 2.0 / (period + 1.0)
    s = values[0]
    out = [s] * len(values)
    for i, x in enumerate(values):
        s = x * k + s * (1.0 - k)
        out[i] = s
    return out


def build_indicators(kls: List[List[float]]) -> Optional[Dict[str, List[float]]]:
    """Compute causal Wilder RSI(14), ATR%(14), EMA(9,21,50,200), VolSurge(20), TakerBuy%, and OBV."""
    n = len(kls)
    if n < 30:
        return None
    ts = [int(k[0]) for k in kls]
    o = [float(k[1]) for k in kls]
    h = [float(k[2]) for k in kls]
    l = [float(k[3]) for k in kls]
    c = [float(k[4]) for k in kls]
    v = [float(k[5]) for k in kls]
    qv = [float(k[6]) for k in kls]
    tb = [float(k[7]) for k in kls]

    rsi = [50.0] * n
    gains = [0.0] * n
    losses = [0.0] * n
    for i in range(1, n):
        diff = c[i] - c[i - 1]
        if diff > 0:
            gains[i] = diff
        else:
            losses[i] = -diff
    ag = sum(gains[1:15]) / 14.0
    al = sum(losses[1:15]) / 14.0
    for i in range(15, n):
        ag = (ag * 13.0 + gains[i]) / 14.0
        al = (al * 13.0 + losses[i]) / 14.0
        rsi[i] = 100.0 if al == 0.0 else 100.0 - 100.0 / (1.0 + ag / al)

    atr_pct = [1.0] * n
    trs = [h[0] - l[0]] + [max(h[i] - l[i], abs(h[i] - c[i - 1]), abs(l[i] - c[i - 1])) for i in range(1, n)]
    atr_val = sum(trs[1:15]) / 14.0
    for i in range(15, n):
        atr_val = (atr_val * 13.0 + trs[i]) / 14.0
        atr_pct[i] = (atr_val / c[i] * 100.0) if c[i] > 0 else 1.0

    e9 = _ema(c, 9)
    e21 = _ema(c, 21)
    e50 = _ema(c, 50)
    e200 = _ema(c, 200)

    obv = [0.0] * n
    for i in range(1, n):
        if c[i] > c[i - 1]:
            obv[i] = obv[i - 1] + v[i]
        elif c[i] < c[i - 1]:
            obv[i] = obv[i - 1] - v[i]
        else:
            obv[i] = obv[i - 1]

    vs = [1.0] * n
    tbuy = [50.0] * n
    for i in range(20, n):
        avg_v = sum(v[i - 20:i]) / 20.0
        vs[i] = (v[i] / avg_v) if avg_v > 0 else 1.0
        tbuy[i] = (tb[i] / qv[i] * 100.0) if qv[i] > 0 else 50.0

    return {
        "ts": ts, "o": o, "h": h, "l": l, "c": c, "v": v, "qv": qv,
        "rsi": rsi, "atr": atr_pct, "e9": e9, "e21": e21, "e50": e50, "e200": e200,
        "vs": vs, "tbuy": tbuy, "obv": obv,
    }


def detect_macro_regime(btc_1h: Optional[Dict[str, List[float]]], btc_4h: Optional[Dict[str, List[float]]]) -> Dict[str, Any]:
    """Classify BTC multi-timeframe macro regime as BULL, TRANSITION, or BEAR_CRASH."""
    if not btc_1h or not btc_4h or len(btc_1h["c"]) < 60 or len(btc_4h["c"]) < 50:
        return {"regime": "TRANSITION", "is_bull": False, "is_bear": False, "btc_1h_ret": 0.0, "btc_rsi_4h": 50.0}

    bi = len(btc_1h["c"]) - 1
    b4 = len(btc_4h["c"]) - 1

    c1 = btc_1h["c"][bi]
    o1 = btc_1h["o"][bi]
    btc_1h_ret = ((c1 - o1) / o1 * 100.0) if o1 > 0 else 0.0

    is_bull = (
        btc_4h["e21"][b4] > btc_4h["e50"][b4]
        and c1 > btc_1h["e50"][bi]
        and c1 > btc_1h["e21"][bi]
    )
    is_bear = (
        btc_4h["e21"][b4] < btc_4h["e50"][b4]
        and btc_4h["c"][b4] < btc_4h["e50"][b4]
        and btc_4h["rsi"][b4] <= 47.0
        and c1 < btc_1h["e50"][bi]
        and btc_1h["e21"][bi] < btc_1h["e50"][bi]
    )

    if is_bull:
        regime = "BULL"
    elif is_bear:
        regime = "BEAR_CRASH"
    else:
        regime = "TRANSITION"

    return {
        "regime": regime,
        "is_bull": is_bull,
        "is_bear": is_bear,
        "btc_price": round(c1, 2),
        "btc_1h_ret": round(btc_1h_ret, 3),
        "btc_rsi_4h": round(btc_4h["rsi"][b4], 2),
        "btc_rsi_1h": round(btc_1h["rsi"][bi], 2),
    }


def compute_net_pnl_after_fees(
    gross_pnl_pct: float,
    has_bnb_fee_shield: bool = True,
    is_futures: bool = False,
) -> Tuple[float, float]:
    """Return (net_pnl_pct, round_trip_fee_pct) strictly deducting Binance fees."""
    if is_futures:
        fee_pct = FUTURES_FEE_PCT
    elif has_bnb_fee_shield:
        fee_pct = SPOT_FEE_BNB_PCT
    else:
        fee_pct = SPOT_FEE_STD_PCT
    net = round(float(gross_pnl_pct) - fee_pct, 4)
    return net, fee_pct


def compute_trade_exit_decision(
    highest_pnl_pct: float,
    current_pnl_pct: float,
    atr_pct: float = 1.0,
    elapsed_minutes: float = 0.0,
    setup: str = "RS_BREAK",
    sl_pct: Optional[float] = None,
    tp_pct: Optional[float] = None,
    max_hold_hours: Optional[float] = None,
) -> Dict[str, Any]:
    """Unified ATR-scaled SL, dynamic profit-locking Trailing Floor, TP, and Time-Stop.

    Aligned identically with 1-minute validated DUAL V1 + Decoupled Super-Leaders.
    """
    atr = max(0.45, min(2.30, float(atr_pct or 1.0)))

    if setup == "DECOUPLED_LEADER":
        eff_sl = float(sl_pct) if sl_pct is not None else -max(1.20, min(2.80, round(atr * 1.6, 2)))
        eff_tp = float(tp_pct) if tp_pct is not None else max(2.20, min(5.00, round(atr * 2.8, 2)))
        eff_max_h = float(max_hold_hours or 20.0)
        high_trig, low_trig = 2.00, 1.40
        high_floor = round(highest_pnl_pct * 0.72, 4)
        low_floor = round(max(0.80, highest_pnl_pct - 0.60), 4)
    elif setup == "BEAR_SHORT":
        eff_sl = float(sl_pct) if sl_pct is not None else -max(1.20, min(3.00, round(atr * 1.7, 2)))
        eff_tp = float(tp_pct) if tp_pct is not None else max(2.20, min(5.50, round(atr * 3.0, 2)))
        eff_max_h = float(max_hold_hours or 24.0)
        high_trig, low_trig = 2.40, 1.50
        high_floor = round(highest_pnl_pct * 0.72, 4)
        low_floor = round(max(0.85, highest_pnl_pct - 0.65), 4)
    else:  # RS_BREAK default
        eff_sl = float(sl_pct) if sl_pct is not None else -max(1.20, min(3.20, round(atr * 1.8, 2)))
        eff_tp = float(tp_pct) if tp_pct is not None else max(2.20, min(6.00, round(atr * 3.2, 2)))
        eff_max_h = float(max_hold_hours or 24.0)
        high_trig, low_trig = 2.50, 1.80
        high_floor = round(highest_pnl_pct * 0.72, 4)
        low_floor = round(max(1.00, highest_pnl_pct - 0.75), 4)

    floor = eff_sl
    phase = 1
    phase_label = f"F1 Proteccion ATR (Cima +{highest_pnl_pct:.2f}% | SL {eff_sl:.2f}%)"

    if highest_pnl_pct >= high_trig:
        floor = max(floor, high_floor)
        phase = 3
        phase_label = f"F3 Cosecha Alta (Cima +{highest_pnl_pct:.2f}% | Piso +{floor:.2f}%)"
    elif highest_pnl_pct >= low_trig:
        floor = max(floor, low_floor)
        phase = 2
        phase_label = f"F2 Ganancia Asegurada (Cima +{highest_pnl_pct:.2f}% | Piso +{floor:.2f}%)"

    should_exit = False
    reason = ""
    if current_pnl_pct <= floor:
        should_exit = True
        if floor > 0:
            reason = f"Trailing Floor +{floor:.2f}% (Cima +{highest_pnl_pct:.2f}%, Actual {current_pnl_pct:+.2f}%)"
        else:
            reason = f"Stop Loss ATR {eff_sl:.2f}% (Actual {current_pnl_pct:+.2f}%)"
    elif current_pnl_pct >= eff_tp:
        should_exit = True
        reason = f"Take Profit ATR +{eff_tp:.2f}% (Actual {current_pnl_pct:+.2f}%)"
    elif elapsed_minutes >= eff_max_h * 60.0:
        should_exit = True
        reason = f"Time-Stop {eff_max_h:.0f}h (Actual {current_pnl_pct:+.2f}%)"

    return {
        "should_exit": should_exit,
        "reason": reason,
        "floor_pct": round(floor, 4),
        "sl_pct": round(eff_sl, 4),
        "tp_pct": round(eff_tp, 4),
        "max_hold_hours": eff_max_h,
        "phase": phase,
        "phase_label": phase_label,
    }


def evaluate_asset_signal(
    symbol: str,
    sym_1h: Optional[Dict[str, List[float]]],
    sym_4h: Optional[Dict[str, List[float]]],
    btc_1h: Optional[Dict[str, List[float]]],
    btc_4h: Optional[Dict[str, List[float]]],
    allow_short: bool = False,
    cooldown_map: Optional[Dict[str, float]] = None,
    now_sec: Optional[float] = None,
) -> Optional[Dict[str, Any]]:
    """Evaluate a symbol for RS_BREAK (LONG), DECOUPLED_LEADER (LONG), or BEAR_SHORT (SHORT)."""
    if symbol == "BTCUSDT" or not sym_1h or not sym_4h or not btc_1h or not btc_4h:
        return None
    if len(sym_1h["c"]) < 60 or len(sym_4h["c"]) < 50 or len(btc_1h["c"]) < 60 or len(btc_4h["c"]) < 50:
        return None

    si = len(sym_1h["c"]) - 1
    s4 = len(sym_4h["c"]) - 1
    bi = len(btc_1h["c"]) - 1

    # Skip stale symbol feeds lagging BTC bar close
    if abs(sym_1h["ts"][si] - btc_1h["ts"][bi]) > 3600000:
        return None

    atr = float(sym_1h["atr"][si])
    if not (0.45 <= atr <= 2.30):
        return None

    macro = detect_macro_regime(btc_1h, btc_4h)
    cur_sec = float(now_sec if now_sec is not None else time.time())
    cd_map = cooldown_map or {}

    rs8 = ((sym_1h["c"][si] - sym_1h["c"][si - 8]) / sym_1h["c"][si - 8]) - (
        (btc_1h["c"][bi] - btc_1h["c"][bi - 8]) / btc_1h["c"][bi - 8]
    )
    rs24 = ((sym_1h["c"][si] - sym_1h["c"][si - 24]) / sym_1h["c"][si - 24]) - (
        (btc_1h["c"][bi] - btc_1h["c"][bi - 24]) / btc_1h["c"][bi - 24]
    )

    def _not_cooled(side_str: str) -> bool:
        key = f"{symbol}_{side_str}"
        return float(cd_map.get(key, 0.0)) <= cur_sec

    def _eval_rs_breakout(setup_name: str, vs_min: float, tbuy_min: float, rs8_min: float, rs24_min: float) -> Optional[Dict[str, Any]]:
        """Shared 8H Relative Strength leader breakout evaluator for RS_BREAK and EARLY_RECOVERY."""
        if not (
            sym_1h["c"][si] > sym_1h["e50"][si]
            and sym_1h["e21"][si] > sym_1h["e50"][si]
            and sym_1h["obv"][si] > sym_1h["obv"][si - 6]
        ):
            return None
        prev_hi = max(sym_1h["h"][si - 8:si])
        body_pct = (sym_1h["c"][si] - sym_1h["o"][si]) / sym_1h["o"][si] * 100.0 if sym_1h["o"][si] > 0 else 99.0
        if not (
            sym_1h["c"][si] > prev_hi
            and sym_1h["vs"][si] >= vs_min
            and sym_1h["tbuy"][si] >= tbuy_min
            and sym_1h["rsi"][si] <= 72.0
            and body_pct <= atr * 2.2
            and rs8 >= rs8_min
            and rs24 >= rs24_min
        ):
            return None
        ex = compute_trade_exit_decision(0.0, 0.0, atr, 0.0, setup="RS_BREAK")
        rank = rs8 * 100.0 + sym_1h["tbuy"][si] * 0.20
        score = int(max(85, min(99, 86 + rs8 * 180 + max(0.0, sym_1h["tbuy"][si] - 54.0) * 0.4)))
        return {
            "symbol": symbol,
            "side": "LONG",
            "setup": setup_name,
            "score": score,
            "quant_rank": round(rank, 4),
            "price": round(sym_1h["c"][si], 8),
            "atr_pct": round(atr, 4),
            "sl_pct": ex["sl_pct"],
            "tp_pct": ex["tp_pct"],
            "max_hold_hours": ex["max_hold_hours"],
            "rs_8h_pct": round(rs8 * 100.0, 2),
            "rs_24h_pct": round(rs24 * 100.0, 2),
            "rsi_1h": round(sym_1h["rsi"][si], 2),
            "vol_surge": round(sym_1h["vs"][si], 2),
            "taker_buy_pct": round(sym_1h["tbuy"][si], 2),
            "obv_rising": True,
            "macro_regime": macro["regime"],
        }

    # 1. BULL: Relative Strength Leader 8H Breakout (Spot LONG)
    if macro["is_bull"] and _not_cooled("LONG"):
        res_bull = _eval_rs_breakout("RS_BREAK", vs_min=1.25, tbuy_min=54.0, rs8_min=0.014, rs24_min=0.015)
        if res_bull:
            return res_bull

    # 2. TRANSITION / NON-BULL: Decoupled 4H Super-Leader (Spot LONG)
    if not macro["is_bull"] and _not_cooled("LONG"):
        if (
            macro["btc_1h_ret"] >= -0.20
            and sym_4h["e21"][s4] > sym_4h["e50"][s4]
            and sym_4h["c"][s4] > sym_4h["e50"][s4]
            and sym_1h["obv"][si] > sym_1h["obv"][si - 6]
        ):
            prev_hi = max(sym_1h["h"][si - 12:si])
            if (
                sym_1h["c"][si] > prev_hi
                and rs24 >= 0.050
                and sym_1h["vs"][si] >= 1.40
                and sym_1h["tbuy"][si] >= 56.0
                and sym_1h["rsi"][si] <= 70.0
            ):
                ex = compute_trade_exit_decision(0.0, 0.0, atr, 0.0, setup="DECOUPLED_LEADER")
                rank = rs24 * 100.0
                score = int(max(86, min(99, 86 + rs24 * 100 + max(0.0, sym_1h["tbuy"][si] - 56.0) * 0.4)))
                return {
                    "symbol": symbol,
                    "side": "LONG",
                    "setup": "DECOUPLED_LEADER",
                    "score": score,
                    "quant_rank": round(rank, 4),
                    "price": round(sym_1h["c"][si], 8),
                    "atr_pct": round(atr, 4),
                    "sl_pct": ex["sl_pct"],
                    "tp_pct": ex["tp_pct"],
                    "max_hold_hours": ex["max_hold_hours"],
                    "rs_8h_pct": round(rs8 * 100.0, 2),
                    "rs_24h_pct": round(rs24 * 100.0, 2),
                    "rsi_1h": round(sym_1h["rsi"][si], 2),
                    "vol_surge": round(sym_1h["vs"][si], 2),
                    "taker_buy_pct": round(sym_1h["tbuy"][si], 2),
                    "obv_rising": True,
                    "macro_regime": macro["regime"],
                }

    # 2b. TRANSITION EARLY RECOVERY: Post-crash rebound with aligned BTC 4H & 1H momentum (Spot LONG)
    if (not macro["is_bull"]) and (not macro["is_bear"]) and _not_cooled("LONG"):
        b4 = len(btc_4h["c"]) - 1
        btc_1h_up = btc_1h["c"][bi] > btc_1h["e21"][bi] and btc_1h["e21"][bi] > btc_1h["e50"][bi]
        btc_4h_rec = btc_4h["c"][b4] > btc_4h["e50"][b4] and btc_4h["rsi"][b4] >= 55.0
        if btc_1h_up and btc_4h_rec and sym_4h["c"][s4] > sym_4h["e50"][s4]:
            res_rec = _eval_rs_breakout("EARLY_RECOVERY", vs_min=1.35, tbuy_min=56.0, rs8_min=0.015, rs24_min=0.020)
            if res_rec:
                return res_rec

    # 3. BEAR CRASH: Weak Laggard 8H Breakdown (Futures SHORT, only when Futures enabled)
    if allow_short and macro["is_bear"] and _not_cooled("SHORT"):
        if (
            sym_4h["c"][s4] < sym_4h["e50"][s4]
            and sym_1h["c"][si] < sym_1h["e50"][si]
            and sym_1h["e21"][si] < sym_1h["e50"][si]
            and sym_1h["obv"][si] < sym_1h["obv"][si - 6]
        ):
            prev_lo = min(sym_1h["l"][si - 8:si])
            body_pct = (sym_1h["o"][si] - sym_1h["c"][si]) / sym_1h["o"][si] * 100.0 if sym_1h["o"][si] > 0 else 99.0
            if (
                sym_1h["c"][si] < prev_lo
                and sym_1h["vs"][si] >= 1.25
                and sym_1h["tbuy"][si] <= 47.0
                and sym_1h["rsi"][si] >= 28.0
                and body_pct <= atr * 2.2
                and rs8 <= -0.010
            ):
                ex = compute_trade_exit_decision(0.0, 0.0, atr, 0.0, setup="BEAR_SHORT")
                rank = (-rs8) * 100.0 + (50.0 - sym_1h["tbuy"][si]) * 0.30
                score = int(max(86, min(99, 86 + (-rs8) * 180 + max(0.0, 47.0 - sym_1h["tbuy"][si]) * 0.4)))
                return {
                    "symbol": symbol,
                    "side": "SHORT",
                    "setup": "BEAR_SHORT",
                    "score": score,
                    "quant_rank": round(rank, 4),
                    "price": round(sym_1h["c"][si], 8),
                    "atr_pct": round(atr, 4),
                    "sl_pct": ex["sl_pct"],
                    "tp_pct": ex["tp_pct"],
                    "max_hold_hours": ex["max_hold_hours"],
                    "rs_8h_pct": round(rs8 * 100.0, 2),
                    "rs_24h_pct": round(rs24 * 100.0, 2),
                    "rsi_1h": round(sym_1h["rsi"][si], 2),
                    "vol_surge": round(sym_1h["vs"][si], 2),
                    "taker_buy_pct": round(sym_1h["tbuy"][si], 2),
                    "obv_rising": False,
                    "macro_regime": macro["regime"],
                }

    return None
