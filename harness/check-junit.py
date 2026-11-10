#!/usr/bin/env python3
"""Reject missing, zero-test, failed or skipped JUnit XML suites."""
import argparse
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

def main() -> int:
    parser = argparse.ArgumentParser(); parser.add_argument('reports', nargs='+', type=Path); args = parser.parse_args()
    tests = failures = skipped = 0
    try:
        for path in args.reports:
            root = ET.parse(path).getroot(); attrs = root.attrib
            count = int(attrs['tests']); failed = int(attrs['failures']) + int(attrs['errors']); ignored = int(attrs['skipped'])
            if count <= 0 or min(failed, ignored) < 0 or failed + ignored > count: raise ValueError('zero or invalid test counts')
            tests += count; failures += failed; skipped += ignored
    except (OSError, ET.ParseError, KeyError, ValueError) as exc:
        print(f'JUnit evidence invalid: {exc}', file=sys.stderr); return 1
    if failures or skipped: print(f'JUnit incomplete: tests={tests}, failures={failures}, skipped={skipped}', file=sys.stderr); return 1
    print(f'JUnit PASS: {tests} tests, 0 failures, 0 skipped')
    return 0

if __name__ == '__main__': raise SystemExit(main())
