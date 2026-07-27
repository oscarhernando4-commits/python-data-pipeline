import requests
import sys

def get_bnb_exact_usd_value():
    url = "https://api.binance.com/api/v3/ticker/price?symbol=BNBUSDT"
    try:
        res = requests.get(url, timeout=5)
        if res.status_code == 200:
            price = float(res.json().get("price", 0.0))
            amount_bnb = 0.007994
            usd_value = amount_bnb * price
            print(f"📊 Binance Spot Live Ticker BNBUSDT:")
            print(f"  - Precio Actual de 1 BNB: ${price:,.2f} USD")
            print(f"  - Cantidad BNB en tu cuenta: {amount_bnb} BNB")
            print(f"  - VALOR EXACTO EN DÓLARES: ${usd_value:,.2f} USD (${usd_value:.4f} USD)")
            return price, usd_value
    except Exception as e:
        print(f"Error: {e}")
        return 0, 0

if __name__ == "__main__":
    sys.stdout.reconfigure(encoding='utf-8')
    get_bnb_exact_usd_value()
