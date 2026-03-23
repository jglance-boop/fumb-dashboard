#!/usr/bin/env python3
"""Replace data arrays in index.html with fresh data from process_data.py output."""
import sys

html_path = sys.argv[1]
data_path = sys.argv[2]

with open(html_path) as f:
    lines = f.readlines()

with open(data_path) as f:
    new_data = f.read()

start_idx = None
end_idx = None
for i, line in enumerate(lines):
    if line.startswith("const PARTNERS = "):
        start_idx = i
    if start_idx is not None and line.startswith("const LN_DATA = {"):
        end_idx = i
        break

if start_idx is None or end_idx is None:
    print("ERROR: Could not find data boundaries", file=sys.stderr)
    sys.exit(1)

new_lines = lines[:start_idx] + [new_data + '\n'] + lines[end_idx:]

with open(html_path, 'w') as f:
    f.writelines(new_lines)

print(f"Replaced lines {start_idx+1}-{end_idx} with fresh data")
