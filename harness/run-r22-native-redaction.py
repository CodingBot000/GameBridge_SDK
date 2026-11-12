#!/usr/bin/env python3
"""Opt-in isolated synthetic-token bridge checks; no real provider credentials."""
import base64
import importlib.util
import json
import os
from pathlib import Path
import re
import secrets
import socket
import subprocess
import sys
import tempfile
import time
import urllib.request
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parent.parent


_redaction_spec = importlib.util.spec_from_file_location('local_mock_redaction', ROOT/'harness/local_mock_redaction.py')
_redaction = importlib.util.module_from_spec(_redaction_spec); _redaction_spec.loader.exec_module(_redaction)
has_mock_credential = _redaction.contains_mock_credential


def error_status(error):
    return 'DEFERRED_ENV' if getattr(error, 'category', None) == 'DEFERRED_ENV' else 'FAIL'


def marker_pass(path):
    try: return path.read_text() == 'PASS\n'
    except OSError: return False


def main():
    if sys.argv[1:] != ['--run-local']:
        print('Usage: run-r22-native-redaction.py --run-local (retains isolated test DB)')
        return 2
    with socket.socket() as sock:
        try: sock.bind(('127.0.0.1', 18080))
        except OSError:
            print('DEFERRED_ENV: local test port 18080 occupied'); return 2
    artifacts = ROOT / 'artifacts'; artifacts.mkdir(exist_ok=True)
    output = Path(tempfile.mkdtemp(prefix='r22-native-', dir=artifacts))
    spec = importlib.util.spec_from_file_location('android_e2e', ROOT/'harness/run-unity-android-mock-e2e.py')
    common = importlib.util.module_from_spec(spec); spec.loader.exec_module(common)
    server = None; log = None; result = {'status':'FAIL','android':'NOT_RUN','swift':'NOT_RUN'}
    try:
        database, password = common.create_isolated_database('gamebridge-sdk-local-postgres-1','gamebridge',54329)
        env = os.environ.copy()
        env.update(SPRING_PROFILES_ACTIVE='local-mock', DATABASE_URL='jdbc:postgresql://127.0.0.1:54329/'+database,
                   DATABASE_USERNAME=database, DATABASE_PASSWORD=password, GAMEBRIDGE_PORT='18080',
                   GAMEBRIDGE_DEV_AUTH_KEY='r22-test-'+secrets.token_hex(24),
                   SERVER_TOKEN_ENCRYPTION_KEY=base64.b64encode(secrets.token_bytes(32)).decode(),
                   GAMEBRIDGE_MAINTENANCE_ENABLED='false', GAMEBRIDGE_RUN_LOCAL_CLIENT_TEST='true',
                   GAMEBRIDGE_R22_SERVER_LOG=str(output/'server.log'),
                   GAMEBRIDGE_R22_ANDROID_MARKER=str(output/'android-log-check.txt'),
                   GAMEBRIDGE_R22_SWIFT_MARKER=str(output/'swift-log-check.txt'))
        build = subprocess.run(['backend/gradlew','-p','backend','bootJar'],cwd=ROOT,env=env,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=240)
        (output/'build.log').write_bytes(build.stdout)
        if build.returncode: raise RuntimeError('BACKEND_BUILD_FAILED')
        log = (output/'server.log').open('wb')
        server = subprocess.Popen(['java','-jar',str(ROOT/'backend/build/libs/gamebridge-backend.jar')],cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT)
        deadline = time.monotonic()+45
        while time.monotonic()<deadline:
            if server.poll() is not None: raise RuntimeError('BACKEND_EXITED')
            try:
                with urllib.request.urlopen('http://127.0.0.1:18080/health',timeout=1) as response:
                    if response.status==200: break
            except Exception: time.sleep(.25)
        else: raise RuntimeError('BACKEND_HEALTH_TIMEOUT')
        started = time.time_ns()
        command=['android/gradlew','-p','android',':sdk-core:test','--rerun-tasks','--tests',
                 'com.gamebridge.LocalMockIntegrationTest.bridge uses real local backend for mock purchase and restore']
        android=subprocess.run(command,cwd=ROOT,env=env,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=240)
        (output/'android.log').write_bytes(android.stdout)
        path=ROOT/'android/sdk-core/build/test-results/test/TEST-com.gamebridge.LocalMockIntegrationTest.xml'
        xml=ET.parse(path).getroot().attrib if path.stat().st_mtime_ns >= started else {}
        if android.returncode==0 and all(int(xml.get(k,-1))==v for k,v in [('tests',1),('failures',0),('errors',0),('skipped',0)]) and marker_pass(output/'android-log-check.txt'): result['android']='PASS'
        swift=subprocess.run(['swift','test','--package-path','ios','--filter','LocalMockIntegrationTests.testBridgeHandlerAgainstLocalBackend'],cwd=ROOT,env=env,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=240)
        (output/'swift.log').write_bytes(swift.stdout); text=swift.stdout.decode(errors='replace')
        summaries=re.findall(r'Executed (\d+) tests?, with (\d+) failures?',text)
        if swift.returncode==0 and summaries and max(int(a) for a,_ in summaries)==1 and all(int(b)==0 for _,b in summaries) and 'test skipped' not in text.lower() and marker_pass(output/'swift-log-check.txt'): result['swift']='PASS'
        log.flush()
        if has_mock_credential((output/'server.log').read_text(encoding='utf-8',errors='replace')): raise RuntimeError('SYNTHETIC_MOCK_CREDENTIAL_IN_SERVER_LOG')
        result['mockCredentialServerLog']='PASS'
        if result['android']==result['swift']=='PASS': result['status']='PASS'
    except (common.GateError, OSError, RuntimeError, ValueError, ET.ParseError, subprocess.TimeoutExpired) as error:
        result['status']=error_status(error)
        result['errorCode']=str(error) if isinstance(error,common.GateError) else type(error).__name__
    finally:
        if server and server.poll() is None:
            server.terminate()
            try: server.wait(timeout=10)
            except subprocess.TimeoutExpired: server.kill(); server.wait()
        if log: log.close()
    result['sourceHead']=subprocess.run(['git','rev-parse','HEAD'],cwd=ROOT,text=True,stdout=subprocess.PIPE,check=False).stdout.strip()
    (output/'result.json').write_text(json.dumps(result,indent=2)+'\n')
    print('R22 native synthetic token:',result['status'],'Android:',result['android'],'Swift:',result['swift'],'Evidence:',output.relative_to(ROOT))
    return 0 if result['status']=='PASS' else 2 if result['status']=='DEFERRED_ENV' else 1

if __name__=='__main__': raise SystemExit(main())
