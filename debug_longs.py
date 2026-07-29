import json

with open('trade_memory.json', 'r', encoding='utf-8') as f:
    trades = json.load(f).get('history', [])

longs = [t for t in trades if t.get('side', 'LONG') == 'LONG']
shorts = [t for t in trades if t.get('side', 'LONG') == 'SHORT']

print(f'Total LONGs: {len(longs)}')
for i, t in enumerate(longs[:5]):
    print(f"{t['timestamp']} | {t['symbol']} | Entry: {t['entry_price']} -> Exit: {t.get('exit_price')} | Result: {t['result']}")

print(f'\nTotal SHORTs: {len(shorts)}')
for i, t in enumerate(shorts[:5]):
    print(f"{t['timestamp']} | {t['symbol']} | Entry: {t['entry_price']} -> Exit: {t.get('exit_price')} | Result: {t['result']}")
