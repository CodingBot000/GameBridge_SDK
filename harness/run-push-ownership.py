#!/usr/bin/env python3
"""Run synthetic token rotation and account transfer checks on an opted-in local DB."""
import importlib.util
import os
from pathlib import Path
import re
import sys
import tempfile

ROOT=Path(__file__).resolve().parent.parent
sys.dont_write_bytecode=True
spec=importlib.util.spec_from_file_location('auth_runner',ROOT/'harness/run-auth-regression.py')
common=importlib.util.module_from_spec(spec); spec.loader.exec_module(common)

def main():
    env=os.environ.copy(); env['PYTHONDONTWRITEBYTECODE']='1'; env.setdefault('ANDROID_HOME',str(Path.home()/'Library/Android/sdk'))
    url=env.get('GAMEBRIDGE_LOCAL_TEST_DB_URL','')
    if env.get('GAMEBRIDGE_RUN_DB_TESTS')!='true' or not url or re.search(r'(?i)([?&](?:user|password)=|://[^/]*@)',url) or not all(env.get(x) for x in ('GAMEBRIDGE_TEST_DB_USER','GAMEBRIDGE_TEST_DB_PASSWORD')):
        print('CONFIG_REQUIRED: isolated local test DB opt-in and credentials',file=sys.stderr); return 2
    env['GAMEBRIDGE_TEST_DB_URL']=url
    artifacts=ROOT/'artifacts'; artifacts.mkdir(exist_ok=True); output=Path(tempfile.mkdtemp(prefix='push-ownership-',dir=artifacts))
    command=['backend/gradlew','-p','backend','test','--rerun-tasks','--tests','com.gamebridge.push.DevPushHttpIntegrationTest.rotation and logout move installation ownership without retaining old tokens','--tests','com.gamebridge.push.PushDispatcherDatabaseTest']
    code,_,started=common.run(command,env,output/'backend.log')
    paths=[ROOT/'backend/build/test-results/test/TEST-com.gamebridge.push.DevPushHttpIntegrationTest.xml',ROOT/'backend/build/test-results/test/TEST-com.gamebridge.push.PushDispatcherDatabaseTest.xml']
    if common.item('backend',code,common.junit_counts(paths,started))['status']!='PASS': print(f'Push ownership DB incomplete; evidence: {output.relative_to(ROOT)}',file=sys.stderr); return 2 if code==2 else 1
    code,_,started=common.run(['android/gradlew','-p','android',':sdk-android:testDebugUnitTest','--tests','com.gamebridge.android.push.AndroidPushHostAdapterTest','--rerun-tasks'],env,output/'android.log')
    counts=common.junit_counts([ROOT/'android/sdk-android/build/test-results/testDebugUnitTest/TEST-com.gamebridge.android.push.AndroidPushHostAdapterTest.xml'],started)
    if common.item('android',code,counts)['status']!='PASS': print(f'Android host fake incomplete; evidence: {output.relative_to(ROOT)}',file=sys.stderr); return 2 if code==2 else 1
    print(f'Push ownership PASS: local DB and Android host fake; evidence directory: {output.relative_to(ROOT)}'); return 0

if __name__=='__main__': raise SystemExit(main())
