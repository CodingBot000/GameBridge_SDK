#!/usr/bin/env python3
"""Opt-in synthetic iOS host delegate XCTest and Unity Player callback boundary."""
import importlib.util, json, os, re, subprocess, sys, tempfile, time
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
spec=importlib.util.spec_from_file_location('consumer',ROOT/'harness/run-unity-consumer-e2e.py');consumer=importlib.util.module_from_spec(spec);spec.loader.exec_module(consumer)
def main():
    if os.environ.get('GAMEBRIDGE_RUN_R43')!='true':print('DEFERRED_ENV: explicit GAMEBRIDGE_RUN_R43=true required');return 2
    stage=os.environ.get('GAMEBRIDGE_UPM_STAGING')
    if not stage:print('DEFERRED_ENV: staged SDK required');return 2
    head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip();cache=os.environ.get('GAMEBRIDGE_UNITY_PACKAGE_CACHE');extra=['--package-cache',cache] if cache else []
    cmd=[sys.executable,'harness/run-unity-ios-mock-e2e.py','--run-local','--adhoc','--host-callback-probe','--staging',stage,*extra]
    try:r=subprocess.run(cmd,cwd=ROOT,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,timeout=1200)
    except (OSError,subprocess.TimeoutExpired):print('DEFERRED_ENV: Unity iOS Player unavailable');return 2
    print(r.stdout,end='')
    if r.returncode==2:return 2
    if not consumer.check_result(r.stdout,r.returncode,head,'ios'):print('FAIL: fresh Unity iOS Player result');return 1
    match=re.search(r'^RESULT PASS\s+EVIDENCE (artifacts/unity-ios-e2e-[A-Za-z0-9_.-]+)\s*$',r.stdout,re.M)
    if not match or 'GB_MOCK_HOST_CALLBACK PASS' not in (ROOT/match.group(1)/'unity-test-markers.log').read_text():print('FAIL: host callback marker missing');return 1
    output=Path(tempfile.mkdtemp(prefix='r43-ios-',dir=ROOT/'artifacts'));generated=subprocess.run(['bash','scripts/generate-ios-project.sh'],cwd=ROOT,text=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    if generated.returncode:print('DEFERRED_ENV: Xcode project generator unavailable');return 2
    sim=subprocess.run(['xcrun','simctl','create','GameBridge-Host-R43-'+str(int(time.time())),'com.apple.CoreSimulator.SimDeviceType.iPhone-16','com.apple.CoreSimulator.SimRuntime.iOS-18-6'],cwd=ROOT,text=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    if sim.returncode:print('DEFERRED_ENV: iOS 18.6 simulator unavailable');return 2
    bundle=output/'result.xcresult';cmd=['xcodebuild','-project',generated.stdout.strip(),'-scheme','GameBridgePushTests','-destination','platform=iOS Simulator,id='+sim.stdout.strip(),'-resultBundlePath',str(bundle),'CODE_SIGN_IDENTITY=-','CODE_SIGNING_REQUIRED=YES','-only-testing:GameBridgePushTests/PushHostTests/testSyntheticHostCallbacksAndCompletion','test','-quiet']
    try:r=subprocess.run(cmd,cwd=ROOT,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,timeout=240)
    except (OSError,subprocess.TimeoutExpired):print('DEFERRED_ENV: iOS XCTest unavailable');return 2
    (output/'xcodebuild.log').write_text(r.stdout)
    if r.returncode or not bundle.exists():print('FAIL: host delegate XCTest');return 1
    report=subprocess.run(['xcrun','xcresulttool','get','test-results','summary','--path',str(bundle),'--format','json'],cwd=ROOT,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
    try:data=json.loads(report.stdout)
    except ValueError:print('FAIL: missing host test summary');return 1
    if report.returncode or data.get('passedTests')!=1 or data.get('failedTests')!=0 or data.get('skippedTests')!=0:print('FAIL: incomplete host test');return 1
    print('R43 iOS synthetic host delegate and Unity callback PASS; evidence:',output.relative_to(ROOT));return 0
if __name__=='__main__':raise SystemExit(main())
