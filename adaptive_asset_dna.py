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

# ─── 1. EXPLICIT TOKEN TO ARCHETYPE MAPPINGS ──────────────────────────────────
# Any token not listed here will be dynamically classified based on ATR, price & volume.

SPRINT_MEME_TOKENS = {
    "PEPE", "PEPEUSDT", "DOGE", "DOGEUSDT", "SHIB", "SHIBUSDT", "FLOKI", "FLOKIUSDT",
    "BONK", "BONKUSDT", "WIF", "WIFUSDT", "BARD", "BARDUSDT", "PENGU", "PENGUUSDT",
    "HEI", "HEIUSDT", "MEME", "MEMEUSDT", "PEOPLE", "PEOPLEUSDT", "NEIRO", "NEIROUSDT",
    "1000SATS", "1000SATSUSDT", "GIGGLE", "GIGGLEUSDT", "TURBO", "TURBOUSDT", "BOME", "BOMEUSDT",
    "1000RATS", "1000RATSUSDT", "1000CAT", "1000CATUSDT", "MYRO", "MYROUSDT", "POPCAT", "POPCATUSDT",
    "TRUMP", "TRUMPUSDT", "WLFI", "WLFIUSDT"
}

BLUE_CHIP_CORE_TOKENS = {
    "BTC", "BTCUSDT", "ETH", "ETHUSDT", "SOL", "SOLUSDT", "BNB", "BNBUSDT",
    "BCH", "BCHUSDT", "ADA", "ADAUSDT", "AVAX", "AVAXUSDT", "LINK", "LINKUSDT",
    "LTC", "LTCUSDT", "XRP", "XRPUSDT", "DOT", "DOTUSDT", "NEAR", "NEARUSDT",
    "ATOM", "ATOMUSDT", "SUI", "SUIUSDT", "TON", "TONUSDT", "TRX", "TRXUSDT"
}

SECTOR_ROTATION_TOKENS = {
    # DeFi / Oracle
    "AAVE", "AAVEUSDT", "UNI", "UNIUSDT", "LDO", "LDOUSDT", "MKR", "MKRUSDT",
    "CRV", "CRVUSDT", "SNX", "SNXUSDT", "DYDX", "DYDXUSDT", "PENDLE", "PENDLEUSDT",
    "SUSHI", "SUSHIUSDT", "1INCH", "1INCHUSDT", "COMP", "COMPUSDT", "API3", "API3USDT",
    # Layer 2
    "ARB", "ARBUSDT", "OP", "OPUSDT", "POL", "POLUSDT", "MATIC", "MATICUSDT",
    "IMX", "IMXUSDT", "STRK", "STRKUSDT", "ZK", "ZKUSDT", "LRC", "LRCUSDT",
    # AI & Compute
    "FET", "FETUSDT", "TAO", "TAOUSDT", "GRT", "GRTUSDT", "WLD", "WLDUSDT",
    "AGIX", "AGIXUSDT", "OCEAN", "OCEANUSDT", "NMR", "NMRUSDT",
    # Gaming / Metaverse
    "GALA", "GALAUSDT", "SAND", "SANDUSDT", "MANA", "MANAUSDT", "AXS", "AXSUSDT",
    # High-Beta L1s / Infrastructure
    "INJ", "INJUSDT", "SEI", "SEIUSDT", "TIA", "TIAUSDT", "APT", "APTUSDT",
    "ZEC", "ZECUSDT", "FIL", "FILUSDT", "AR", "ARUSDT", "KAS", "KASUSDT"
}

THIN_BOOK_MICRO_TOKENS = {
    "MUB", "MUBUSDT", "TUT", "TUTUSDT", "GPS", "GPSUSDT", "DEXE", "DEXEUSDT",
    "PROM", "PROMUSDT", "ASTER", "ASTERUSDT", "BICO", "BICOUSDT", "EDEN", "EDENUSDT",
    "KAITO", "KAITOUSDT", "STORJ", "STORJUSDT", "JST", "JSTUSDT", "DODO", "DODOUSDT",
    "EUL", "EULUSDT", "ALPINE", "ALPINEUSDT", "ONG", "ONGUSDT", "BMT", "BMTUSDT"
}


# ─── 2. ARCHETYPE PROFILES & DNA CONFIGURATION ────────────────────────────────

ARCHETYPE_CONFIGS = {
    "HYPER_VOLATILE_SPRINT": {
        "archetype": "HYPER_VOLATILE_SPRINT",
        "label": "🐆 SPRINT HIPER-VOLÁTIL (Meme / High-Beta)",
        "emoji": "🐆",
        "initial_sl_pct": -2.80,          # Margen amplio para absorber mechazos de microcentavos
        "max_stagnation_minutes": 240,    # Mínimo 4 horas de paciencia para permitir despegue
        "phase_2_trigger_pct": 0.45,      # Asegura ganancias al subir +0.45%
        "phase_2_retention_ratio": 0.75,  # Retiene el 75% de la cima alcanzada
        "phase_3_trigger_pct": 1.50,      # Expansión de impulso
        "phase_3_retention_ratio": 0.70,  # Retiene el 70% de la cima alcanzada
        "phase_4_retention_ratio": 0.65,  # Retiene el 65% de la cima alcanzada en megapump
        "required_vol_surge_1m": 1.8,     # Exige ignición de volumen sub-minuto brutal
        "required_min_bids_pct": 52.0,    # Libro con clara dominancia de compradores
        "trend_ride_enabled": False,      # Tomar ganancias en retrocesos
        "wick_slack": 0.35,
        "guideline_for_ai": "Trata este activo como un SPRINT. Exige volumen explosivo en 1M/10s. Cosecha ganancias con retención escalonada (75% -> 70% -> 65%) y dale hasta 4h de paciencia en Fase 1."
    },
    "BLUE_CHIP_CORE": {
        "archetype": "BLUE_CHIP_CORE",
        "label": "🏛️ BLUE-CHIP INSTITUCIONAL (L1 / Core)",
        "emoji": "🏛️",
        "initial_sl_pct": -2.00,          # Soporte estructural estándar
        "max_stagnation_minutes": 360,    # 6 horas para maduración completa de tendencia macro 4H
        "phase_2_trigger_pct": 0.55,      # Break-even estándar
        "phase_2_retention_ratio": 0.75,  # Retiene el 75% de la cima alcanzada
        "phase_3_trigger_pct": 2.50,      # Expansión de tendencia
        "phase_3_retention_ratio": 0.70,  # Retiene el 70% de la cima alcanzada
        "phase_4_retention_ratio": 0.65,  # Retiene el 65% de la cima alcanzada
        "required_vol_surge_1m": 0.8,     # Volumen orgánico institucional
        "required_min_bids_pct": 46.0,
        "trend_ride_enabled": True,       # Acompañar tendencia con MA25 de 5m/15m
        "wick_slack": 0.45,
        "guideline_for_ai": "Trata este activo como un CORE INSTITUCIONAL. Valida confluencia con Suelo 7D y FII. Dale hasta 6 horas de respiración y monta la tendencia con medias móviles."
    },
    "SECTOR_ROTATION": {
        "archetype": "SECTOR_ROTATION",
        "label": "🧩 ROTACIÓN SECTORIAL (L2 / DeFi / AI)",
        "emoji": "🧩",
        "initial_sl_pct": -2.00,          # Margen estándar
        "max_stagnation_minutes": 300,    # 5 horas para capturar rotación completa de sesión
        "phase_2_trigger_pct": 0.50,
        "phase_2_retention_ratio": 0.75,  # Retiene 75% de la cima
        "phase_3_trigger_pct": 2.20,
        "phase_3_retention_ratio": 0.70,  # Retiene 70% de la cima
        "phase_4_retention_ratio": 0.65,  # Retiene 65% de la cima
        "required_vol_surge_1m": 1.1,
        "required_min_bids_pct": 48.0,
        "trend_ride_enabled": True,
        "wick_slack": 0.40,
        "guideline_for_ai": "Trata este activo como ROTACIÓN SECTORIAL. Prioriza si su sector está CALIENTE hoy. Dale hasta 5 horas buscando expansiones de +2% a +4%."
    },
    "THIN_BOOK_MICRO": {
        "archetype": "THIN_BOOK_MICRO",
        "label": "🎯 MICRO-CAP / LIBRO DELGADO",
        "emoji": "🎯",
        "initial_sl_pct": -1.50,          # SL ajustado porque los libros delgados caen rápido
        "max_stagnation_minutes": 240,    # Mínimo 4 horas de paciencia
        "phase_2_trigger_pct": 0.40,      # Bloqueo de ganancia
        "phase_2_retention_ratio": 0.75,  # Retiene 75% de la cima
        "phase_3_trigger_pct": 1.20,
        "phase_3_retention_ratio": 0.70,  # Retiene 70% de la cima
        "phase_4_retention_ratio": 0.65,  # Retiene 65% de la cima
        "required_vol_surge_1m": 1.5,
        "required_min_bids_pct": 54.0,    # Exige fuerte muro comprador
        "trend_ride_enabled": False,
        "wick_slack": 0.30,
        "guideline_for_ai": "Trata este activo como LIBRO DELGADO. Exige volumen real y muro de Bids. Dale hasta 4 horas para desarrollar el movimiento."
    }
}


# ─── 3. CLASIFICADOR DINÁMICO DE ADN ──────────────────────────────────────────

def get_asset_dna_archetype(symbol: str, atr_15m_pct: float = 0.30, price: float = 1.0, volume_24h_usd: float = 10000000.0) -> Dict[str, Any]:
    """
    Classifies any crypto symbol into its specialized DNA Archetype.
    1. Checks explicit token registry.
    2. If unlisted, uses volatility (ATR), unit price, and 24h volume to classify dynamically.
    """
    clean_sym = symbol.replace("USDT", "").replace("USDC", "").replace("FDUSD", "").upper()
    
    # Check explicit mappings
    if clean_sym in SPRINT_MEME_TOKENS or symbol in SPRINT_MEME_TOKENS:
        arch_key = "HYPER_VOLATILE_SPRINT"
    elif clean_sym in BLUE_CHIP_CORE_TOKENS or symbol in BLUE_CHIP_CORE_TOKENS:
        arch_key = "BLUE_CHIP_CORE"
    elif clean_sym in SECTOR_ROTATION_TOKENS or symbol in SECTOR_ROTATION_TOKENS:
        arch_key = "SECTOR_ROTATION"
    elif clean_sym in THIN_BOOK_MICRO_TOKENS or symbol in THIN_BOOK_MICRO_TOKENS:
        arch_key = "THIN_BOOK_MICRO"
    else:
        # Dynamic phenotypic classification based on market structure
        if atr_15m_pct >= 0.70 or clean_sym.startswith("1000") or "DOGE" in clean_sym or "PEPE" in clean_sym or "CAT" in clean_sym:
            arch_key = "HYPER_VOLATILE_SPRINT"
        elif price >= 100.0 and volume_24h_usd < 8000000.0:
            arch_key = "THIN_BOOK_MICRO"
        elif volume_24h_usd >= 50000000.0 and atr_15m_pct <= 0.45:
            arch_key = "BLUE_CHIP_CORE"
        else:
            arch_key = "SECTOR_ROTATION"

    config = dict(ARCHETYPE_CONFIGS[arch_key])
    config["symbol"] = symbol
    config["clean_symbol"] = clean_sym
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
    Sistema Dinámico Cuántico de 2 FASES:
    - FASE 1 (Cima < +0.50%): Entrada y absorción base con Stop-Loss defensivo (-2.00%).
    - FASE 2 (Cima >= +0.50%): Trailing Proporcional Dinámico retiene el 80% de la cima alcanzada (Piso = Cima * 0.80).
    """
    arch = archetype_dna.get("archetype", "SECTOR_ROTATION")
    initial_sl = float(archetype_dna.get("initial_sl_pct", -2.00))
    p2_trigger = float(archetype_dna.get("phase_2_trigger_pct", 0.50))
    emoji = archetype_dna.get("emoji", "🧬")
    label = archetype_dna.get("label", arch)

    # 🎯 FÓRMULA PROPORCIONAL DINÁMICA: Retiene el 80% de la cima más alta (Tolera 20% de retroceso)
    retention_ratio = 0.80

    if highest_pnl_pct >= p2_trigger:
        sl_pct = round(highest_pnl_pct * retention_ratio, 2)
        phase = 2
        phase_label = f"🚀 FASE 2 TRAILING 80% ({emoji} Cima +{highest_pnl_pct:.2f}% | Retención 80% -> Piso +{sl_pct:.2f}%)"
    else:
        sl_pct = initial_sl
        phase = 1
        phase_label = f"🛡️ FASE 1 ENTRADA ({emoji} {label}: SL {initial_sl:.2f}%)"

    return sl_pct, phase, phase_label


# ─── 5. VERIFICACIÓN DE ESTANCAMIENTO POR ARQUETIPO ──────────────────────────

def check_archetype_stagnation_exit(
    archetype_dna: Dict[str, Any],
    holding_minutes: int,
    pnl_pct: float,
    phase: int
) -> Tuple[bool, str]:
    """
    Determines if a trade should exit due to stagnation based on the asset's patience window.
    - Sprint memes: 12 min max.
    - Thin books: 15 min max.
    - Sector rotation: 35 min max.
    - Blue chips: 60 min max.
    """
    if phase > 1:
        return False, ""  # If already in profit protection (Phase 2+), let the trailing stop handle it

    max_mins = int(archetype_dna.get("max_stagnation_minutes", 60))
    emoji = archetype_dna.get("emoji", "⏱️")
    arch_name = archetype_dna.get("archetype", "GENERAL")

    if holding_minutes >= max_mins and abs(pnl_pct) <= 0.75:
        reason = f"🚀 Liberación por Estancamiento ADN {emoji} ({holding_minutes}m en Fase 1 sin despegue para {arch_name}, PnL={pnl_pct:+.2f}%)"
        return True, reason

    return False, ""
