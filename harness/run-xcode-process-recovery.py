#!/usr/bin/env python3
"""Opt-in local StoreKit process-death test; retains dedicated simulator and DB."""
import base64, json, os, secrets, socket, subprocess, sys, tempfile, time, urllib.request
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
BUNDLE = 'com.gamebridge.sdk.recovery.harness'

def main():
    if sys.argv[1:] != ['--run-local']:
        print('Usage: run-xcode-process-recovery.py --run-local (retains dedicated simulator and DB)'); return 2
    initializer=os.environ.get('GAMEBRIDGE_PROCESS_STOREKIT_INIT','named')
    if initializer not in ('named','url'): print('CONFIG_REQUIRED: StoreKit initializer must be named or url'); return 2
    executor=os.environ.get('GAMEBRIDGE_PROCESS_STOREKIT_EXECUTOR','main')
    if executor not in ('main','background'): print('CONFIG_REQUIRED: StoreKit executor must be main or background'); return 2
    out = Path(tempfile.mkdtemp(prefix='xcode-process-recovery-', dir=ROOT/'artifacts'))
    suffix = secrets.token_hex(5); name = 'gamebridge_ci_'+suffix; password = secrets.token_hex(24)
    def run(args, **kw):
        return subprocess.run(args,cwd=ROOT,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,**kw)
    for sql in (f"CREATE ROLE {name} LOGIN PASSWORD '{password}'",f'CREATE DATABASE {name} OWNER {name}'):
        result = run(['docker','exec','-i','gamebridge-sdk-local-postgres-1','psql','-X','-U','gamebridge','-d','postgres','-v','ON_ERROR_STOP=1'],input=sql+';\n')
        if result.returncode: print('CONFIG_REQUIRED: local test DB unavailable'); return 2
    print('Retained test DB:',name,flush=True)
    with socket.socket() as sock: sock.bind(('127.0.0.1',0)); port=sock.getsockname()[1]
    base=f'http://127.0.0.1:{port}'; auth='local-process-'+secrets.token_hex(24)
    env=os.environ.copy(); env.update(SPRING_PROFILES_ACTIVE='local-mock',DATABASE_URL=f'jdbc:postgresql://127.0.0.1:54329/{name}',DATABASE_USERNAME=name,DATABASE_PASSWORD=password,GAMEBRIDGE_PORT=str(port),GAMEBRIDGE_DEV_AUTH_KEY=auth,SERVER_TOKEN_ENCRYPTION_KEY=base64.b64encode(secrets.token_bytes(32)).decode(),GAMEBRIDGE_MAINTENANCE_ENABLED='false',GAMEBRIDGE_FINALIZATION_POLL_INTERVAL_MS='3600000')
    build=run(['backend/gradlew','-p','backend','bootJar'],env=env); (out/'backend-build.log').write_text(build.stdout)
    if build.returncode: print('Backend build failed:',out); return 1
    project=run(['bash','scripts/generate-ios-project.sh']);
    if project.returncode: print('Xcode generation failed:',out); return 1
    runtime=os.environ.get('GAMEBRIDGE_PROCESS_SIM_RUNTIME','com.apple.CoreSimulator.SimRuntime.iOS-18-6')
    sim=run(['xcrun','simctl','create','GameBridge-Process-'+suffix,'com.apple.CoreSimulator.SimDeviceType.iPhone-16',runtime])
    if sim.returncode: print('Simulator unavailable:',out); return 2
    device=sim.stdout.strip(); print('Retained simulator:',device,flush=True)
    log=(out/'backend.log').open('w'); server=subprocess.Popen(['java','-jar',str(ROOT/'backend/build/libs/gamebridge-backend.jar')],cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT)
    report={'status':'FAIL','database':name,'simulator':device,'runtime':runtime,'storeKitInitializer':initializer,'storeKitExecutor':executor,'sourceHead':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'sourceDirty':bool(subprocess.check_output(['git','status','--porcelain'],cwd=ROOT,text=True).strip()),'limitations':['Xcode local StoreKit and synthetic local database only','not Unity or Apple sandbox']}
    try:
        deadline=time.monotonic()+60
        while time.monotonic()<deadline:
            if server.poll() is not None: raise RuntimeError('backend exited')
            try:
                with urllib.request.urlopen(base+'/health',timeout=1) as response:
                    if response.status==200: break
            except Exception: time.sleep(.25)
        else: raise RuntimeError('backend health timeout')
        derived=out/'Derived'; result=run(['xcodebuild','-project',project.stdout.strip().splitlines()[-1],'-scheme','GameBridgeRecoveryHarness','-configuration','Debug','-destination',f'platform=iOS Simulator,id={device}','-derivedDataPath',str(derived),'CODE_SIGN_IDENTITY=-','CODE_SIGNING_REQUIRED=YES','build','-quiet'],timeout=180)
        (out/'xcodebuild.log').write_text(result.stdout)
        if result.returncode: raise RuntimeError('test app build failed')
        app=derived/'Build/Products/Debug-iphonesimulator/GameBridgeRecoveryHarness.app'
        if not (app/'GameBridge.storekit').exists(): raise RuntimeError('StoreKit configuration missing')
        for args in (['boot',device],['bootstatus',device,'-b'],['install',device,str(app)]):
            result=run(['xcrun','simctl']+args,timeout=180)
            if result.returncode: raise RuntimeError('simulator setup failed: '+args[0])
        container=run(['xcrun','simctl','get_app_container',device,BUNDLE,'data'])
        if container.returncode: raise RuntimeError('app container unavailable')
        status=Path(container.stdout.strip())/'Documents/gamebridge-recovery-status.json'
        def launch(phase):
            launch_env=os.environ.copy(); launch_env.update(SIMCTL_CHILD_GAMEBRIDGE_PROCESS_TEST_PHASE=phase,SIMCTL_CHILD_GAMEBRIDGE_PROCESS_TEST_BASE_URL=base,SIMCTL_CHILD_GAMEBRIDGE_PROCESS_TEST_AUTH_KEY=auth,SIMCTL_CHILD_GAMEBRIDGE_PROCESS_STOREKIT_INIT=initializer,SIMCTL_CHILD_GAMEBRIDGE_PROCESS_STOREKIT_EXECUTOR=executor)
            result=run(['xcrun','simctl','launch',device,BUNDLE],env=launch_env,timeout=30)
            if result.returncode: raise RuntimeError('launch failed: '+phase)
            deadline=time.monotonic()+75
            while time.monotonic()<deadline:
                try: data=json.loads(status.read_text())
                except (OSError,ValueError): time.sleep(.25); continue
                if data.get('phase')=='failed': raise RuntimeError('app reported failure: '+str(data))
                if data.get('phase')==('pending' if phase=='prepare' else 'recovered'): return data
                time.sleep(.25)
            try: last=json.loads(status.read_text())
            except (OSError,ValueError): last={}
            raise RuntimeError('app phase timeout: '+phase+'; stage='+str(last.get('stage','unreported')))
        print('Testing committed purchase and process termination...',flush=True)
        first=launch('prepare'); report['prepare']=first
        terminated=run(['xcrun','simctl','terminate',device,BUNDLE],timeout=30)
        if terminated.returncode: raise RuntimeError('first process termination failed')
        second=launch('recover'); report['recover']=second
        if first.get('balance')!='100' or second.get('balance')!='100' or not first.get('pid') or first.get('pid')==second.get('pid'): raise RuntimeError('process or balance assertion failed')
        report['status']='PASS'
    except (RuntimeError,subprocess.TimeoutExpired) as exc: report['error']=str(exc)
    finally:
        run(['xcrun','simctl','terminate',device,BUNDLE],timeout=30)
        server.terminate()
        try: server.wait(timeout=10)
        except subprocess.TimeoutExpired: server.kill(); server.wait()
        log.close(); (out/'result.json').write_text(json.dumps(report,indent=2)+'\n')
    print('Result:',report['status'],report.get('error',''),'Evidence:',out.relative_to(ROOT)); return 0 if report['status']=='PASS' else 1
if __name__=='__main__': raise SystemExit(main())
