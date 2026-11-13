#!/usr/bin/env python3
"""Exercise fail-closed checks using new fixtures and explicitly opted-in test DBs."""
import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.dont_write_bytecode = True
from result_aggregator import summarize
spec = importlib.util.spec_from_file_location('auth_runner', ROOT/'harness/run-auth-regression.py')
common = importlib.util.module_from_spec(spec); spec.loader.exec_module(common)

def summarize_lanes(lanes, expected):
    normalized = [dict(x, tests=x.get('checks', 0)) if x.get('tests', 0) == 0 and 'checks' in x else x for x in lanes]
    return summarize(normalized, expected)


def sandbox_report(path, started, code):
    result = {'name':'sandbox-fake-token', 'required':True, 'status':'FAIL', 'exitCode':code,
              'tests':0, 'failures':0, 'errors':0, 'skipped':0}
    try:
        if path.stat().st_mtime_ns < started: return result
        xml = ET.parse(path).getroot()
        for key in ('tests', 'failures', 'errors', 'skipped'): result[key] = int(xml.attrib[key])
        cases = xml.findall('testcase')
        exact = (len(cases) == 1 and cases[0].get('name') == 'sandbox rejects mock identity token with 401()' and
                 cases[0].find('failure') is None and cases[0].find('error') is None and cases[0].find('skipped') is None)
        if code == 0 and exact and result['tests'] == 1 and all(result[k] == 0 for k in ('failures','errors','skipped')):
            result['status'] = 'PASS'
        elif code == 2: result['status'] = 'DEFERRED_ENV'
    except (OSError, ET.ParseError, KeyError, ValueError):
        if code == 2: result['status'] = 'DEFERRED_ENV'
    return result


def main() -> int:
    artifacts = ROOT/'artifacts'; artifacts.mkdir(exist_ok=True)
    workspace = Path(tempfile.mkdtemp(prefix='harness-self-', dir=artifacts)); env = os.environ.copy(); env['PYTHONDONTWRITEBYTECODE'] = '1'
    lanes = []
    def expect_marker(name, command, marker, environment=None):
        code, text, _ = common.run(command, environment or env, workspace/f'{name}.log')
        passed = code == 0 and marker in text
        lane = {'name':name,'status':'PASS' if passed else ('DEFERRED_ENV' if code == 2 else 'FAIL'),
                'required':True,'tests':0,'checks':1 if passed else 0,'failures':1 if code != 2 and not passed else 0,'errors':0,'skipped':0,'exitCode':code}
        if passed and name in ('contract-negative', 'ledger-mutation'):
            try:
                if name == 'contract-negative':
                    outer = re.search(r'^Negative evidence directory: (artifacts/negative-contract-[A-Za-z0-9_-]+)$', text, re.M)
                    nested_text = (ROOT/outer.group(1)/'negative.log').read_text() if outer else ''
                    nested = re.search(r'^Evidence directory: (artifacts/contracts-[A-Za-z0-9_-]+)$', nested_text, re.M)
                    suites = json.loads((ROOT/nested.group(1)/'result.json').read_text())['suites'] if nested else []
                    natives = [x for x in suites if x['suite'] in ('kotlin','swift')]
                    cs = [x for x in suites if x['suite'] == 'csharp']
                    if (len(suites) != 3 or len(cs) != 1 or cs[0]['status'] != 'PASS' or cs[0]['exitCode'] != 0 or cs[0]['tests'] != 1 or
                        len(natives) != 2 or {x['suite'] for x in natives} != {'kotlin','swift'} or
                        any(x['status'] != 'FAIL' or x['exitCode'] != 1 or x['tests'] < 1 or x.get('failures') != 1 or x.get('skipped') != 0 for x in natives)):
                        raise ValueError('negative contract counts')
                    lane.update(tests=sum(x['tests'] for x in natives), expectedFailures=2, evidence=outer.group(1))
                else:
                    match = re.search(r'^Evidence directory: (artifacts/ledger-mutation-[A-Za-z0-9_-]+)$', text, re.M)
                    if not match: raise ValueError('ledger evidence missing')
                    files = [ET.parse(ROOT/match.group(1)/(name+'.junit.xml')).getroot() for name in ('mutation','normal')]
                    if [(int(x.get('tests','-1')),int(x.get('failures','-1')),int(x.get('errors','-1')),int(x.get('skipped','-1'))) for x in files] != [(1,1,0,0),(1,0,0,0)]:
                        raise ValueError('ledger counts')
                    lane.update(tests=2, expectedFailures=1, evidence=match.group(1))
            except (OSError, ValueError, KeyError, TypeError, ET.ParseError):
                lane.update(status='FAIL', failures=1, tests=0)
        lanes.append(lane)
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
    lanes.append({'name':'failed-and-zero-test','status':'PASS' if good else 'FAIL','required':True,'tests':0,'checks':sum(checks),'failures':0 if good else 1,'errors':0,'skipped':0,'exitCode':0 if good else 1})
    sandbox = env.get('GAMEBRIDGE_SANDBOX_TEST_DB_URL','')
    safe = bool(sandbox) and not re.search(r'(?i)([?&](?:user|password)=|://[^/]*@)',sandbox)
    if env.get('GAMEBRIDGE_RUN_AUTH_DB_TESTS') == 'true' and safe and all(env.get(k) for k in ('GAMEBRIDGE_TEST_DB_USER','GAMEBRIDGE_TEST_DB_PASSWORD')):
        lane_env = env.copy(); lane_env['GAMEBRIDGE_TEST_DB_URL'] = sandbox
        code, _, started = common.run(['backend/gradlew','-p','backend','test','--rerun-tasks','--tests','*AuthHttpIntegrationTest.*sandbox rejects mock identity token with 401*'],lane_env,workspace/'sandbox-fake-token.log')
        report_path = ROOT/'backend/build/test-results/test/TEST-com.gamebridge.auth.AuthHttpIntegrationTest.xml'
        result = sandbox_report(report_path, started, code)
        if report_path.is_file() and report_path.stat().st_mtime_ns >= started:
            shutil.copyfile(report_path, workspace/'sandbox-fake-token.junit.xml')
        lanes.append(result)
    else: lanes.append({'name':'sandbox-fake-token','status':'DEFERRED_ENV','required':True,'tests':0,'skipped':0,'exitCode':2})
    code, text, _ = common.run(['python3','harness/run-contracts.py'], env, workspace/'normal-contracts.log')
    match = re.search(r'^Evidence directory: (artifacts/contracts-[A-Za-z0-9_-]+)$', text, re.M)
    try:
        contract_report = json.loads((ROOT / match.group(1) / 'result.json').read_text()) if match else {}
        suites = contract_report['suites']
        valid = (code == 0 and len(suites) == 3 and {x['suite'] for x in suites} == {'kotlin','swift','csharp'} and
                 all(x['status'] == 'PASS' and x['exitCode'] == 0 and x['tests'] > 0 and x.get('failures',0) == 0 and x.get('skipped',0) == 0 for x in suites))
        tests = sum(x['tests'] for x in suites if x['suite'] != 'csharp') if valid else 0
    except (OSError, ValueError, KeyError, TypeError): valid = False; tests = 0
    lanes.append({'name':'normal-contracts','status':'PASS' if valid else ('DEFERRED_ENV' if code == 2 else 'FAIL'),
                  'required':True,'tests':tests,'checks':1 if valid else 0,'failures':0 if valid else 1,'errors':0,'skipped':0,'exitCode':code})
    expected = {'progress-negative','manifest-negative','package-negative','contract-negative','bridge-mutation',
                'ledger-mutation','failed-and-zero-test','sandbox-fake-token','normal-contracts'}
    # Checker invocations count as checks, not test cases; preserve fail-closed aggregation.
    summary = summarize_lanes(lanes, expected)
    report = {'scope':'harness-negative-self-check','sourceHead':subprocess.run(['git','rev-parse','HEAD'],cwd=ROOT,text=True,stdout=subprocess.PIPE,stderr=subprocess.DEVNULL,check=False).stdout.strip(),
              'workingTree':'HEAD plus uncommitted changes may be present','timestampUtc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'lanes':lanes,'summary':summary}
    (workspace/'result.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    for lane in lanes: print(f"{lane['name']}: {lane['status']} (tests={lane['tests']}, checks={lane.get('checks',0)}, expected_failures={lane.get('expectedFailures',0)}, failures={lane.get('failures',0)}, errors={lane.get('errors',0)}, skipped={lane['skipped']}, exit={lane['exitCode']})")
    print('Evidence directory:',workspace.relative_to(ROOT))
    return summary['exitCode']

if __name__ == '__main__': raise SystemExit(main())
