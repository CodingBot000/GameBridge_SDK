#!/usr/bin/env python3
"""Validate scenario inventory and executable references; this does not run product tests."""
import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

def check(root: Path, manifest_path: Path | None = None) -> list[str]:
    errors = []
    try:
        plan = (root / 'docs/DEVELOPMENT_PLAN.md').read_text(encoding='utf-8')
        manifest = json.loads((manifest_path or root / 'harness/regression-manifest.json').read_text(encoding='utf-8'))
        expected = re.findall(r'^\| (R\d\d) \|', plan, re.M)
        scenarios = manifest['scenarios']; suites = manifest['suites']
        ids = [x['id'] for x in scenarios]
        if len(expected) != 50 or len(ids) != 50 or len(set(ids)) != len(ids) or set(ids) != set(expected):
            errors.append('scenario IDs must match the 50 planned IDs exactly')
        for entry in scenarios:
            ident = entry.get('id', '?')
            for field in ('description', 'expected', 'platform', 'level', 'mode', 'coverage', 'entry', 'candidateSuites', 'evidence'):
                if not entry.get(field): errors.append(f'{ident}: missing {field}')
            if entry.get('required') is not True: errors.append(f'{ident}: required must be true')
            if entry.get('coverage') not in ('PARTIAL', 'NOT_IMPLEMENTED', 'IMPLEMENTED'): errors.append(f'{ident}: invalid coverage')
            if entry.get('entry') != ['python3', 'harness/run-scenario.py', ident]: errors.append(f'{ident}: invalid entry')
            if not (root / entry.get('evidence', '')).is_file(): errors.append(f'{ident}: evidence reference missing')
            for suite in entry.get('candidateSuites', []):
                if suite not in suites: errors.append(f'{ident}: unknown suite {suite}')
        for ident, suite in suites.items():
            command = suite.get('command')
            if not isinstance(command, list) or not command or not all(isinstance(x, str) and x for x in command):
                errors.append(f'{ident}: invalid command'); continue
            executable = command[0]
            if '/' in executable and not (root / executable).is_file(): errors.append(f'{ident}: missing command {executable}')
            if executable == 'python3' and len(command) > 1 and not (root / command[1]).is_file(): errors.append(f'{ident}: missing entry {command[1]}')
    except (OSError, ValueError, KeyError, TypeError) as exc:
        errors.append(f'manifest read/shape error: {exc}')
    return errors

def main() -> int:
    parser = argparse.ArgumentParser(); parser.add_argument('--root', type=Path, default=ROOT); parser.add_argument('--manifest', type=Path); args = parser.parse_args()
    errors = check(args.root, args.manifest)
    if errors:
        for error in errors: print(error, file=sys.stderr)
        return 1
    print('Manifest inventory valid: 50 required scenarios; coverage has not been executed.')
    return 0

if __name__ == '__main__': raise SystemExit(main())
