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
                                    stderr=subprocess.STDOUT,timeout=1200,check=False)
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
    simple('progress',['python3','scripts/verify-progress.py'],'Progress ledger consistency checks passed')
    simple('manifest',['python3','harness/check-manifest.py'],'Manifest inventory valid')
    simple('api-baseline',['python3','harness/check-api-baseline.py'],'Baseline source comparison PASS')
    simple('api-baseline-negative',['python3','harness/check-api-baseline-negative.py'],'Public API mutation detected')
    simple('aggregation-self',['python3','-m','unittest','discover','-s','harness','-p','test_aggregation.py','-v'],'OK')
    simple('progress-negative',['python3','harness/check-progress-negative.py'],'Progress negatives PASS')
    simple('manifest-negative',['python3','harness/check-manifest-negative.py'],'Negative manifest: missing R49 rejected')
    simple('contract-negative',['python3','harness/check-contract-negative.py'],'Negative contract: Kotlin and Swift rejected')
    nested('contracts',['python3','harness/run-contracts.py'])
    simple('bridge-mutation',['python3','harness/check-bridge-mutation.py'],'Duplicate response guard mutation: detected')
    nested('auth',['python3','harness/run-auth-regression.py'])
    nested('purchase',['python3','harness/run-purchase-regression.py'])
    ledger_env = env.copy()
    if env.get('GAMEBRIDGE_LOCAL_TEST_DB_URL'): ledger_env['GAMEBRIDGE_TEST_DB_URL'] = env['GAMEBRIDGE_LOCAL_TEST_DB_URL']
    simple('ledger-mutation',['python3','harness/check-ledger-mutation.py'],'Ledger mutation detected',ledger_env)
    nested('push',['python3','harness/run-push-regression.py'])
    manifest = json.loads((ROOT/'harness/regression-manifest.json').read_text(encoding='utf-8'))
    incomplete = [entry['id'] for entry in manifest['scenarios'] if entry.get('required') and entry.get('coverage') != 'IMPLEMENTED']
    lanes.append({'name':'scenario-coverage','status':'NOT_IMPLEMENTED' if incomplete else 'PASS','required':True,
                  'tests':0 if incomplete else len(manifest['scenarios']),'skipped':0,'exitCode':2 if incomplete else 0,
                  'command':['python3','harness/check-manifest.py'],'evidence':'harness/regression-manifest.json','incompleteCount':len(incomplete)})
    lanes.append({'name':'unity-editor-runtime','status':'NOT_RUN','required':True,'tests':0,'skipped':0,'exitCode':2,
                  'command':[],'evidence':'docs/PROGRESS.md','reason':'Unity runtime lane is not automated; ENV-002 is separately recorded'})
    progress = (ROOT/'docs/PROGRESS.md').read_text(encoding='utf-8')
    failed_rows = []
    for line in progress.splitlines():
        if re.match(r'^\| P\d\d-T\d\d \|',line):
            cells = [cell.strip() for cell in line.strip().strip('|').split('|')]
            if len(cells) == 7 and cells[3] == 'FAIL': failed_rows.append(cells[0])
    if failed_rows:
        lanes.append({'name':'recorded-unresolved-failures','status':'FAIL','required':True,'tests':0,'skipped':0,'exitCode':1,
                      'command':[],'evidence':'docs/PROGRESS.md','reason':'previous failures not rerun by this command','tasks':failed_rows})
    summary = summarize(lanes)
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
