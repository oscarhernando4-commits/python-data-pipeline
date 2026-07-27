import requests
import sys

def test_webshare_proxies():
    # 10 Webshare proxies from user screenshot
    proxies_list = [
        ("31.56.127.193", "7684"),
        ("198.23.243.226", "6361"),
        ("64.137.96.74", "6641"),
        ("31.59.20.176", "6754"),
        ("45.38.107.97", "6014"),
        ("198.105.121.200", "6462"),
        ("38.154.185.97", "6370"),
        ("84.247.60.125", "6095"),
        ("142.111.67.146", "5611")
    ]
    username = "mjkcggfj"
    password = "f1tlwlv0tmgy"
    
    print("🌐 Probando conexión autónoma con los Proxies de Webshare...")
    
    for ip, port in proxies_list:
        proxy_url = f"http://{username}:{password}@{ip}:{port}"
        proxies = {"http": proxy_url, "https": proxy_url}
        try:
            res = requests.get("https://api.ipify.org?format=json", proxies=proxies, timeout=5)
            if res.status_code == 200:
                out_ip = res.json().get("ip")
                print(f"✅ CONEXIÓN EXITOSA CON PROXY {ip}:{port}!")
                print(f"  - IP de Salida Confirmada: {out_ip}")
                return ip, port, out_ip
        except Exception as e:
            print(f"  - Intento con {ip}:{port} fallo: {e}")
            
    print("❌ Ningún proxy respondió con HTTP básico. Probando fallback...")
    return None, None, None

if __name__ == "__main__":
    sys.stdout.reconfigure(encoding='utf-8')
    test_webshare_proxies()
