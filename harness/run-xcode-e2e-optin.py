#!/usr/bin/env python3
"""Fail-closed wrapper for explicit local Xcode StoreKit + DB recovery verification."""
import json
import os
from pathlib import Path
import re
import subprocess
import sys

ROOT=Path(__file__).resolve().parent.parent

def main():
    if os.environ.get('GAMEBRIDGE_RUN_XCODE_STOREKIT_HARNESS') != 'true':
        print('CONFIG_REQUIRED: explicit Xcode local DB harness opt-in',file=sys.stderr); return 2
    try:
        run=subprocess.run([sys.executable,'harness/run-xcode-storekit-e2e.py','--run-local'],cwd=ROOT,env=os.environ.copy(),stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,timeout=300)
        match=re.search(r'Evidence directory: (artifacts/xcode-storekit-e2e-[A-Za-z0-9_.-]+)',run.stdout)
        if run.returncode != 0 or not match: raise ValueError('runner failed or evidence missing')
        path=(ROOT/match.group(1)/'result.json').resolve()
        if not path.is_relative_to((ROOT/'artifacts').resolve()): raise ValueError('unsafe evidence')
        report=json.loads(path.read_text()); head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
        if report.get('sourceHead') != head or report.get('status') != 'PASS' or report.get('passed') != 1 or report.get('skipped') != 0:
            raise ValueError('stale, failed or skipped test')
    except (OSError,ValueError,subprocess.SubprocessError): print('Xcode local recovery incomplete',file=sys.stderr); return 1
    print('Xcode local recovery PASS:',match.group(1)); return 0

if __name__=='__main__': raise SystemExit(main())
