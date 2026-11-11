#!/usr/bin/env python3
"""Opt-in fresh Unity iOS Simulator -> Swift -> LOCAL_MOCK Backend/DB test."""
import argparse, base64, hashlib, json, os, re, secrets, socket, subprocess, sys, tempfile, threading, time, urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
BUNDLE='com.gamebridge.sdk.mockiosconsumer'
STEPS=('initialize','login','products','purchase','wallet','logout')
OPS=('mock-auth','catalog','entitlements','verify','logout')

def main():
    parser=argparse.ArgumentParser(); parser.add_argument('--run-local',action='store_true',required=True); parser.add_argument('--staging',type=Path,required=True); parser.add_argument('--adhoc',action='store_true',help='Use local ad-hoc Simulator signing; no Apple account'); args=parser.parse_args()
    out=Path(tempfile.mkdtemp(prefix='unity-ios-e2e-',dir=ROOT/'artifacts'))
    def run(cmd,**kw): return subprocess.run([str(x) for x in cmd],cwd=ROOT,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,**kw)
    def must(cmd,label,**kw):
        p=run(cmd,**kw)
        if p.returncode: raise RuntimeError(label)
        return p.stdout
    def digest(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
    head=must(['git','rev-parse','HEAD'],'git').strip(); dirty=bool(must(['git','status','--porcelain','--untracked-files=no'],'git-status').strip())
    result={'status':'FAIL','scope':'Unity iOS Simulator -> Swift C ABI -> LOCAL_MOCK Backend/PostgreSQL','sourceHead':head,'sourceTrackedDirty':dirty,'unityPlayer':'NOT_RUN','realAppleLogin':'NOT_RUN','realStorePurchase':'NOT_RUN'}
    server=None; serverlog=None; player=None; markers=[]; leaks=[]
    try:
        stage=args.staging.resolve(); must(['python3','harness/check-staging.py',stage],'staging')
        source=ROOT/'unity/Packages/com.gamebridge.sdk'; packaged=stage/'com.gamebridge.sdk'
        for item in source.rglob('*'):
            if item.is_file() and (not (packaged/item.relative_to(source)).is_file() or digest(item)!=digest(packaged/item.relative_to(source))): raise RuntimeError('UPM_STAGING_SOURCE_MISMATCH')
        framework=packaged/'Editor/GameBridgeArtifacts~/iOS/GameBridgeNative.xcframework'; must(['python3','scripts/verify-xcframework.py',framework],'xcframework')
        result['stagingManifestSha256']=digest(stage/'SHA256SUMS')
        result['iosSimulatorBinarySha256']=digest(framework/'ios-arm64_x86_64-simulator/GameBridgeNative.framework/GameBridgeNative')
        env=os.environ.copy(); env['GAMEBRIDGE_UPM_STAGING']=str(stage)
        prepared=must(['bash','scripts/prepare-unity-ios-mock.sh','--prepare'],'prepare',env=env)
        match=re.search(r'^Prepared consumer: (/.+)$',prepared,re.M)
        if not match: raise RuntimeError('consumer path')
        project=Path(match.group(1)); xcode=out/'xcode'
        exported=run(['bash','scripts/build-unity-ios-mock.sh',project,xcode],env=env,timeout=1200)
        (out/'unity-export.log').write_text(exported.stdout)
        if exported.returncode: raise RuntimeError('UNITY_EXPORT_FAILED')
        pbx=(xcode/'Unity-iPhone.xcodeproj/project.pbxproj').read_text()
        if 'GameBridgeNative.xcframework in Frameworks' not in pbx: raise RuntimeError('XCFRAMEWORK_NOT_LINKED')
        derived=out/'Derived'
        signing=['CODE_SIGN_IDENTITY=-','CODE_SIGNING_REQUIRED=YES'] if args.adhoc else ['CODE_SIGNING_ALLOWED=NO']
        result['signing']='local-ad-hoc' if args.adhoc else 'disabled'
        build=run(['xcodebuild','-project',xcode/'Unity-iPhone.xcodeproj','-scheme','Unity-iPhone','-configuration','Debug','-sdk','iphonesimulator','-derivedDataPath',derived,'ARCHS=arm64',*signing,'build','-quiet'],timeout=600)
        (out/'xcodebuild.log').write_text(build.stdout)
        if build.returncode: raise RuntimeError('XCODE_BUILD_FAILED')
        products=derived/'Build/Products/Debug-iphonesimulator'; app=next(products.glob('*.app'),None)
        binary=products/'UnityFramework.framework/UnityFramework'
        if app is None or not binary.is_file(): raise RuntimeError('SIMULATOR_APP_MISSING')
        symbols=must(['nm','-g',binary],'NM_FAILED')
        if any(not re.search(r'\b_GB_'+name+r'\b',symbols) for name in ('ProtocolVersion','SetCallback','Dispatch','Shutdown')): raise RuntimeError('C_ABI_SYMBOL_MISSING')
        result['unityPlayer']='BUILT_NOT_RUN'; result['unityBinarySha256']=digest(binary)
        bootjar=run(['backend/gradlew','-p','backend','bootJar'],timeout=240)
        (out/'backend-build.log').write_text(bootjar.stdout)
        if bootjar.returncode: raise RuntimeError('BACKEND_BUILD_FAILED')
        suffix=secrets.token_hex(5); db='gamebridge_ci_'+suffix; password=secrets.token_hex(24); key='unity-ios-'+secrets.token_hex(24)
        for sql in (f"CREATE ROLE {db} LOGIN PASSWORD '{password}'",f'CREATE DATABASE {db} OWNER {db}'):
            must(['docker','exec','-i','gamebridge-sdk-local-postgres-1','psql','-X','-U','gamebridge','-d','postgres','-v','ON_ERROR_STOP=1'],'DATABASE_CREATE_FAILED',input=sql+';\n')
        result['database']=db
        with socket.socket() as sock: sock.bind(('127.0.0.1',0)); port=sock.getsockname()[1]
        be=os.environ.copy(); be.update(SPRING_PROFILES_ACTIVE='local-mock',DATABASE_URL=f'jdbc:postgresql://127.0.0.1:54329/{db}',DATABASE_USERNAME=db,DATABASE_PASSWORD=password,GAMEBRIDGE_PORT=str(port),GAMEBRIDGE_DEV_AUTH_KEY=key,SERVER_TOKEN_ENCRYPTION_KEY=base64.b64encode(secrets.token_bytes(32)).decode(),GAMEBRIDGE_MAINTENANCE_ENABLED='false',GAMEBRIDGE_LOCAL_TRACE_ENABLED='true')
        serverlog=(out/'server.log').open('w'); server=subprocess.Popen(['java','-jar',str(ROOT/'backend/build/libs/gamebridge-backend.jar')],cwd=ROOT,env=be,stdout=serverlog,stderr=subprocess.STDOUT)
        for _ in range(160):
            if server.poll() is not None: raise RuntimeError('BACKEND_EXITED')
            try:
                with urllib.request.urlopen(f'http://127.0.0.1:{port}/health',timeout=1) as reply:
                    if reply.status==200: break
            except Exception: time.sleep(.25)
        else: raise RuntimeError('BACKEND_HEALTH_TIMEOUT')
        sim=must(['xcrun','simctl','create','GameBridge-Unity-iOS-'+suffix,'com.apple.CoreSimulator.SimDeviceType.iPhone-16','com.apple.CoreSimulator.SimRuntime.iOS-18-6'],'SIMULATOR_CREATE_FAILED').strip();result['simulator']=sim
        for command in (['boot',sim],['bootstatus',sim,'-b'],['install',sim,app]): must(['xcrun','simctl']+command,'SIMULATOR_'+command[0].upper()+'_FAILED',timeout=180)
        launch_env=os.environ.copy(); launch_env.update(SIMCTL_CHILD_GAMEBRIDGE_IOS_MOCK_URL=f'http://127.0.0.1:{port}',SIMCTL_CHILD_GAMEBRIDGE_IOS_MOCK_KEY=key)
        player=subprocess.Popen(['xcrun','simctl','launch','--console',sim,BUNDLE],cwd=ROOT,env=launch_env,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,bufsize=1)
        result['unityPlayer']='LAUNCHED_PENDING'
        def read_player():
            for line in player.stdout:
                if key in line or password in line: leaks.append(True); continue
                if 'GB_MOCK_' in line: markers.append(line.strip())
        thread=threading.Thread(target=read_player,daemon=True);thread.start()
        for _ in range(180):
            joined='\n'.join(markers)
            if leaks: raise RuntimeError('SYNTHETIC_SECRET_IN_PLAYER_LOG')
            if 'GB_MOCK_RESULT FAIL' in joined: raise RuntimeError('UNITY_PLAYER_REPORTED_FAILURE')
            if 'GB_MOCK_RESULT PASS LOCAL_MOCK' in joined: break
            if player.poll() is not None: raise RuntimeError('UNITY_PLAYER_EXITED')
            time.sleep(1)
        else: raise RuntimeError('UNITY_PLAYER_TIMEOUT')
        (out/'unity-test-markers.log').write_text('\n'.join(markers)+'\n')
        text='\n'.join(markers)
        for step in STEPS:
            if f'GB_MOCK_STEP {step} PASS' not in text: raise RuntimeError('UNITY_STEP_MISSING_'+step)
        if 'GB_MOCK_MAIN_THREAD PASS' not in text: raise RuntimeError('UNITY_MAIN_THREAD_MISSING')
        for kind in ('INITIALIZE','AUTH','PURCHASE'):
            if not re.search(r'GB_MOCK_NATIVE kind='+kind+r' outcome=SUCCEEDED requestId=[0-9a-fA-F-]{36}',text): raise RuntimeError('NATIVE_DIAGNOSTIC_MISSING_'+kind)
        serverlog.flush(); trace=(out/'server.log').read_text()
        if key in trace or password in trace: raise RuntimeError('SYNTHETIC_SECRET_IN_SERVER_LOG')
        counts={op:len(re.findall(r'LOCAL_MOCK_TRACE operation='+re.escape(op)+r' method=(?:GET|POST) requestId=[0-9a-fA-F-]{36} status=200',trace)) for op in OPS}
        if any(n<1 for n in counts.values()): raise RuntimeError('BACKEND_TRACE_MISSING')
        ledger=must(['docker','exec','-i','gamebridge-sdk-local-postgres-1','psql','-X','-U','gamebridge','-d',db,'-t','-A','-v','ON_ERROR_STOP=1'],'LEDGER_QUERY_FAILED',input='SELECT count(*),coalesce(sum(delta),0) FROM wallet_ledger;\n')
        if ledger.strip()!='1|100': raise RuntimeError('LEDGER_MISMATCH')
        result.update(status='PASS',unityPlayer='PASS',unityMarkerCount=len(markers),backendTraceCounts=counts,ledgerCount=1,ledgerDelta=100)
    except (RuntimeError,OSError,subprocess.TimeoutExpired,StopIteration) as exc: result['errorCode']=str(exc) if isinstance(exc,RuntimeError) else type(exc).__name__
    finally:
        if player and player.poll() is None: player.terminate(); player.wait(timeout=10)
        if markers and not leaks: (out/'unity-test-markers.log').write_text('\n'.join(markers)+'\n')
        if server:
            server.terminate()
            try: server.wait(timeout=10)
            except subprocess.TimeoutExpired: server.kill();server.wait()
        if serverlog: serverlog.close()
        (out/'result.json').write_text(json.dumps(result,indent=2)+'\n')
    print('RESULT',result['status'],result.get('errorCode',''),'EVIDENCE',out.relative_to(ROOT)); return 0 if result['status']=='PASS' else 1
if __name__=='__main__': raise SystemExit(main())
