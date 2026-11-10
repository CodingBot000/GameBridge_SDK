#!/usr/bin/env python3
"""Exercise fail-closed checks using new fixtures and explicitly opted-in test DBs."""
import importlib.util
import json
import os
import re
import subprocess
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.dont_write_bytecode = True
from result_aggregator import summarize
spec = importlib.util.spec_from_file_location('auth_runner', ROOT/'harness/run-auth-regression.py')
common = importlib.util.module_from_spec(spec); spec.loader.exec_module(common)

def main() -> int:
    artifacts = ROOT/'artifacts'; artifacts.mkdir(exist_ok=True)
    workspace = Path(tempfile.mkdtemp(prefix='harness-self-', dir=artifacts)); env = os.environ.copy(); env['PYTHONDONTWRITEBYTECODE'] = '1'
    lanes = []
    def expect_marker(name, command, marker, environment=None):
        code, text, _ = common.run(command, environment or env, workspace/f'{name}.log')
        passed = code == 0 and marker in text
        lanes.append({'name':name,'status':'PASS' if passed else ('DEFERRED_ENV' if code == 2 else 'FAIL'),
                      'required':True,'tests':1 if passed else 0,'skipped':0,'exitCode':code})
    expect_marker('progress-negative',['python3','harness/check-progress-negative.py'],'Progress negatives PASS')
    expect_marker('manifest-negative',['python3','harness/check-manifest-negative.py'],'Negative manifest: missing R49 rejected')
    expect_marker('package-negative',['python3','harness/check-package-negative.py'],'Package negatives PASS')
    expect_marker('contract-negative',['python3','harness/check-contract-negative.py'],'Negative contract: Kotlin and Swift rejected')
    expect_marker('bridge-mutation',['python3','harness/check-bridge-mutation.py'],'Duplicate response guard mutation: detected')
    ledger_env = env.copy(); local_url = env.get('GAMEBRIDGE_LOCAL_TEST_DB_URL','')
    if local_url: ledger_env['GAMEBRIDGE_TEST_DB_URL'] = local_url
    expect_marker('ledger-mutation',['python3','harness/check-ledger-mutation.py'],'Ledger mutation detected',ledger_env)
    zero = workspace/'zero.xml'; zero.write_text('<testsuite tests="0" failures="0" errors="0" skipped="0"/>',encoding='utf-8')
    failure = workspace/'failure.xml'; failure.write_text('<testsuite tests="1" failures="1" errors="0" skipped="0"/>',encoding='utf-8')
    checks = []
    for fixture in (zero,failure):
        code, _, _ = common.run(['python3','harness/check-junit.py',str(fixture)],env,workspace/f'{fixture.stem}.log')
        checks.append(code == 1)
    failed = subprocess.run([sys.executable,'-c','raise SystemExit(7)'],cwd=ROOT,check=False).returncode
    checks.append(failed == 7 and summarize([{'name':'failure','status':'FAIL','required':True,'tests':1,'exitCode':failed}])['exitCode'] == 1)
    good = all(checks)
    lanes.append({'name':'failed-and-zero-test','status':'PASS' if good else 'FAIL','required':True,'tests':3 if good else 0,'skipped':0,'exitCode':0 if good else 1})
    sandbox = env.get('GAMEBRIDGE_SANDBOX_TEST_DB_URL','')
    safe = bool(sandbox) and not re.search(r'(?i)([?&](?:user|password)=|://[^/]*@)',sandbox)
    if env.get('GAMEBRIDGE_RUN_AUTH_DB_TESTS') == 'true' and safe and all(env.get(k) for k in ('GAMEBRIDGE_TEST_DB_USER','GAMEBRIDGE_TEST_DB_PASSWORD')):
        lane_env = env.copy(); lane_env['GAMEBRIDGE_TEST_DB_URL'] = sandbox
        code, _, started = common.run(['backend/gradlew','-p','backend','test','--rerun-tasks','--tests','com.gamebridge.auth.AuthHttpIntegrationTest'],lane_env,workspace/'sandbox-fake-token.log')
        counts = common.junit_counts([ROOT/'backend/build/test-results/test/TEST-com.gamebridge.auth.AuthHttpIntegrationTest.xml'],started)
        test_source = (ROOT/'backend/src/test/kotlin/com/gamebridge/auth/AuthHttpIntegrationTest.kt').read_text(encoding='utf-8')
        if 'mock:identity:synthetic' not in test_source: counts = (0,0,0)
        result = common.item('sandbox-fake-token',code,counts); result['name'] = result.pop('suite'); result['required'] = True; lanes.append(result)
    else: lanes.append({'name':'sandbox-fake-token','status':'DEFERRED_ENV','required':True,'tests':0,'skipped':0,'exitCode':2})
    expect_marker('normal-contracts',['python3','harness/run-contracts.py'],'csharp: PASS')
    summary = summarize(lanes)
    report = {'scope':'harness-negative-self-check','sourceHead':subprocess.run(['git','rev-parse','HEAD'],cwd=ROOT,text=True,stdout=subprocess.PIPE,stderr=subprocess.DEVNULL,check=False).stdout.strip(),
              'workingTree':'HEAD plus uncommitted changes may be present','timestampUtc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'lanes':lanes,'summary':summary}
    (workspace/'result.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    for lane in lanes: print(f"{lane['name']}: {lane['status']} (tests={lane['tests']}, exit={lane['exitCode']})")
    print('Evidence directory:',workspace.relative_to(ROOT))
    return summary['exitCode']

if __name__ == '__main__': raise SystemExit(main())
