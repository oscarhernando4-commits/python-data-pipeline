import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

# Real money
real_data = json.load(open('real_money_account.json', 'r', encoding='utf-8'))

# Simulation matrix
sim_data = json.load(open('matrix_100_simulations.json', 'r', encoding='utf-8'))

# Trade memory stats
mem_data = json.load(open('trade_memory.json', 'r', encoding='utf-8'))

# Summary real money
print("==== REAL MONEY ACCOUNT ====")
print(f"Current Balance: ${real_data['current_balance_usd']:.2f}")
print(f"Net PnL: ${real_data['net_pnl_usd']:.2f}")
print(f"Wins: {real_data['wins']}, Losses: {real_data['losses']}, Trades: {real_data['trades_count']}")
print(f"Status: {real_data['status']}")
pos = real_data.get('position')
if pos:
    print(f"Active Position: {pos['side']} {pos['symbol']} @ Entry {pos['entry_price']}")
else:
    print("Active Position: None")

# Summary simulation matrix
total_bal = sum(a['current_balance'] for a in sim_data['accounts'])
active = sum(1 for a in sim_data['accounts'] if a['position'])
wins = sum(a['wins'] for a in sim_data['accounts'])
losses = sum(a['losses'] for a in sim_data['accounts'])
total_initial = len(sim_data['accounts']) * 10

print("\n==== TESTNET (100 ACCOUNTS) ====")
print(f"Total Balance: ${total_bal:.2f} (Initial: ${total_initial:.2f})")
print(f"Net PnL: ${total_bal - total_initial:.2f}")
print(f"Wins: {wins}, Losses: {losses}, Total Trades Recorded: {wins+losses}")
print(f"Active Positions: {active} / {len(sim_data['accounts'])}")

print("\n==== OVERALL MEMORY STATS ====")
print(f"Total Trades: {mem_data['stats']['total_trades']}")
print(f"Wins: {mem_data['stats']['wins']}, Losses: {mem_data['stats']['losses']}")
print(f"Win Rate: {mem_data['stats']['win_rate_pct']}%")
print(f"Total PnL: ${mem_data['stats']['total_pnl_usd']:.2f}")

# Group stats in testnet
print("\n==== TESTNET PERFORMANCE BY GROUP ====")
groups = {}
for a in sim_data['accounts']:
    g = a.get('group_name', 'Unknown')
    if g not in groups:
        groups[g] = {'bal': 0, 'wins': 0, 'losses': 0, 'count': 0}
    groups[g]['bal'] += a['current_balance']
    groups[g]['wins'] += a['wins']
    groups[g]['losses'] += a['losses']
    groups[g]['count'] += 1

for g, s in sorted(groups.items()):
    wr = (s['wins'] / (s['wins']+s['losses']) * 100) if (s['wins']+s['losses']) > 0 else 0
    pnl = s['bal'] - (s['count'] * 10)
    print(f"{g}: {s['count']} accs | PnL: ${pnl:.2f} | {s['wins']}W/{s['losses']}L ({wr:.1f}%)")
