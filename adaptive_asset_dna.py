"""
Adaptive Quantum Asset DNA Engine for Binance Crypto Trading
Replaces static blacklists with dynamic behavioral archetypes:
1. HYPER_VOLATILE_SPRINT (Memes / High-Beta: PEPE, DOGE, HEI, PENGU, SHIB, FLOKI, BARD, WIF, BONK, etc.)
2. BLUE_CHIP_CORE (Institutional L1 / Core: BTC, ETH, SOL, BNB, BCH, ADA, AVAX, LINK, LTC, XRP, DOT, NEAR, ATOM, SUI)
3. SECTOR_ROTATION (L2 / DeFi / AI / Gaming: ARB, OP, AAVE, UNI, LDO, FET, TAO, GRT, ZEC, GALA, POL, STRK, INJ, SEI)
4. THIN_BOOK_MICRO (Micro-Caps / Thin Books: MUB, TUT, GPS, DEXE, PROM, ASTER, BICO, EDEN, KAITO, STORJ, JST, DODO, EUL)

Every asset is assigned tailored risk parameters, stop-loss margins, maximum patience windows,
and trailing profit retention rules.
"""

from typing import Dict, Any, Tuple

# ─── 1. EXPLICIT TOKEN TO ARCHETYPE MAPPINGS (TOP 100 CMC OFICIAL) ───────────
# Any token not listed here will be dynamically classified based on ATR, price & volume.

SPRINT_MEME_TOKENS = {
    "PEPE", "PEPEUSDT", "DOGE", "DOGEUSDT", "SHIB", "SHIBUSDT", "FLOKI", "FLOKIUSDT",
    "BONK", "BONKUSDT", "WIF", "WIFUSDT", "PENGU", "PENGUUSDT", "TRUMP", "TRUMPUSDT",
    "PUMP", "PUMPUSDT", "WLFI", "WLFIUSDT", "ASTER", "ASTERUSDT", "BOME", "BOMEUSDT",
    "1000SATS", "1000SATSUSDT", "GIGGLE", "GIGGLEUSDT"
}

BLUE_CHIP_CORE_TOKENS = {
    "BTC", "BTCUSDT", "ETH", "ETHUSDT", "SOL", "SOLUSDT", "BNB", "BNBUSDT",
    "XRP", "XRPUSDT", "ADA", "ADAUSDT", "AVAX", "AVAXUSDT", "SUI", "SUIUSDT",
    "NEAR", "NEARUSDT", "DOT", "DOTUSDT", "ATOM", "ATOMUSDT", "ICP", "ICPUSDT",
    "SEI", "SEIUSDT", "APT", "APTUSDT", "TIA", "TIAUSDT", "LTC", "LTCUSDT",
    "BCH", "BCHUSDT", "ETC", "ETCUSDT", "XLM", "XLMUSDT", "TRX", "TRXUSDT",
    "ALGO", "ALGOUSDT", "HBAR", "HBARUSDT", "LINK", "LINKUSDT", "STX", "STXUSDT"
}

SECTOR_ROTATION_TOKENS = {
    # DeFi / RWA / Yield
    "AAVE", "AAVEUSDT", "UNI", "UNIUSDT", "ENA", "ENAUSDT", "ONDO", "ONDOUSDT",
    "CRV", "CRVUSDT", "JUP", "JUPUSDT", "AERO", "AEROUSDT", "MORPHO", "MORPHOUSDT",
    "CAKE", "CAKEUSDT", "INJ", "INJUSDT", "NEXO", "NEXOUSDT", "SKY", "SKYUSDT",
    # AI & Compute
    "TAO", "TAOUSDT", "FET", "FETUSDT", "RENDER", "RENDERUSDT", "WLD", "WLDUSDT", "FIL", "FILUSDT",
    # Layer 2 & Modular Infra
    "ARB", "ARBUSDT", "ETHFI", "ETHFIUSDT", "ZRO", "ZROUSDT", "POL", "POLUSDT",
    "PYTH", "PYTHUSDT", "STRK", "STRKUSDT", "OP", "OPUSDT", "IMX", "IMXUSDT",
    # Payments / Privacy / Utility
    "DASH", "DASHUSDT", "ZEC", "ZECUSDT", "VET", "VETUSDT", "VIRTUAL", "VIRTUALUSDT", "SUN", "SUNUSDT"
}

THIN_BOOK_MICRO_TOKENS = {
    "JST", "JSTUSDT", "QNT", "QNTUSDT", "ONG", "ONGUSDT", "PROM", "PROMUSDT"
}

# 🚫 BLACKLIST DE FAN TOKENS E ILÍQUIDOS CON LIBROS DE SPOOFING FANTASMA
ILLIQUID_FAN_TOKENS = {
    "SANTOS", "SANTOSUSDT", "ALPINE", "ALPINEUSDT", "LAZIO", "LAZIOUSDT", 
    "PORTO", "PORTOUSDT", "BAR", "BARUSDT", "CITY", "CITYUSDT", "PSG", "PSGUSDT", 
    "ATM", "ATMUSDT", "ASR", "ASRUSDT", "OG", "OGUSDT", "JUV", "JUVUSDT"
}


# ─── 2. ARCHETYPE PROFILES & DNA CONFIGURATION ────────────────────────────────

ARCHETYPE_CONFIGS = {
    "HYPER_VOLATILE_SPRINT": {
        "archetype": "HYPER_VOLATILE_SPRINT",
        "label": "🐆 SPRINT HIPER-VOLÁTIL (Meme / High-Beta)",
        "emoji": "🐆",
        "initial_sl_pct": -1.80,
        "max_stagnation_minutes": 1440,
        "stagnation_decay_minutes": 960,
        "decay_sl_pct": -1.50,
        "phase_2_trigger_pct": 1.80,
        "phase_2_retention_ratio": 0.72,
        "phase_3_trigger_pct": 2.50,
        "phase_3_retention_ratio": 0.75,
        "required_vol_surge_1m": 1.25,
        "required_min_bids_pct": 52.0,
        "trend_ride_enabled": True,
        "wick_slack": 0.65,
        "guideline_for_ai": "RS LEADER / HIGH-BETA. Meta ATR +2.2% a +5.5%, SL ATR -1.2% a -3.2%."
    },
    "BLUE_CHIP_CORE": {
        "archetype": "BLUE_CHIP_CORE",
        "label": "🏛️ BLUE-CHIP INSTITUCIONAL (L1 / Core)",
        "emoji": "🏛️",
        "initial_sl_pct": -1.60,
        "max_stagnation_minutes": 1440,
        "stagnation_decay_minutes": 960,
        "decay_sl_pct": -1.40,
        "phase_2_trigger_pct": 1.50,
        "phase_2_retention_ratio": 0.72,
        "phase_3_trigger_pct": 2.40,
        "phase_3_retention_ratio": 0.75,
        "required_vol_surge_1m": 1.0,
        "required_min_bids_pct": 48.0,
        "trend_ride_enabled": True,
        "wick_slack": 0.60,
        "guideline_for_ai": "CORE LEADER. Meta ATR +2.2% a +5.0%, SL ATR -1.2% a -2.8%."
    },
    "SECTOR_ROTATION": {
        "archetype": "SECTOR_ROTATION",
        "label": "🧩 ROTACIÓN SECTORIAL (L2 / DeFi / AI)",
        "emoji": "🧩",
        "initial_sl_pct": -1.80,
        "max_stagnation_minutes": 1440,
        "stagnation_decay_minutes": 960,
        "decay_sl_pct": -1.50,
        "phase_2_trigger_pct": 1.80,
        "phase_2_retention_ratio": 0.72,
        "phase_3_trigger_pct": 2.50,
        "phase_3_retention_ratio": 0.75,
        "required_vol_surge_1m": 1.25,
        "required_min_bids_pct": 50.0,
        "trend_ride_enabled": True,
        "wick_slack": 0.65,
        "guideline_for_ai": "ROTACIÓN SECTORIAL RS. Meta ATR +2.2% a +6.0%, SL ATR -1.2% a -3.2%."
    },
    "THIN_BOOK_MICRO": {
        "archetype": "THIN_BOOK_MICRO",
        "label": "🎯 MICRO-CAP / LIBRO DELGADO",
        "emoji": "🎯",
        "initial_sl_pct": -1.60,
        "max_stagnation_minutes": 1200,
        "stagnation_decay_minutes": 720,
        "decay_sl_pct": -1.30,
        "phase_2_trigger_pct": 1.40,
        "phase_2_retention_ratio": 0.72,
        "phase_3_trigger_pct": 2.00,
        "phase_3_retention_ratio": 0.75,
        "required_vol_surge_1m": 1.30,
        "required_min_bids_pct": 52.0,
        "trend_ride_enabled": True,
        "wick_slack": 0.60,
        "guideline_for_ai": "LIBRO DELGADO. Exige RS + volumen >= 1.25x."
    }
}






# ─── 3. CLASIFICADOR DINÁMICO DE ADN ──────────────────────────────────────────

def get_asset_dna_archetype(symbol: str, atr_15m_pct: float = None, price: float = 1.0, volume_24h_usd: float = 10000000.0) -> Dict[str, Any]:
    """
    Classifies any crypto symbol into its specialized DNA Archetype.
    1. Checks explicit token registry.
    2. If unlisted, uses volatility (ATR), unit price, and 24h volume to classify dynamically.
    """
    clean_sym = symbol.replace("USDT", "").replace("USDC", "").replace("FDUSD", "").upper()
    
    effective_atr = atr_15m_pct if (atr_15m_pct is not None and atr_15m_pct > 0) else 0.50
    
    # Check explicit mappings
    if clean_sym in ILLIQUID_FAN_TOKENS or symbol in ILLIQUID_FAN_TOKENS:
        config = dict(ARCHETYPE_CONFIGS["THIN_BOOK_MICRO"])
        config["is_blacklisted_fan_token"] = True
        config["symbol"] = symbol
        config["clean_symbol"] = clean_sym
        return config
    elif clean_sym in SPRINT_MEME_TOKENS or symbol in SPRINT_MEME_TOKENS:
        arch_key = "HYPER_VOLATILE_SPRINT"
    elif clean_sym in BLUE_CHIP_CORE_TOKENS or symbol in BLUE_CHIP_CORE_TOKENS:
        arch_key = "BLUE_CHIP_CORE"
    elif clean_sym in SECTOR_ROTATION_TOKENS or symbol in SECTOR_ROTATION_TOKENS:
        arch_key = "SECTOR_ROTATION"
    elif clean_sym in THIN_BOOK_MICRO_TOKENS or symbol in THIN_BOOK_MICRO_TOKENS:
        arch_key = "THIN_BOOK_MICRO"
    else:
        # Dynamic phenotypic classification based on market structure
        if effective_atr >= 0.70 or clean_sym.startswith("1000") or "DOGE" in clean_sym or "PEPE" in clean_sym or "CAT" in clean_sym:
            arch_key = "HYPER_VOLATILE_SPRINT"
        elif price >= 100.0 and volume_24h_usd < 8000000.0:
            arch_key = "THIN_BOOK_MICRO"
        elif volume_24h_usd >= 50000000.0 and effective_atr <= 0.45:
            arch_key = "BLUE_CHIP_CORE"
        else:
            arch_key = "SECTOR_ROTATION"

    config = dict(ARCHETYPE_CONFIGS[arch_key])
    config["symbol"] = symbol
    config["clean_symbol"] = clean_sym
    config["is_blacklisted_fan_token"] = False
    
    # 🚫 VETO ESTRICTO ANTI-ZOMBI Y ANTI-MEGA-CAP PESADA:
    # Para scalping de $15 USD y meta >= +2% diario, activos con ATR < 0.35% o Blue-Chips lentas están descalificados.
    # CRITICAL: When atr_15m_pct is None (pre-MTF first call), do NOT veto — let the pipeline fetch live ATR first.
    is_slow_major = bool(clean_sym in BLUE_CHIP_CORE_TOKENS and effective_atr < 0.40)
    if atr_15m_pct is not None:
        config["is_low_volatility_zombie"] = bool(atr_15m_pct < 0.35 or is_slow_major)
    else:
        config["is_low_volatility_zombie"] = False  # Allow pipeline to fetch live ATR before vetoing
        
    # 🧬 INYECCIÓN DE ADN PERSONALIZADO APRENDIDO (Desde quant_database SQLite):
    try:
        import quant_database
        dna_p = quant_database.get_crypto_dna_profile(symbol)
        if dna_p:
            config["dna_profile"] = dna_p
            config["dna_tier"] = dna_p.get("dna_tier", "BALANCED")
            rec_target = float(dna_p.get("recommended_target_pct", 0.85))
            if 0.70 <= rec_target <= 1.40:
                config["phase_2_trigger_pct"] = rec_target
            if dna_p.get("dna_tier") == "☠️ TÓXICO":
                config["is_toxic_tier"] = True
                config["guideline_for_ai"] = f"⛔ VETO ACTIVO: Token con historial tóxico comprobado en SQLite (WR {dna_p.get('win_rate_pct', 0):.1f}% < 40%)."
            else:
                config["is_toxic_tier"] = False
    except Exception:
        pass

    if config.get("is_toxic_tier", False):
        pass
    elif config.get("is_low_volatility_zombie", False):
        config["guideline_for_ai"] = "⛔ VETO ACTIVO: Volatilidad/Elasticidad insuficiente (ATR 15M < 0.35% o Mega-Cap lenta). Prohibido para scalping spot."
    return config


# ─── 4. CÁLCULO DE TRAILING ESPECÍFICO POR ARQUETIPO ──────────────────────────

def calculate_archetype_trailing(
    archetype_dna: Dict[str, Any],
    highest_pnl_pct: float,
    current_pnl_pct: float,
    holding_minutes: int,
    atr_pct: float = 1.0,
    setup: str = "RS_BREAK",
    sl_pct_override: float = None,
    tp_pct_override: float = None,
) -> Tuple[float, int, str]:
    """Compute unified ATR-scaled trailing floor, phase, and descriptive label.

    Delegates directly to quant_edge_engine.compute_trade_exit_decision so live
    execution, guardian heartbeat, and validated backtests stay identical.
    """
    import quant_edge_engine

    emoji = archetype_dna.get("emoji", "🧬")
    decision = quant_edge_engine.compute_trade_exit_decision(
        highest_pnl_pct=highest_pnl_pct,
        current_pnl_pct=current_pnl_pct,
        atr_pct=max(0.45, float(atr_pct or 1.0)),
        elapsed_minutes=float(holding_minutes or 0),
        setup=setup,
        sl_pct=sl_pct_override,
        tp_pct=tp_pct_override,
    )
    floor_pct = decision["floor_pct"]
    phase = decision["phase"]
    phase_label = f"{emoji} {decision['phase_label']}"
    return floor_pct, phase, phase_label





# ─── 5. VERIFICACIÓN DE ESTANCAMIENTO POR ARQUETIPO ──────────────────────────

def check_archetype_stagnation_exit(
    archetype_dna: Dict[str, Any],
    holding_minutes: int,
    pnl_pct: float,
    phase: int
) -> Tuple[bool, str]:
    """Time-stop verification synchronized with 20h-24h quant horizon (no premature cuts)."""
    max_mins = int(archetype_dna.get("max_stagnation_minutes", 1440))
    if holding_minutes >= max_mins:
        return True, f"⏱️ Time-Stop cuantitativo ({holding_minutes}m >= {max_mins}m, PnL={pnl_pct:+.2f}%). Rotando capital."
    return False, ""


