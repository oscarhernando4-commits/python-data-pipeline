import real_money_trader
import requests
import time
import hmac
import hashlib
from urllib.parse import urlencode

timestamp = int(time.time() * 1000)
params = {"timestamp": timestamp}
query_string = urlencode(params)
signature = hmac.new(real_money_trader.API_SECRET.encode("utf-8"), query_string.encode("utf-8"), hashlib.sha256).hexdigest()
params["signature"] = signature
headers = {"X-MBX-APIKEY": real_money_trader.API_KEY}

url = f"{real_money_trader.BASE_URL}/api/v3/account"
try:
    print(f"Connecting to {url} using proxy {real_money_trader.PROXIES}")
    res = requests.get(url, headers=headers, params=params, proxies=real_money_trader.PROXIES, timeout=10)
    print(res.status_code)
    print(res.text)
except Exception as e:
    print(f"Error: {e}")
