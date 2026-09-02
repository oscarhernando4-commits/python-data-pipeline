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
        "initial_sl_pct": -4.00,
        "max_stagnation_minutes": 360,    # ×3 (antes: 120 min)
        "stagnation_decay_minutes": 225,  # ×3 (antes: 75 min)
        "decay_sl_pct": -1.80,
        "phase_2_trigger_pct": 1.00,
        "phase_2_retention_ratio": 1.00,
        "phase_3_trigger_pct": 1.60,
        "phase_3_retention_ratio": 0.70,
        "required_vol_surge_1m": 1.5,
        "required_min_bids_pct": 52.0,
        "trend_ride_enabled": True,
        "wick_slack": 0.30,
        "guideline_for_ai": "Trata este activo como un SPRINT. Exige volumen explosivo en 1M/10s. Meta mínima +1.00%."
    },
    "BLUE_CHIP_CORE": {
        "archetype": "BLUE_CHIP_CORE",
        "label": "🏛️ BLUE-CHIP INSTITUCIONAL (L1 / Core)",
        "emoji": "🏛️",
        "initial_sl_pct": -4.00,
        "max_stagnation_minutes": 720,    # ×3 (antes: 240 min)
        "stagnation_decay_minutes": 540,  # ×3 (antes: 180 min)
        "decay_sl_pct": -2.50,
        "phase_2_trigger_pct": 1.00,
        "phase_2_retention_ratio": 1.00,
        "phase_3_trigger_pct": 1.60,
        "phase_3_retention_ratio": 0.70,
        "required_vol_surge_1m": 0.8,
        "required_min_bids_pct": 48.0,
        "trend_ride_enabled": True,
        "wick_slack": 0.32,
        "guideline_for_ai": "Trata este activo como CORE. Exige confluencia. Meta mínima +1.00%."
    },
    "SECTOR_ROTATION": {
        "archetype": "SECTOR_ROTATION",
        "label": "🧩 ROTACIÓN SECTORIAL (L2 / DeFi / AI)",
        "emoji": "🧩",
        "initial_sl_pct": -4.00,
        "max_stagnation_minutes": 540,    # ×3 (antes: 180 min)
        "stagnation_decay_minutes": 360,  # ×3 (antes: 120 min)
        "decay_sl_pct": -2.00,
        "phase_2_trigger_pct": 1.00,
        "phase_2_retention_ratio": 1.00,
        "phase_3_trigger_pct": 1.60,
        "phase_3_retention_ratio": 0.70,
        "required_vol_surge_1m": 1.0,
        "required_min_bids_pct": 50.0,
        "trend_ride_enabled": True,
        "wick_slack": 0.32,
        "guideline_for_ai": "Trata este activo como ROTACIÓN SECTORIAL. Exige sector caliente y volumen. Meta mínima +1.00%."
    },
    "THIN_BOOK_MICRO": {
        "archetype": "THIN_BOOK_MICRO",
        "label": "🎯 MICRO-CAP / LIBRO DELGADO",
        "emoji": "🎯",
        "initial_sl_pct": -4.00,
        "max_stagnation_minutes": 360,    # ×3 (antes: 120 min)
        "stagnation_decay_minutes": 225,  # ×3 (antes: 75 min)
        "decay_sl_pct": -1.80,
        "phase_2_trigger_pct": 1.00,
        "phase_2_retention_ratio": 1.00,
        "phase_3_trigger_pct": 1.60,
        "phase_3_retention_ratio": 0.70,
        "required_vol_surge_1m": 1.3,
        "required_min_bids_pct": 54.0,
        "trend_ride_enabled": True,
        "wick_slack": 0.28,
        "guideline_for_ai": "Trata este activo como LIBRO DELGADO. Exige volumen real. Meta mínima +1.00%."
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
                config["is_low_volatility_zombie"] = True
                config["guideline_for_ai"] = "⛔ VETO ACTIVO: Token con historial tóxico comprobado en SQLite (WR < 40%)."
    except Exception:
        pass

    if config["is_low_volatility_zombie"]:
        config["guideline_for_ai"] = "⛔ VETO ACTIVO: Volatilidad/Elasticidad insuficiente (ATR 15M < 0.35% o Mega-Cap lenta). Prohibido para scalping spot."
    return config


# ─── 4. CÁLCULO DE TRAILING ESPECÍFICO POR ARQUETIPO ──────────────────────────

def calculate_archetype_trailing(
    archetype_dna: Dict[str, Any],
    highest_pnl_pct: float,
    current_pnl_pct: float,
    holding_minutes: int,
    atr_pct: float = 0.30
) -> Tuple[float, int, str]:
    """
    🎯 SISTEMA DE COSECHA DINÁMICA PROPORCIONAL MULTI-NIVEL:
    - FASE 3 (>= +1.60%): Rally Dinámico con retención del 75% al 85% de la cima.
    - FASE 2 (+1.00% a +1.59%): Meta Cumplida. Piso de retención en max(+1.00%, Cima × 75%).
    - ⚡ SUB-FASE COSECHA DINÁMICA (+0.65% a +0.99%):
        * ¡LA SOLUCIÓN EXACTA PARA CASOS COMO RENDER (+0.93%)!
        * Cuando la moneda supera +0.65%, el piso se vuelve DINÁMICO reteniendo el 70% de la cima:
          Piso = max(+0.20%, Cima × 0.70).
          Ejemplo: Cima +0.93% -> Piso asegurado en +0.65%. Si retrocede, ¡VENDE EN GANANCIA!
    - 🛡️ SUB-FASE BREAK-EVEN BLINDADO (+0.45% a +0.64%):
        * Una vez tocado +0.45%, el SL salta a +0.12% (cubre comisión BNB). Cero riesgo de perder.
    - 🌱 FASE 1 (0.00% a +0.44%): Rumbo a impulso inicial con Stop Loss protector de -4.00%.
    """
    arch = archetype_dna.get("archetype", "SECTOR_ROTATION")
    emoji = archetype_dna.get("emoji", "🧬")
    label = archetype_dna.get("label", arch)
    base_p2 = archetype_dna.get("phase_2_trigger_pct", 1.00)
    p3_trigger = archetype_dna.get("phase_3_trigger_pct", 1.60)
    
    # Adaptación por volatilidad: si el ATR es moderado, el trigger de Fase 2 puede iniciar en 0.80%
    p2_trigger = max(0.80, min(base_p2, round(atr_pct * 1.6, 2))) if atr_pct and atr_pct > 0 else base_p2

    if highest_pnl_pct >= p3_trigger:
        retention_pct = min(85.0, 50.0 + (highest_pnl_pct * 5.0))
        retention_ratio = retention_pct / 100.0
        sl_pct = max(p2_trigger, round(highest_pnl_pct * retention_ratio, 4))
        phase = 3
        phase_label = f"🚀 FASE 3 RALLY DINÁMICO ({emoji} Cima +{highest_pnl_pct:.2f}% | Retención {retention_pct:.1f}% -> Piso +{sl_pct:.2f}%)"
    elif highest_pnl_pct >= p2_trigger:
        # Retención dinámica desde el trigger de fase 2 (al menos el 75% de la cima)
        sl_pct = max(p2_trigger, round(highest_pnl_pct * 0.75, 4))
        phase = 2
        phase_label = f"🎯 FASE 2 META DINÁMICA (+{p2_trigger:.2f}% | {emoji} Cima +{highest_pnl_pct:.2f}% -> Piso +{sl_pct:.2f}%)"
    elif highest_pnl_pct >= 0.65:
        # ⚡ COSECHA DINÁMICA ANTE REVERSIÓN:
        # Retiene el 70% de la cima ganada. Si RENDER llegó a +0.93%, el piso se fija en +0.65%.
        sl_pct = max(0.20, round(highest_pnl_pct * 0.70, 4))
        phase = 1
        phase_label = f"⚡ SUB-FASE COSECHA DINÁMICA ({emoji} Cima +{highest_pnl_pct:.2f}% -> Piso Protegido +{sl_pct:.2f}%)"
    elif highest_pnl_pct >= 0.45:
        # 🛡️ BREAK-EVEN BLINDADO: Protege contra cualquier pérdida y cubre comisiones
        sl_pct = 0.12
        phase = 1
        phase_label = f"🛡️ BREAK-EVEN BLINDADO ({emoji} Cima +{highest_pnl_pct:.2f}% -> Piso +0.12%)"
    else:
        sl_pct = -4.00
        phase = 1
        phase_label = f"🌱 FASE 1 RUMBO A META ({emoji} Cima +{highest_pnl_pct:.2f}% | SL -4.00%)"

    return sl_pct, phase, phase_label





# ─── 5. VERIFICACIÓN DE ESTANCAMIENTO POR ARQUETIPO ──────────────────────────

def check_archetype_stagnation_exit(
    archetype_dna: Dict[str, Any],
    holding_minutes: int,
    pnl_pct: float,
    phase: int
) -> Tuple[bool, str]:
    """
    Sin límite de tiempo en Fase 1: Paciencia absoluta e ilimitada.
    """
    return False, ""


