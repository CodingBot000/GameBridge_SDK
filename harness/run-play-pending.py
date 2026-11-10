#!/usr/bin/env python3
"""Run Play Billing fake pending, transition and timeout tests without a real store."""
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
    env=os.environ.copy(); env['PYTHONDONTWRITEBYTECODE']='1'; env.setdefault('ANDROID_HOME',str(Path.home()/'Library/Android/sdk'))
    artifacts=ROOT/'artifacts'; artifacts.mkdir(exist_ok=True); output=Path(tempfile.mkdtemp(prefix='play-pending-',dir=artifacts))
    command=['android/gradlew','-p','android',':sdk-android:testDebugUnitTest','--tests','com.gamebridge.android.purchase.GooglePlayBillingProviderTest','--rerun-tasks']
    code,_,started=common.run(command,env,output/'test.log')
    path=ROOT/'android/sdk-android/build/test-results/testDebugUnitTest/TEST-com.gamebridge.android.purchase.GooglePlayBillingProviderTest.xml'
    counts=common.junit_counts([path],started)
    if common.item('play',code,counts)['status'] != 'PASS': print(f'Play fake incomplete; evidence directory: {output.relative_to(ROOT)}',file=sys.stderr); return 2 if code==2 else 1
    print(f'Play pending fake PASS: {counts[0]} tests; evidence directory: {output.relative_to(ROOT)}'); return 0

if __name__=='__main__': raise SystemExit(main())
