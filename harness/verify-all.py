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
import hashlib
import uuid
from pathlib import Path
sys.dont_write_bytecode = True
from result_aggregator import summarize, runner_inconsistent
from error_contract import copy_error_evidence
from measurement_contract import measured_lane, valid_checker
from execution_evidence import observe, valid_observation, metadata, source_identity

from process_output import timeout_output

ROOT = Path(__file__).resolve().parent.parent

def scenario_mapping_lane(manifest, checker, root):
    scenarios = manifest.get('scenarios', [])
    partial = [x['id'] for x in scenarios if x.get('required') and x.get('coverage') == 'PARTIAL']
    unimplemented = [x['id'] for x in scenarios if x.get('required') and x.get('coverage') == 'NOT_IMPLEMENTED']
    path = Path(checker.get('evidence', '')) if checker else Path()
    evidence_ok = (checker is not None and checker.get('name') == 'manifest' and checker.get('status') == 'PASS' and
                   checker.get('exitCode') == 0 and checker.get('tests') == 0 and valid_checker(checker) and bool(checker.get('evidence')) and
                   not path.is_absolute() and '..' not in path.parts and (root/path).is_file() and
                   (root/path).resolve().is_relative_to(root.resolve()))
    status = ('FAIL' if not evidence_ok else 'NOT_IMPLEMENTED' if unimplemented else 'PARTIAL' if partial else 'PASS')
    return {'name':'scenario-coverage','status':status,'required':True,'tests':0,'checks':1 if evidence_ok else 0,
            'failures':0,'measurement':'checker','samples':0,'players':0,'errors':None,'errorModel':'checker-exit','evidenceKind':'static-mapping','executionStatus':'NOT_RUN','mappedScenarios':len(scenarios),
            'skipped':0,'exitCode':0 if status == 'PASS' else 1,'command':checker.get('command',[]) if checker else [],
            'evidence':checker.get('evidence','') if checker else '',
            'checkerEvidence':checker.get('checkerEvidence') if checker else None, 'partialCount':len(partial),'unimplementedCount':len(unimplemented)}


def nested_lane(name, item, command, evidence):
    fields = ('tests','checks','samples','players','failures','errors','skipped','exitCode','errorModel','measurement','checkerEvidence')
    return {'name':name+'/'+str(item.get('suite','?')), 'status':item.get('status','FAIL'), 'required':True,
            **{key:item[key] for key in fields if key in item},
            'command':item.get('command',command),'evidence':item.get('evidence',evidence), 'producerEvidence':evidence}



def lane_row(lane):
    errors = lane['errors'] if 'errors' in lane and lane['errors'] is not None else ('UNMEASURED' if 'errors' in lane or lane.get('errorModel') in ('included-in-failures','checker-exit') else 'MISSING')
    return f"| {lane['name']} | {lane['status']} | {lane.get('tests','MISSING')} | {lane.get('checks','MISSING')} | {lane.get('samples','MISSING')} | {lane.get('players','MISSING')} | {lane.get('failures','MISSING')} | {errors} | {lane.get('errorModel','UNSPECIFIED')} | {lane.get('skipped','MISSING')} | {lane.get('exitCode','MISSING')} | {lane.get('measurement','MISSING')} |"



def collect_nested(name, command, code, text, observation, required_suites):
    """Only a report emitted inside this observed invocation is eligible."""
    invalid={'name':name+'/evidence','status':'DEFERRED_ENV' if code==2 else 'FAIL',
             'required':True,'tests':0,'skipped':0,'exitCode':code,'command':command,'evidence':observation['path']}
    try:
        if not valid_observation(observation):raise ValueError('invalid parent observation')
        matches=re.findall(r'^Evidence directory: (artifacts/[A-Za-z0-9_.-]+)$',text,re.M)
        if len(matches)!=1:raise ValueError('ambiguous report')
        path=ROOT/matches[0]/'result.json'
        if path.is_symlink() or not path.resolve().is_relative_to(ROOT/'artifacts'):raise ValueError('report path')
        if not observation['startedNs']<=path.stat().st_mtime_ns<=observation['finishedNs']:raise ValueError('stale report')
        report=json.loads(path.read_text())
        if report.get('runId')!=observation['invocationId']:raise ValueError('wrong invocation')
        if any(report.get(k)!=observation[k] for k in ('sourceHead','sourceDigest')):raise ValueError('wrong source')
        items=report.get('suites',report.get('lanes'))
        if not isinstance(items,list) or not items:raise ValueError('empty report')
        lanes=[]
        for item in items:
            if not isinstance(item,dict):raise ValueError('invalid child')
            child=dict(item,suite=item.get('suite',item.get('name','?')))
            lane=nested_lane(name,child,command,str(path))
            lane.update(parentExecution=observation,producerSha256=hashlib.sha256(path.read_bytes()).hexdigest())
            lanes.append(lane)
        names={name+'/'+x for x in required_suites}
        child_summary=summarize(lanes,names)
        statuses=[x['status'] for x in lanes]
        if runner_inconsistent(code,statuses) or child_summary['exitCode']!=code:
            lanes.append({**invalid,'status':'FAIL'})
        return lanes
    except (OSError,ValueError,KeyError,TypeError):return [invalid]

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
        started=time.time_ns(); invocation=uuid.uuid4().hex
        child_env=(environment or env).copy();child_env['GAMEBRIDGE_HARNESS_RUN_ID']=invocation
        try:
            result = subprocess.run(command,cwd=ROOT,env=child_env,text=True,errors='replace',stdout=subprocess.PIPE,
                                    stderr=subprocess.STDOUT,timeout=3600 if name == 'push' and env.get('GAMEBRIDGE_RUN_UNITY_PUSH_E2E') == 'true' else 1200,check=False)
            code, text = result.returncode, result.stdout
        except (OSError,subprocess.TimeoutExpired) as exc:
            code, text = 2, timeout_output(exc) if isinstance(exc,subprocess.TimeoutExpired) else f'{type(exc).__name__}: suite unavailable\n'
        log = output/f'{name}.log'; log.write_text(text,encoding='utf-8')
        return code,text,log.relative_to(ROOT).as_posix(),observe(command,code,text,log,started,invocation)
    def simple(name, command, marker, environment=None):
        code,text,log,observation = execute(name,command,environment)
        lane=measured_lane(name,command,code,text,ROOT/log,marker,observation)
        lane['evidence']=log
        lanes.append(lane)
    def nested(name, command, expected):
        code,text,log,observation=execute(name,command)
        lanes.extend(collect_nested(name,command,code,text,observation,expected))
    self_names={'progress-negative','manifest-negative','package-negative','contract-negative','bridge-mutation',
                'ledger-mutation','failed-and-zero-test','sandbox-fake-token','normal-contracts'}
    nested('harness-self',['python3','harness/run-self-check.py'],self_names)
    simple('progress',['python3','scripts/verify-progress.py'],'Progress ledger consistency checks passed')
    simple('manifest',['python3','harness/check-manifest.py'],'Manifest inventory valid')
    simple('api-baseline',['python3','harness/check-api-baseline.py'],'Baseline source comparison PASS')
    simple('api-baseline-negative',['python3','harness/check-api-baseline-negative.py'],'Public API mutation detected')
    simple('csharp-compat',['bash','scripts/check-csharp-compat.sh'],'Legacy C# consumer source: PASS')
    simple('aggregation-self',['python3','-m','unittest','discover','-s','harness','-p','test_aggregation.py','-v'],'OK')
    simple('progress-negative',['python3','harness/check-progress-negative.py'],'Progress negatives PASS')
    simple('manifest-negative',['python3','harness/check-manifest-negative.py'],'Negative manifest: missing R49 rejected')
    simple('contract-negative',['python3','harness/check-contract-negative.py'],'Negative contract: Kotlin and Swift rejected')
    nested('contracts',['python3','harness/run-contracts.py'],{'kotlin','swift','csharp'})
    simple('bridge-mutation',['python3','harness/check-bridge-mutation.py'],'Duplicate response guard mutation: detected')
    simple('lifecycle-stress',['bash','scripts/stress-csharp-lifecycle.sh'],'"samples": 100')
    simple('r50-negative',['python3','harness/run-r50.py'],'R50 PASS:')
    simple('purchase-verifier',['python3','harness/run-purchase-verifier.py'],'Purchase verifier PASS:')
    simple('session-replay',['python3','harness/run-session-replay.py'],'Local session replay PASS:')
    simple('push-router-scenarios',['python3','harness/run-push-router-scenarios.py'],'Push router scenarios PASS:')
    simple('push-ownership',['python3','harness/run-push-ownership.py'],'Push ownership PASS:')
    simple('android-dependency-negative',['python3','harness/check-android-dependency-negative.py'],'Android dependency negative PASS:')
    simple('ios-xcframework-negative',['python3','harness/check-ios-xcframework-negative.py'],'iOS XCFramework negatives PASS:')
    nested('auth',['python3','harness/run-auth-regression.py'],{'backend-jwt-fake','backend-sandbox-test-key-db','android-native-fake','swift-native-fake'})
    nested('purchase',['python3','harness/run-purchase-regression.py'],{'local-postgres-fixtures','sandbox-http-fixtures','android-native-fake','swift-native-fake','android-local-response-loss','swift-local-response-loss','xcode-storekit-local-db-recovery','xcode-storekit-process-recovery'})
    ledger_env = env.copy()
    if env.get('GAMEBRIDGE_LOCAL_TEST_DB_URL'): ledger_env['GAMEBRIDGE_TEST_DB_URL'] = env['GAMEBRIDGE_LOCAL_TEST_DB_URL']
    simple('ledger-mutation',['python3','harness/check-ledger-mutation.py'],'Ledger mutation detected',ledger_env)
    nested('push',['python3','harness/run-push-regression.py'],{'backend-push-fake','sandbox-push-http-fake','android-push-fake','swift-push-fake','ios-host-simulator-synthetic','mock-permission-denied','upm-staging-integrity','package-negative-fixtures','local-push-native-db-e2e','unity-player-notifications'})
    pii_evidence, pii_nonce = env.get('GAMEBRIDGE_UNITY_PII_EVIDENCE'), env.get('GAMEBRIDGE_UNITY_PII_NONCE')
    if pii_evidence and pii_nonce:
        simple('unity-pii-e2e',['python3','harness/check-unity-pii-evidence.py',pii_evidence,pii_nonce],'Unity PII current-run PASS:')
    else:
        lanes.append({'name':'unity-pii-e2e','status':'DEFERRED_ENV','required':True,'tests':0,'skipped':0,'exitCode':2,
                      'command':['python3','harness/check-unity-pii-evidence.py'],'evidence':'docs/PROGRESS.md','reason':'current-run PII Player evidence not supplied'})
    manifest = json.loads((ROOT/'harness/regression-manifest.json').read_text(encoding='utf-8'))
    checker = next((lane for lane in lanes if lane['name'] == 'manifest'), None)
    lanes.append(scenario_mapping_lane(manifest, checker, ROOT))
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
        *(f'harness-self/{x}' for x in self_names), 'progress', 'manifest', 'api-baseline', 'api-baseline-negative', 'csharp-compat',
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
    report = {'mode':'strict-local' if args.strict_local else 'available',**metadata(),'sourceDirty':dirty,
              'timestampUtc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'environment':{'os':platform.platform()},
              'summary':summary,'lanes':lanes,'external':{'status':'WAITING_USER' if external_waits else 'NOT_RUN','taskCount':external_waits,'tasks':external_tasks}}
    (output/'result.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    lines = ['# Local verification summary','',f"Source: `{head}`; working tree dirty: {dirty}.",f"Overall: **{summary['status']}** (exit {summary['exitCode']}).",'', '| Lane | Status | Tests | Checks | Samples | Players | Failures | Errors | Error model | Skipped | Exit | Measurement |', '|---|---|---:|---:|---:|---:|---:|---:|---|---:|---:|---|']
    lines += [lane_row(lane) for lane in lanes]
    lines += ['',f"External: {report['external']['status']} ({external_waits} tasks); not an external test pass."]
    (output/'summary.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    print(f"Overall: {summary['status']} (exit {summary['exitCode']}); external {report['external']['status']} ({external_waits} tasks)")
    print('Evidence directory:',output.relative_to(ROOT))
    return summary['exitCode']

if __name__ == '__main__': raise SystemExit(main())
