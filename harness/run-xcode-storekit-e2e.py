#!/usr/bin/env python3
"""Opt-in Xcode local test with retained isolated DB and simulator; never reaches Apple servers."""
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
import xml.etree.ElementTree as ET

from process_output import timeout_output
from ios_test_diagnostics import Timeline,toolchain,configuration_hash

ROOT = Path(__file__).resolve().parent.parent
CONTAINER = 'gamebridge-sdk-local-postgres-1'

def main():
    if sys.argv[1:] not in (['--run-local'],['--run-local','--diagnose']):
        print('Usage: python3 harness/run-xcode-storekit-e2e.py --run-local (retains dedicated test DB, role and simulator)')
        return 2
    diagnostic=Timeline();diagnose='--diagnose' in sys.argv
    diagnostic.mark('runner-start')
    artifacts = ROOT/'artifacts'; artifacts.mkdir(exist_ok=True)
    output = Path(tempfile.mkdtemp(prefix='xcode-storekit-e2e-',dir=artifacts))
    suffix = secrets.token_hex(5); name = 'gamebridge_ci_' + suffix; password = secrets.token_hex(24)
    for sql in (f"CREATE ROLE {name} LOGIN PASSWORD '{password}'", f'CREATE DATABASE {name} OWNER {name}'):
        created = subprocess.run(['docker','exec','-i',CONTAINER,'psql','-X','-U','gamebridge','-d','postgres','-v','ON_ERROR_STOP=1'],
                                 input=sql+';\n',text=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        if created.returncode: print('CONFIG_REQUIRED: dedicated local PostgreSQL container unavailable'); return 2
    print('Retained local test database and role:',name,flush=True)
    with socket.socket() as sock: sock.bind(('127.0.0.1',0)); port = sock.getsockname()[1]
    base = f'http://127.0.0.1:{port}'; auth = 'local-xcode-auth-' + secrets.token_hex(24)
    env = os.environ.copy(); env.update(SPRING_PROFILES_ACTIVE='local-mock', DATABASE_URL=f'jdbc:postgresql://127.0.0.1:54329/{name}',
        DATABASE_USERNAME=name, DATABASE_PASSWORD=password, GAMEBRIDGE_PORT=str(port), GAMEBRIDGE_DEV_AUTH_KEY=auth,
        SERVER_TOKEN_ENCRYPTION_KEY=base64.b64encode(secrets.token_bytes(32)).decode(), GAMEBRIDGE_MAINTENANCE_ENABLED='false',
        GAMEBRIDGE_FINALIZATION_POLL_INTERVAL_MS='3600000')
    build = subprocess.run(['backend/gradlew','-p','backend','bootJar'],cwd=ROOT,env=env,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
    (output/'backend-build.log').write_text(build.stdout)
    if build.returncode: print('Backend build failed; evidence:',output.relative_to(ROOT)); return 1
    generated = subprocess.run(['bash','scripts/generate-ios-project.sh'],cwd=ROOT,env=env,text=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    (output/'project-generation.log').write_text(generated.stderr)
    if generated.returncode: print('Xcode project unavailable; evidence:',output.relative_to(ROOT)); return 2
    project = Path(generated.stdout.strip())
    scheme = project/'xcshareddata/xcschemes/GameBridgeStoreKit.xcscheme'
    tree = ET.parse(scheme); root = tree.getroot(); test_action = root.find('TestAction'); test_action.set('shouldUseLaunchSchemeArgsEnv','NO')
    variables = test_action.find('EnvironmentVariables')
    if variables is None: variables = ET.SubElement(test_action,'EnvironmentVariables')
    for key,value in {'GAMEBRIDGE_RUN_XCODE_DB_E2E':'true','GAMEBRIDGE_XCODE_E2E_BASE_URL':base,'GAMEBRIDGE_XCODE_E2E_AUTH_KEY':auth}.items():
        ET.SubElement(variables,'EnvironmentVariable',{'key':key,'value':value,'isEnabled':'YES'})
    tree.write(scheme,encoding='utf-8',xml_declaration=True)
    created_sim = subprocess.run(['xcrun','simctl','create','GameBridge-StoreKit-DB-'+suffix,'com.apple.CoreSimulator.SimDeviceType.iPhone-16','com.apple.CoreSimulator.SimRuntime.iOS-18-6'],
                                 cwd=ROOT,text=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    if created_sim.returncode: print('iOS 18.6 simulator unavailable; evidence:',output.relative_to(ROOT)); return 2
    simulator = created_sim.stdout.strip();diagnostic.mark('simulator-created',simulator); print('Retained dedicated simulator:',simulator,flush=True)
    log = (output/'backend.log').open('w')
    server = subprocess.Popen(['java','-jar',str(ROOT/'backend/build/libs/gamebridge-backend.jar')],cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT)
    status='FAIL'; test_code=1; summary={};diagnostic_failure=None
    try:
        deadline = time.monotonic()+45
        while time.monotonic() < deadline:
            if server.poll() is not None: break
            try:
                with urllib.request.urlopen(base+'/health',timeout=1) as response:
                    if response.status == 200: break
            except Exception: time.sleep(.25)
        else: raise RuntimeError('BACKEND_HEALTH_TIMEOUT')
        if server.poll() is not None:raise RuntimeError('BACKEND_EXITED_BEFORE_HEALTH')
        diagnostic.mark('backend-health-ready',simulator)
        if diagnose:
            for action in (['boot',simulator],['bootstatus',simulator,'-b']):
                prepared=subprocess.run(['xcrun','simctl']+action,cwd=ROOT,text=True,capture_output=True,timeout=180)
                if prepared.returncode:raise RuntimeError('diagnostic boot preparation failed')
            diagnostic.mark('owned-simulator-boot-ready',simulator)
        result_path=output/'result.xcresult'
        command=['xcodebuild','-project',str(project),'-scheme','GameBridgeStoreKit','-destination',f'platform=iOS Simulator,id={simulator}',
                 '-resultBundlePath',str(result_path),'CODE_SIGN_IDENTITY=-','CODE_SIGNING_REQUIRED=YES','-only-testing:GameBridgeStoreKitTests/XcodeStoreKitLocalDatabaseTests','test','-quiet']
        if diagnose:command += ['-parallel-testing-enabled','NO','-derivedDataPath',str(output/'Derived')]
        diagnostic.mark('xctest-invocation-start',simulator)
        print('Running Xcode local StoreKit + local database recovery E2E...',flush=True)
        try: result=subprocess.run(command,cwd=ROOT,env=env,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=180); test_code=result.returncode; (output/'xcodebuild.log').write_text(result.stdout)
        except subprocess.TimeoutExpired as exc: (output/'xcodebuild.log').write_text(timeout_output(exc)); test_code=124
        diagnostic.mark('xctest-invocation-return',simulator)
        if result_path.exists():
            report=subprocess.run(['xcrun','xcresulttool','get','test-results','summary','--path',str(result_path),'--format','json'],cwd=ROOT,text=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
            if report.returncode == 0:
                try: summary=json.loads(report.stdout)
                except ValueError: pass
        if test_code == 0 and summary.get('passedTests') == 1 and summary.get('skippedTests') == 0 and summary.get('failedTests') == 0: status='PASS'
    except (RuntimeError,subprocess.TimeoutExpired) as error:
        diagnostic_failure=type(error).__name__+': '+str(error)
        diagnostic.mark('diagnostic-invocation-failed',simulator)
    finally:
        server.terminate()
        try: server.wait(timeout=10)
        except subprocess.TimeoutExpired: server.kill(); server.wait()
        log.close()
    report={'status':status,'sourceHead':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
            'sourceDirty':bool(subprocess.check_output(['git','status','--porcelain'],cwd=ROOT,text=True).strip()),
            'database':name,'simulator':simulator,'testExitCode':test_code,'timedOut':test_code==124,'diagnosticFailure':diagnostic_failure,'diagnosticMode':diagnose,'toolchain':toolchain(),'configurationSha256':configuration_hash(ROOT/'ios/StoreKit/GameBridge.storekit'),'diagnosticEvents':diagnostic.events,'passed':summary.get('passedTests',0),'skipped':summary.get('skippedTests',0),
            'limitations':['Xcode local StoreKit and synthetic development DB only','public native Xcode-local grant path','not Unity player or Apple sandbox']}
    (output/'result.json').write_text(json.dumps(report,indent=2)+'\n')
    print('Result:',status,'Evidence directory:',output.relative_to(ROOT)); return 0 if status=='PASS' else 1

if __name__=='__main__': raise SystemExit(main())
