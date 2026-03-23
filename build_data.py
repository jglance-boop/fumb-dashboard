#!/usr/bin/env python3
"""Convert Snowflake query JSON results into JS data declarations for the dashboard."""
import json, sys

def load_json(path):
    with open(path) as f:
        return json.load(f)

def rows_by_partner(data, val_key='AMOUNT_USD'):
    out = {}
    for row in data:
        p = row['PARTNER']
        out.setdefault(p, [])
        usd = float(row[val_key]) if isinstance(row[val_key], str) else row[val_key]
        out[p].append({
            'ds': row['DS'],
            'cust': row['NUM_CUSTOMERS'],
            'usd': round(usd, 2),
            'tx': row['NUM_TX']
        })
    return out

def payout_by_partner(data):
    out = {}
    for row in data:
        p = row['PARTNER']
        out.setdefault(p, [])
        out[p].append({
            'ds': row['DS'],
            'new': row['NEW_CUSTOMERS'],
            'cum': row['CUMULATIVE_CUSTOMERS'],
            'payout': float(row['CUMULATIVE_PAYOUT_USD'])
        })
    return out

def fmt_arr(arr, indent=2):
    lines = []
    for r in arr:
        if 'new' in r:
            lines.append(f'{{"ds":"{r["ds"]}","new":{r["new"]},"cum":{r["cum"]},"payout":{r["payout"]}}}')
        else:
            lines.append(f'{{"ds":"{r["ds"]}","cust":{r["cust"]},"usd":{r["usd"]},"tx":{r["tx"]}}}')
    sp = ' ' * indent
    return '[\n' + ',\n'.join(f'{sp}{l}' for l in lines) + '\n]'

lightning_daily = load_json(sys.argv[1])['data']
buy_daily = load_json(sys.argv[2])['data']
lightning_weekly = load_json(sys.argv[3])['data']
lightning_monthly = load_json(sys.argv[4])['data']
buy_weekly = load_json(sys.argv[5])['data']
buy_monthly = load_json(sys.argv[6])['data']
payout_data = load_json(sys.argv[7])['data']

partners = ['FUMB', 'THNDR', 'ZBD-App', 'ZBD-SDK']

def safe_name(p):
    return p.replace('-', '_')

ld = rows_by_partner(lightning_daily)
lw = rows_by_partner(lightning_weekly)
lm = rows_by_partner(lightning_monthly)
bd = rows_by_partner(buy_daily, 'VOLUME_USD')
bw = rows_by_partner(buy_weekly, 'VOLUME_USD')
bm = rows_by_partner(buy_monthly, 'VOLUME_USD')
po = payout_by_partner(payout_data)

partner_list = ','.join(f"'{p}'" for p in partners)
print(f"const PARTNERS = [{partner_list}];")
print("const PARTNER_COLORS = {FUMB:'#1a73e8', THNDR:'#f7931a', 'ZBD-App':'#7c3aed', 'ZBD-SDK':'#10b981'};")
print()

for gran_label, datasets in [('DAILY', ld), ('WEEKLY', lw), ('MONTHLY', lm)]:
    for p in partners:
        arr = datasets.get(p, [])
        print(f"const LN_{gran_label}_{safe_name(p)} = {fmt_arr(arr)};")
    print()

for gran_label, datasets in [('DAILY', bd), ('WEEKLY', bw), ('MONTHLY', bm)]:
    for p in partners:
        arr = datasets.get(p, [])
        print(f"const BUY_{gran_label}_{safe_name(p)} = {fmt_arr(arr)};")
    print()

for p in partners:
    arr = po.get(p, [])
    print(f"const PAYOUT_{safe_name(p)} = {fmt_arr(arr)};")
print()
