#!/usr/bin/env python3
"""Update docs/index.html with fresh FUMB-only data."""
import json, sys

DATA_FILE = sys.argv[1]

with open(DATA_FILE) as f:
    raw = json.load(f)

results = raw['results']
ln_daily = [r for r in results[0]['result']['data'] if r['PARTNER'] == 'FUMB']
ln_weekly = [r for r in results[1]['result']['data'] if r['PARTNER'] == 'FUMB']
ln_monthly = [r for r in results[2]['result']['data'] if r['PARTNER'] == 'FUMB']

def fmt_row(r):
    usd = round(float(r['AMOUNT_USD']), 2)
    return f'{{"ds":"{r["DS"]}","cust":{r["NUM_CUSTOMERS"]},"usd":{usd},"tx":{r["NUM_TX"]}}}'

def fmt_arr(rows):
    lines = [f'  {fmt_row(r)}' for r in rows]
    return '[\n' + ',\n'.join(lines) + '\n]'

html_path = 'docs/index.html'
with open(html_path) as f:
    lines = f.readlines()

daily_start = weekly_start = monthly_start = None
daily_end = weekly_end = monthly_end = None

for i, line in enumerate(lines):
    stripped = line.strip()
    if stripped.startswith('const DAILY_DATA = '):
        daily_start = i
    if stripped.startswith('const WEEKLY_DATA = '):
        weekly_start = i
    if stripped.startswith('const MONTHLY_DATA = '):
        monthly_start = i

for i, line in enumerate(lines):
    stripped = line.strip()
    if daily_start is not None and i > daily_start and stripped == '];':
        if daily_end is None:
            daily_end = i
    if weekly_start is not None and i > weekly_start and stripped == '];':
        if daily_end is not None and weekly_end is None:
            weekly_end = i
    if monthly_start is not None and i > monthly_start and stripped == '];':
        if weekly_end is not None and monthly_end is None:
            monthly_end = i

new_lines = (
    lines[:daily_start] +
    [f'const DAILY_DATA = {fmt_arr(ln_daily)};\n\n'] +
    lines[daily_end+1:weekly_start] +
    [f'const WEEKLY_DATA = {fmt_arr(ln_weekly)};\n\n'] +
    lines[weekly_end+1:monthly_start] +
    [f'const MONTHLY_DATA = {fmt_arr(ln_monthly)};\n\n'] +
    lines[monthly_end+1:]
)

with open(html_path, 'w') as f:
    f.writelines(new_lines)

print(f"Updated docs/index.html: {len(ln_daily)} daily, {len(ln_weekly)} weekly, {len(ln_monthly)} monthly rows")
