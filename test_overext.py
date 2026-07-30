import sys, os, time
os.chdir(os.path.dirname(os.path.abspath(__file__)))
from dotenv import load_dotenv
load_dotenv()
sys.stdout.reconfigure(encoding='utf-8')

import real_money_trader

print("Simulating Overextension SHORT trigger on UNI...")
res = real_money_trader.evaluate_and_trade_real_money(
    best_symbol="UNIUSDT",
    best_score=20,
    current_price=4.4,
    is_bearish=True,
    is_learned_signal=True
)
print("Result:")
print(res)
