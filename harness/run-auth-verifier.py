#!/usr/bin/env python3
"""Run the synthetic Google/Apple JWT verifier checks; no provider network is used."""
import os
from pathlib import Path
import subprocess
import sys
import time
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parent.parent

def main():
    env = os.environ.copy(); env['PYTHONDONTWRITEBYTECODE'] = '1'
    started = time.time_ns()
    try:
        result = subprocess.run(['backend/gradlew','-p','backend','test','--tests','com.gamebridge.auth.IdentityVerifierTest','--rerun-tasks'],
                                cwd=ROOT,env=env,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,timeout=180)
        path = ROOT/'backend/build/test-results/test/TEST-com.gamebridge.auth.IdentityVerifierTest.xml'
        if result.returncode != 0 or path.stat().st_mtime_ns < started: raise ValueError('suite failed or result is stale')
        root = ET.parse(path).getroot(); counts = root.attrib
        names = {case.get('name','') for case in root.findall('testcase')}
        if int(counts['tests']) < 6 or int(counts['failures']) or int(counts['errors']) or int(counts['skipped']): raise ValueError('failed, skipped or missing tests')
        if not any('wrong audience issuer nonce expiry algorithm and signature fail closed' in name for name in names): raise ValueError('required assertion missing')
    except (OSError,ValueError,KeyError,ET.ParseError,subprocess.TimeoutExpired) as error:
        print(f'Auth verifier incomplete: {type(error).__name__}',file=sys.stderr); return 1
    print(f'Auth verifier PASS: {counts["tests"]} synthetic tests, no external provider.')
    return 0

if __name__ == '__main__': raise SystemExit(main())
