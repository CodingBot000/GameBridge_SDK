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
            if entry.get('coverage') == 'IMPLEMENTED':
                assertions = entry.get('assertions')
                if not isinstance(assertions, list) or not assertions:
                    errors.append(f'{ident}: implemented requires assertion mapping')
                else:
                    for assertion in assertions:
                        if not isinstance(assertion, dict): errors.append(f'{ident}: invalid assertion mapping'); continue
                        test_file = assertion.get('testFile', ''); test_case = assertion.get('testCase', ''); suite = assertion.get('suite', '')
                        path = Path(test_file)
                        if (not test_file or path.is_absolute() or '..' in path.parts or suite not in entry.get('candidateSuites', []) or
                            not (root / path).is_file() or not (root / path).resolve().is_relative_to(root.resolve()) or
                            not test_case or test_case not in (root / path).read_text(encoding='utf-8')):
                            errors.append(f'{ident}: invalid assertion mapping')
                if not str(entry.get('evidence', '')).startswith('docs/evidence/'):
                    errors.append(f'{ident}: implemented requires specific evidence')
            if entry.get('entry') != ['python3', 'harness/run-scenario.py', ident]: errors.append(f'{ident}: invalid entry')
            evidence_path = Path(entry.get('evidence', ''))
            if evidence_path.is_absolute() or '..' in evidence_path.parts or not (root / evidence_path).is_file() or not (root / evidence_path).resolve().is_relative_to(root.resolve()):
                errors.append(f'{ident}: evidence reference missing')
            for suite in entry.get('candidateSuites', []):
                if suite not in suites: errors.append(f'{ident}: unknown suite {suite}')
        for ident, suite in suites.items():
            timeout = suite.get('timeoutSeconds', 600)
            if type(timeout) is not int or not 1 <= timeout <= 3600: errors.append(f'{ident}: invalid timeout')
            command = suite.get('command')
            if not isinstance(command, list) or not command or not all(isinstance(x, str) and x for x in command):
                errors.append(f'{ident}: invalid command'); continue
            def local_file(value):
                path = Path(value)
                return (not path.is_absolute() and '..' not in path.parts and
                        (root / path).is_file() and (root / path).resolve().is_relative_to(root.resolve()))
            executable = command[0]
            if '/' in executable and not local_file(executable): errors.append(f'{ident}: invalid local command')
            if executable in ('python3', 'bash') and (len(command) < 2 or not local_file(command[1])):
                errors.append(f'{ident}: invalid local entry')
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
