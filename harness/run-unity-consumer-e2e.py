#!/usr/bin/env python3
"""Opt-in fresh Android + iOS Unity consumer Player test; no prior result reuse."""
import json, os, re, subprocess, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent

def check_result(output, code, expected_head, platform):
    if code != 0: return False
    prefix='unity-android-e2e' if platform=='android' else 'unity-ios-e2e'
    match=re.search(r'^RESULT PASS\s+EVIDENCE (artifacts/'+prefix+r'-[A-Za-z0-9_.-]+)\s*$',output,re.M)
    if not match:return False
    location=(ROOT/match.group(1)/'result.json').resolve()
    if not location.is_relative_to((ROOT/'artifacts').resolve()):return False
    try:data=json.loads(location.read_text())
    except (OSError,ValueError):return False
    return (data.get('status')=='PASS' and data.get('unityPlayer')=='PASS' and data.get('sourceHead')==expected_head
            and data.get('sourceTrackedDirty') is False and data.get('ledgerCount')==1 and data.get('ledgerDelta')==100)

def main():
    if os.environ.get('GAMEBRIDGE_RUN_UNITY_CONSUMER_E2E')!='true':
        print('DEFERRED_ENV: explicit GAMEBRIDGE_RUN_UNITY_CONSUMER_E2E=true required');return 2
    stage=os.environ.get('GAMEBRIDGE_UPM_STAGING');serial=os.environ.get('GAMEBRIDGE_ANDROID_SERIAL');avd=os.environ.get('GAMEBRIDGE_TEST_AVD_NAME')
    if not stage or not serial or not avd or not avd.startswith('GameBridge_V2_'):
        print('DEFERRED_ENV: staged SDK and fresh dedicated Android emulator required');return 2
    head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    cache=os.environ.get('GAMEBRIDGE_UNITY_PACKAGE_CACHE');extra=['--package-cache',cache] if cache else []
    commands=[('android',[sys.executable,'harness/run-unity-android-mock-e2e.py','--run-local','--staging',stage,'--serial',serial,'--expected-avd',avd,*extra]),
              ('ios',[sys.executable,'harness/run-unity-ios-mock-e2e.py','--run-local','--adhoc','--staging',stage,*extra])]
    for platform,command in commands:
        print('Running fresh Unity '+platform+' consumer...',flush=True)
        try: result=subprocess.run(command,cwd=ROOT,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=1200)
        except (OSError,subprocess.TimeoutExpired): print('DEFERRED_ENV: consumer unavailable or timed out');return 2
        print(result.stdout, end='',flush=True)
        if result.returncode==2:return 2
        if not check_result(result.stdout,result.returncode,head,platform):print('FAIL: fresh '+platform+' Player evidence invalid');return 1
    print('R49 fresh Android and iOS Unity consumer PASS');return 0
if __name__=='__main__':raise SystemExit(main())
