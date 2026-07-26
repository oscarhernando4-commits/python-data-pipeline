import os
import subprocess
import sys

def setup_scheduled_task():
    python_exe = r"C:\Users\hosca\AppData\Local\Python\pythoncore-3.14-64\python.exe"
    script_path = r"c:\Users\hosca\Documents\Antigravity\BINANCE\run_15m_loop.py"
    task_name = "BinanceQuantTradingDaemon15m"
    
    # 1. Delete task if exists
    subprocess.run(f'schtasks /delete /tn "{task_name}" /f', shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    # 2. Create task running every 15 mins
    cmd = f'schtasks /create /tn "{task_name}" /tr "\"{python_exe}\" \"{script_path}\"" /sc minute /mo 15 /f'
    res = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    print(f"Schtasks output: {res.stdout} {res.stderr}")

if __name__ == '__main__':
    setup_scheduled_task()
