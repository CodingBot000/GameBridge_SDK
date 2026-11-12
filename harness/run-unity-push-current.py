#!/usr/bin/env python3
"""Run both real Unity LOCAL_MOCK push Players in this invocation, or defer."""
import json, os, re, subprocess, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
REQUIRED=('GB_PUSH_STEP receive-deduplicate-main-thread PASS','GB_PUSH_STEP background-foreground-main-thread PASS',
          'GB_PUSH_STEP network-recovery-online-only PASS','GB_PUSH_STEP unregister-logout-no-late-event PASS',
          'GB_PUSH_STEP session-switch-no-stale-event PASS','GB_PUSH_STEP synthetic-late-callback-rejected PASS',
          'GB_PUSH_RESULT PASS LOCAL_MOCK')

def check_result(output,code,head,platform):
    if code!=0:return False
    match=re.search(r'^RESULT PASS\s+EVIDENCE (artifacts/unity-'+platform+r'-push-[A-Za-z0-9_.-]+)\s*$',output,re.M)
    if not match:return False
    directory=(ROOT/match.group(1)).resolve()
    if not directory.is_relative_to((ROOT/'artifacts').resolve()):return False
    try:
        data=json.loads((directory/'result.json').read_text());markers=(directory/'unity-push-markers.log').read_text()
    except (OSError,ValueError):return False
    expected_network='PASS' if platform=='android' else 'PASS_LOCAL_TRANSPORT_FAULT'
    return (data.get('status')=='PASS' and data.get('player')=='PASS' and data.get('sourceHead')==head
            and data.get('sourceTrackedDirty') is False and data.get('mockPush')=='PASS'
            and data.get('background')=='PASS' and data.get('networkRecovery')==expected_network
            and data.get('reconnectFailure')=='PASS' and isinstance(data.get('rejectedReconnectAttempts'),int)
            and not isinstance(data.get('rejectedReconnectAttempts'),bool) and data['rejectedReconnectAttempts']>0
            and data.get('deduplication')=='PASS' and data.get('mainThread')=='PASS'
            and data.get('sessionSwitch')=='PASS' and type(data.get('deviceTokens')) is int and data['deviceTokens']==0
            and all(marker in markers for marker in REQUIRED))

def main():
    if os.environ.get('GAMEBRIDGE_RUN_UNITY_PUSH_E2E')!='true':print('DEFERRED_ENV: explicit Unity push opt-in required');return 2
    stage=os.environ.get('GAMEBRIDGE_UPM_STAGING');serial=os.environ.get('GAMEBRIDGE_PUSH_ANDROID_SERIAL');avd=os.environ.get('GAMEBRIDGE_PUSH_TEST_AVD_NAME')
    if not stage or not serial or not avd or not avd.startswith('GameBridge_V2_'):
        print('DEFERRED_ENV: staged SDK and fresh dedicated push AVD required');return 2
    head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip();cache=os.environ.get('GAMEBRIDGE_UNITY_PACKAGE_CACHE')
    commands=[('android',[sys.executable,'harness/run-unity-android-mock-push-e2e.py','--run-local','--staging',stage,'--serial',serial,'--expected-avd',avd]),
              ('ios',[sys.executable,'harness/run-unity-ios-mock-push-e2e.py','--run-local','--staging',stage,*(['--package-cache',cache] if cache else [])])]
    for platform,command in commands:
        print('Running fresh Unity '+platform+' LOCAL_MOCK push...',flush=True)
        try:result=subprocess.run(command,cwd=ROOT,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,timeout=1500)
        except (OSError,subprocess.TimeoutExpired):print('DEFERRED_ENV: Unity push runner unavailable or timed out');return 2
        print(result.stdout,end='',flush=True)
        if result.returncode==2:return 2
        if not check_result(result.stdout,result.returncode,head,platform):print('FAIL: '+platform+' Unity push evidence incomplete');return 1
    print('Unity push current-run PASS: Android and iOS LOCAL_MOCK Players, 2 tests');return 0
if __name__=='__main__':raise SystemExit(main())
