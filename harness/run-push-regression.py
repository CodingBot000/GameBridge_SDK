#!/usr/bin/env python3
"""Push and packaging evidence; no fake lane stands in for remote delivery or Unity."""
import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.dont_write_bytecode = True
spec = importlib.util.spec_from_file_location('auth_runner', ROOT/'harness/run-auth-regression.py')
common = importlib.util.module_from_spec(spec); spec.loader.exec_module(common)

def swift_counts(text):
    values = [(int(a),int(b)) for a,b in re.findall(r'Executed (\d+) tests?, with (\d+) failures?', text)]
    tests, failures = max(values, default=(0,0), key=lambda x:x[0])
    return tests, failures, max((int(x) for x in re.findall(r'with (\d+) tests? skipped', text)), default=0)

def main() -> int:
    artifacts = ROOT/'artifacts'; artifacts.mkdir(exist_ok=True)
    output = Path(tempfile.mkdtemp(prefix='push-regression-', dir=artifacts)); env = os.environ.copy()
    env.setdefault('ANDROID_HOME', str(Path.home()/'Library/Android/sdk')); results = []
    backend = ('PushPoliciesTest','PushRetryWorkerTest','TokenCipherTest','PublicServiceConfigControllerTest','DevPushProductionRouteTest')
    command = ['backend/gradlew','-p','backend','test','--rerun-tasks']
    for cls in backend: command += ['--tests',f'com.gamebridge.push.{cls}']
    code, _, started = common.run(command, env, output/'backend.log')
    results.append(common.item('backend-push-fake', code, common.junit_counts([ROOT/f'backend/build/test-results/test/TEST-com.gamebridge.push.{cls}.xml' for cls in backend],started)))
    url = env.get('GAMEBRIDGE_TEST_DB_URL',''); safe = bool(url) and not re.search(r'(?i)([?&](?:user|password)=|://[^/]*@)',url)
    if env.get('GAMEBRIDGE_RUN_AUTH_DB_TESTS') == 'true' and safe and all(env.get(x) for x in ('GAMEBRIDGE_TEST_DB_USER','GAMEBRIDGE_TEST_DB_PASSWORD')):
        code, _, started = common.run(['backend/gradlew','-p','backend','test','--rerun-tasks','--tests','com.gamebridge.push.SandboxPushHttpIntegrationTest'], env, output/'sandbox-http.log')
        results.append(common.item('sandbox-push-http-fake', code, common.junit_counts([ROOT/'backend/build/test-results/test/TEST-com.gamebridge.push.SandboxPushHttpIntegrationTest.xml'],started)))
    else: results.append(common.item('sandbox-push-http-fake',2,(0,0,0)))
    command = ['android/gradlew','-p','android',':sdk-core:test','--rerun-tasks','--tests','com.gamebridge.PushPayloadTest','--tests','com.gamebridge.PushRouterTest',
               ':sdk-android:testDebugUnitTest','--tests','com.gamebridge.android.push.AndroidPushHostAdapterTest',
               ':sdk-unity-bridge:testDebugUnitTest','--tests','com.gamebridge.bridge.HostPushDeliveryTest']
    code, _, started = common.run(command, env, output/'android.log')
    paths = [ROOT/'android/sdk-core/build/test-results/test/TEST-com.gamebridge.PushPayloadTest.xml',ROOT/'android/sdk-core/build/test-results/test/TEST-com.gamebridge.PushRouterTest.xml',
             ROOT/'android/sdk-android/build/test-results/testDebugUnitTest/TEST-com.gamebridge.android.push.AndroidPushHostAdapterTest.xml',
             ROOT/'android/sdk-unity-bridge/build/test-results/testDebugUnitTest/TEST-com.gamebridge.bridge.HostPushDeliveryTest.xml']
    results.append(common.item('android-push-fake',code,common.junit_counts(paths,started)))
    if shutil.which('swift'):
        code, text, _ = common.run(['swift','test','--package-path','ios','--filter','PushRouterTests|PushPayloadTests|LocalMockMaintenanceTests|CBridgeTests'],env,output/'swift.log')
        results.append(common.item('swift-push-fake',code,swift_counts(text)))
    else: results.append(common.item('swift-push-fake',2,(0,0,0)))
    project, simulator = env.get('GAMEBRIDGE_IOS_PROJECT'), env.get('GAMEBRIDGE_IOS_SIMULATOR_ID')
    if project and simulator and Path(project).is_dir() and shutil.which('xcodebuild') and shutil.which('xcrun'):
        result_path = output/'push-host.xcresult'
        command = ['xcodebuild','-project',project,'-scheme','GameBridgePushTests','-destination',f'platform=iOS Simulator,id={simulator}',
                   '-resultBundlePath',str(result_path),'CODE_SIGN_IDENTITY=-','CODE_SIGNING_REQUIRED=YES','-only-testing:GameBridgePushTests/PushHostTests','test','-quiet']
        code, _, _ = common.run(command,env,output/'ios-host.log'); counts = (0,0,0)
        if result_path.exists():
            try:
                summary = subprocess.run(['xcrun','xcresulttool','get','test-results','summary','--path',str(result_path),'--format','json'],
                                         cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, timeout=30, check=False)
                data = json.loads(summary.stdout) if summary.returncode == 0 else {}
                counts = (int(data.get('totalTestCount',0)),int(data.get('failedTests',0)),int(data.get('skippedTests',0)))
            except (OSError, ValueError, subprocess.TimeoutExpired): pass
        results.append(common.item('ios-host-simulator-synthetic',code,counts))
    else: results.append(common.item('ios-host-simulator-synthetic',2,(0,0,0)))
    staging = env.get('GAMEBRIDGE_UPM_STAGING')
    if staging:
        code, text, _ = common.run(['python3','harness/check-staging.py',staging],env,output/'staging.log')
        results.append(common.item('upm-staging-integrity',code,(1 if 'Staging integrity PASS:' in text else 0,0,0)))
    else: results.append(common.item('upm-staging-integrity',2,(0,0,0)))
    code, text, _ = common.run(['python3','harness/check-package-negative.py'],env,output/'package-negative.log')
    results.append(common.item('package-negative-fixtures',code,(1 if 'Package negatives PASS:' in text else 0,0,0)))
    if env.get('GAMEBRIDGE_RUN_MOCK_PUSH_HARNESS') == 'true':
        code, text, _ = common.run(['python3','harness/run-mock-push-e2e.py','--run-local'],env,output/'mock-e2e.log')
        match = re.search(r'Evidence directory: (artifacts/mock-push-e2e-[A-Za-z0-9_.-]+)', text)
        counts = (0,0,0)
        if match:
            try:
                report_path = (ROOT/match.group(1)/'result.json').resolve()
                if report_path.is_relative_to(artifacts.resolve()):
                    data = json.loads(report_path.read_text(encoding='utf-8'))
                    head = subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
                    if data.get('sourceHead') == head and data.get('status') == 'PASS' and len(data.get('suites',[])) == 2 and all(x.get('status') == 'PASS' for x in data['suites']): counts = (2,0,0)
            except (OSError,ValueError,subprocess.CalledProcessError): pass
        results.append(common.item('local-push-native-db-e2e',code,counts))
    else: results.append(common.item('local-push-native-db-e2e',2,(0,0,0)))
    results.append({'suite':'unity-player-notifications','status':'DEFERRED_ENV','exitCode':2,'tests':0,'failures':0,'skipped':0})
    head = subprocess.run(['git','rev-parse','HEAD'],cwd=ROOT,text=True,stdout=subprocess.PIPE,stderr=subprocess.DEVNULL,check=False).stdout.strip()
    report = {'scope':'push-and-package-partial','sourceHead':head,'workingTree':'HEAD plus uncommitted changes may be present',
              'timestampUtc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'suites':results}
    (output/'result.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    for item in results: print(f"{item['suite']}: {item['status']} (tests={item['tests']}, exit={item['exitCode']})")
    print('Evidence directory:',output.relative_to(ROOT))
    if any(item['status'] in ('FAIL','NOT_IMPLEMENTED') for item in results): return 1
    if any(item['status']!='PASS' for item in results): return 2
    return 0

if __name__ == '__main__': raise SystemExit(main())
