#!/usr/bin/env python3
"""Fail closed on missing, skipped or incomplete isolated sample test results."""
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

def passed(path, code):
    if code != 0: return False
    try:
        root=ET.parse(path).getroot()
        tests=[item for item in root.iter('test-case') if item.get('fullname')=='OfflineSampleTests.SampleInitializesAndCompletesMockPurchase']
        return (root.get('result')=='Passed' and root.get('total')=='1' and root.get('passed')=='1'
                and root.get('failed')=='0' and root.get('skipped')=='0' and root.get('inconclusive')=='0'
                and len(tests)==1 and tests[0].get('result')=='Passed'
                and all(marker in ''.join(tests[0].itertext()) for marker in ('GB_OFFLINE_SAMPLE_FLOW PASS', 'GB_NATIVE_SAMPLE_EDITOR_GUARD PASS')))
    except (OSError,ET.ParseError,ValueError): return False

if __name__=='__main__':
    if len(sys.argv)!=3 or not sys.argv[2].isdigit() or not passed(Path(sys.argv[1]),int(sys.argv[2])):
        print('FAIL: sample result is missing, failed, skipped or incomplete',file=sys.stderr);raise SystemExit(1)
    print('Offline sample fake flow and Native sample Editor guard PASS: 1 test; not Package Manager UI or rendered visual QA')
