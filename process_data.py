#!/usr/bin/env python3
"""Process Snowflake query results JSON into JS data declarations for the dashboard."""
import json, sys

DATA_FILE = sys.argv[1]

with open(DATA_FILE) as f:
    raw = json.load(f)

results = raw['results']
ln_daily_data = results[0]['result']['data']
ln_weekly_data = results[1]['result']['data']
ln_monthly_data = results[2]['result']['data']
buy_daily_data = results[3]['result']['data']
buy_weekly_data = results[4]['result']['data']
buy_monthly_data = results[5]['result']['data']
payout_data = results[6]['result']['data']

partners = ['FUMB', 'THNDR', 'ZBD-App', 'ZBD-SDK']

def safe_name(p):
    return p.replace('-', '_')

def rows_by_partner(data, usd_key='AMOUNT_USD'):
    out = {}
    for row in data:
        p = row['PARTNER']
        out.setdefault(p, [])
        usd = float(row[usd_key])
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

ld = rows_by_partner(ln_daily_data)
lw = rows_by_partner(ln_weekly_data)
lm = rows_by_partner(ln_monthly_data)
bd = rows_by_partner(buy_daily_data, 'VOLUME_USD')
bw = rows_by_partner(buy_weekly_data, 'VOLUME_USD')
bm = rows_by_partner(buy_monthly_data, 'VOLUME_USD')
po = payout_by_partner(payout_data)

lines = []
partner_list = ','.join(f"'{p}'" for p in partners)
lines.append(f"const PARTNERS = [{partner_list}];")
lines.append("const PARTNER_COLORS = {FUMB:'#1a73e8', THNDR:'#f7931a', 'ZBD-App':'#7c3aed', 'ZBD-SDK':'#10b981'};")
lines.append("")

for gran_label, datasets in [('DAILY', ld), ('WEEKLY', lw), ('MONTHLY', lm)]:
    for p in partners:
        arr = datasets.get(p, [])
        lines.append(f"const LN_{gran_label}_{safe_name(p)} = {fmt_arr(arr)};")
    lines.append("")

for gran_label, datasets in [('DAILY', bd), ('WEEKLY', bw), ('MONTHLY', bm)]:
    for p in partners:
        arr = datasets.get(p, [])
        lines.append(f"const BUY_{gran_label}_{safe_name(p)} = {fmt_arr(arr)};")
    lines.append("")

for p in partners:
    arr = po.get(p, [])
    lines.append(f"const PAYOUT_{safe_name(p)} = {fmt_arr(arr)};")
lines.append("")

print('\n'.join(lines))
