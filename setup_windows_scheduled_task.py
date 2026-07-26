import os
import subprocess
import sys

def setup_scheduled_task():
    task_name = "BinanceQuantObsidianSync2H"
    python_exe = r"C:\Users\hosca\AppData\Local\Python\pythoncore-3.14-64\python.exe"
    script_path = r"c:\Users\hosca\Documents\Antigravity\BINANCE\auto_git_sync.py"
    
    # Delete existing 5m task if present
    subprocess.run(f'schtasks /delete /tn "BinanceQuantObsidianSync5m" /f', shell=True, capture_output=True)
    subprocess.run(f'schtasks /delete /tn "{task_name}" /f', shell=True, capture_output=True)
    
    # Create new task that runs auto_git_sync.py every 120 minutes (2 hours) silently
    cmd = (
        f'schtasks /create /tn "{task_name}" '
        f'/tr "{python_exe} \\"{script_path}\\"" '
        f'/sc minute /mo 120 /ru "%USERNAME%" /f'
    )
    
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.returncode == 0:
        print(f"✅ Windows Task '{task_name}' successfully created to auto-sync Obsidian every 120 minutes (2 Hours)!")
    else:
        print(f"Task creation output: {result.stdout} {result.stderr}")

if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    setup_scheduled_task()
