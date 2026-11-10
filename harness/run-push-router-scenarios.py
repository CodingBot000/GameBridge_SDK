#!/usr/bin/env python3
"""Run synthetic router and maintenance-recovery checks; no remote push is sent."""
import importlib.util
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile

ROOT=Path(__file__).resolve().parent.parent
sys.dont_write_bytecode=True
spec=importlib.util.spec_from_file_location('auth_runner',ROOT/'harness/run-auth-regression.py')
common=importlib.util.module_from_spec(spec); spec.loader.exec_module(common)

def main():
    env=os.environ.copy(); env['PYTHONDONTWRITEBYTECODE']='1'; env.setdefault('ANDROID_HOME',str(Path.home()/'Library/Android/sdk'))
    artifacts=ROOT/'artifacts'; artifacts.mkdir(exist_ok=True); output=Path(tempfile.mkdtemp(prefix='push-router-scenarios-',dir=artifacts))
    classes=('PushRouterTest','PushPayloadTest','LocalMockRecoveryTest')
    command=['android/gradlew','-p','android',':sdk-core:test','--rerun-tasks']
    for cls in classes: command += ['--tests',f'com.gamebridge.{cls}']
    code,_,started=common.run(command,env,output/'android.log')
    paths=[ROOT/f'android/sdk-core/build/test-results/test/TEST-com.gamebridge.{cls}.xml' for cls in classes]
    if common.item('android',code,common.junit_counts(paths,started))['status'] != 'PASS': print('Android router/recovery not passed',file=sys.stderr); return 2 if code==2 else 1
    code,text,_=common.run(['swift','test','--package-path','ios','--filter','PushRouterTests|PushPayloadTests|LocalMockRecoveryTests'],env,output/'swift.log')
    values=[(int(a),int(b)) for a,b in re.findall(r'Executed (\d+) tests?, with (\d+) failures?',text)]
    tests,failures=max(values,default=(0,0),key=lambda x:x[0]); skipped=max((int(x) for x in re.findall(r'with (\d+) tests? skipped',text)),default=0)
    if common.item('swift',code,(tests,failures,skipped))['status'] != 'PASS': print('Swift router/recovery not passed',file=sys.stderr); return 2 if code==2 else 1
    code,text,_=common.run(['bash','scripts/smoke-csharp-registry.sh'],env,output/'csharp.log')
    if code != 0 or 'Registry, facade and offline fake smoke passed' not in text: print('Managed router fake not passed',file=sys.stderr); return 2 if code==2 else 1
    print(f'Push router scenarios PASS: Native and managed synthetic checks; evidence directory: {output.relative_to(ROOT)}'); return 0

if __name__=='__main__': raise SystemExit(main())
