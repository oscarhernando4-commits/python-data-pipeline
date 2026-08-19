import datetime

# 1. SESSIONS dict mapping session names to UTC start/end hours, labels, signal_multiplier, and blackout bool
SESSIONS = {
    "ASIAN_DEAD_ZONE": {"start": 0, "end": 4, "label": "Asian Early Session (Asian High-Beta)", "signal_multiplier": 0.85, "blackout": False},
    "ASIAN_MORNING": {"start": 4, "end": 8, "label": "Asian Morning (Tokyo/Singapore Active)", "signal_multiplier": 0.95, "blackout": False},
    "LONDON_OPEN": {"start": 8, "end": 12, "label": "London Open (High Vol)", "signal_multiplier": 1.15, "blackout": False},
    "LONDON_LUNCH": {"start": 12, "end": 14, "label": "London Lunch / Pre-NYSE (Med Vol)", "signal_multiplier": 1.00, "blackout": False},
    "NYSE_OPEN": {"start": 14, "end": 18, "label": "NYSE Open (Max Vol)", "signal_multiplier": 1.30, "blackout": False},
    "NYSE_LUNCH": {"start": 18, "end": 21, "label": "NYSE Lunch / Close (Med Vol)", "signal_multiplier": 1.00, "blackout": False},
    "US_OVERNIGHT": {"start": 21, "end": 24, "label": "US Evening / Pacific Session", "signal_multiplier": 0.90, "blackout": False},
}

# 2. HOURLY_PUMP_MULTIPLIERS dict with hours 0-23 mapping to floats
HOURLY_PUMP_MULTIPLIERS = {
    0: 0.85, 1: 0.85, 2: 0.90, 3: 0.90, 4: 0.90, 5: 0.95, 6: 0.95, 7: 1.00,
    8: 1.10, 9: 1.15, 10: 1.20, 11: 1.20, 12: 1.10, 13: 1.05,
    14: 1.25, 15: 1.35, 16: 1.30, 17: 1.25, 18: 1.10, 19: 1.00, 20: 0.95,
    21: 0.90, 22: 0.90, 23: 0.85
}

# 3. TOKEN_PEAK_HOURS dict
TOKEN_PEAK_HOURS = {
    "LINK": [8, 9, 10, 14, 15],
    "AAVE": [14, 15, 16],
    "UNI": [14, 15, 16],
    "SOL": [2, 3, 4, 14, 15],
    "ETH": [8, 9, 14, 15, 16],
    "ADA": [4, 5, 6, 14],
    "ATOM": [8, 9, 14],
    "DOT": [8, 9, 14],
    "XRP": [1, 2, 3, 14],
    "AVAX": [14, 15, 16],
    "SUI": [2, 3, 14],
    "HBAR": [8, 9, 14],
    "ZEC": [14, 15],
    "BCH": [8, 9, 14],
    "BNB": [2, 3, 4, 8],
    "TON": [8, 9, 10],
    "KAS": [14, 15]
}

# 4. get_current_session(utc_hour=None)
def get_current_session(utc_hour=None):
    if utc_hour is None:
        utc_hour = datetime.datetime.utcnow().hour
        
    session_name = "UNKNOWN"
    session_info = {"label": "Unknown", "signal_multiplier": 1.0, "blackout": False}
    
    for name, info in SESSIONS.items():
        if info["start"] <= utc_hour < info["end"]:
            session_name = name
            session_info = info
            break
            
    return {
        "session_name": session_name,
        "session_label": session_info["label"],
        "utc_hour": utc_hour,
        "signal_multiplier": session_info["signal_multiplier"],
        "is_blackout": session_info["blackout"],
        "hourly_multiplier": HOURLY_PUMP_MULTIPLIERS.get(utc_hour, 1.0)
    }

# 5. get_token_time_score(symbol, utc_hour=None)
def get_token_time_score(symbol, utc_hour=None):
    if utc_hour is None:
        utc_hour = datetime.datetime.utcnow().hour
        
    is_weekend = datetime.datetime.utcnow().weekday() >= 5
    
    session_data = get_current_session(utc_hour)
    hourly_mult = session_data["hourly_multiplier"]
    
    is_token_peak_hour = False
    token_base = symbol.replace("USDT", "")
    if token_base in TOKEN_PEAK_HOURS and utc_hour in TOKEN_PEAK_HOURS[token_base]:
        is_token_peak_hour = True
        
    peak_bonus = 0.15 if is_token_peak_hour else 0.0
    weekend_penalty = -0.20 if is_weekend else 0.0
    
    final_time_multiplier = hourly_mult + peak_bonus + weekend_penalty
    
    # Clamp 0.20-1.50
    final_time_multiplier = max(0.20, min(1.50, final_time_multiplier))
    
    is_blackout_hour = session_data["is_blackout"]
    hard_veto_entry = True if (is_blackout_hour and final_time_multiplier < 0.50) else False
    
    explanation = f"Hour {utc_hour} UTC ({session_data['session_label']}). Base Mult: {hourly_mult:.2f}."
    if is_token_peak_hour:
        explanation += f" Token {token_base} Peak Bonus (+0.15)."
    if is_weekend:
        explanation += f" Weekend Penalty (-0.20)."
        
    return {
        "final_time_multiplier": final_time_multiplier,
        "is_blackout_hour": is_blackout_hour,
        "hard_veto_entry": hard_veto_entry,
        "is_token_peak_hour": is_token_peak_hour,
        "is_weekend": is_weekend,
        "explanation": explanation
    }

# 6. apply_time_score_to_signal(base_score, symbol, utc_hour=None)
def apply_time_score_to_signal(base_score, symbol, utc_hour=None):
    time_info = get_token_time_score(symbol, utc_hour)
    time_multiplier = time_info["final_time_multiplier"]
    
    time_adjusted_score = base_score * time_multiplier
    hard_veto = time_info["hard_veto_entry"]
    
    should_trade = (time_adjusted_score >= 55) and not hard_veto
    confidence_adjustment = time_adjusted_score - base_score
    
    return {
        "original_score": base_score,
        "time_adjusted_score": time_adjusted_score,
        "time_multiplier": time_multiplier,
        "time_info": time_info,
        "should_trade": should_trade,
        "confidence_adjustment": confidence_adjustment
    }
