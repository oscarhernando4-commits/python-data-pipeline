"""
🏛️ Módulo de Estrategias Institucionales Cuantitativas
=========================================================
Implementa las 3 estrategias matemáticas clave usadas por el Medallion Fund
y los fondos de cobertura más sofisticados del mundo:

1. Movimiento Browniano Geométrico (GBM) - Detector de Anomalías
2. Diversificación por Correlación de Pearson - Filtro de Portfolio
3. Arbitraje Spot/Futuros + Ornstein-Uhlenbeck Mean Reversion

Basado en: "Así arruina el TRADING a miles de personas cada año" - evidencia científica
Referencia: Medallion Fund (James Simons), correlaciones institucionales, HFT arbitrage
"""

import math
import json
import os
import urllib.request

BASE_URL = 'https://data-api.binance.vision'

# ============================================================
# 1. MOVIMIENTO BROWNIANO GEOMÉTRICO (GBM) - DETECTOR DE ANOMALÍAS
# ============================================================
# dS = μS·dt + σS·dW  (Ecuación de Black-Scholes)
# 
# El mercado a corto plazo es ALEATORIO (Browniano). Los traders retail
# pierden porque operan dentro del RUIDO. Este detector identifica cuándo
# un movimiento es ESTADÍSTICAMENTE SIGNIFICATIVO (no ruido) usando Z-Score.
#
# Si |Z| < 1.5 → Es RUIDO BROWNIANO → NO OPERAR (trampa retail)
# Si |Z| > 2.5 → Es ANOMALÍA REAL → Señal institucional válida
# ============================================================

class GBMAnomalyDetector:
    """
    Geometric Brownian Motion Anomaly Detector.
    Identifica movimientos NO aleatorios (pumps, dumps, breakouts reales)
    separándolos del ruido browniano que destruye a los traders retail.
    
    Fórmula: Z_GBM = (r_t - E[r]) / (σ * √Δt)
    donde E[r] = (μ - ½σ²)·Δt (retorno esperado bajo GBM)
    """
    
    def __init__(self, window=50, z_threshold=2.5):
        self.window = window
        self.z_threshold = z_threshold
    
    def analyze(self, closes, dt=1.0):
        """
        Analiza una serie de precios de cierre y detecta anomalías.
        
        Args:
            closes: lista de precios de cierre (min 51 elementos)
            dt: intervalo de tiempo normalizado (1.0 = 1 vela)
            
        Returns:
            dict con gbm_zscore, is_anomaly, anomaly_type, drift, volatility
        """
        if len(closes) < self.window + 1:
            return {
                'gbm_zscore': 0.0, 'is_anomaly': False, 'anomaly_type': 'INSUFFICIENT_DATA',
                'drift': 0.0, 'volatility': 0.0, 'signal_strength': 'NOISE'
            }
        
        # Calcular log-returns
        log_returns = []
        for i in range(1, len(closes)):
            if closes[i] > 0 and closes[i-1] > 0:
                log_returns.append(math.log(closes[i] / closes[i-1]))
            else:
                log_returns.append(0.0)
        
        # Tomar ventana rolling
        recent_returns = log_returns[-self.window:]
        current_return = log_returns[-1]
        
        # Calcular drift (μ) y volatilidad (σ) rolling
        n = len(recent_returns)
        mu = sum(recent_returns) / n / dt  # Drift anualizado
        
        variance = sum((r - (mu * dt))**2 for r in recent_returns) / (n - 1)
        sigma = math.sqrt(variance) / math.sqrt(dt)  # Volatilidad
        
        if sigma < 1e-10:
            return {
                'gbm_zscore': 0.0, 'is_anomaly': False, 'anomaly_type': 'ZERO_VOL',
                'drift': mu, 'volatility': 0.0, 'signal_strength': 'NOISE'
            }
        
        # Retorno esperado bajo GBM: E[r] = (μ - ½σ²)·Δt
        expected_return = (mu - 0.5 * sigma**2) * dt
        return_std = sigma * math.sqrt(dt)
        
        # Z-Score GBM
        z_score = (current_return - expected_return) / return_std
        
        # Clasificar anomalía
        abs_z = abs(z_score)
        is_anomaly = abs_z > self.z_threshold
        
        if z_score > self.z_threshold:
            anomaly_type = 'PUMP_BREAKOUT'
        elif z_score < -self.z_threshold:
            anomaly_type = 'DUMP_CRASH'
        else:
            anomaly_type = 'BROWNIAN_NOISE'
        
        # Fuerza de la señal
        if abs_z > 3.0:
            signal_strength = 'EXTREME'
        elif abs_z > 2.5:
            signal_strength = 'STRONG'
        elif abs_z > 1.5:
            signal_strength = 'MODERATE'
        else:
            signal_strength = 'NOISE'
        
        return {
            'gbm_zscore': round(z_score, 3),
            'is_anomaly': is_anomaly,
            'anomaly_type': anomaly_type,
            'drift': round(mu, 6),
            'volatility': round(sigma, 6),
            'signal_strength': signal_strength,
            'expected_return_pct': round(expected_return * 100, 4),
            'actual_return_pct': round(current_return * 100, 4)
        }


# ============================================================
# 2. ORNSTEIN-UHLENBECK (OU) - REVERSIÓN A LA MEDIA
# ============================================================
# dX = θ(μ - X)·dt + σ·dW
#
# Detecta cuándo un precio se ha desviado tanto de su media que
# ESTADÍSTICAMENTE debe revertir. Más riguroso que RSI.
# ============================================================

class OUMeanReversion:
    """
    Ornstein-Uhlenbeck Process via AR(1) Discrete Regression.
    Calcula velocidad de reversión (theta), half-life, y Z-Score del proceso.
    
    Más riguroso que RSI porque calcula el HALF-LIFE estadístico exacto
    (cuántas velas tardará en revertir a la media).
    """
    
    def __init__(self, window=100, dt=1.0):
        self.window = window
        self.dt = dt
    
    def fit_predict(self, closes):
        """
        Ajusta modelo OU a la serie de precios y genera señal.
        
        Returns:
            dict con theta, mu, half_life, zscore, signal
        """
        if len(closes) < self.window:
            return {'valid': False, 'zscore': 0.0, 'half_life': 999, 'signal': 'NEUTRAL'}
        
        y = closes[-self.window:]
        x_data = y[:-1]
        y_data = y[1:]
        
        n = len(x_data)
        
        # Regresión lineal: y = a + b*x
        sum_x = sum(x_data)
        sum_y = sum(y_data)
        sum_xy = sum(x_data[i] * y_data[i] for i in range(n))
        sum_x2 = sum(x_data[i]**2 for i in range(n))
        
        denom = n * sum_x2 - sum_x**2
        if abs(denom) < 1e-10:
            return {'valid': False, 'zscore': 0.0, 'half_life': 999, 'signal': 'NEUTRAL'}
        
        b = (n * sum_xy - sum_x * sum_y) / denom
        a = (sum_y - b * sum_x) / n
        
        # Si b >= 1 o b <= 0, no hay reversión a la media
        if b >= 1.0 or b <= 0.0:
            return {'valid': False, 'zscore': 0.0, 'half_life': 999, 'signal': 'NEUTRAL', 'theta': 0.0}
        
        # Parámetros OU
        theta = -math.log(b) / self.dt  # Velocidad de reversión
        mu = a / (1.0 - b)  # Media de equilibrio
        half_life = math.log(2.0) / theta  # Velas para revertir al 50%
        
        # Varianza de residuos
        residuals = [y_data[i] - (a + b * x_data[i]) for i in range(n)]
        res_var = sum(r**2 for r in residuals) / (n - 2) if n > 2 else 1.0
        
        # Varianza estacionaria
        stat_var = res_var / (1.0 - b**2)
        stat_std = math.sqrt(stat_var) if stat_var > 0 else 1.0
        
        # Z-Score OU
        current = y[-1]
        zscore = (current - mu) / stat_std if stat_std > 0 else 0.0
        
        # Señal
        if zscore > 2.0 and half_life < 24:
            signal = 'SHORT'  # Muy por encima de la media, revertirá pronto
        elif zscore < -2.0 and half_life < 24:
            signal = 'LONG'  # Muy por debajo de la media, rebotará pronto
        else:
            signal = 'NEUTRAL'
        
        return {
            'valid': True,
            'theta': round(theta, 4),
            'mu': round(mu, 2),
            'half_life': round(half_life, 1),
            'zscore': round(zscore, 3),
            'signal': signal,
            'current_price': round(current, 4),
            'equilibrium_price': round(mu, 4)
        }


# ============================================================
# 3. DIVERSIFICACIÓN POR CORRELACIÓN DE PEARSON
# ============================================================
# ρ(X,Y) = Cov(X,Y) / (σ_X · σ_Y)
#
# Los fondos institucionales NUNCA abren 2 posiciones en activos
# altamente correlacionados. Si BTC y ETH están correlacionados 0.92,
# tener LONG en ambos es como tener DOBLE posición en uno solo.
# ============================================================

class CorrelationDiversifier:
    """
    Portfolio Risk Filter using Rolling Pearson Correlation.
    Bloquea nuevas posiciones si están demasiado correlacionadas con las activas.
    """
    
    def __init__(self, max_correlation=0.75, lookback_bars=50):
        self.max_correlation = max_correlation
        self.lookback_bars = lookback_bars
    
    def pearson_correlation(self, x_vals, y_vals):
        """Calcula correlación de Pearson entre 2 series de log-returns."""
        n = min(len(x_vals), len(y_vals))
        if n < 10:
            return 0.0
        
        x = x_vals[-n:]
        y = y_vals[-n:]
        
        mean_x = sum(x) / n
        mean_y = sum(y) / n
        
        cov_xy = sum((x[i] - mean_x) * (y[i] - mean_y) for i in range(n)) / (n - 1)
        var_x = sum((x[i] - mean_x)**2 for i in range(n)) / (n - 1)
        var_y = sum((y[i] - mean_y)**2 for i in range(n)) / (n - 1)
        
        denom = math.sqrt(var_x * var_y)
        if denom < 1e-10:
            return 0.0
        
        return cov_xy / denom
    
    def get_log_returns(self, closes):
        """Convierte precios de cierre a log-returns."""
        returns = []
        for i in range(1, len(closes)):
            if closes[i] > 0 and closes[i-1] > 0:
                returns.append(math.log(closes[i] / closes[i-1]))
            else:
                returns.append(0.0)
        return returns
    
    def check_diversification(self, candidate_symbol, candidate_closes, 
                               active_positions_data):
        """
        Verifica si una nueva posición está suficientemente diversificada
        respecto a las posiciones activas.
        
        Args:
            candidate_symbol: símbolo a evaluar (ej: "ETHUSDT")
            candidate_closes: lista de precios de cierre del candidato
            active_positions_data: dict {symbol: closes_list} de posiciones activas
            
        Returns:
            dict con approved, max_correlation, blocking_asset, reason
        """
        if not active_positions_data:
            return {
                'approved': True, 'max_correlation': 0.0,
                'blocking_asset': None,
                'reason': 'Sin posiciones activas → Diversificación OK'
            }
        
        cand_returns = self.get_log_returns(candidate_closes[-self.lookback_bars:])
        
        max_corr = 0.0
        max_corr_asset = None
        correlations = {}
        
        for sym, sym_closes in active_positions_data.items():
            if sym == candidate_symbol:
                continue
            sym_returns = self.get_log_returns(sym_closes[-self.lookback_bars:])
            corr = self.pearson_correlation(cand_returns, sym_returns)
            correlations[sym] = round(corr, 3)
            
            if abs(corr) > abs(max_corr):
                max_corr = corr
                max_corr_asset = sym
        
        approved = abs(max_corr) <= self.max_correlation
        
        return {
            'approved': approved,
            'candidate': candidate_symbol,
            'max_correlation': round(max_corr, 3),
            'blocking_asset': max_corr_asset if not approved else None,
            'all_correlations': correlations,
            'reason': (
                f"Diversificación OK (max corr={max_corr:.2f} ≤ {self.max_correlation})"
                if approved else
                f"⛔ BLOQUEADO: Correlación {max_corr:.2f} con {max_corr_asset} > {self.max_correlation} (riesgo sistémico)"
            )
        }


# ============================================================
# 4. DETECTOR DE ARBITRAJE SPOT/FUTUROS
# ============================================================
# Basis% = (F - S) / S × 100
# Los fondos HFT explotan estas ineficiencias sin adivinar dirección.
# ============================================================

class SpotFuturesArbitrageDetector:
    """
    Detecta oportunidades de arbitraje entre Spot y Futuros Perpetuos.
    Cash & Carry: Comprar Spot + Vender Futures cuando basis > fees.
    """
    
    def __init__(self, spot_fee=0.00075, futures_fee=0.0004):
        self.spot_fee = spot_fee
        self.futures_fee = futures_fee
        self.total_roundtrip_fee = (spot_fee * 2) + (futures_fee * 2)
    
    def check_basis(self, spot_price, futures_price, funding_rate_8h=0.0001, holding_days=7):
        """
        Calcula el basis y yield neto de una operación cash & carry.
        
        Returns:
            dict con basis_pct, net_yield_pct, annualized_apy, is_profitable
        """
        if spot_price <= 0 or futures_price <= 0:
            return {'basis_pct': 0.0, 'is_profitable': False}
        
        basis = futures_price - spot_price
        basis_pct = (basis / spot_price) * 100.0
        
        # Yield por funding (3 pagos de 8h por día)
        funding_yield = funding_rate_8h * (holding_days * 3)
        
        # Yield neto = basis + funding - fees
        net_yield = (basis_pct / 100.0) + funding_yield - self.total_roundtrip_fee
        annualized = net_yield * (365.0 / holding_days) * 100.0
        
        return {
            'basis_pct': round(basis_pct, 4),
            'funding_8h_pct': round(funding_rate_8h * 100, 4),
            'net_yield_pct': round(net_yield * 100, 4),
            'annualized_apy_pct': round(annualized, 2),
            'is_profitable': net_yield > 0.005,  # > 0.5% neto
            'direction': 'LONG_SPOT_SHORT_FUTURES' if basis_pct > 0 else 'SHORT_SPOT_LONG_FUTURES'
        }


# ============================================================
# FUNCIÓN PRINCIPAL DE ANÁLISIS INSTITUCIONAL
# ============================================================

# Instancias globales reutilizables
_gbm_detector = GBMAnomalyDetector(window=50, z_threshold=2.5)
_ou_model = OUMeanReversion(window=100, dt=1.0)
_corr_filter = CorrelationDiversifier(max_correlation=0.75, lookback_bars=50)
_arb_detector = SpotFuturesArbitrageDetector()

def analyze_institutional(closes, symbol="UNKNOWN"):
    """
    Ejecuta el análisis institucional completo sobre un activo.
    Usa Movimiento Browniano + Ornstein-Uhlenbeck.
    
    Args:
        closes: lista de precios de cierre (mínimo 101)
        symbol: nombre del símbolo para logging
        
    Returns:
        dict con todos los indicadores institucionales
    """
    gbm = _gbm_detector.analyze(closes)
    ou = _ou_model.fit_predict(closes)
    
    # Generar veredicto institucional combinado
    gbm_z = abs(gbm.get('gbm_zscore', 0))
    ou_z = abs(ou.get('zscore', 0))
    
    # FILTRO BROWNIANO: Si el movimiento es solo ruido, NO operar
    is_brownian_noise = gbm.get('signal_strength') == 'NOISE'
    
    # Señal combinada institucional
    if is_brownian_noise and ou.get('signal') == 'NEUTRAL':
        institutional_verdict = 'NO_TRADE_BROWNIAN_NOISE'
    elif gbm.get('anomaly_type') == 'PUMP_BREAKOUT' and ou.get('signal') != 'SHORT':
        institutional_verdict = 'BREAKOUT_CONFIRMED'
    elif gbm.get('anomaly_type') == 'DUMP_CRASH':
        institutional_verdict = 'CRASH_DETECTED'
    elif ou.get('signal') == 'LONG' and not is_brownian_noise:
        institutional_verdict = 'MEAN_REVERSION_LONG'
    elif ou.get('signal') == 'SHORT' and not is_brownian_noise:
        institutional_verdict = 'MEAN_REVERSION_SHORT'
    else:
        institutional_verdict = 'NEUTRAL'
    
    return {
        'symbol': symbol,
        'gbm': gbm,
        'ou': ou,
        'institutional_verdict': institutional_verdict,
        'is_brownian_noise': is_brownian_noise,
        'trade_quality': 'A+' if gbm_z > 2.5 else ('B' if gbm_z > 1.5 else 'C_NOISE')
    }


def check_correlation_filter(candidate_symbol, all_closes_map, active_symbols):
    """
    Verifica diversificación antes de abrir nueva posición.
    
    Args:
        candidate_symbol: símbolo a evaluar
        all_closes_map: dict {symbol: [closes]} de todos los símbolos analizados
        active_symbols: lista de símbolos con posición abierta
        
    Returns:
        dict con approved, max_correlation, reason
    """
    if not active_symbols or candidate_symbol not in all_closes_map:
        return {'approved': True, 'max_correlation': 0.0, 'reason': 'OK'}
    
    active_data = {s: all_closes_map[s] for s in active_symbols if s in all_closes_map}
    
    return _corr_filter.check_diversification(
        candidate_symbol, 
        all_closes_map[candidate_symbol],
        active_data
    )


# ============================================================
# TEST STANDALONE
# ============================================================
if __name__ == "__main__":
    import sys
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass
    
    print("=" * 60)
    print("🏛️ TEST: Módulo de Estrategias Institucionales Cuantitativas")
    print("=" * 60)
    
    # Fetch real BTCUSDT klines for testing
    try:
        url = f"{BASE_URL}/api/v3/klines?symbol=BTCUSDT&interval=15m&limit=120"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as response:
            klines = json.loads(response.read().decode())
        closes = [float(k[4]) for k in klines]
        print(f"\n📊 BTCUSDT 15m: {len(closes)} velas cargadas (${closes[-1]:,.2f})")
    except Exception as e:
        print(f"Error fetching klines: {e}")
        closes = [100 + i * 0.1 + (i % 7) * 0.5 for i in range(120)]
    
    # Test 1: GBM Anomaly Detector
    print("\n--- 1. MOVIMIENTO BROWNIANO (GBM) ---")
    result = _gbm_detector.analyze(closes)
    print(f"  Z-Score GBM: {result['gbm_zscore']}")
    print(f"  Tipo: {result['anomaly_type']}")
    print(f"  Fuerza: {result['signal_strength']}")
    print(f"  Drift (μ): {result['drift']}")
    print(f"  Volatilidad (σ): {result['volatility']}")
    
    # Test 2: OU Mean Reversion
    print("\n--- 2. ORNSTEIN-UHLENBECK (Reversión a Media) ---")
    ou_result = _ou_model.fit_predict(closes)
    print(f"  Valid: {ou_result.get('valid')}")
    print(f"  Z-Score OU: {ou_result.get('zscore')}")
    print(f"  Half-Life: {ou_result.get('half_life')} velas")
    print(f"  Señal: {ou_result.get('signal')}")
    print(f"  Precio Equilibrio: ${ou_result.get('equilibrium_price', 0):,.2f}")
    
    # Test 3: Full Institutional Analysis
    print("\n--- 3. ANÁLISIS INSTITUCIONAL COMBINADO ---")
    full = analyze_institutional(closes, "BTCUSDT")
    print(f"  Veredicto: {full['institutional_verdict']}")
    print(f"  Es Ruido Browniano: {full['is_brownian_noise']}")
    print(f"  Calidad de Trade: {full['trade_quality']}")
    
    # Test 4: Correlation Filter
    print("\n--- 4. FILTRO DE CORRELACIÓN ---")
    try:
        url2 = f"{BASE_URL}/api/v3/klines?symbol=ETHUSDT&interval=15m&limit=120"
        req2 = urllib.request.Request(url2, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req2, timeout=10) as response2:
            eth_klines = json.loads(response2.read().decode())
        eth_closes = [float(k[4]) for k in eth_klines]
        
        corr_result = check_correlation_filter(
            "ETHUSDT", 
            {"BTCUSDT": closes, "ETHUSDT": eth_closes},
            ["BTCUSDT"]
        )
        print(f"  BTC-ETH Correlación: {corr_result.get('max_correlation')}")
        print(f"  Aprobado: {corr_result.get('approved')}")
        print(f"  Razón: {corr_result.get('reason')}")
    except Exception as e:
        print(f"  Error: {e}")
    
    print("\n" + "=" * 60)
    print("✅ Todas las pruebas completadas")
    print("=" * 60)
