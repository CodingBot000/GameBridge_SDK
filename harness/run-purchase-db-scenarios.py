#!/usr/bin/env python3
"""Run synthetic Apple purchase DB/HTTP invariants using explicitly supplied test DBs."""
import importlib.util
import os
from pathlib import Path
import re
import sys
import tempfile

ROOT = Path(__file__).resolve().parent.parent
sys.dont_write_bytecode = True
spec = importlib.util.spec_from_file_location('auth_runner', ROOT/'harness/run-auth-regression.py')
common = importlib.util.module_from_spec(spec); spec.loader.exec_module(common)

def main():
    env = os.environ.copy(); env['PYTHONDONTWRITEBYTECODE'] = '1'
    local = env.get('GAMEBRIDGE_LOCAL_TEST_DB_URL',''); sandbox = env.get('GAMEBRIDGE_SANDBOX_TEST_DB_URL','')
    if (env.get('GAMEBRIDGE_RUN_DB_TESTS') != 'true' or env.get('GAMEBRIDGE_RUN_AUTH_DB_TESTS') != 'true' or
        not all(env.get(k) for k in ('GAMEBRIDGE_TEST_DB_USER','GAMEBRIDGE_TEST_DB_PASSWORD')) or
        not local or not sandbox or any(re.search(r'(?i)([?&](?:user|password)=|://[^/]*@)', value) for value in (local,sandbox))):
        print('CONFIG_REQUIRED: explicit isolated local/sandbox test DB opt-in and separate credentials',file=sys.stderr); return 2
    artifacts = ROOT/'artifacts'; artifacts.mkdir(exist_ok=True); output = Path(tempfile.mkdtemp(prefix='purchase-db-scenarios-',dir=artifacts))
    for label, url, cls in (('local',local,'AppleGrantDatabaseTest'),('sandbox',sandbox,'ApplePurchaseHttpIntegrationTest')):
        lane=env.copy(); lane['GAMEBRIDGE_TEST_DB_URL']=url
        code, _, started = common.run(['backend/gradlew','-p','backend','test','--tests',f'com.gamebridge.purchase.{cls}','--rerun-tasks'],lane,output/(label+'.log'))
        counts=common.junit_counts([ROOT/f'backend/build/test-results/test/TEST-com.gamebridge.purchase.{cls}.xml'],started)
        if common.item(label,code,counts)['status'] != 'PASS':
            print(f'Purchase DB scenario {label} failed; evidence directory: {output.relative_to(ROOT)}',file=sys.stderr); return 1
    print(f'Purchase DB scenarios PASS: local and sandbox synthetic tests; evidence directory: {output.relative_to(ROOT)}')
    return 0

if __name__ == '__main__': raise SystemExit(main())
