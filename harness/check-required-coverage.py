#!/usr/bin/env python3
"""CI gate: inventory entries marked partial are not completed tests."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
try:
    data = json.loads((ROOT/'harness/regression-manifest.json').read_text(encoding='utf-8'))
    scenarios = data['scenarios']
    if len(scenarios) != 50 or {item['id'] for item in scenarios} != {f'R{i:02d}' for i in range(1,51)}: raise ValueError('incomplete inventory')
    missing = [item['id'] for item in scenarios if item.get('required') is not True or item.get('coverage') != 'IMPLEMENTED']
    if missing:
        print(f'NOT_IMPLEMENTED: {len(missing)} required scenarios lack complete assertion coverage', file=sys.stderr)
        raise SystemExit(1)
except (OSError, ValueError, KeyError, TypeError) as error:
    print(f'Coverage manifest invalid: {error}', file=sys.stderr); raise SystemExit(1)
print('Required scenario coverage recorded; platform results remain separate.')
