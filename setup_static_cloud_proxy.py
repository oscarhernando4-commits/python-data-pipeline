import os
import sys

def apply_static_proxy_to_scripts():
    print("🌐 Configurando enrutamiento de IP Estática para la Nube 24/7...")
    
    # 1. Update test_real_binance_account.py
    test_script_path = os.path.join(os.path.dirname(__file__), "test_real_binance_account.py")
    if os.path.exists(test_script_path):
        with open(test_script_path, "r", encoding="utf-8") as f:
            content = f.read()
        if "PROXIES" not in content:
            proxy_code = '''
# Static Proxy Configuration for 24/7 Cloud Execution
PROXY_URL = os.getenv("FIXIE_URL", os.getenv("QUOTAGUARDSTATIC_URL", ""))
PROXIES = {"http": PROXY_URL, "https": PROXY_URL} if PROXY_URL else None
'''
            content = proxy_code + content
            content = content.replace("requests.get(url, headers=headers, params=params, timeout=10)", "requests.get(url, headers=headers, params=params, proxies=PROXIES, timeout=10)")
            with open(test_script_path, "w", encoding="utf-8") as f:
                f.write(content)
            print("  - test_real_binance_account.py actualizado con soporte de IP estática.")

    # 2. Update real_money_trader.py
    trader_script_path = os.path.join(os.path.dirname(__file__), "real_money_trader.py")
    if os.path.exists(trader_script_path):
        with open(trader_script_path, "r", encoding="utf-8") as f:
            content = f.read()
        if "PROXIES" not in content:
            proxy_code = '''
# Static Proxy Configuration for 24/7 Cloud Execution
PROXY_URL = os.getenv("FIXIE_URL", os.getenv("QUOTAGUARDSTATIC_URL", ""))
PROXIES = {"http": PROXY_URL, "https": PROXY_URL} if PROXY_URL else None
'''
            content = proxy_code + content
            content = content.replace("requests.get(url, headers=headers, params=params, timeout=10)", "requests.get(url, headers=headers, params=params, proxies=PROXIES, timeout=10)")
            content = content.replace("requests.post(url, headers=headers, params=params, timeout=10)", "requests.post(url, headers=headers, params=params, proxies=PROXIES, timeout=10)")
            with open(trader_script_path, "w", encoding="utf-8") as f:
                f.write(content)
            print("  - real_money_trader.py actualizado con soporte de IP estática.")

if __name__ == "__main__":
    sys.stdout.reconfigure(encoding='utf-8')
    apply_static_proxy_to_scripts()
