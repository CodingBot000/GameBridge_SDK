#!/usr/bin/env python3
"""Run both real Unity LOCAL_MOCK push Players in this invocation, or defer."""
import argparse, json, os, re, subprocess, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
REQUIRED=('GB_PUSH_STEP receive-deduplicate-main-thread PASS','GB_PUSH_STEP background-foreground-main-thread PASS',
          'GB_PUSH_STEP network-recovery-online-only PASS','GB_PUSH_STEP unregister-logout-no-late-event PASS',
          'GB_PUSH_STEP session-switch-no-stale-event PASS','GB_PUSH_STEP synthetic-late-callback-rejected PASS',
          'GB_PUSH_RESULT PASS LOCAL_MOCK')

def check_result(output,code,head,platform,expected_pid=None):
    if code!=0:return False
    match=re.search(r'^RESULT PASS\s+EVIDENCE (artifacts/unity-'+platform+r'-push-[A-Za-z0-9_.-]+)\s*$',output,re.M)
    if not match:return False
    directory=(ROOT/match.group(1)).resolve()
    if not directory.is_relative_to((ROOT/'artifacts').resolve()):return False
    try:
        data=json.loads((directory/'result.json').read_text());markers=(directory/'unity-push-markers.log').read_text()
    except (OSError,ValueError):return False
    if platform=='android':
        binding=data.get('emulatorBinding',{})
        if not isinstance(binding,dict):return False
        if (type(binding.get('pid')) is not int or binding['pid']<=0 or binding.get('portsOwned') is not True or
            type(binding.get('consolePort')) is not int or binding['consolePort']%2 or
            binding.get('serial')!='emulator-'+str(binding['consolePort']) or
            not str(binding.get('avd','')).startswith('GameBridge_V2_') or binding.get('adbPort')!=binding['consolePort']+1 or
            (expected_pid is not None and binding['pid']!=int(expected_pid))):return False
    expected_network='PASS' if platform=='android' else 'PASS_LOCAL_TRANSPORT_FAULT'
    return (data.get('status')=='PASS' and data.get('player')=='PASS' and data.get('sourceHead')==head
            and data.get('sourceTrackedDirty') is False and data.get('mockPush')=='PASS'
            and data.get('background')=='PASS' and data.get('networkRecovery')==expected_network
            and data.get('reconnectFailure')=='PASS' and isinstance(data.get('rejectedReconnectAttempts'),int)
            and not isinstance(data.get('rejectedReconnectAttempts'),bool) and data['rejectedReconnectAttempts']>0
            and data.get('deduplication')=='PASS' and data.get('mainThread')=='PASS'
            and data.get('sessionSwitch')=='PASS' and type(data.get('deviceTokens')) is int and data['deviceTokens']==0
            and all(marker in markers for marker in REQUIRED))

def commands_for(args, env):
    stage=env.get('GAMEBRIDGE_UPM_STAGING');cache=env.get('GAMEBRIDGE_UNITY_PACKAGE_CACHE')
    if not stage:raise ValueError('staged SDK required')
    if bool(args.gui_project)!=bool(args.gui_build_receipt):raise ValueError('GUI project/receipt required together')
    if getattr(args,'ack_known_fullscreen_notice',False) and not args.gui_project:raise ValueError('Notice input requires explicit GUI/owned binding')
    if args.platform=='ios' and args.gui_project:raise ValueError('Android GUI input cannot be used for iOS-only execution')
    commands=[]
    if args.platform!='ios':
        serial=env.get('GAMEBRIDGE_PUSH_ANDROID_SERIAL');avd=env.get('GAMEBRIDGE_PUSH_TEST_AVD_NAME');pid=env.get('GAMEBRIDGE_PUSH_EMULATOR_PID','')
        if not serial or not avd or not avd.startswith('GameBridge_V2_') or not pid.isdecimal():raise ValueError('fresh dedicated push AVD binding required')
        command=[sys.executable,'harness/run-unity-android-mock-push-e2e.py','--run-local','--staging',stage,'--serial',serial,'--expected-avd',avd,'--expected-emulator-pid',pid]
        if args.gui_project:
            if not args.expected_adb_server_pid:raise ValueError('GUI ADB server binding required')
            command+=['--gui-project',str(args.gui_project),'--gui-build-receipt',str(args.gui_build_receipt),'--expected-adb-server-pid',str(args.expected_adb_server_pid),'--startup-diagnostics']
        if getattr(args,'ack_known_fullscreen_notice',False):command+=['--ack-known-fullscreen-notice']
        if args.adb:command+=['--adb',args.adb]
        commands.append(('android',command))
    if args.platform!='android':commands.append(('ios',[sys.executable,'harness/run-unity-ios-mock-push-e2e.py','--run-local','--staging',stage,*(['--package-cache',cache] if cache else [])]))
    return commands


def main():
    p=argparse.ArgumentParser();p.add_argument('--platform',choices=('android','ios','both'),default='both')
    p.add_argument('--gui-project',type=Path);p.add_argument('--gui-build-receipt',type=Path)
    p.add_argument('--expected-adb-server-pid',type=int);p.add_argument('--adb');p.add_argument('--ack-known-fullscreen-notice',action='store_true');args=p.parse_args()
    if os.environ.get('GAMEBRIDGE_RUN_UNITY_PUSH_E2E')!='true':print('DEFERRED_ENV: explicit Unity push opt-in required');return 2
    try:commands=commands_for(args,os.environ)
    except ValueError as error:print('DEFERRED_ENV:',error);return 2
    head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip();pid=os.environ.get('GAMEBRIDGE_PUSH_EMULATOR_PID')
    for platform,command in commands:
        print('Running fresh Unity '+platform+' LOCAL_MOCK push...',flush=True)
        try:result=subprocess.run(command,cwd=ROOT,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,timeout=1500)
        except (OSError,subprocess.TimeoutExpired):print('DEFERRED_ENV: Unity push runner unavailable or timed out');return 2
        print(result.stdout,end='',flush=True)
        if result.returncode==2:return 2
        if not check_result(result.stdout,result.returncode,head,platform,pid if platform=='android' else None):print('FAIL: '+platform+' Unity push evidence incomplete');return 1
    if args.platform=='both':print('Unity push current-run PASS: Android and iOS LOCAL_MOCK Players, 2 tests')
    else:print('Unity push current-run PASS:',args.platform,'LOCAL_MOCK Player, 1 test; other platform NOT_RUN')
    return 0
if __name__=='__main__':raise SystemExit(main())
