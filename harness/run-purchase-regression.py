#!/usr/bin/env python3
"""Run isolated purchase regressions; missing DB/backend lanes never count as passes."""
import importlib.util
import json
import os
import re
import shutil
import subprocess
import tempfile
import time
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.dont_write_bytecode = True
spec = importlib.util.spec_from_file_location('auth_runner', ROOT/'harness/run-auth-regression.py')
common = importlib.util.module_from_spec(spec); spec.loader.exec_module(common)

def safe_url(value): return bool(value) and not re.search(r'(?i)([?&](?:user|password)=|://[^/]*@)', value)
def swift_counts(text):
    values = [(int(a), int(b)) for a,b in re.findall(r'Executed (\d+) tests?, with (\d+) failures?', text)]
    tests, failures = max(values, default=(0,0), key=lambda x:x[0])
    skipped = max((int(x) for x in re.findall(r'with (\d+) tests? skipped', text)), default=0)
    return tests, failures, skipped

def main() -> int:
    artifacts = ROOT/'artifacts'; artifacts.mkdir(exist_ok=True)
    output = Path(tempfile.mkdtemp(prefix='purchase-regression-', dir=artifacts)); env = os.environ.copy()
    env.setdefault('ANDROID_HOME', str(Path.home()/'Library/Android/sdk')); env.pop('GAMEBRIDGE_MUTATE_LEDGER_TEST', None)
    results = []; db_creds = all(env.get(k) for k in ('GAMEBRIDGE_TEST_DB_USER','GAMEBRIDGE_TEST_DB_PASSWORD'))
    local = env.get('GAMEBRIDGE_LOCAL_TEST_DB_URL', ''); sandbox = env.get('GAMEBRIDGE_SANDBOX_TEST_DB_URL', '')
    if env.get('GAMEBRIDGE_RUN_DB_TESTS') == 'true' and db_creds and safe_url(local):
        lane = env.copy(); lane['GAMEBRIDGE_TEST_DB_URL'] = local
        classes = ('LedgerInvariantDatabaseTest','GoogleGrantDatabaseTest','AppleGrantDatabaseTest','FinalizationDatabaseTest','PurchaseBindingsDatabaseTest')
        command = ['backend/gradlew','-p','backend','test','--rerun-tasks']
        for cls in classes: command += ['--tests',f'com.gamebridge.purchase.{cls}']
        code, _, started = common.run(command, lane, output/'local-db.log')
        paths = [ROOT/f'backend/build/test-results/test/TEST-com.gamebridge.purchase.{cls}.xml' for cls in classes]
        results.append(common.item('local-postgres-fixtures', code, common.junit_counts(paths, started)))
    else: results.append(common.item('local-postgres-fixtures', 2, (0,0,0)))
    if env.get('GAMEBRIDGE_RUN_AUTH_DB_TESTS') == 'true' and db_creds and safe_url(sandbox):
        lane = env.copy(); lane['GAMEBRIDGE_TEST_DB_URL'] = sandbox
        classes = ('GooglePurchaseHttpIntegrationTest','ApplePurchaseHttpIntegrationTest')
        command = ['backend/gradlew','-p','backend','test','--rerun-tasks']
        for cls in classes: command += ['--tests',f'com.gamebridge.purchase.{cls}']
        code, _, started = common.run(command, lane, output/'sandbox-db.log')
        paths = [ROOT/f'backend/build/test-results/test/TEST-com.gamebridge.purchase.{cls}.xml' for cls in classes]
        results.append(common.item('sandbox-http-fixtures', code, common.junit_counts(paths, started)))
    else: results.append(common.item('sandbox-http-fixtures', 2, (0,0,0)))
    command = ['android/gradlew','-p','android',':sdk-core:test','--rerun-tasks','--tests','com.gamebridge.LocalMockRecoveryTest',
               ':sdk-android:testDebugUnitTest','--tests','com.gamebridge.android.purchase.GooglePlayBillingProviderTest']
    code, _, started = common.run(command, env, output/'android.log')
    paths = [ROOT/'android/sdk-core/build/test-results/test/TEST-com.gamebridge.LocalMockRecoveryTest.xml',
             ROOT/'android/sdk-android/build/test-results/testDebugUnitTest/TEST-com.gamebridge.android.purchase.GooglePlayBillingProviderTest.xml']
    results.append(common.item('android-native-fake', code, common.junit_counts(paths, started)))
    if shutil.which('swift'):
        code, text, _ = common.run(['swift','test','--package-path','ios','--filter','StoreKitBillingProviderTests|LocalMockRecoveryTests|PurchaseCoordinatorTests|XcodeAttemptJournalTests|XcodeMockClientTests'], env, output/'swift.log')
        results.append(common.item('swift-native-fake', code, swift_counts(text)))
    else: results.append(common.item('swift-native-fake', 2, (0,0,0)))
    if env.get('GAMEBRIDGE_RUN_LOCAL_CLIENT_TEST') == 'true' and env.get('GAMEBRIDGE_DEV_AUTH_KEY'):
        command = ['android/gradlew','-p','android',':sdk-core:test','--rerun-tasks','--tests',
                   'com.gamebridge.LocalMockIntegrationTest.persisted mock transaction recovers after committed response is lost', '--tests',
                   'com.gamebridge.LocalMockIntegrationTest.native client uses server authoritative wallet and restores session']
        code, _, started = common.run(command, env, output/'android-loss.log')
        results.append(common.item('android-local-response-loss', code, common.junit_counts([ROOT/'android/sdk-core/build/test-results/test/TEST-com.gamebridge.LocalMockIntegrationTest.xml'], started)))
        if shutil.which('swift'):
            code, text, _ = common.run(['swift','test','--package-path','ios','--filter','LocalMockIntegrationTests.testPersistedMockTransactionRecoversAfterCommittedResponseIsLost|LocalMockIntegrationTests.testLocalServerWalletAndRestore'], env, output/'swift-loss.log')
            results.append(common.item('swift-local-response-loss', code, swift_counts(text)))
        else: results.append(common.item('swift-local-response-loss', 2, (0,0,0)))
    else:
        results.extend([common.item('android-local-response-loss', 2, (0,0,0)), common.item('swift-local-response-loss', 2, (0,0,0))])
    if env.get('GAMEBRIDGE_RUN_XCODE_STOREKIT_HARNESS') == 'true':
        code, text, _ = common.run(['python3','harness/run-xcode-storekit-e2e.py','--run-local'], env, output/'xcode-local-db.log')
        match = re.search(r'Evidence directory: (artifacts/xcode-storekit-e2e-[A-Za-z0-9_.-]+)', text)
        counts = (0,0,0)
        if match:
            try:
                result_path = (ROOT/match.group(1)/'result.json').resolve()
                if result_path.is_relative_to(artifacts.resolve()):
                    result = json.loads(result_path.read_text(encoding='utf-8'))
                    source = subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
                    if result.get('sourceHead') == source and result.get('status') == 'PASS' and result.get('passed') == 1 and result.get('skipped') == 0:
                        counts = (1,0,0)
            except (OSError,ValueError,subprocess.CalledProcessError): pass
        results.append(common.item('xcode-storekit-local-db-recovery',code,counts))
    else: results.append(common.item('xcode-storekit-local-db-recovery',2,(0,0,0)))
    head = subprocess.run(['git','rev-parse','HEAD'], cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, check=False).stdout.strip()
    report = {'scope':'synthetic-purchase-regression-only','sourceHead':head,'workingTree':'HEAD plus uncommitted changes may be present',
              'timestampUtc':time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),'suites':results}
    (output/'result.json').write_text(json.dumps(report,indent=2)+'\n', encoding='utf-8')
    for value in results: print(f"{value['suite']}: {value['status']} (tests={value['tests']}, exit={value['exitCode']})")
    print('Evidence directory:', output.relative_to(ROOT))
    if any(value['status']=='FAIL' for value in results): return 1
    if any(value['status']!='PASS' for value in results): return 2
    return 0

if __name__ == '__main__': raise SystemExit(main())
