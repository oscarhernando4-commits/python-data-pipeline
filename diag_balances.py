import os
import sys
import requests
import urllib.parse as urllib
import time
import hmac
import hashlib

# Load from api_connector to get env vars and proxies
import api_connector as api

def check_balances_raw():
    timestamp = int(time.time() * 1000)
    params = {"timestamp": timestamp}
    query_string = urllib.urlencode(params)
    
    API_KEY = "FuS10ou00y7fGxKSkYqVPRD4PCqwf0SyWiM5NiLtNECN8KTPeqrc6pfUcjhPJU62"
    API_SECRET = "gaXCTRgLw6GZNNSO8rxRuIPn1jImt0vyjJPMBQ5InDQBPQW2TgdqrEnpLOoZjOhC"
    
    signature = hmac.new(API_SECRET.encode("utf-8"), query_string.encode("utf-8"), hashlib.sha256).hexdigest()
    params["signature"] = signature
    headers = {"X-MBX-APIKEY": API_KEY}
    
    print("--- SPOT BALANCE (NO PROXY) ---")
    res1 = requests.get(f"{api.BASE_URL}/api/v3/account", headers=headers, params=params)
    print("Status:", res1.status_code)
    try:
        spot = res1.json().get("balances", [])
        for s in spot:
            if float(s["free"]) > 0 or float(s["locked"]) > 0:
                print(f"SPOT {s['asset']}: {s['free']} / {s['locked']}")
    except:
        print("Body:", res1.text)

    print("\n--- FUTURES BALANCE (WITH PROXY) ---")
    res2 = requests.get(f"{api.FAPI_URL}/fapi/v2/account", headers=headers, params=params, proxies=api.PROXIES)
    print("Status:", res2.status_code)
    try:
        fut = res2.json().get("assets", [])
        for f in fut:
            if float(f["availableBalance"]) > 0 or float(f["walletBalance"]) > 0:
                print(f"FUTURES {f['asset']}: {f['availableBalance']} / {f['walletBalance']}")
    except:
        print("Body:", res2.text)

if __name__ == "__main__":
    check_balances_raw()
