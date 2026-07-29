import json
import os
import sys

# Change stdout encoding for Windows
sys.stdout.reconfigure(encoding='utf-8')

with open('matrix_100_simulations.json', encoding='utf-8') as f:
    d = json.load(f)

print("=== TESTNET (KAMIKAZE) ===")
print(f"Total PnL: ${d.get('net_pnl_usd', 0):.2f}")
print(f"Wins: {len(d.get('winning_accounts', []))} | Losses: {len(d.get('losing_accounts', []))}")

accounts = d.get('accounts', [])
active = sum(1 for a in accounts if a.get('position'))

print(f"Active trades: {active}")
if accounts:
    first = accounts[0]
    print(f"Sample Account: {first.get('account_id')} | Pair: {first.get('symbol')} | Status: {first.get('status')}")

if os.path.exists('real_money_account.json'):
    with open('real_money_account.json', encoding='utf-8') as f:
        r = json.load(f)
    print("\n=== REAL MONEY ===")
    print(f"Total Balance: ${r.get('current_balance_usd', 0):.2f}")
    if r.get('position'):
        print(f"In Trade: YES | Symbol: {r.get('position').get('symbol')} | Entry: {r.get('position').get('entry_price')}")
    else:
        print("In Trade: NO")
    print(f"Trades completed: {r.get('trades_count', 0)}")
    print(f"Status: {r.get('status', 'Unknown')}")
