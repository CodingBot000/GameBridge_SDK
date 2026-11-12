#!/usr/bin/env python3
"""Auth regression with an explicit sandbox DB opt-in; never uses real provider credentials."""
import json
import os
import re
import shutil
import subprocess
import tempfile
import time
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

def run(command, env, log, timeout=600):
    started = time.time_ns()
    try:
        process = subprocess.run(command, cwd=ROOT, env=env, text=True, errors='replace',
                                 stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=timeout, check=False)
        code, output = process.returncode, process.stdout
    except (OSError, subprocess.TimeoutExpired) as exc:
        code, output = 2, f'{type(exc).__name__}: suite unavailable or timed out\n'
    log.write_text(output, encoding='utf-8')
    return code, output, started

def junit_counts(paths, started):
    tests = failures = skipped = 0
    try:
        for path in paths:
            if path.stat().st_mtime_ns < started: raise ValueError('stale report')
            data = ET.parse(path).getroot().attrib
            tests += int(data['tests']); failures += int(data['failures']) + int(data['errors']); skipped += int(data['skipped'])
    except (OSError, ET.ParseError, KeyError, ValueError): return (0, 0, 0)
    return tests, failures, skipped

def item(name, code, counts):
    tests, failures, skipped = counts
    status = 'PASS' if code == 0 and tests > 0 and failures == 0 and skipped == 0 else ('DEFERRED_ENV' if code == 2 else 'FAIL')
    return {'suite':name, 'status':status, 'exitCode':code, 'tests':tests, 'failures':failures, 'skipped':skipped}

def main() -> int:
    artifacts = ROOT/'artifacts'; artifacts.mkdir(exist_ok=True)
    output = Path(tempfile.mkdtemp(prefix='auth-regression-', dir=artifacts)); env = os.environ.copy()
    env.setdefault('ANDROID_HOME', str(Path.home()/'Library/Android/sdk'))
    results = []
    code, _, started = run(['backend/gradlew','-p','backend','test','--rerun-tasks','--tests','com.gamebridge.auth.IdentityVerifierTest'], env, output/'backend-unit.log')
    results.append(item('backend-jwt-fake', code, junit_counts([ROOT/'backend/build/test-results/test/TEST-com.gamebridge.auth.IdentityVerifierTest.xml'], started)))
    db_url = env.get('GAMEBRIDGE_TEST_DB_URL', '')
    embedded_credentials = bool(re.search(r'(?i)([?&](?:user|password)=|://[^/]*@)', db_url))
    db_ready = (env.get('GAMEBRIDGE_RUN_AUTH_DB_TESTS') == 'true' and not embedded_credentials and
                all(env.get(x) for x in ('GAMEBRIDGE_TEST_DB_URL','GAMEBRIDGE_TEST_DB_USER','GAMEBRIDGE_TEST_DB_PASSWORD')))
    if db_ready:
        classes = ('AuthFlowDatabaseTest','AuthHttpIntegrationTest')
        command = ['backend/gradlew','-p','backend','test','--rerun-tasks']
        for cls in classes: command += ['--tests',f'com.gamebridge.auth.{cls}']
        code, _, started = run(command, env, output/'backend-sandbox-db.log')
        paths = [ROOT/f'backend/build/test-results/test/TEST-com.gamebridge.auth.{cls}.xml' for cls in classes]
        results.append(item('backend-sandbox-test-key-db', code, junit_counts(paths, started)))
    else: results.append(item('backend-sandbox-test-key-db', 2, (0,0,0)))
    command = ['android/gradlew','-p','android',':sdk-core:test','--rerun-tasks','--tests','com.gamebridge.LocalMockRefreshTest',
               ':sdk-android:testDebugUnitTest','--tests','com.gamebridge.android.auth.GoogleAuthProviderTest']
    code, _, started = run(command, env, output/'android.log')
    paths = [ROOT/'android/sdk-core/build/test-results/test/TEST-com.gamebridge.LocalMockRefreshTest.xml',
             ROOT/'android/sdk-android/build/test-results/testDebugUnitTest/TEST-com.gamebridge.android.auth.GoogleAuthProviderTest.xml']
    results.append(item('android-native-fake', code, junit_counts(paths, started)))
    if shutil.which('swift'):
        code, text, _ = run(['swift','test','--package-path','ios','--filter','AppleAuthProviderTests|LocalMockRefreshTests'], env, output/'swift.log')
        counts = [(int(a),int(b)) for a,b in re.findall(r'Executed (\d+) tests?, with (\d+) failures?', text)]
        tests, failures = max(counts, default=(0,0), key=lambda x:x[0]); skipped = max((int(v) for v in re.findall(r'with (\d+) tests? skipped', text)), default=0)
        results.append(item('swift-native-fake', code, (tests, failures, skipped)))
    else: results.append(item('swift-native-fake', 2, (0,0,0)))
    head = subprocess.run(['git','rev-parse','HEAD'], cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, check=False).stdout.strip()
    report = {'scope':'synthetic-auth-session-only', 'sourceHead':head, 'workingTree':'HEAD plus uncommitted changes may be present',
              'timestampUtc':time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()), 'suites':results}
    (output/'result.json').write_text(json.dumps(report,indent=2)+'\n', encoding='utf-8')
    for value in results: print(f"{value['suite']}: {value['status']} (tests={value['tests']}, exit={value['exitCode']})")
    print('Evidence directory:', output.relative_to(ROOT))
    if any(value['status']=='FAIL' for value in results): return 1
    if any(value['status']!='PASS' for value in results): return 2
    return 0

if __name__ == '__main__': raise SystemExit(main())
