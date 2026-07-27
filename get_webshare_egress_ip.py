import requests
import sys

def get_proxy_egress_ip():
    proxy_url = "http://mjkcggfj:f1tlwlv0tmgy@31.56.127.193:7684"
    proxies = {"http": proxy_url, "https": proxy_url}
    
    print(f"📡 Probeando la dirección IP exacta de salida del proxy de Webshare...")
    try:
        res = requests.get("https://api.ipify.org?format=json", proxies=proxies, timeout=10)
        if res.status_code == 200:
            egress_ip = res.json().get("ip")
            print(f"🎉 ¡DIRECCIÓN IP DE SALIDA EXACTA DEL PROXY ES: {egress_ip}")
            return egress_ip
    except Exception as e:
        print(f"Error consultando IP del proxy: {e}")
        return None

if __name__ == "__main__":
    sys.stdout.reconfigure(encoding='utf-8')
    get_proxy_egress_ip()
