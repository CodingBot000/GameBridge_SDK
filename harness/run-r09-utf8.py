#!/usr/bin/env python3
"""Explicit Android JNI GUI/batch and independent iOS C ABI evidence; never fallback."""
import argparse, importlib.util, json, os, re, subprocess, sys, tempfile, uuid
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
spec=importlib.util.spec_from_file_location('consumer',ROOT/'harness/run-unity-consumer-e2e.py');consumer=importlib.util.module_from_spec(spec);spec.loader.exec_module(consumer)


def android_command(args, stage, serial, avd, cache):
    if not stage or not serial or not avd or not avd.startswith('GameBridge_V2_'):
        raise ValueError('staging and fresh dedicated Android emulator required')
    if bool(args.gui_project)!=bool(args.gui_build_receipt):raise ValueError('GUI project and receipt required together')
    command=[sys.executable,'harness/run-unity-android-mock-e2e.py','--run-local','--utf8-probe','--staging',stage,'--serial',serial,'--expected-avd',avd]
    if args.gui_project:
        if not args.expected_emulator_pid or not args.expected_adb_server_pid:raise ValueError('GUI owned emulator/server binding required')
        command+=['--gui-project',str(args.gui_project),'--gui-build-receipt',str(args.gui_build_receipt),
                  '--expected-emulator-pid',str(args.expected_emulator_pid),'--expected-adb-server-pid',str(args.expected_adb_server_pid)]
    elif cache:command+=['--package-cache',cache]
    if args.adb:command+=['--adb',args.adb]
    if args.startup_diagnostics:command+=['--startup-diagnostics']
    return command


def run_android(command, head, out):
    try:r=subprocess.run(command,cwd=ROOT,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,timeout=1200)
    except (OSError,subprocess.TimeoutExpired):return dict(status='DEFERRED_ENV',exitCode=2,errorCode='ANDROID_COMMAND_UNAVAILABLE_OR_TIMEOUT')
    (out/'android.log').write_text(r.stdout);print(r.stdout,end='')
    match=re.search(r'^RESULT (?:PASS|FAIL|DEFERRED_ENV)\s+.*?EVIDENCE (artifacts/unity-android-e2e-[A-Za-z0-9_.-]+)\s*$',r.stdout,re.M)
    evidence=match.group(1) if match else None
    child={}
    if evidence and not (ROOT/evidence).resolve().is_relative_to((ROOT/'artifacts').resolve()):evidence=None
    if evidence:
        try:child=json.loads((ROOT/evidence/'result.json').read_text())
        except (OSError,ValueError):pass
    if not isinstance(child,dict):child={}
    if r.returncode==2:return dict(status='DEFERRED_ENV',exitCode=2,evidence=evidence,errorCode=child.get('errorCode','ANDROID_DEFERRED'))
    try:valid=bool(child) and type(child.get('ledgerCount')) is int and type(child.get('ledgerDelta')) is int and consumer.check_result(r.stdout,r.returncode,head,'android')
    except (OSError,ValueError,TypeError,AttributeError):valid=False
    if not valid:
        return dict(status='FAIL',exitCode=r.returncode or 1,evidence=evidence,errorCode=child.get('errorCode','ANDROID_RESULT_INVALID'))
    if not evidence or child.get('utf8Probe') is not True or 'GB_UTF8_JNI_ROUNDTRIP PASS' not in (ROOT/evidence/'unity-test-markers.log').read_text():
        return dict(status='FAIL',exitCode=1,evidence=evidence,errorCode='JNI_MARKER_OR_PROBE_MISSING')
    return dict(status='PASS',exitCode=0,evidence=evidence,marker='GB_UTF8_JNI_ROUNDTRIP PASS',sourceHead=head,assertions='UNMEASURED')


def run_ios(out):
    device=None;result=dict(status='FAIL',exitCode=1)
    try:
        generated=subprocess.run(['bash','scripts/generate-ios-project.sh'],cwd=ROOT,text=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        if generated.returncode:return dict(status='DEFERRED_ENV',exitCode=2,errorCode='XCODE_PROJECT_UNAVAILABLE')
        sim=subprocess.run(['xcrun','simctl','create','GameBridge-CBridge-R09-'+out.name,'com.apple.CoreSimulator.SimDeviceType.iPhone-16','com.apple.CoreSimulator.SimRuntime.iOS-18-6'],cwd=ROOT,text=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        if sim.returncode:return dict(status='DEFERRED_ENV',exitCode=2,errorCode='IOS_18_6_SIMULATOR_UNAVAILABLE')
        device=str(uuid.UUID(sim.stdout.strip()));result['device']=device
        bundle=out/'result.xcresult';cmd=['xcodebuild','-project',generated.stdout.strip(),'-scheme','GameBridgeCBridge','-destination','platform=iOS Simulator,id='+device,'-resultBundlePath',str(bundle),'CODE_SIGN_IDENTITY=-','CODE_SIGNING_REQUIRED=YES','-only-testing:GameBridgeCBridgeTests/CBridgeTests/testHostPushEventRoutingAndDedup','test','-quiet']
        try:r=subprocess.run(cmd,cwd=ROOT,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,timeout=240)
        except (OSError,subprocess.TimeoutExpired):result.update(status='DEFERRED_ENV',exitCode=2,errorCode='IOS_COMMAND_UNAVAILABLE_OR_TIMEOUT');return result
        (out/'xcodebuild.log').write_text(r.stdout)
        if r.returncode or not bundle.exists():result.update(errorCode='IOS_XCTEST_FAILED',exitCode=r.returncode or 1);return result
        report=subprocess.run(['xcrun','xcresulttool','get','test-results','summary','--path',str(bundle),'--format','json'],cwd=ROOT,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
        data=json.loads(report.stdout);(out/'ios-summary.json').write_text(json.dumps(data,indent=2)+'\n')
        if report.returncode or data.get('passedTests')!=1 or data.get('failedTests')!=0 or data.get('skippedTests')!=0:result.update(errorCode='IOS_TEST_COUNT_INVALID');return result
        result.update(status='PASS',exitCode=0,tests=1,failures=0,skipped=0,evidence=str(bundle.relative_to(ROOT)));return result
    except (OSError,ValueError):result.update(errorCode='IOS_RESULT_UNAVAILABLE');return result
    finally:
        if device:
            # Only the new Simulator created by this invocation; never erase/delete.
            stopped=subprocess.run(['xcrun','simctl','shutdown',device],cwd=ROOT,text=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
            result['ownedSimulatorShutdownExitCode']=stopped.returncode
            confirmed=stopped.returncode==0
            if stopped.returncode==149:
                try:
                    listing=subprocess.run(['xcrun','simctl','list','devices','-j'],cwd=ROOT,text=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
                    confirmed=listing.returncode==0 and any(x.get('udid')==device and x.get('state')=='Shutdown' for group in json.loads(listing.stdout)['devices'].values() for x in group)
                except (ValueError,KeyError,TypeError):confirmed=False
            if not confirmed:result.update(status='FAIL',exitCode=1,errorCode='OWNED_SIMULATOR_SHUTDOWN_FAILED')


def main():
    p=argparse.ArgumentParser();p.add_argument('--platform',choices=('android','ios','both'),default='both')
    p.add_argument('--gui-project',type=Path);p.add_argument('--gui-build-receipt',type=Path)
    p.add_argument('--expected-emulator-pid',type=int);p.add_argument('--expected-adb-server-pid',type=int)
    p.add_argument('--adb');p.add_argument('--startup-diagnostics',action='store_true');args=p.parse_args()
    if os.environ.get('GAMEBRIDGE_RUN_R09')!='true':print('DEFERRED_ENV: explicit GAMEBRIDGE_RUN_R09=true required');return 2
    command=None
    if args.platform!='ios':
        try:command=android_command(args,os.environ.get('GAMEBRIDGE_UPM_STAGING'),os.environ.get('GAMEBRIDGE_ANDROID_SERIAL'),os.environ.get('GAMEBRIDGE_TEST_AVD_NAME'),os.environ.get('GAMEBRIDGE_UNITY_PACKAGE_CACHE'))
        except ValueError as error:print('DEFERRED_ENV:',error);return 2
    elif args.gui_project or args.gui_build_receipt:p.error('Android GUI input cannot be used for iOS-only execution')
    out=Path(tempfile.mkdtemp(prefix='r09-utf8-',dir=ROOT/'artifacts'));head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    report=dict(sourceHead=head,scope='independent Android JNI and iOS synthetic C ABI',platform=args.platform,android={'status':'NOT_RUN'},ios={'status':'NOT_RUN'})
    if command:report['android']=run_android(command,head,out)
    if args.platform!='android':report['ios']=run_ios(out)
    selected=[report[x] for x in ('android','ios') if args.platform in (x,'both')]
    code=1 if any(x['status']=='FAIL' for x in selected) else 2 if any(x['status']!='PASS' for x in selected) else 0
    report.update(status='PASS' if code==0 else 'FAIL' if code==1 else 'DEFERRED_ENV',exitCode=code)
    (out/'result.json').write_text(json.dumps(report,indent=2)+'\n')
    if args.platform=='both' and code==0:print('R09 Android JNI and iOS C ABI UTF-8 PASS; evidence:',out.relative_to(ROOT))
    else:print('R09',args.platform,report['status'],'Android',report['android']['status'],'iOS',report['ios']['status'],'evidence:',out.relative_to(ROOT))
    return code
if __name__=='__main__':raise SystemExit(main())
