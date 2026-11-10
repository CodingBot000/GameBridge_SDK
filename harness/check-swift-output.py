#!/usr/bin/env python3
"""Fail when required XCTest classes are absent, skipped or have no tests."""
import argparse
import re
import sys
from pathlib import Path

def main() -> int:
    parser = argparse.ArgumentParser(); parser.add_argument('log', type=Path); parser.add_argument('classes', nargs='+'); args = parser.parse_args()
    try: text = args.log.read_text(encoding='utf-8')
    except OSError as exc: print(f'Swift test log unavailable: {exc}', file=sys.stderr); return 1
    counts = [(int(a), int(b)) for a,b in re.findall(r'Executed (\d+) tests?, with (\d+) failures?', text)]
    tests, failures = max(counts, default=(0,0), key=lambda x:x[0])
    skipped = max((int(x) for x in re.findall(r'with (\d+) tests? skipped', text)), default=0)
    absent = [name for name in args.classes if f"Test Suite '{name}' passed" not in text]
    if tests <= 0 or failures or skipped or absent:
        print(f'Swift evidence incomplete: tests={tests}, failures={failures}, skipped={skipped}, absent={len(absent)}', file=sys.stderr); return 1
    print(f'Swift XCTest PASS: {tests} tests, required classes={len(args.classes)}, 0 failures, 0 skipped')
    return 0

if __name__ == '__main__': raise SystemExit(main())
