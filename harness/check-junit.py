#!/usr/bin/env python3
"""Reject missing, zero-test, failed or skipped JUnit XML suites."""
import argparse
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

def main() -> int:
    parser = argparse.ArgumentParser(); parser.add_argument('reports', nargs='+', type=Path); parser.add_argument('--require-test', action='append', default=[])
    args = parser.parse_args()
    names = set()
    tests = failures = skipped = 0
    try:
        for path in args.reports:
            root = ET.parse(path).getroot(); attrs = root.attrib
            names.update(case.get('name', '').removesuffix('()') for case in root.iter('testcase'))
            count = int(attrs['tests']); failed = int(attrs['failures']) + int(attrs['errors']); ignored = int(attrs['skipped'])
            if count <= 0 or min(failed, ignored) < 0 or failed + ignored > count: raise ValueError('zero or invalid test counts')
            tests += count; failures += failed; skipped += ignored
    except (OSError, ET.ParseError, KeyError, ValueError) as exc:
        print(f'JUnit evidence invalid: {exc}', file=sys.stderr); return 1
    missing = set(args.require_test) - names
    if missing:
        print('Missing JUnit tests: ' + ', '.join(sorted(missing)), file=sys.stderr); return 1
    if failures or skipped: print(f'JUnit incomplete: tests={tests}, failures={failures}, skipped={skipped}', file=sys.stderr); return 1
    print(f'JUnit PASS: {tests} tests, 0 failures, 0 skipped')
    return 0

if __name__ == '__main__': raise SystemExit(main())
