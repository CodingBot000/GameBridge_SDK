#!/usr/bin/env python3
"""Run candidate checks, but never treat partial coverage as a completed scenario."""
import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

def main() -> int:
    parser = argparse.ArgumentParser(); parser.add_argument('scenario'); args = parser.parse_args()
    manifest = json.loads((ROOT / 'harness/regression-manifest.json').read_text(encoding='utf-8'))
    scenario = next((x for x in manifest['scenarios'] if x['id'] == args.scenario), None)
    if scenario is None: print('Unknown scenario', file=sys.stderr); return 2
    failed = False; missing = False
    for name in scenario['candidateSuites']:
        command = manifest['suites'][name]['command']
        try:
            result = subprocess.run(command, cwd=ROOT, timeout=600, check=False)
            code = result.returncode
        except (OSError, subprocess.TimeoutExpired): code = 2
        print(f'{args.scenario} / {name}: exit {code}', flush=True)
        if code == 2: missing = True
        elif code != 0: failed = True
    if failed: return 1
    if missing or scenario['coverage'] != 'IMPLEMENTED':
        print(f"{args.scenario}: {scenario['coverage']} — not a completed scenario", file=sys.stderr); return 2
    return 0

if __name__ == '__main__': raise SystemExit(main())
