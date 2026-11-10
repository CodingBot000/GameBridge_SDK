#!/usr/bin/env python3
"""Check the planned task ledger without claiming product validation."""
import argparse
import re
import sys
from pathlib import Path
from collections import Counter

ROOT = Path(__file__).resolve().parent.parent
IMPL = {'NOT_STARTED', 'IN_PROGRESS', 'IMPLEMENTED', 'BLOCKED'}
LOCAL = {'NOT_RUN', 'PASS', 'FAIL', 'PARTIAL', 'DEFERRED_ENV', 'REVIEW_ONLY'}
EXTERNAL = {'N/A', 'WAITING_USER', 'PASS', 'FAIL', 'DEFERRED_ENV'}


def check(plan, progress, log, setup, root=ROOT):
    errors = []
    ids = re.findall(r'^#### (P\d\d-T\d\d)\b', plan, re.M)
    rows = re.findall(r'^\| (P\d\d-T\d\d) \|([^\n]+)', progress, re.M)
    if len(ids) != len(set(ids)) or not ids:
        errors.append('plan task IDs missing or duplicated')
    actual = [task for task, _ in rows]
    if len(actual) != len(set(actual)):
        errors.append('ledger task IDs duplicated')
    if set(ids) != set(actual):
        errors.append('plan and ledger task IDs differ')
    for task, raw in rows:
        cols = [value.strip() for value in raw.strip().strip('|').split('|')]
        if len(cols) != 6:
            errors.append(f'{task}: expected six fields after ID')
            continue
        _, implementation, local, external, evidence, blockers = cols
        if implementation not in IMPL or local not in LOCAL or external not in EXTERNAL:
            errors.append(f'{task}: invalid status')
        if (local == 'PASS' or external == 'PASS') and evidence in ('', '-'):
            errors.append(f'{task}: PASS requires evidence')
        if implementation == 'IMPLEMENTED' and f'[{task}]' not in log:
            errors.append(f'{task}: IMPLEMENTED requires work log entry')
        for reference in re.findall(r'docs/[A-Za-z0-9_./-]+\.(?:md|json)', evidence):
            path = Path(reference)
            if path.is_absolute() or '..' in path.parts or not (root / path).is_file() or not (root / path).resolve().is_relative_to(root.resolve()): errors.append(f'{task}: evidence file missing: {reference}')
        for reference in re.findall(r'WORK_LOG (P\d\d-T\d\d)', evidence):
            if f'[{reference}]' not in log: errors.append(f'{task}: work log evidence missing: {reference}')
        if external == 'WAITING_USER':
            refs = re.findall(r'USER-[A-Z-]+', blockers)
            if not refs or any(ref not in setup for ref in refs):
                errors.append(f'{task}: WAITING_USER requires setup references')
    declared_total = re.search(r'^- 계획 Task 총수: (\d+)$', progress, re.M)
    if not declared_total or int(declared_total.group(1)) != len(ids): errors.append('declared task total differs from plan')
    parsed = [[value.strip() for value in raw.strip().strip('|').split('|')] for _, raw in rows]
    if all(len(value) == 6 for value in parsed):
        for label, index, valid in [('구현', 1, IMPL), ('로컬 검증', 2, LOCAL)]:
            match = re.search(r'^- ' + label + r': (.+)$', progress, re.M)
            pairs = re.findall(r'([A-Z_]+) (\d+)', match.group(1) if match else '')
            declared = dict((key, int(value)) for key, value in pairs)
            actual_counts = Counter(value[index] for value in parsed)
            if len(pairs) != len(declared) or set(declared) != valid or any(declared.get(key) != actual_counts.get(key, 0) for key in valid): errors.append(f'{label}: declared counts differ from ledger')
        match = re.search(r'^- 실연동 대상 Task: (\d+) / (.+)$', progress, re.M)
        pairs = re.findall(r'([A-Z_]+) (\d+)', match.group(2) if match else '')
        declared = dict((key, int(value)) for key, value in pairs)
        actual_counts = Counter(value[3] for value in parsed if value[3] != 'N/A')
        external_states = EXTERNAL - {'N/A'}
        if not match or len(pairs) != len(declared) or int(match.group(1)) != sum(actual_counts.values()) or set(declared) != external_states or any(declared.get(key) != actual_counts.get(key, 0) for key in external_states):
            errors.append('external: declared counts differ from ledger')
    return errors


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--root', type=Path, default=ROOT, help='document root (for isolated checks)')
    args = parser.parse_args()
    try:
        docs = args.root / 'docs'
        values = [(docs / name).read_text(encoding='utf-8') for name in ('DEVELOPMENT_PLAN.md', 'PROGRESS.md', 'WORK_LOG.md', 'USER_SETUP.md')]
        errors = check(*values, root=args.root)
    except (OSError, UnicodeError) as exc:
        print(f'document read failed: {exc}', file=sys.stderr)
        return 1
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1
    print('Progress ledger consistency checks passed; product tests are separate.')
    return 0

if __name__ == '__main__':
    sys.exit(main())
