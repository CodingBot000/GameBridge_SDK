#!/usr/bin/env python3
"""Reject missing, skipped, failed, or incomplete Unity consumer XML reports."""
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

def main():
    if len(sys.argv) != 2: print('Usage: check-unity-test-result.py RESULTS_XML', file=sys.stderr); return 2
    try:
        root = ET.parse(Path(sys.argv[1])).getroot()
        cases = root.findall('.//test-case')
        wanted = {'DomainReloadEnabled', 'DomainReloadDisabled'}
        passing = {node.get('name') for node in cases if node.get('result') == 'Passed'}
        if not wanted.issubset(passing) or any(node.get('result') != 'Passed' for node in cases):
            raise ValueError('required test missing, skipped or failed')
    except (OSError, ET.ParseError, ValueError) as error:
        print(f'Unity consumer result invalid: {error}', file=sys.stderr); return 1
    print(f'Unity consumer tests PASS: {len(cases)} executed; Editor only.')
    return 0

if __name__ == '__main__': raise SystemExit(main())
