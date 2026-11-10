#!/usr/bin/env python3
"""Check the planned task ledger without claiming product validation."""
import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
IMPL = {'NOT_STARTED', 'IN_PROGRESS', 'IMPLEMENTED', 'BLOCKED'}
LOCAL = {'NOT_RUN', 'PASS', 'FAIL', 'PARTIAL', 'DEFERRED_ENV', 'REVIEW_ONLY'}
EXTERNAL = {'N/A', 'WAITING_USER', 'PASS', 'FAIL', 'DEFERRED_ENV'}


def check(plan, progress, log, setup):
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
        if external == 'WAITING_USER':
            refs = re.findall(r'USER-[A-Z-]+', blockers)
            if not refs or any(ref not in setup for ref in refs):
                errors.append(f'{task}: WAITING_USER requires setup references')
    return errors


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--root', type=Path, default=ROOT, help='document root (for isolated checks)')
    args = parser.parse_args()
    try:
        docs = args.root / 'docs'
        errors = check(*( (docs / name).read_text(encoding='utf-8') for name in
            ('DEVELOPMENT_PLAN.md', 'PROGRESS.md', 'WORK_LOG.md', 'USER_SETUP.md')))
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
