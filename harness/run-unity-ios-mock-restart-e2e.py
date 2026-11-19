#!/usr/bin/env python3
"""Opt-in Unity iOS Simulator LOCAL_MOCK process restart/pending test."""
import argparse, importlib.util, json, os, re, secrets, shutil, subprocess, tempfile, threading, time
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
BUNDLE='com.gamebridge.sdk.mockiosconsumer'
def load(name,path):
    spec=importlib.util.spec_from_file_location(name,ROOT/path);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module
common=load('android_e2e','harness/run-unity-android-mock-e2e.py');push=load('ios_push','harness/run-unity-ios-mock-push-e2e.py');restart=load('android_restart','harness/run-unity-android-mock-restart-e2e.py')

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--run-local',required=True,action='store_true');ap.add_argument('--staging',required=True,type=Path);ap.add_argument('--package-cache',type=Path);args=ap.parse_args()
    out=Path(tempfile.mkdtemp(prefix='unity-ios-restart-',dir=ROOT/'artifacts'));must=common.must;run=common.run;server=log=proxy=None;players=[];markers=[];leaks=[]
    head=must(['git','rev-parse','HEAD'],'GIT_HEAD').strip();dirty=bool(must(['git','status','--porcelain','--untracked-files=no'],'GIT_STATUS').strip());result={'status':'FAIL','scope':'Unity iOS Simulator LOCAL_MOCK process restart; not StoreKit','sourceHead':head,'sourceTrackedDirty':dirty,'player':'NOT_RUN'}
    try:
        stage=args.staging.resolve();must(['python3','harness/check-staging.py',stage],'STAGING_INVALID');common.verify_staged_source_matches_checkout(stage)
        env=os.environ.copy();env['GAMEBRIDGE_UPM_STAGING']=str(stage);prepared=must(['bash','scripts/prepare-unity-ios-mock.sh','--prepare'],'PREPARE_FAILED',env=env);match=re.search(r'^Prepared consumer: (/.+)$',prepared,re.M)
        if not match:raise common.GateError('CONSUMER_PATH')
        project=Path(match.group(1))
        if args.package_cache:result['embeddedCachedPackages']=push.embed_cached_packages(args.package_cache.resolve(),project)
        shutil.copy2(ROOT/'tests/UnityIosRestartConsumer/MockIosPlayerScenario.cs',project/'Assets/MockIosPlayerScenario.cs');xcode=out/'xcode'
        export=run(['bash','scripts/build-unity-ios-mock.sh',project,xcode],timeout=1200,env=env);(out/'unity-export.log').write_text(export.stdout)
        if export.returncode:raise common.GateError('UNITY_EXPORT_FAILED')
        derived=out/'Derived';build=run(['xcodebuild','-project',xcode/'Unity-iPhone.xcodeproj','-scheme','Unity-iPhone','-configuration','Debug','-sdk','iphonesimulator','-derivedDataPath',derived,'ARCHS=arm64','CODE_SIGN_IDENTITY=-','CODE_SIGNING_REQUIRED=YES','build','-quiet'],timeout=600);(out/'xcodebuild.log').write_text(build.stdout)
        if build.returncode:raise common.GateError('XCODE_BUILD_FAILED')
        products=derived/'Build/Products/Debug-iphonesimulator';app=next(products.glob('*.app'));binary=products/'UnityFramework.framework/UnityFramework';result['binarySha256']=common.sha256(binary);result['player']='BUILT_NOT_RUN'
        must(['backend/gradlew','-p','backend','bootJar'],'BACKEND_BUILD',timeout=240);db,password=common.create_isolated_database('gamebridge-sdk-local-postgres-1','gamebridge',54329);result['database']=db
        server,log,port,key=common.start_backend(ROOT/'backend/build/libs/gamebridge-backend.jar',out,db,password,54329)
        proxy=restart.FaultProxy(port);threading.Thread(target=proxy.serve_forever,daemon=True).start();proxyport=proxy.server_address[1]
        suffix=secrets.token_hex(5);sim=must(['xcrun','simctl','create','GameBridge-Unity-iOS-Restart-'+suffix,'com.apple.CoreSimulator.SimDeviceType.iPhone-16','com.apple.CoreSimulator.SimRuntime.iOS-18-6'],'SIMULATOR_CREATE').strip();result['simulator']=sim
        for command in (['boot',sim],['bootstatus',sim,'-b'],['install',sim,app]):must(['xcrun','simctl']+command,'SIMULATOR_'+command[0].upper(),timeout=180)
        def launch(phase):
            env=os.environ.copy();env.update(SIMCTL_CHILD_GAMEBRIDGE_IOS_MOCK_URL=f'http://127.0.0.1:{proxyport}',SIMCTL_CHILD_GAMEBRIDGE_IOS_MOCK_KEY=key,SIMCTL_CHILD_GAMEBRIDGE_IOS_MOCK_PHASE=phase)
            p=subprocess.Popen(['xcrun','simctl','launch','--console',sim,BUNDLE],cwd=ROOT,env=env,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,bufsize=1);players.append(p)
            def capture():
                for line in p.stdout:
                    if key in line or password in line:leaks.append(True);continue
                    if 'GB_RESTART_' in line:markers.append(line.strip())
            threading.Thread(target=capture,daemon=True).start()
        def wait(pattern,seconds=150):
            deadline=time.monotonic()+seconds
            while time.monotonic()<deadline:
                text='\n'.join(markers)
                if leaks:raise common.GateError('SECRET_IN_PLAYER_LOG')
                if 'GB_RESTART_RESULT FAIL' in text:raise common.GateError('PLAYER_REPORTED_FAILURE')
                match=re.search(pattern,text)
                if match:return match.group(1)
                if players[-1].poll() is not None:raise common.GateError('PLAYER_EXITED')
                time.sleep(.5)
            raise common.GateError('PLAYER_TIMEOUT')
        def ledger():return must(['docker','exec','-i','gamebridge-sdk-local-postgres-1','psql','-X','-U','gamebridge','-d',db,'-t','-A','-v','ON_ERROR_STOP=1'],'LEDGER_QUERY',input_text='SELECT count(*),coalesce(sum(delta),0) FROM wallet_ledger;\n').strip()
        launch('prepare');first=wait(r'GB_RESTART_PENDING PASS pid=(\d+)')
        if proxy.faults!=1 or ledger()!='1|100':raise common.GateError('FIRST_COMMIT_NOT_CONFIRMED')
        must(['xcrun','simctl','terminate',sim,BUNDLE],'TERMINATE_FAILED',timeout=30)
        launch('recover');second=wait(r'GB_RESTART_RESULT PASS LOCAL_MOCK MAIN_THREAD pid=(\d+)')
        if first==second or ledger()!='1|100':raise common.GateError('RESTART_OR_LEDGER_MISMATCH')
        log.flush();trace=(out/'server.log').read_text()
        if key in trace or password in trace:raise common.GateError('SECRET_IN_SERVER_LOG')
        result.update(status='PASS',player='PASS',processRestart='PASS',sessionRestore='PASS',pendingRecovery='PASS',ledgerCount=1,ledgerDelta=100)
    except KeyboardInterrupt:result.update(status='INTERRUPTED',errorCode='USER_OR_ENV_INTERRUPTION')
    except common.GateError as error:result.update(status=error.category,errorCode=str(error))
    except Exception as error:result['errorCode']=type(error).__name__
    finally:
        for p in players:
            if p.poll() is None:p.terminate();p.wait(timeout=10)
        if markers and not leaks:(out/'unity-restart-markers.log').write_text('\n'.join(markers)+'\n')
        if proxy:proxy.shutdown();proxy.server_close()
        if server:
            server.terminate()
            try:server.wait(timeout=10)
            except subprocess.TimeoutExpired:server.kill();server.wait()
        if log:log.close()
        (out/'result.json').write_text(json.dumps(result,indent=2)+'\n')
    print('RESULT',result['status'],result.get('errorCode',''),'EVIDENCE',out.relative_to(ROOT));return 0 if result['status']=='PASS' else 2 if result['status']=='DEFERRED_ENV' else 1
if __name__=='__main__':raise SystemExit(main())
