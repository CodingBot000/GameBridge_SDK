#!/usr/bin/env python3
"""Run synthetic purchase verifier checks, including the real Apple JWS decoder rejection path."""
import importlib.util
import os
from pathlib import Path
import sys
import tempfile

ROOT=Path(__file__).resolve().parent.parent
sys.dont_write_bytecode=True
spec=importlib.util.spec_from_file_location('auth_runner',ROOT/'harness/run-auth-regression.py')
common=importlib.util.module_from_spec(spec); spec.loader.exec_module(common)

def main():
    env=os.environ.copy(); env['PYTHONDONTWRITEBYTECODE']='1'
    artifacts=ROOT/'artifacts'; artifacts.mkdir(exist_ok=True); output=Path(tempfile.mkdtemp(prefix='purchase-verifier-',dir=artifacts))
    classes=('ApplePurchaseVerifierTest','GooglePurchaseVerifierTest')
    command=['backend/gradlew','-p','backend','test','--rerun-tasks']
    for cls in classes: command += ['--tests',f'com.gamebridge.purchase.{cls}']
    code,_,started=common.run(command,env,output/'test.log')
    counts=common.junit_counts([ROOT/f'backend/build/test-results/test/TEST-com.gamebridge.purchase.{cls}.xml' for cls in classes],started)
    if common.item('verifier',code,counts)['status'] != 'PASS':
        print(f'Purchase verifier FAILED; evidence directory: {output.relative_to(ROOT)}',file=sys.stderr); return 1
    print(f'Purchase verifier PASS: {counts[0]} synthetic tests; evidence directory: {output.relative_to(ROOT)}'); return 0

if __name__=='__main__': raise SystemExit(main())
