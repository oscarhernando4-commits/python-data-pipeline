import requests
import sys

def get_public_ip():
    try:
        res = requests.get("https://api.ipify.org?format=json", timeout=5)
        if res.status_code == 200:
            ip = res.json().get("ip")
            print(f"🌐 Tu Dirección IP Pública Actual en tu PC/WiFi es: {ip}")
            return ip
    except Exception as e:
        print(f"Error obteniendo IP: {e}")
        return None

if __name__ == "__main__":
    sys.stdout.reconfigure(encoding='utf-8')
    get_public_ip()
