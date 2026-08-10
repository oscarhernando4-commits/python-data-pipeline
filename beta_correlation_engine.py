import numpy as np
import requests
import time
from typing import Dict, Any, List

def fetch_5m_returns(symbol: str, limit: int = 30) -> np.ndarray:
    """
    Fetches the 5-minute candle closing prices from Binance and calculates log returns.
    """
    url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval=5m&limit={limit+1}"
    try:
        res = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=5)
        if res.status_code == 200:
            data = res.json()
            closes = [float(k[4]) for k in data]
            if len(closes) >= 2:
                prices = np.array(closes)
                returns = np.diff(np.log(prices))
                return returns
    except Exception:
        pass
    return np.array([])

def calculate_beta_correlation(symbol: str, btc_returns: np.ndarray = None) -> Dict[str, Any]:
    """
    Calculates Pearson Correlation (Rho) and Beta against BTCUSDT using rolling 5m returns.
    - Rho > 0.80: High Correlation (High risk if BTC drops)
    - Rho < 0.40: Low/Decoupled Correlation (Safe Refuge / Independent Movement)
    """
    if symbol in ["BTCUSDT", "PAXGUSDT", "XAUTUSDT"]:
        return {
            "symbol": symbol,
            "rho": 0.0 if symbol != "BTCUSDT" else 1.0,
            "beta": 0.0 if symbol != "BTCUSDT" else 1.0,
            "correlation_label": "REFUGIO / INDEPENDIENTE" if symbol != "BTCUSDT" else "CORRELACIÓN BASE",
            "is_blocked_by_btc_correlation": False,
            "recommendation": "PRIORIDAD REFUGIO" if symbol != "BTCUSDT" else "ACTIVO MATRIZ"
        }

    try:
        if btc_returns is None or len(btc_returns) < 10:
            btc_returns = fetch_5m_returns("BTCUSDT", limit=30)
            
        alt_returns = fetch_5m_returns(symbol, limit=30)
        
        min_len = min(len(btc_returns), len(alt_returns))
        if min_len < 10:
            return {
                "symbol": symbol,
                "rho": 0.50,
                "beta": 1.00,
                "correlation_label": "MODERADA (Default)",
                "is_blocked_by_btc_correlation": False,
                "recommendation": "SIN DATOS SUFICIENTES"
            }
            
        r_btc = btc_returns[-min_len:]
        r_alt = alt_returns[-min_len:]
        
        var_btc = np.var(r_btc)
        if var_btc == 0:
            var_btc = 1e-8
            
        cov_matrix = np.cov(r_alt, r_btc)
        cov = cov_matrix[0, 1]
        
        std_alt = np.std(r_alt)
        std_btc = np.std(r_btc)
        
        if std_alt * std_btc == 0:
            rho = 0.0
        else:
            rho = float(cov / (std_alt * std_btc))
            
        beta = float(cov / var_btc)
        
        # Determine correlation label & block criteria
        if rho >= 0.80:
            label = "🔴 ALTA CORRELACIÓN BIFURCADA"
        elif rho >= 0.50:
            label = "🟡 CORRELACIÓN MODERADA"
        elif rho >= 0.20:
            label = "🟢 BAJA CORRELACIÓN (Rotación)"
        else:
            label = "🛡️ DESCORRELACIONADO / INDEPENDIENTE"
            
        return {
            "symbol": symbol,
            "rho": round(rho, 2),
            "beta": round(beta, 2),
            "correlation_label": label,
            "is_high_correlation": rho >= 0.80,
            "is_decoupled": rho < 0.40
        }
    except Exception as e:
        return {
            "symbol": symbol,
            "rho": 0.50,
            "beta": 1.00,
            "correlation_label": f"NEUTRAL ({e})",
            "is_high_correlation": False,
            "is_decoupled": False
        }

if __name__ == "__main__":
    print("⚡ Testing Beta Correlation Engine...")
    print("LINKUSDT:", calculate_beta_correlation("LINKUSDT"))
    print("XAUTUSDT:", calculate_beta_correlation("XAUTUSDT"))
