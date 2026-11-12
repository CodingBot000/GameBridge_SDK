#!/usr/bin/env python3
"""Aggregate executed evidence and preserve missing, failed and external states."""
import argparse
import json
import os
import platform
import re
import subprocess
import sys
import tempfile
import time
from pathlib import Path
sys.dont_write_bytecode = True
from result_aggregator import summarize, runner_inconsistent

ROOT = Path(__file__).resolve().parent.parent

def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--strict-local', action='store_true'); mode.add_argument('--available', action='store_true')
    args = parser.parse_args(); env = os.environ.copy(); env['PYTHONDONTWRITEBYTECODE'] = '1'
    artifacts = ROOT/'artifacts'; artifacts.mkdir(exist_ok=True)
    output = Path(tempfile.mkdtemp(prefix='verify-all-', dir=artifacts)); lanes = []
    head = subprocess.run(['git','rev-parse','HEAD'],cwd=ROOT,text=True,stdout=subprocess.PIPE,stderr=subprocess.DEVNULL,check=False).stdout.strip()
    dirty = bool(subprocess.run(['git','status','--porcelain'],cwd=ROOT,text=True,stdout=subprocess.PIPE,stderr=subprocess.DEVNULL,check=False).stdout.strip())
    def execute(name, command, environment=None):
        print(f'Running {name}...', flush=True)
        try:
            result = subprocess.run(command,cwd=ROOT,env=environment or env,text=True,errors='replace',stdout=subprocess.PIPE,
                                    stderr=subprocess.STDOUT,timeout=3600 if name == 'push' and env.get('GAMEBRIDGE_RUN_UNITY_PUSH_E2E') == 'true' else 1200,check=False)
            code, text = result.returncode, result.stdout
        except (OSError,subprocess.TimeoutExpired) as exc:
            code, text = 2, f'{type(exc).__name__}: suite unavailable or timed out\n'
        log = output/f'{name}.log'; log.write_text(text,encoding='utf-8')
        return code,text,log.relative_to(ROOT).as_posix()
    def simple(name, command, marker, environment=None):
        code,text,log = execute(name,command,environment)
        count = 1 if marker in text else 0
        if name == 'aggregation-self':
            match = re.search(r'Ran (\d+) tests?', text); count = int(match.group(1)) if match else 0
        if name == 'unity-editor-runtime':
            match = re.search(r'Unity consumer tests PASS: (\d+) executed', text); count = int(match.group(1)) if match else 0
        if name == 'unity-pii-e2e':
            count = 2 if marker in text else 0
        if name == 'purchase-verifier':
            match = re.search(r'Purchase verifier PASS: (\d+) synthetic tests', text); count = int(match.group(1)) if match else 0
        if name == 'lifecycle-stress':
            match = re.search(r'"samples"\s*:\s*(\d+)', text)
            count = int(match.group(1)) if match and '"liveClients": 0' in text and '"liveTransports": 0' in text else 0
        passed = code == 0 and marker in text and count > 0
        status = 'PASS' if passed else ('DEFERRED_ENV' if code == 2 else 'FAIL')
        lanes.append({'name':name,'status':status,'required':True,'tests':count if passed else 0,'skipped':0,'exitCode':code,'command':command,'evidence':log})
    def nested(name, command):
        code,text,log = execute(name,command)
        match = re.search(r'^Evidence directory: (artifacts/[A-Za-z0-9_.-]+)$',text,re.M)
        report = None
        if match:
            path = (ROOT/match.group(1)/'result.json').resolve()
            try:
                if path.is_relative_to(artifacts.resolve()): report = json.loads(path.read_text(encoding='utf-8'))
            except (OSError,ValueError): pass
        if not isinstance(report,dict) or not isinstance(report.get('suites'),list) or not report['suites'] or report.get('sourceHead') != head:
            lanes.append({'name':name,'status':'DEFERRED_ENV' if code == 2 else 'FAIL','required':True,'tests':0,'skipped':0,'exitCode':code,'command':command,'evidence':log}); return
        start = len(lanes)
        for item in report['suites']:
            lanes.append({'name':name+'/'+str(item.get('suite','?')), 'status':item.get('status','FAIL'), 'required':True,
                          'tests':item.get('tests',0), 'skipped':item.get('skipped',0), 'failures':item.get('failures',0),
                          'exitCode':item.get('exitCode',1), 'command':command, 'evidence':match.group(1)+'/result.json'})
        statuses = [value['status'] for value in lanes[start:]]
        if runner_inconsistent(code, statuses):
            lanes.append({'name':name+'/runner-consistency','status':'FAIL','required':True,'tests':0,'skipped':0,'exitCode':code,'command':command,'evidence':log})
    simple('harness-self',['python3','harness/run-self-check.py'],'normal-contracts: PASS')
    simple('progress',['python3','scripts/verify-progress.py'],'Progress ledger consistency checks passed')
    simple('manifest',['python3','harness/check-manifest.py'],'Manifest inventory valid')
    simple('api-baseline',['python3','harness/check-api-baseline.py'],'Baseline source comparison PASS')
    simple('api-baseline-negative',['python3','harness/check-api-baseline-negative.py'],'Public API mutation detected')
    simple('csharp-compat',['bash','scripts/check-csharp-compat.sh'],'Legacy C# consumer source: PASS')
    simple('aggregation-self',['python3','-m','unittest','discover','-s','harness','-p','test_aggregation.py','-v'],'OK')
    simple('progress-negative',['python3','harness/check-progress-negative.py'],'Progress negatives PASS')
    simple('manifest-negative',['python3','harness/check-manifest-negative.py'],'Negative manifest: missing R49 rejected')
    simple('contract-negative',['python3','harness/check-contract-negative.py'],'Negative contract: Kotlin and Swift rejected')
    nested('contracts',['python3','harness/run-contracts.py'])
    simple('bridge-mutation',['python3','harness/check-bridge-mutation.py'],'Duplicate response guard mutation: detected')
    simple('lifecycle-stress',['bash','scripts/stress-csharp-lifecycle.sh'],'"samples": 100')
    simple('r50-negative',['python3','harness/run-r50.py'],'R50 PASS:')
    simple('purchase-verifier',['python3','harness/run-purchase-verifier.py'],'Purchase verifier PASS:')
    simple('session-replay',['python3','harness/run-session-replay.py'],'Local session replay PASS:')
    simple('push-router-scenarios',['python3','harness/run-push-router-scenarios.py'],'Push router scenarios PASS:')
    simple('push-ownership',['python3','harness/run-push-ownership.py'],'Push ownership PASS:')
    simple('android-dependency-negative',['python3','harness/check-android-dependency-negative.py'],'Android dependency negative PASS:')
    simple('ios-xcframework-negative',['python3','harness/check-ios-xcframework-negative.py'],'iOS XCFramework negatives PASS:')
    nested('auth',['python3','harness/run-auth-regression.py'])
    nested('purchase',['python3','harness/run-purchase-regression.py'])
    ledger_env = env.copy()
    if env.get('GAMEBRIDGE_LOCAL_TEST_DB_URL'): ledger_env['GAMEBRIDGE_TEST_DB_URL'] = env['GAMEBRIDGE_LOCAL_TEST_DB_URL']
    simple('ledger-mutation',['python3','harness/check-ledger-mutation.py'],'Ledger mutation detected',ledger_env)
    nested('push',['python3','harness/run-push-regression.py'])
    pii_evidence, pii_nonce = env.get('GAMEBRIDGE_UNITY_PII_EVIDENCE'), env.get('GAMEBRIDGE_UNITY_PII_NONCE')
    if pii_evidence and pii_nonce:
        simple('unity-pii-e2e',['python3','harness/check-unity-pii-evidence.py',pii_evidence,pii_nonce],'Unity PII current-run PASS:')
    else:
        lanes.append({'name':'unity-pii-e2e','status':'DEFERRED_ENV','required':True,'tests':0,'skipped':0,'exitCode':2,
                      'command':['python3','harness/check-unity-pii-evidence.py'],'evidence':'docs/PROGRESS.md','reason':'current-run PII Player evidence not supplied'})
    manifest = json.loads((ROOT/'harness/regression-manifest.json').read_text(encoding='utf-8'))
    partial = [entry['id'] for entry in manifest['scenarios'] if entry.get('required') and entry.get('coverage') == 'PARTIAL']
    unimplemented = [entry['id'] for entry in manifest['scenarios'] if entry.get('required') and entry.get('coverage') == 'NOT_IMPLEMENTED']
    incomplete = partial + unimplemented
    coverage_status = 'NOT_IMPLEMENTED' if unimplemented else 'PARTIAL' if partial else 'PASS'
    lanes.append({'name':'scenario-coverage','status':coverage_status,'required':True,
                  'tests':0 if incomplete else len(manifest['scenarios']),'skipped':0,'exitCode':1 if incomplete else 0,
                  'command':['python3','harness/check-manifest.py'],'evidence':'harness/regression-manifest.json',
                  'partialCount':len(partial),'unimplementedCount':len(unimplemented)})
    if env.get('GAMEBRIDGE_RUN_UNITY_EDITOR') == 'true':
        simple('unity-editor-runtime',['bash','scripts/build-unity.sh','--editor-smoke'],'Unity consumer tests PASS:')
    else:
        lanes.append({'name':'unity-editor-runtime','status':'NOT_RUN','required':True,'tests':0,'skipped':0,'exitCode':2,
                      'command':['bash','scripts/build-unity.sh','--editor-smoke'],'evidence':'docs/PROGRESS.md','reason':'Editor runner not opted in; ENV-002 is separately recorded'})
    progress = (ROOT/'docs/PROGRESS.md').read_text(encoding='utf-8')
    failed_rows = []
    for line in progress.splitlines():
        if re.match(r'^\| P\d\d-T\d\d \|',line):
            cells = [cell.strip() for cell in line.strip().strip('|').split('|')]
            if len(cells) == 7 and cells[3] == 'FAIL': failed_rows.append(cells[0])
    if failed_rows:
        lanes.append({'name':'recorded-unresolved-failures','status':'FAIL','required':True,'tests':0,'skipped':0,'exitCode':1,
                      'command':[],'evidence':'docs/PROGRESS.md','reason':'previous failures not rerun by this command','tasks':failed_rows})
    required_names = {
        'harness-self', 'progress', 'manifest', 'api-baseline', 'api-baseline-negative', 'csharp-compat',
        'aggregation-self', 'progress-negative', 'manifest-negative', 'contract-negative', 'bridge-mutation',
        'lifecycle-stress', 'r50-negative', 'purchase-verifier', 'session-replay', 'push-router-scenarios', 'push-ownership', 'android-dependency-negative', 'ios-xcframework-negative', 'ledger-mutation', 'scenario-coverage', 'unity-editor-runtime', 'unity-pii-e2e',
        *(f'contracts/{name}' for name in ('kotlin','swift','csharp')),
        *(f'auth/{name}' for name in ('backend-jwt-fake','backend-sandbox-test-key-db','android-native-fake','swift-native-fake')),
        *(f'purchase/{name}' for name in ('local-postgres-fixtures','sandbox-http-fixtures','android-native-fake','swift-native-fake',
                                         'android-local-response-loss','swift-local-response-loss','xcode-storekit-local-db-recovery','xcode-storekit-process-recovery')),
        *(f'push/{name}' for name in ('backend-push-fake','sandbox-push-http-fake','android-push-fake','swift-push-fake',
                                     'ios-host-simulator-synthetic','mock-permission-denied','upm-staging-integrity','package-negative-fixtures',
                                     'local-push-native-db-e2e','unity-player-notifications')),
    }
    if failed_rows: required_names.add('recorded-unresolved-failures')
    summary = summarize(lanes, required_names)
    external_tasks = re.findall(r'^\| (P\d\d-T\d\d) \|[^\n]*\| WAITING_USER \|',progress,re.M)
    external_waits = len(external_tasks)
    report = {'mode':'strict-local' if args.strict_local else 'available','sourceHead':head,'sourceDirty':dirty,
              'timestampUtc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'environment':{'os':platform.platform()},
              'summary':summary,'lanes':lanes,'external':{'status':'WAITING_USER' if external_waits else 'NOT_RUN','taskCount':external_waits,'tasks':external_tasks}}
    (output/'result.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    lines = ['# Local verification summary','',f"Source: `{head}`; working tree dirty: {dirty}.",f"Overall: **{summary['status']}** (exit {summary['exitCode']}).",'', '| Lane | Status | Tests | Skipped |', '|---|---|---:|---:|']
    lines += [f"| {lane['name']} | {lane['status']} | {lane['tests']} | {lane['skipped']} |" for lane in lanes]
    lines += ['',f"External: {report['external']['status']} ({external_waits} tasks); not an external test pass."]
    (output/'summary.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    print(f"Overall: {summary['status']} (exit {summary['exitCode']}); external {report['external']['status']} ({external_waits} tasks)")
    print('Evidence directory:',output.relative_to(ROOT))
    return summary['exitCode']

if __name__ == '__main__': raise SystemExit(main())
