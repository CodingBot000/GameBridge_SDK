#!/usr/bin/env python3
"""R50: required suite omission and missing evidence must fail closed."""
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parent.parent

def main():
    env = os.environ.copy(); env['PYTHONDONTWRITEBYTECODE'] = '1'
    for command in ([sys.executable,'-m','unittest','discover','-s','harness','-p','test_aggregation.py','-v'],
                    [sys.executable,'harness/check-progress-negative.py']):
        try: result = subprocess.run(command,cwd=ROOT,env=env,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,timeout=60)
        except (OSError,subprocess.TimeoutExpired): return 2
        if result.returncode != 0:
            print(result.stdout, file=sys.stderr); return 1
    print('R50 PASS: missing required suite and evidence are rejected; product tests are separate.')
    return 0

if __name__ == '__main__': raise SystemExit(main())
