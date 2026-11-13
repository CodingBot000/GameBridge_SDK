#!/usr/bin/env python3
"""Run candidate checks, but never treat partial coverage as a completed scenario."""
import argparse
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

def main() -> int:
    parser = argparse.ArgumentParser(); parser.add_argument('scenario')
    parser.add_argument('--manifest', type=Path, default=ROOT / 'harness/regression-manifest.json')
    args = parser.parse_args()
    try:
        manifest = json.loads(args.manifest.read_text(encoding='utf-8'))
        if not isinstance(manifest, dict): raise ValueError('manifest must be an object')
        spec = importlib.util.spec_from_file_location('manifest_checker', ROOT / 'harness/check-manifest.py')
        checker = importlib.util.module_from_spec(spec); spec.loader.exec_module(checker)
        errors = checker.check(ROOT, manifest_data=manifest)
    except (OSError, ValueError, TypeError, AttributeError) as exc:
        print(f'Manifest validation failed: {type(exc).__name__}', file=sys.stderr); return 1
    if errors:
        for error in errors: print(error, file=sys.stderr)
        print('Manifest validation failed; no suites executed', file=sys.stderr); return 1
    scenario = next((x for x in manifest['scenarios'] if x['id'] == args.scenario), None)
    if scenario is None: print('Unknown scenario', file=sys.stderr); return 2
    failed = False; missing = False
    for name in scenario['candidateSuites']:
        suite = manifest['suites'][name]; command = suite['command']
        try:
            result = subprocess.run(command, cwd=ROOT, timeout=suite.get('timeoutSeconds',600), check=False)
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
