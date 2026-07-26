import subprocess
import time
import sys
import os
from datetime import datetime

REPO_PATH = r"c:\Users\hosca\Documents\Antigravity\BINANCE"

def run_git_pull():
    sys.stdout.reconfigure(encoding='utf-8')
    try:
        result = subprocess.run(
            ["git", "pull", "origin", "main"],
            cwd=REPO_PATH,
            capture_output=True,
            text=True,
            timeout=30
        )
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if "Already up to date" not in result.stdout:
            print(f"[{now_str}] Obsidian Auto-Synced from Cloud: {result.stdout.strip()}")
        else:
            print(f"[{now_str}] Obsidian in sync with Cloud.")
    except Exception as e:
        print(f"Sync notice: {e}")

if __name__ == '__main__':
    run_git_pull()
