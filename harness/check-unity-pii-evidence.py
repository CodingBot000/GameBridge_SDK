#!/usr/bin/env python3
"""Fail-closed validation of this gate's synthetic PII Player evidence."""
import json
import re
import subprocess
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent


def safe_path(relative, pattern):
    if not isinstance(relative,str) or not re.fullmatch(pattern,relative): return None
    path=(ROOT/relative).resolve()
    return path if path.is_relative_to((ROOT/'artifacts').resolve()) else None


def check(relative, nonce, head):
    if not isinstance(nonce,str) or not re.fullmatch(r'[0-9a-f]{32}',nonce): return False
    path=safe_path(relative,r'artifacts/unity-pii-current-[A-Za-z0-9_.-]+/result\.json')
    if path is None:return False
    try:
        data=json.loads(path.read_text()); suites=data['suites']
        if data.get('status')!='PASS' or data.get('sourceHead')!=head or data.get('nonce')!=nonce or set(suites)!={'android','ios'}:return False
        for platform in ('android','ios'):
            child=safe_path(suites[platform],r'artifacts/unity-'+platform+r'-e2e-[A-Za-z0-9_.-]+/result\.json')
            if child is None:return False
            result=json.loads(child.read_text()); markers=(child.parent/'unity-test-markers.log').read_text()
            if not (result.get('status')=='PASS' and result.get('sourceHead')==head and result.get('sourceTrackedDirty') is False
                    and result.get('piiProbe') is True and result.get('unityPlayer')=='PASS'
                    and type(result.get('ledgerCount')) is int and result['ledgerCount']==1
                    and type(result.get('ledgerDelta')) is int and result['ledgerDelta']==100
                    and 'GB_PII_PROBE PASS' in markers and 'GB_MOCK_RESULT PASS LOCAL_MOCK' in markers): return False
        return True
    except (OSError,ValueError,TypeError,KeyError):return False


def main():
    if len(sys.argv)!=3: print('DEFERRED_ENV: current gate evidence and nonce required');return 2
    head=subprocess.run(['git','rev-parse','HEAD'],cwd=ROOT,text=True,stdout=subprocess.PIPE,stderr=subprocess.DEVNULL,check=False)
    if head.returncode or not check(sys.argv[1],sys.argv[2],head.stdout.strip()): print('FAIL: current Unity PII evidence incomplete');return 1
    print('Unity PII current-run PASS: Android and iOS LOCAL_MOCK Players, 2 tests');return 0
if __name__=='__main__':raise SystemExit(main())
