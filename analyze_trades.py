import json

with open('trade_memory.json', 'r', encoding='utf-8') as f:
    data = json.load(f)
    trades = data.get('history', [])

long_w=0; long_l=0; long_pnl=0.0
short_w=0; short_l=0; short_pnl=0.0

for t in trades:
    side = t.get('side', 'LONG')
    res = t.get('result', 'LOSS')
    pnl = float(t.get('pnl_usd', 0.0))
    
    if side == 'LONG':
        long_pnl += pnl
        if res == 'WIN': long_w += 1
        else: long_l += 1
    elif side == 'SHORT':
        short_pnl += pnl
        if res == 'WIN': short_w += 1
        else: short_l += 1

print('--- OVERALL BY SIDE ---')
print(f'LONG  -> Wins: {long_w} | Losses: {long_l} | PnL: ${long_pnl:.2f}')
print(f'SHORT -> Wins: {short_w} | Losses: {short_l} | PnL: ${short_pnl:.2f}')

print('\n--- BY GROUP ---')
groups = {}
for t in trades:
    g = t.get('group_name', 'Unknown')
    res = t.get('result', 'LOSS')
    side = t.get('side', 'LONG')
    if g not in groups:
        groups[g] = {'w':0, 'l':0, 'LONG_L':0, 'SHORT_L':0}
    if res == 'WIN': groups[g]['w'] += 1
    else: 
        groups[g]['l'] += 1
        if side == 'LONG': groups[g]['LONG_L'] += 1
        else: groups[g]['SHORT_L'] += 1

for g, st in sorted(groups.items()):
    print(f'{g} -> W: {st["w"]} | L: {st["l"]} (LongLoss: {st["LONG_L"]}, ShortLoss: {st["SHORT_L"]})')
