#!/usr/bin/env python3
"""Run opted-in local checks against new retained databases; never touches existing DBs."""
import base64
import os
from pathlib import Path
import secrets
import socket
import subprocess
import sys
import tempfile
import time
import urllib.request

ROOT = Path(__file__).resolve().parent.parent
CONTAINER = 'gamebridge-sdk-local-postgres-1'

def wait_health(base, process):
    deadline = time.monotonic() + 45
    while time.monotonic() < deadline:
        if process.poll() is not None: return False
        try:
            with urllib.request.urlopen(base+'/health',timeout=1) as response:
                if response.status == 200: return True
        except Exception: time.sleep(.25)
    return False

def main():
    if sys.argv[1:] != ['--run-local']:
        print('Usage: python3 harness/run-strict-local-isolated.py --run-local (retains dedicated test DBs and roles)'); return 2
    staging = ROOT/'artifacts/upm-validated-20261111'
    if not staging.is_dir(): print('CONFIG_REQUIRED: latest local UPM staging missing'); return 2
    artifacts=ROOT/'artifacts'; artifacts.mkdir(exist_ok=True)
    output=Path(tempfile.mkdtemp(prefix='strict-isolated-',dir=artifacts))
    with socket.socket() as sock:
        try: sock.bind(('127.0.0.1',18080))
        except OSError: print('DEFERRED_ENV: dedicated local test port 18080 is occupied'); return 2
    suffix=secrets.token_hex(5); role='gamebridge_ci_'+suffix; password=secrets.token_hex(24)
    local=role+'_local'; sandbox=role+'_sandbox'
    for sql in (f"CREATE ROLE {role} LOGIN PASSWORD '{password}'",f'CREATE DATABASE {local} OWNER {role}',f'CREATE DATABASE {sandbox} OWNER {role}'):
        result=subprocess.run(['docker','exec','-i',CONTAINER,'psql','-X','-U','gamebridge','-d','postgres','-v','ON_ERROR_STOP=1'],
                              input=sql+';\n',text=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        if result.returncode: print('CONFIG_REQUIRED: dedicated local PostgreSQL container unavailable'); return 2
    print('Retained local/sandbox test databases:',local,sandbox,flush=True)
    auth='isolated-test-auth-'+secrets.token_hex(24)
    shared=os.environ.copy(); shared.update(DATABASE_USERNAME=role,DATABASE_PASSWORD=password,GAMEBRIDGE_DEV_AUTH_KEY=auth,
        SERVER_TOKEN_ENCRYPTION_KEY=base64.b64encode(secrets.token_bytes(32)).decode(),
        SERVER_PURCHASE_ENCRYPTION_KEY=base64.b64encode(secrets.token_bytes(32)).decode(), GAMEBRIDGE_MAINTENANCE_ENABLED='false',
        GAMEBRIDGE_FINALIZATION_POLL_INTERVAL_MS='3600000')
    build=subprocess.run(['backend/gradlew','-p','backend','bootJar'],cwd=ROOT,env=shared,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
    (output/'backend-build.log').write_text(build.stdout)
    if build.returncode: print('Backend build failed; evidence:',output.relative_to(ROOT)); return 1
    logs=[]; processes=[]
    def start(profile,db,port):
        environment=shared.copy(); environment.update(SPRING_PROFILES_ACTIVE=profile,DATABASE_URL=f'jdbc:postgresql://127.0.0.1:54329/{db}',GAMEBRIDGE_PORT=str(port))
        log=(output/(profile+'.log')).open('w'); logs.append(log)
        process=subprocess.Popen(['java','-jar',str(ROOT/'backend/build/libs/gamebridge-backend.jar')],cwd=ROOT,env=environment,stdout=log,stderr=subprocess.STDOUT); processes.append(process)
        return process
    try:
        local_server=start('local-mock',local,18080)
        if not wait_health('http://127.0.0.1:18080',local_server): print('Local test server unavailable; evidence:',output.relative_to(ROOT)); return 1
        with socket.socket() as sock: sock.bind(('127.0.0.1',0)); sandbox_port=sock.getsockname()[1]
        sandbox_server=start('sandbox',sandbox,sandbox_port)
        if not wait_health(f'http://127.0.0.1:{sandbox_port}',sandbox_server): print('Sandbox fixture server unavailable; evidence:',output.relative_to(ROOT)); return 1
        sandbox_server.terminate(); sandbox_server.wait(timeout=10)
        editor=Path('/Applications/Unity/Hub/Editor/6000.5.8f1/Unity.app/Contents/MacOS/Unity')
        managed=editor.parent.parent/'Resources/Scripting/Managed/Newtonsoft.Json.dll'
        env=shared.copy(); env.update(GAMEBRIDGE_RUN_DB_TESTS='true',GAMEBRIDGE_RUN_AUTH_DB_TESTS='true',GAMEBRIDGE_RUN_LOCAL_CLIENT_TEST='true',
            GAMEBRIDGE_TEST_DB_URL=f'jdbc:postgresql://127.0.0.1:54329/{sandbox}',GAMEBRIDGE_LOCAL_TEST_DB_URL=f'jdbc:postgresql://127.0.0.1:54329/{local}',
            GAMEBRIDGE_SANDBOX_TEST_DB_URL=f'jdbc:postgresql://127.0.0.1:54329/{sandbox}',GAMEBRIDGE_TEST_DB_USER=role,GAMEBRIDGE_TEST_DB_PASSWORD=password,
            GAMEBRIDGE_RUN_MOCK_PUSH_HARNESS='true',GAMEBRIDGE_RUN_XCODE_STOREKIT_HARNESS='true',GAMEBRIDGE_UPM_STAGING=str(staging),
            GAMEBRIDGE_MAVEN_REPO=str(ROOT/'artifacts/maven-final-20261111'),
            GAMEBRIDGE_IOS_XCFRAMEWORK=str(ROOT/'artifacts/ios-final-20261111/GameBridgeNative.xcframework'),
            UNITY_EDITOR_PATH=str(editor),NEWTONSOFT_DLL=str(managed),GAMEBRIDGE_NEWTONSOFT_DLL=str(managed))
        generated=subprocess.run(['bash','scripts/generate-ios-project.sh'],cwd=ROOT,env=env,text=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        (output/'ios-project.log').write_text(generated.stderr)
        sim=subprocess.run(['xcrun','simctl','create','GameBridge-Push-Strict-'+suffix,'com.apple.CoreSimulator.SimDeviceType.iPhone-16','com.apple.CoreSimulator.SimRuntime.iOS-18-6'],
                           cwd=ROOT,text=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        if generated.returncode == 0 and sim.returncode == 0:
            env['GAMEBRIDGE_IOS_PROJECT']=generated.stdout.strip()
            env['GAMEBRIDGE_IOS_SIMULATOR_ID']=sim.stdout.strip()
            print('Retained synthetic host test simulator:',sim.stdout.strip(),flush=True)
        else: print('iOS synthetic host lane unavailable; it remains deferred.',flush=True)
        print('Running strict local aggregation; Unity Editor and external services remain separate...',flush=True)
        try:
            result=subprocess.run(['bash','scripts/verify-all.sh','--strict-local'],cwd=ROOT,env=env,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=900)
            (output/'aggregate.log').write_text(result.stdout); print(result.stdout,flush=True)
            return result.returncode
        except subprocess.TimeoutExpired:
            (output/'aggregate.log').write_text('Strict aggregation timed out.\n'); print('Strict aggregation timed out; evidence:',output.relative_to(ROOT)); return 1
    finally:
        for process in reversed(processes):
            if process.poll() is None:
                process.terminate()
                try: process.wait(timeout=10)
                except subprocess.TimeoutExpired: process.kill(); process.wait()
        for log in logs: log.close()
        print('Orchestration evidence:',output.relative_to(ROOT),flush=True)

if __name__=='__main__': raise SystemExit(main())
