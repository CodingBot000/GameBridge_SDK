#!/usr/bin/env python3
"""Opt-in Unity iOS Simulator LOCAL_MOCK push/lifecycle; never APNs."""
import argparse, importlib.util, json, os, re, secrets, select, shutil, socket, socketserver, subprocess, tempfile, threading, time, urllib.error, urllib.request, uuid
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
_redaction_spec = importlib.util.spec_from_file_location('local_mock_redaction', ROOT/'harness/local_mock_redaction.py')
_redaction = importlib.util.module_from_spec(_redaction_spec); _redaction_spec.loader.exec_module(_redaction)

BUNDLE='com.gamebridge.sdk.mockiosconsumer'
spec=importlib.util.spec_from_file_location('android_e2e',ROOT/'harness/run-unity-android-mock-e2e.py');common=importlib.util.module_from_spec(spec);spec.loader.exec_module(common)

class LinkProxy(socketserver.ThreadingTCPServer):
    allow_reuse_address=True; daemon_threads=True
    def __init__(self, upstream):
        super().__init__(('127.0.0.1',0),LinkHandler);self.upstream=upstream;self.online=True;self.rejected=0;self.lock=threading.Lock();self.connections=set()
    def disconnect(self):
        with self.lock:
            self.online=False
            for sock in list(self.connections):
                try: sock.shutdown(socket.SHUT_RDWR)
                except OSError: pass
    def reconnect(self):
        with self.lock:self.online=True
class LinkHandler(socketserver.BaseRequestHandler):
    def handle(self):
        proxy=self.server
        with proxy.lock:
            if not proxy.online:
                proxy.rejected += 1
                return
            proxy.connections.add(self.request)
        upstream=None
        try:
            upstream=socket.create_connection(('127.0.0.1',proxy.upstream),timeout=5)
            with proxy.lock:
                if not proxy.online:return
                proxy.connections.add(upstream)
            while True:
                readable,_,_=select.select([self.request,upstream],[],[],10)
                with proxy.lock:
                    if not proxy.online:return
                for source in readable:
                    data=source.recv(65536)
                    if not data:return
                    (upstream if source is self.request else self.request).sendall(data)
        except OSError: pass
        finally:
            with proxy.lock:
                proxy.connections.discard(self.request)
                if upstream:proxy.connections.discard(upstream)
            if upstream:upstream.close()

def embed_cached_packages(cache, project):
    """Copy exact previously resolved Unity packages into this disposable consumer only."""
    required={'com.unity.mobile.notifications':'2.5.0','com.unity.nuget.newtonsoft-json':'3.2.2'}
    resolved={}
    for name,version in required.items():
        candidates=[]
        for directory in cache.glob(name+'@*'):
            try:
                info=json.loads((directory/'package.json').read_text())
                if info.get('name')==name and info.get('version')==version: candidates.append(directory)
            except (OSError,ValueError): pass
        if len(candidates)!=1: raise common.GateError('CACHED_PACKAGE_MISSING_OR_AMBIGUOUS','DEFERRED_ENV')
        destination=project/'Packages'/name
        if destination.exists(): raise common.GateError('CACHED_PACKAGE_DESTINATION_EXISTS')
        # Package tests are not runtime dependencies; embedded test assemblies otherwise
        # become visible to the consumer without the Unity Test Framework.
        shutil.copytree(candidates[0],destination,ignore=shutil.ignore_patterns("Tests", "Tests.meta"))
        if json.loads((destination/'package.json').read_text()).get('version')!=version: raise common.GateError('CACHED_PACKAGE_COPY_INVALID')
        resolved[name]=version
    return resolved

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--run-local',required=True,action='store_true');ap.add_argument('--staging',required=True,type=Path);ap.add_argument('--package-cache',type=Path,help='Existing exact-version Unity PackageCache to copy into isolated project');args=ap.parse_args()
    out=Path(tempfile.mkdtemp(prefix='unity-ios-push-',dir=ROOT/'artifacts'));must=common.must;run=common.run;server=log=proxy=player=None;markers=[];leaks=[]
    head=must(['git','rev-parse','HEAD'],'GIT_HEAD').strip();dirty=bool(must(['git','status','--porcelain','--untracked-files=no'],'GIT_STATUS').strip());result={'status':'FAIL','scope':'Unity iOS Simulator LOCAL_MOCK push; not APNs','sourceHead':head,'sourceTrackedDirty':dirty,'player':'NOT_RUN','background':'NOT_RUN','networkRecovery':'NOT_RUN','processRestart':'NOT_RUN'}
    try:
        stage=args.staging.resolve();must(['python3','harness/check-staging.py',stage],'STAGING_INVALID');common.verify_staged_source_matches_checkout(stage)
        env=os.environ.copy();env['GAMEBRIDGE_UPM_STAGING']=str(stage);prepared=must(['bash','scripts/prepare-unity-ios-mock.sh','--prepare'],'PREPARE_FAILED',env=env);match=re.search(r'^Prepared consumer: (/.+)$',prepared,re.M)
        if not match:raise common.GateError('CONSUMER_PATH')
        project=Path(match.group(1))
        if args.package_cache:result['embeddedCachedPackages']=embed_cached_packages(args.package_cache.resolve(),project)
        shutil.copy2(ROOT/'tests/UnityIosPushConsumer/MockIosPlayerScenario.cs',project/'Assets/MockIosPlayerScenario.cs');shutil.copy2(ROOT/'tests/UnityLateCallbackPlayer/LateCallbackProbe.cs',project/'Assets/LateCallbackProbe.cs');shutil.copy2(ROOT/'tests/UnityLateCallbackPlayer/link.xml',project/'Assets/link.xml');xcode=out/'xcode'
        export=run(['bash','scripts/build-unity-ios-mock.sh',project,xcode],timeout=1200,env=env);(out/'unity-export.log').write_text(export.stdout)
        if export.returncode:raise common.GateError('UNITY_EXPORT_FAILED')
        derived=out/'Derived';build=run(['xcodebuild','-project',xcode/'Unity-iPhone.xcodeproj','-scheme','Unity-iPhone','-configuration','Debug','-sdk','iphonesimulator','-derivedDataPath',derived,'ARCHS=arm64','CODE_SIGN_IDENTITY=-','CODE_SIGNING_REQUIRED=YES','build','-quiet'],timeout=600);(out/'xcodebuild.log').write_text(build.stdout)
        if build.returncode:raise common.GateError('XCODE_BUILD_FAILED')
        products=derived/'Build/Products/Debug-iphonesimulator';app=next(products.glob('*.app'));binary=products/'UnityFramework.framework/UnityFramework'
        result['binarySha256']=common.sha256(binary);result['player']='BUILT_NOT_RUN'
        must(['backend/gradlew','-p','backend','bootJar'],'BACKEND_BUILD',timeout=240);db,password=common.create_isolated_database('gamebridge-sdk-local-postgres-1','gamebridge',54329);result['database']=db
        installation=str(uuid.uuid4());admin='local-admin-'+secrets.token_hex(24);os.environ['GAMEBRIDGE_DEV_PUSH_ADMIN_KEY']=admin;os.environ['GAMEBRIDGE_DEV_PUSH_ALLOWLIST']=installation
        server,log,port,key=common.start_backend(ROOT/'backend/build/libs/gamebridge-backend.jar',out,db,password,54329)
        proxy=LinkProxy(port);threading.Thread(target=proxy.serve_forever,daemon=True).start();proxyport=proxy.server_address[1]
        def post(endpoint,body,headers):
            req=urllib.request.Request(f'http://127.0.0.1:{port}'+endpoint,data=json.dumps(body).encode(),headers={'Content-Type':'application/json',**headers},method='POST')
            try:
                with urllib.request.urlopen(req,timeout=10) as r:return r.status,json.loads(r.read())
            except urllib.error.HTTPError as exc:return exc.code,{}
        status,auth=post('/v1/dev/auth',{'subject':'A'},{'X-Development-Key':key})
        if status!=200 or 'accessToken' not in auth:raise common.GateError('HOST_AUTH_FAILED')
        bearer=auth['accessToken'];body={'installationId':installation,'messageId':'unity-push-test','route':'home','title':'mock','body':'mock'}
        def send(message='unity-push-test',token=None):
            body['messageId']=message;return post('/v1/dev/push/send',body,{'X-Admin-Key':admin,'Authorization':'Bearer '+(token or bearer)})
        suffix=secrets.token_hex(5);sim=must(['xcrun','simctl','create','GameBridge-Unity-iOS-Push-'+suffix,'com.apple.CoreSimulator.SimDeviceType.iPhone-16','com.apple.CoreSimulator.SimRuntime.iOS-18-6'],'SIMULATOR_CREATE').strip();result['simulator']=sim
        for command in (['boot',sim],['bootstatus',sim,'-b'],['install',sim,app]):must(['xcrun','simctl']+command,'SIMULATOR_'+command[0].upper(),timeout=180)
        launch_env=os.environ.copy();launch_env.update(SIMCTL_CHILD_GAMEBRIDGE_IOS_MOCK_URL=f'http://127.0.0.1:{proxyport}',SIMCTL_CHILD_GAMEBRIDGE_IOS_MOCK_KEY=key,SIMCTL_CHILD_GAMEBRIDGE_IOS_MOCK_INSTALLATION=installation)
        player=subprocess.Popen(['xcrun','simctl','launch','--console',sim,BUNDLE],cwd=ROOT,env=launch_env,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,bufsize=1)
        def capture():
            for line in player.stdout:
                if any(secret in line for secret in (key,password,admin,bearer)) or _redaction.contains_mock_credential(line):leaks.append(True);continue
                if 'GB_PUSH_' in line:markers.append(line.strip())
        threading.Thread(target=capture,daemon=True).start()
        def wait(marker,seconds=90):
            deadline=time.monotonic()+seconds
            while time.monotonic()<deadline:
                text='\n'.join(markers)
                if leaks:raise common.GateError('SECRET_IN_PLAYER_LOG')
                if 'GB_PUSH_RESULT FAIL' in text:raise common.GateError('PLAYER_REPORTED_FAILURE')
                if marker in text:return text
                if player.poll() is not None:raise common.GateError('PLAYER_EXITED')
                time.sleep(.5)
            raise common.GateError('TIMEOUT_'+marker)
        wait('GB_PUSH_READY');time.sleep(5)
        for _ in range(2):
            status,reply=send()
            if status!=200 or reply.get('delivery')!='SIMULATED':raise common.GateError('MOCK_SEND_FAILED')
            time.sleep(.4)
        wait('GB_PUSH_RECEIVED 1');wait('GB_PUSH_WAIT_BACKGROUND')
        must(['xcrun','simctl','openurl',sim,f'http://127.0.0.1:{port}/health'],'BACKGROUND_FAILED',timeout=30);wait('GB_PUSH_BACKGROUND')
        must(['xcrun','simctl','launch',sim,BUNDLE],'FOREGROUND_FAILED',timeout=30);wait('GB_PUSH_FOREGROUND');wait('GB_PUSH_WAIT_OFFLINE')
        proxy.disconnect();time.sleep(18)
        if proxy.rejected < 1:raise common.GateError('RECONNECT_FAILURE_NOT_OBSERVED')
        status,reply=send('unity-offline-test')
        if status!=200 or reply.get('delivery')!='SIMULATED':raise common.GateError('OFFLINE_SEND_FAILED')
        result['rejectedReconnectAttempts']=proxy.rejected
        proxy.reconnect();time.sleep(22)
        for _ in range(2):
            status,reply=send('unity-reconnected-test')
            if status!=200 or reply.get('delivery')!='SIMULATED':raise common.GateError('RECONNECTED_SEND_FAILED')
            time.sleep(.4)
        wait('GB_PUSH_RECONNECTED_RECEIVED');wait('GB_PUSH_UNREGISTERED')
        status,_=send()
        if status!=403:raise common.GateError('UNREGISTERED_SEND_NOT_REJECTED')
        wait('GB_PUSH_B_READY');status,_=send()
        if status!=403:raise common.GateError('PREVIOUS_SESSION_SEND_NOT_REJECTED')
        status,auth_b=post('/v1/dev/auth',{'subject':'B'},{'X-Development-Key':key})
        if status!=200 or 'accessToken' not in auth_b:raise common.GateError('HOST_AUTH_B_FAILED')
        bearer_b=auth_b['accessToken'];time.sleep(5)
        for _ in range(2):
            status,reply=send('unity-session-b',bearer_b)
            if status!=200 or reply.get('delivery')!='SIMULATED':raise common.GateError('SESSION_B_SEND_FAILED')
            time.sleep(.4)
        text=wait('GB_PUSH_RESULT PASS LOCAL_MOCK')
        for required in ('GB_PUSH_STEP receive-deduplicate-main-thread PASS','GB_PUSH_STEP background-foreground-main-thread PASS','GB_PUSH_STEP network-recovery-online-only PASS','GB_PUSH_STEP unregister-logout-no-late-event PASS','GB_PUSH_STEP session-switch-no-stale-event PASS','GB_PUSH_STEP synthetic-late-callback-rejected PASS'):
            if required not in text:raise common.GateError('PUSH_ASSERTIONS_MISSING')
        if text.count('GB_PUSH_RECEIVED 1')!=1 or 'GB_PUSH_RECEIVED 2' in text:raise common.GateError('PUSH_DUPLICATE')
        log.flush();trace=(out/'server.log').read_text()
        if any(secret in trace for secret in (key,password,admin,bearer,bearer_b)) or _redaction.contains_mock_credential(trace):raise common.GateError('SECRET_IN_SERVER_LOG')
        dbcheck=must(['docker','exec','-i','gamebridge-sdk-local-postgres-1','psql','-X','-U','gamebridge','-d',db,'-t','-A','-v','ON_ERROR_STOP=1'],'PUSH_DB_QUERY',input_text='SELECT count(*) FROM device_tokens;\n')
        if dbcheck.strip()!='0':raise common.GateError('PUSH_TOKEN_NOT_DELETED')
        result.update(status='PASS',player='PASS',mockPush='PASS',deduplication='PASS',mainThread='PASS',background='PASS',networkRecovery='PASS_LOCAL_TRANSPORT_FAULT',reconnectFailure='PASS',sessionSwitch='PASS',deviceTokens=0)
    except KeyboardInterrupt:result.update(status='INTERRUPTED',errorCode='USER_OR_ENV_INTERRUPTION')
    except common.GateError as error:result.update(status=error.category,errorCode=str(error))
    except Exception as error:result['errorCode']=type(error).__name__
    finally:
        if player and player.poll() is None:player.terminate();player.wait(timeout=10)
        if markers and not leaks:(out/'unity-push-markers.log').write_text('\n'.join(markers)+'\n')
        if proxy:proxy.shutdown();proxy.server_close()
        if server:
            server.terminate()
            try:server.wait(timeout=10)
            except subprocess.TimeoutExpired:server.kill();server.wait()
        if log:log.close()
        (out/'result.json').write_text(json.dumps(result,indent=2)+'\n')
    print('RESULT',result['status'],result.get('errorCode',''),'EVIDENCE',out.relative_to(ROOT));return 0 if result['status']=='PASS' else 2 if result['status']=='DEFERRED_ENV' else 1
if __name__=='__main__':raise SystemExit(main())
