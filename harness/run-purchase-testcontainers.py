#!/usr/bin/env python3
"""Run unchanged purchase invariants using owned, loopback-only Testcontainers DBs."""
import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
import uuid
from pathlib import Path
from execution_evidence import metadata
ROOT=Path(__file__).resolve().parent.parent
spec=importlib.util.spec_from_file_location('common_tc',ROOT/'harness/run-auth-regression.py')
common=importlib.util.module_from_spec(spec);spec.loader.exec_module(common)

ledger_spec=importlib.util.spec_from_file_location('tc_ledger',ROOT/'harness/check-ledger-mutation.py')
ledger=importlib.util.module_from_spec(ledger_spec);ledger_spec.loader.exec_module(ledger)

CASES={
 'tcPurchaseLocal':(('LedgerInvariantDatabaseTest','GoogleGrantDatabaseTest','AppleGrantDatabaseTest','FinalizationDatabaseTest','PurchaseBindingsDatabaseTest'),7,0),
 'tcLedgerMutation':(('LedgerInvariantDatabaseTest',),1,1),
 'tcLedgerNormal':(('LedgerInvariantDatabaseTest',),1,0),
 'tcPurchaseSandbox':(('GooglePurchaseHttpIntegrationTest','ApplePurchaseHttpIntegrationTest'),2,0),
}


def valid_container(proof,head,run,task):
    return (task in CASES and isinstance(proof,dict) and proof.get('sourceHead')==head and proof.get('runId')==run and
            proof.get('task')==task and proof.get('profile')==('sandbox' if task=='tcPurchaseSandbox' else 'local-mock') and proof.get('image')=='postgres:17.6-alpine3.22' and
            proof.get('containerStarted') is True and proof.get('containerStopped') is True and
            proof.get('loopbackOnly') is True and type(proof.get('mappedPort')) is int and 0<proof['mappedPort']<=65535 and
            isinstance(proof.get('containerId'),str) and bool(re.fullmatch('[a-f0-9]{64}',proof['containerId'])))




def named_ledger_evidence(task,paths,started):
    if task not in ('tcLedgerMutation','tcLedgerNormal'):return True
    try:return len(paths)==1 and ledger.valid_report(paths[0],started,task=='tcLedgerMutation')
    except (OSError,ValueError,ledger.ET.ParseError):return False

def removed_container(result):
    error=(result.stderr or '').casefold()
    return result.returncode==1 and ('no such object:' in error or 'no such container:' in error)

def main():
    if sys.argv[1:]!=['--run-local']:
        print('DEFERRED_ENV: --run-local required');return 2
    env=os.environ.copy()
    try:
        endpoint=env.get('DOCKER_HOST') or subprocess.check_output(['docker','context','inspect','--format','{{.Endpoints.docker.Host}}'],text=True,timeout=10).strip()
        if not endpoint.startswith('unix://') or not Path(endpoint[7:]).is_socket():raise ValueError('local socket required')
    except (OSError,ValueError,subprocess.SubprocessError):
        print('DEFERRED_ENV: local Docker Unix socket required');return 2
    (ROOT/'artifacts').mkdir(exist_ok=True)
    out=Path(tempfile.mkdtemp(prefix='purchase-testcontainers-',dir=ROOT/'artifacts'))
    identity=metadata();run=uuid.uuid4().hex
    env.update(DOCKER_HOST=endpoint,GAMEBRIDGE_RUN_TESTCONTAINERS='true',GAMEBRIDGE_TESTCONTAINERS_RUN_ID=run,
               GAMEBRIDGE_TESTCONTAINERS_SOURCE_HEAD=identity['sourceHead'],GAMEBRIDGE_TESTCONTAINERS_EVIDENCE=str(out))
    suites=[]
    for task,(classes,expected,failures) in CASES.items():
        command=['backend/gradlew','-p','backend','--init-script',str(ROOT/'harness/purchase-testcontainers.init.gradle.kts'),task,'--rerun-tasks']
        code,text,started=common.run(command,env,out/(task+'.log'),timeout=600)
        paths=[ROOT/f'backend/build/test-results/{task}/TEST-com.gamebridge.purchase.{cls}.xml' for cls in classes]
        counts=common.junit_counts(paths,started)
        proof_path=out/(task+'.container.json')
        proof={}
        try:
            if proof_path.stat().st_mtime_ns<started:raise ValueError('stale container receipt')
            proof=json.loads(proof_path.read_text())
        except (OSError,ValueError):pass
        removed=False
        if valid_container(proof,identity['sourceHead'],run,task):
            checked=subprocess.run(['docker','inspect',proof['containerId']],env=env,text=True,capture_output=True,timeout=10)
            removed=removed_container(checked)
        good=(code==(1 if failures else 0) and tuple(counts)==(expected,failures,0) and counts.errors==0 and
              valid_container(proof,identity['sourceHead'],run,task) and removed and named_ledger_evidence(task,paths,started))
        for path in paths:
            if path.exists() and path.stat().st_mtime_ns>=started:shutil.copyfile(path,out/(task+'-'+path.name))
        suites.append({'suite':task,'status':'PASS' if good else 'FAIL','exitCode':code,'tests':counts[0],
                       'failures':counts[1],'errors':counts.errors,'skipped':counts[2],'expectedFailures':failures,
                       'errorModel':'separate','containerRemoved':removed})
        print(task,suites[-1]['status'],'tests',counts[0],'expectedFailures',failures,'exit',code,flush=True)
        if not good:break
    passed=len(suites)==len(CASES) and all(x['status']=='PASS' for x in suites)
    report={**identity,'scope':'owned-Testcontainers-purchase-fixtures','runId':run,'status':'PASS' if passed else 'FAIL',
            'suites':suites,'tests':sum(x['tests'] for x in suites),'checks':len(suites),
            'expectedFailures':sum(x['expectedFailures'] for x in suites)}
    (out/'result.json').write_text(json.dumps(report,indent=2)+'\n')
    if passed:print('Testcontainers purchase PASS:',report['tests'],'executed tests;',report['expectedFailures'],'expected mutation failure')
    print('Evidence directory:',out.relative_to(ROOT))
    return 0 if passed else 1

if __name__=='__main__':raise SystemExit(main())
