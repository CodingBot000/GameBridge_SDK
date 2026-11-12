#!/usr/bin/env python3
"""Opt-in real Android JNI Player and iOS Simulator C ABI UTF-8 regression."""
import importlib.util, json, os, re, subprocess, sys, tempfile, time
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
spec=importlib.util.spec_from_file_location('consumer',ROOT/'harness/run-unity-consumer-e2e.py');consumer=importlib.util.module_from_spec(spec);spec.loader.exec_module(consumer)
def main():
    if os.environ.get('GAMEBRIDGE_RUN_R09')!='true':print('DEFERRED_ENV: explicit GAMEBRIDGE_RUN_R09=true required');return 2
    stage=os.environ.get('GAMEBRIDGE_UPM_STAGING');serial=os.environ.get('GAMEBRIDGE_ANDROID_SERIAL');avd=os.environ.get('GAMEBRIDGE_TEST_AVD_NAME')
    if not stage or not serial or not avd or not avd.startswith('GameBridge_V2_'):print('DEFERRED_ENV: staging and fresh dedicated Android emulator required');return 2
    head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip();cache=os.environ.get('GAMEBRIDGE_UNITY_PACKAGE_CACHE');extra=['--package-cache',cache] if cache else []
    command=[sys.executable,'harness/run-unity-android-mock-e2e.py','--run-local','--utf8-probe','--staging',stage,'--serial',serial,'--expected-avd',avd,*extra]
    try:r=subprocess.run(command,cwd=ROOT,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,timeout=1200)
    except (OSError,subprocess.TimeoutExpired):print('DEFERRED_ENV: Android Player unavailable');return 2
    print(r.stdout,end='')
    if r.returncode==2:return 2
    if not consumer.check_result(r.stdout,r.returncode,head,'android'):print('FAIL: fresh Android Player result');return 1
    match=re.search(r'^RESULT PASS\s+EVIDENCE (artifacts/unity-android-e2e-[A-Za-z0-9_.-]+)\s*$',r.stdout,re.M)
    if not match or 'GB_UTF8_JNI_ROUNDTRIP PASS' not in (ROOT/match.group(1)/'unity-test-markers.log').read_text():print('FAIL: JNI marker missing');return 1
    output=Path(tempfile.mkdtemp(prefix='r09-ios-',dir=ROOT/'artifacts'));generated=subprocess.run(['bash','scripts/generate-ios-project.sh'],cwd=ROOT,text=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    if generated.returncode:print('DEFERRED_ENV: Xcode project generator unavailable');return 2
    sim=subprocess.run(['xcrun','simctl','create','GameBridge-CBridge-R09-'+str(int(time.time())),'com.apple.CoreSimulator.SimDeviceType.iPhone-16','com.apple.CoreSimulator.SimRuntime.iOS-18-6'],cwd=ROOT,text=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    if sim.returncode:print('DEFERRED_ENV: iOS 18.6 simulator unavailable');return 2
    bundle=output/'result.xcresult';cmd=['xcodebuild','-project',generated.stdout.strip(),'-scheme','GameBridgeCBridge','-destination','platform=iOS Simulator,id='+sim.stdout.strip(),'-resultBundlePath',str(bundle),'CODE_SIGN_IDENTITY=-','CODE_SIGNING_REQUIRED=YES','-only-testing:GameBridgeCBridgeTests/CBridgeTests/testHostPushEventRoutingAndDedup','test','-quiet']
    try:r=subprocess.run(cmd,cwd=ROOT,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,timeout=240)
    except (OSError,subprocess.TimeoutExpired):print('DEFERRED_ENV: iOS test unavailable');return 2
    (output/'xcodebuild.log').write_text(r.stdout)
    if r.returncode or not bundle.exists():print('FAIL: iOS Simulator XCTest');return 1
    report=subprocess.run(['xcrun','xcresulttool','get','test-results','summary','--path',str(bundle),'--format','json'],cwd=ROOT,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
    try:data=json.loads(report.stdout)
    except ValueError:print('FAIL: missing iOS test summary');return 1
    if report.returncode or data.get('passedTests')!=1 or data.get('failedTests')!=0 or data.get('skippedTests')!=0:print('FAIL: incomplete iOS test');return 1
    print('R09 Android JNI and iOS C ABI UTF-8 PASS; evidence:',output.relative_to(ROOT));return 0
if __name__=='__main__':raise SystemExit(main())
