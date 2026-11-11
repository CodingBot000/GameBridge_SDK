#!/usr/bin/env python3
"""Opt-in Android Kotlin bridge/local DB test; retains isolated emulator app and DB."""
import base64, json, os, re, secrets, socket, subprocess, sys, tempfile, time, urllib.request
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
ADB = Path.home()/'Library/Android/sdk/platform-tools/adb'
SERIAL = 'emulator-5598'

def main():
    if sys.argv[1:] != ['--run-local']:
        print('Usage: run-android-mock-bridge-e2e.py --run-local (retains dedicated emulator app and database)'); return 2
    expected = (ROOT/'artifacts/v2-test-avd-name.txt').read_text().strip()
    def run(args, **kwargs):
        return subprocess.run(args,cwd=ROOT,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,**kwargs)
    name = run([str(ADB),'-s',SERIAL,'emu','avd','name'])
    if name.returncode or name.stdout.splitlines()[0] != expected or not expected.startswith('GameBridge_V2_'):
        print('CONFIG_REQUIRED: dedicated GameBridge V2 emulator not running'); return 2
    installed = run([str(ADB),'-s',SERIAL,'shell','pm','list','packages','com.gamebridge.sample'])
    if installed.returncode or 'package:com.gamebridge.sample' in installed.stdout:
        print('CONFIG_REQUIRED: expected clean dedicated emulator (existing app preserved)'); return 2
    out=Path(tempfile.mkdtemp(prefix='android-mock-bridge-e2e-',dir=ROOT/'artifacts'))
    db='gamebridge_ci_'+secrets.token_hex(5); password=secrets.token_hex(24); key='local-v2-'+secrets.token_hex(24)
    for sql in (f"CREATE ROLE {db} LOGIN PASSWORD '{password}'",f'CREATE DATABASE {db} OWNER {db}'):
        created=run(['docker','exec','-i','gamebridge-sdk-local-postgres-1','psql','-X','-U','gamebridge','-d','postgres','-v','ON_ERROR_STOP=1'],input=sql+';\n')
        if created.returncode: print('CONFIG_REQUIRED: isolated local PostgreSQL unavailable'); return 2
    print('Retained dedicated test DB:',db,flush=True)
    with socket.socket() as sock: sock.bind(('127.0.0.1',0)); port=sock.getsockname()[1]
    env=os.environ.copy(); env.update(SPRING_PROFILES_ACTIVE='local-mock',DATABASE_URL=f'jdbc:postgresql://127.0.0.1:54329/{db}',DATABASE_USERNAME=db,DATABASE_PASSWORD=password,GAMEBRIDGE_PORT=str(port),GAMEBRIDGE_DEV_AUTH_KEY=key,SERVER_TOKEN_ENCRYPTION_KEY=base64.b64encode(secrets.token_bytes(32)).decode(),GAMEBRIDGE_MAINTENANCE_ENABLED='false',GAMEBRIDGE_LOCAL_TRACE_ENABLED='true')
    log=(out/'server.log').open('w'); server=subprocess.Popen(['java','-jar',str(ROOT/'backend/build/libs/gamebridge-backend.jar')],cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT)
    result={'status':'FAIL','scope':'Android Kotlin bridge and isolated local backend, not Unity','database':db,'sourceHead':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'sourceDirty':bool(subprocess.check_output(['git','status','--porcelain'],cwd=ROOT,text=True).strip())}
    try:
        for _ in range(160):
            if server.poll() is not None: raise RuntimeError('server exited')
            try:
                with urllib.request.urlopen(f'http://127.0.0.1:{port}/health',timeout=1) as response:
                    if response.status == 200: break
            except Exception: time.sleep(.25)
        else: raise RuntimeError('server health timeout')
        for apk in ('android/sample-app/build/outputs/apk/debug/sample-app-debug.apk','android/sample-app/build/outputs/apk/androidTest/debug/sample-app-debug-androidTest.apk'):
            installed=run([str(ADB),'-s',SERIAL,'install',str(ROOT/apk)],timeout=90)
            if installed.returncode: raise RuntimeError('test APK installation failed')
        command=[str(ADB),'-s',SERIAL,'shell','am','instrument','-w','-e','class','com.gamebridge.sample.LocalMockBridgeDeviceTest','-e','gamebridge_mock_url',f'http://10.0.2.2:{port}','-e','gamebridge_mock_key',key,'com.gamebridge.sample.test/androidx.test.runner.AndroidJUnitRunner']
        test=run(command,timeout=150); (out/'instrumentation.log').write_text(test.stdout.replace(key,'[REDACTED]'))
        if test.returncode or not re.search(r'OK \(1 test\)',test.stdout) or 'FAILURES!!!' in test.stdout: raise RuntimeError('instrumented Android test did not pass')
        device_log=run([str(ADB),'-s',SERIAL,'logcat','-d','-v','brief','-s','GB_NATIVE_E2E:I','*:S'],timeout=15)
        if device_log.returncode: raise RuntimeError('native diagnostic log unavailable')
        lines=[line for line in device_log.stdout.splitlines() if 'GB_NATIVE_E2E' in line]
        native='\n'.join(lines)+'\n'
        for operation in ('sdk.initialize','auth.signIn','store.products','store.purchase','store.entitlements','auth.signOut'):
            if not re.search(r'operation='+re.escape(operation)+r' requestId=[0-9a-f-]{36} status=PASS',native): raise RuntimeError('native request evidence missing')
        if key in native or password in native: raise RuntimeError('synthetic secret appeared in native log')
        (out/'native-requests.log').write_text(native)
        log.flush(); trace=(out/'server.log').read_text()
        operations=['mock-auth','catalog','entitlements','verify','logout']
        if any(not re.search(r'LOCAL_MOCK_TRACE operation='+op+r' method=(?:GET|POST) requestId=[0-9a-f-]{36} status=200',trace) for op in operations): raise RuntimeError('expected backend trace missing')
        if key in trace or password in trace: raise RuntimeError('synthetic secret appeared in server log')
        query=run(['docker','exec','-i','gamebridge-sdk-local-postgres-1','psql','-X','-U','gamebridge','-d',db,'-t','-A','-v','ON_ERROR_STOP=1'],input='SELECT count(*), coalesce(sum(delta),0) FROM wallet_ledger;\n')
        if query.returncode or query.stdout.strip()!='1|100': raise RuntimeError('wallet ledger assertion failed')
        result.update(status='PASS',tests=1,skipped=0,ledgerCount=1,ledgerDelta=100)
    except (OSError,RuntimeError,subprocess.TimeoutExpired) as exc: result['error']=str(exc)
    finally:
        server.terminate()
        try: server.wait(timeout=10)
        except subprocess.TimeoutExpired: server.kill(); server.wait()
        log.close(); (out/'result.json').write_text(json.dumps(result,indent=2)+'\n')
    print('Result:',result['status'],result.get('error',''),'Evidence:',out.relative_to(ROOT)); return 0 if result['status']=='PASS' else 1
if __name__=='__main__': raise SystemExit(main())
