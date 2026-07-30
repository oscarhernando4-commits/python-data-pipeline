import time
import sys
import os
from datetime import datetime
import autotrade_daemon
import pipeline_processor

def run_single_15m_scan():
    sys.stdout.reconfigure(encoding='utf-8')
    now_start = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{now_start}] 🚀 Starting High-Frequency Trading Scan & Obsidian Sync...")
    sys.stdout.flush()
    
    try:
        # 1. Run 100-Account Live Matrix Cycle & Obsidian Table Update
        pipeline_processor.run_infinite_trading_matrix_cycle()
        
        # 2. Run General Daemon Scan
        try:
            autotrade_daemon.run_automated_scan_and_trade()
        except Exception as e_daemon:
            print(f"Autotrade daemon notice: {e_daemon}")
        
        now_done = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{now_done}] ✅ 15-Minute scan completed successfully! Closing process automatically...")
        sys.stdout.flush()
    except Exception as e:
        print(f"Error during scan cycle: {e}")
        sys.stdout.flush()
        
    # Exit process cleanly so terminal/task closes immediately
    sys.exit(0)

if __name__ == '__main__':
    run_single_15m_scan()
