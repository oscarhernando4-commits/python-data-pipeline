import json
import sys
sys.stdout.reconfigure(encoding='utf-8')

with open('matrix_100_simulations.json', 'r', encoding='utf-8') as f:
    data = json.load(f)
    print(f'Total Fund: ${data.get("current_total_usd", 0):.2f} (Net: ${data.get("net_pnl_usd", 0):.2f})')
    print(f'Global Win Rate: {data.get("global_win_rate_pct", 0)}%')
    
    with open('real_money_account.json', 'r', encoding='utf-8') as fr:
        real_data = json.load(fr)
        print(f'\nCUENTA REAL BINANCE')
        print(f'   Balance: ${real_data.get("current_balance", 0):.2f} | Status: {real_data.get("status")}')
    
    groups = {}
    for acc in data['accounts']:
        gid = acc['group_name']
        if gid not in groups:
            groups[gid] = {'pnl': 0, 'wins': 0, 'losses': 0, 'open': 0, 'active_sym': ''}
        groups[gid]['pnl'] += acc['pnl_usd']
        groups[gid]['wins'] += acc['wins']
        groups[gid]['losses'] += acc['losses']
        if 'EN_OPERACION_VIVO' in acc['status']:
            groups[gid]['open'] += 1
            if not groups[gid]['active_sym']:
                groups[gid]['active_sym'] = acc['symbol'] + ' ' + (acc['position']['side'] if acc.get('position') else '')
    
    for g, stats in sorted(groups.items()):
        total = stats['wins'] + stats['losses']
        wr = (stats['wins'] / total * 100) if total > 0 else 0
        print(f'\n{g}')
        print(f'   PnL: ${stats["pnl"]:.2f} | WinRate: {wr:.1f}% ({stats["wins"]}W / {stats["losses"]}L)')
        if stats['open'] > 0:
            print(f'   => {stats["open"]} cuentas en operacion AHORA ({stats["active_sym"]})')
        else:
            print(f'   => 0 operaciones abiertas (Esperando)')
