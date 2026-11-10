#!/usr/bin/env python3
"""Opt-in local-only test. Creates a uniquely named DB/role, never deletes existing state."""
import base64
import json
import os
from pathlib import Path
import secrets
import socket
import subprocess
import sys
import tempfile
import time
import urllib.request
import uuid
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parent.parent
CONTAINER = 'gamebridge-sdk-local-postgres-1'

def main():
    if sys.argv[1:] != ['--run-local']:
        print('Usage: python3 harness/run-mock-push-e2e.py --run-local (creates a retained test DB and role)')
        return 2
    artifacts = ROOT / 'artifacts'; artifacts.mkdir(exist_ok=True)
    output = Path(tempfile.mkdtemp(prefix='mock-push-e2e-', dir=artifacts))
    suffix = secrets.token_hex(5); name = 'gamebridge_ci_' + suffix; password = secrets.token_hex(24)
    for sql in (f"CREATE ROLE {name} LOGIN PASSWORD '{password}'", f'CREATE DATABASE {name} OWNER {name}'):
        created = subprocess.run(['docker','exec','-i',CONTAINER,'psql','-X','-U','gamebridge','-d','postgres','-v','ON_ERROR_STOP=1'],
                                 input=sql+';\n', text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if created.returncode:
            print('CONFIG_REQUIRED: dedicated local PostgreSQL container or permission unavailable'); return 2
    print('Retained local test database and role:', name, flush=True)
    with socket.socket() as sock:
        sock.bind(('127.0.0.1', 0)); port = sock.getsockname()[1]
    base = f'http://127.0.0.1:{port}'; installation = str(uuid.uuid4())
    auth = 'local-test-auth-' + secrets.token_hex(24); admin = 'local-test-admin-' + secrets.token_hex(24)
    env = os.environ.copy(); env.update(SPRING_PROFILES_ACTIVE='local-mock', DATABASE_URL=f'jdbc:postgresql://127.0.0.1:54329/{name}',
        DATABASE_USERNAME=name, DATABASE_PASSWORD=password, GAMEBRIDGE_PORT=str(port), GAMEBRIDGE_DEV_AUTH_KEY=auth,
        GAMEBRIDGE_DEV_PUSH_ADMIN_KEY=admin, GAMEBRIDGE_DEV_PUSH_ALLOWLIST=installation,
        SERVER_TOKEN_ENCRYPTION_KEY=base64.b64encode(secrets.token_bytes(32)).decode(), GAMEBRIDGE_FINALIZATION_POLL_INTERVAL_MS='3600000',
        GAMEBRIDGE_RUN_MOCK_PUSH_E2E='true', GAMEBRIDGE_PUSH_E2E_BASE_URL=base, GAMEBRIDGE_PUSH_E2E_AUTH_KEY=auth,
        GAMEBRIDGE_PUSH_E2E_ADMIN_KEY=admin, GAMEBRIDGE_PUSH_E2E_INSTALLATION=installation,
        ANDROID_HOME=env.get('ANDROID_HOME',str(Path.home()/'Library/Android/sdk')))
    build = subprocess.run(['backend/gradlew','-p','backend','bootJar'],cwd=ROOT,env=env,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
    (output/'backend-build.log').write_text(build.stdout)
    if build.returncode: print('Backend build failed; evidence:',output.relative_to(ROOT)); return 1
    server_log = (output/'backend.log').open('w')
    server = subprocess.Popen(['java','-jar',str(ROOT/'backend/build/libs/gamebridge-backend.jar')],cwd=ROOT,env=env,stdout=server_log,stderr=subprocess.STDOUT)
    suites = []
    try:
        deadline = time.monotonic()+45
        while time.monotonic() < deadline:
            if server.poll() is not None: break
            try:
                with urllib.request.urlopen(base+'/health',timeout=1) as response:
                    if response.status == 200: break
            except Exception: time.sleep(.25)
        else: print('Backend health timeout; evidence:',output.relative_to(ROOT)); return 1
        if server.poll() is not None: print('Backend exited before health; evidence:',output.relative_to(ROOT)); return 1
        commands = [('android',['android/gradlew','-p','android',':sdk-core:test','--tests','com.gamebridge.MockPushLocalIntegrationTest','--rerun-tasks']),
                    ('swift',['swift','test','--package-path','ios','--filter','MockPushLocalIntegrationTests'])]
        for label, command in commands:
            print('Running',label,'local Backend push E2E...',flush=True)
            try: result = subprocess.run(command,cwd=ROOT,env=env,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=120)
            except subprocess.TimeoutExpired: suites.append({'name':label,'status':'FAIL','reason':'timeout'}); continue
            (output/(label+'.log')).write_text(result.stdout)
            ran = False
            if label == 'android':
                path = ROOT/'android/sdk-core/build/test-results/test/TEST-com.gamebridge.MockPushLocalIntegrationTest.xml'
                try:
                    xml = ET.parse(path).getroot(); ran = int(xml.get('tests','0')) > 0 and int(xml.get('skipped','0')) == 0 and int(xml.get('failures','0')) == 0 and int(xml.get('errors','0')) == 0
                except (OSError,ValueError,ET.ParseError): pass
            else: ran = 'Executed 1 test, with 0 failures' in result.stdout and '1 test skipped' not in result.stdout
            suites.append({'name':label,'status':'PASS' if result.returncode == 0 and ran else 'FAIL','exitCode':result.returncode})
    finally:
        server.terminate()
        try: server.wait(timeout=10)
        except subprocess.TimeoutExpired: server.kill(); server.wait()
        server_log.close()
    status = 'PASS' if len(suites)==2 and all(x['status']=='PASS' for x in suites) else 'FAIL'
    report = {'status':status,'sourceHead':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
              'sourceDirty':bool(subprocess.check_output(['git','status','--porcelain'],cwd=ROOT,text=True).strip()),'database':name,'suites':suites,'limitations':['LOCAL_MOCK only','not Unity player, real device, or remote push']}
    (output/'result.json').write_text(json.dumps(report,indent=2)+'\n')
    print('Result:',status,'Evidence directory:',output.relative_to(ROOT)); return 0 if status == 'PASS' else 1

if __name__ == '__main__': raise SystemExit(main())
