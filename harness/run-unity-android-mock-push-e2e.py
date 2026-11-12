#!/usr/bin/env python3
"""Opt-in Unity Android LOCAL_MOCK push test. Never remote FCM; retains test data."""
import argparse, importlib.util, json, os, re, secrets, shutil, subprocess, sys, tempfile, threading, time, urllib.request, urllib.error, uuid
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
spec=importlib.util.spec_from_file_location('android_e2e',ROOT/'harness/run-unity-android-mock-e2e.py'); common=importlib.util.module_from_spec(spec);spec.loader.exec_module(common)
proxy_spec=importlib.util.spec_from_file_location('ios_push',ROOT/'harness/run-unity-ios-mock-push-e2e.py'); proxy_module=importlib.util.module_from_spec(proxy_spec);proxy_spec.loader.exec_module(proxy_module)

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--run-local',required=True,action='store_true');parser.add_argument('--staging',type=Path,required=True);parser.add_argument('--serial',required=True);parser.add_argument('--expected-avd',required=True);args=parser.parse_args()
    out=Path(tempfile.mkdtemp(prefix='unity-android-push-',dir=ROOT/'artifacts'));must=common.must;run=common.run;server=None;log=None;proxy=None;network_changed=False;adb=None;serial=None
    head=must(['git','rev-parse','HEAD'],'GIT_HEAD').strip();dirty=bool(must(['git','status','--porcelain','--untracked-files=no'],'GIT_STATUS').strip()); result={'status':'FAIL','scope':'Unity Android LOCAL_MOCK push; not FCM','sourceHead':head,'sourceTrackedDirty':dirty,'player':'NOT_RUN','background':'NOT_RUN','networkRecovery':'NOT_RUN','processRestart':'NOT_RUN'}
    try:
        stage=args.staging.resolve();must(['python3','harness/check-staging.py',stage],'STAGING_INVALID');common.verify_staged_source_matches_checkout(stage)
        adb=common.locate_adb(None)
        if not adb: raise common.GateError('ADB_MISSING','DEFERRED_ENV')
        serial,avd=common.find_dedicated_device(adb,args.serial,args.expected_avd);result['avd']=avd
        env=os.environ.copy();env['GAMEBRIDGE_UPM_STAGING']=str(stage)
        prepared=must(['bash','scripts/prepare-unity-android-mock.sh','--prepare'],'PREPARE_FAILED',env=env);match=re.search(r'^Prepared consumer: (/.+)$',prepared,re.M)
        if not match:raise common.GateError('CONSUMER_PATH')
        project=Path(match.group(1));shutil.copy2(ROOT/'tests/UnityAndroidPushConsumer/MockPlayerScenario.cs',project/'Assets/MockPlayerScenario.cs')
        apk=out/'push-consumer.apk';build=run(['bash','scripts/build-unity-android-mock.sh',project,apk],timeout=1200,env=env);(out/'unity-build.log').write_text(build.stdout)
        if build.returncode: raise common.GateError('UNITY_BUILD_FAILED')
        result['apkSha256']=common.sha256(apk);result['player']='BUILT_NOT_RUN'
        must(['backend/gradlew','-p','backend','bootJar'],'BACKEND_BUILD',timeout=240);db,password=common.create_isolated_database('gamebridge-sdk-local-postgres-1','gamebridge',54329);result['database']=db
        installation=str(uuid.uuid4());admin='local-admin-'+secrets.token_hex(24);os.environ['GAMEBRIDGE_DEV_PUSH_ADMIN_KEY']=admin;os.environ['GAMEBRIDGE_DEV_PUSH_ALLOWLIST']=installation
        server,log,port,key=common.start_backend(ROOT/'backend/build/libs/gamebridge-backend.jar',out,db,password,54329)
        proxy=proxy_module.LinkProxy(port);threading.Thread(target=proxy.serve_forever,daemon=True).start();proxyport=proxy.server_address[1]
        def post(endpoint,body,headers):
            req=urllib.request.Request(f'http://127.0.0.1:{port}'+endpoint,data=json.dumps(body).encode(),headers={'Content-Type':'application/json',**headers},method='POST')
            try:
                with urllib.request.urlopen(req,timeout=10) as r:return r.status,json.loads(r.read())
            except urllib.error.HTTPError as exc:return exc.code,{}
        status,auth=post('/v1/dev/auth',{'subject':'A'},{'X-Development-Key':key})
        if status!=200 or 'accessToken' not in auth:raise common.GateError('HOST_AUTH_FAILED')
        bearer=auth['accessToken'];body={'installationId':installation,'messageId':'unity-push-test','route':'home','title':'mock','body':'mock'}
        def send(message='unity-push-test'):
            body['messageId']=message
            return post('/v1/dev/push/send',body,{'X-Admin-Key':admin,'Authorization':'Bearer '+bearer})
        common.wait_for_dedicated_device(adb,serial,avd)
        installed=run([adb,'-s',serial,'install',apk],timeout=120);(out/'adb-install.log').write_text(installed.stdout)
        if installed.returncode or 'Success' not in installed.stdout:raise common.GateError('INSTALL_FAILED')
        must([adb,'-s',serial,'logcat','-c'],'LOGCAT_CLEAR')
        launch=run([adb,'-s',serial,'shell','am','start','-W','-n',common.PACKAGE+'/com.unity3d.player.UnityPlayerGameActivity','--es','gamebridge_mock_url',f'http://10.0.2.2:{proxyport}','--es','gamebridge_mock_key',key,'--es','gamebridge_installation',installation],timeout=30)
        (out/'adb-launch.log').write_text(launch.stdout.replace(key,'[REDACTED]'))
        if launch.returncode or not re.search(r'^Status:\s*ok\s*$',launch.stdout,re.M):raise common.GateError('LAUNCH_FAILED')
        def logs():
            text=must([adb,'-s',serial,'logcat','-d','-v','brief','-s','Unity:I','*:S'],'LOGCAT_FAILED',timeout=20)
            if key in text or password in text or admin in text or bearer in text:raise common.GateError('SYNTHETIC_SECRET_IN_PLAYER_LOG')
            return '\n'.join(line for line in text.splitlines() if 'GB_PUSH_' in line)
        def wait(marker,seconds=90):
            deadline=time.monotonic()+seconds
            while time.monotonic()<deadline:
                text=logs()
                if 'GB_PUSH_RESULT FAIL' in text:raise common.GateError('PLAYER_REPORTED_FAILURE')
                if marker in text:return text
                time.sleep(.5)
            raise common.GateError('TIMEOUT_'+marker)
        wait('GB_PUSH_READY');time.sleep(5)
        for _ in range(2):
            status,reply=send()
            if status!=200 or reply.get('delivery')!='SIMULATED':raise common.GateError('MOCK_SEND_FAILED')
            time.sleep(.4)
        wait('GB_PUSH_RECEIVED 1');wait('GB_PUSH_WAIT_BACKGROUND')
        must([adb,'-s',serial,'shell','input','keyevent','KEYCODE_HOME'],'BACKGROUND_FAILED')
        wait('GB_PUSH_BACKGROUND')
        resumed=run([adb,'-s',serial,'shell','am','start','-W','-n',common.PACKAGE+'/com.unity3d.player.UnityPlayerGameActivity'],timeout=30)
        if resumed.returncode or not re.search(r'^Status:\s*ok\s*$',resumed.stdout,re.M):raise common.GateError('FOREGROUND_FAILED')
        wait('GB_PUSH_FOREGROUND');wait('GB_PUSH_WAIT_OFFLINE')
        proxy.disconnect()
        network_changed=True
        must([adb,'-s',serial,'shell','svc','wifi','disable'],'WIFI_DISABLE_FAILED')
        must([adb,'-s',serial,'shell','svc','data','disable'],'DATA_DISABLE_FAILED')
        time.sleep(3)
        probe=run([adb,'-s',serial,'shell','toybox','nc','-w','3','10.0.2.2',str(port)],input_text='GET /health HTTP/1.0\r\n\r\n',timeout=10)
        if '200' in probe.stdout:raise common.GateError('NETWORK_STILL_ONLINE')
        status,reply=send('unity-offline-test')
        if status!=200 or reply.get('delivery')!='SIMULATED':raise common.GateError('OFFLINE_SEND_FAILED')
        must([adb,'-s',serial,'shell','svc','wifi','enable'],'WIFI_ENABLE_FAILED')
        must([adb,'-s',serial,'shell','svc','data','enable'],'DATA_ENABLE_FAILED')
        network_changed=False
        for _ in range(20):
            probe=run([adb,'-s',serial,'shell','toybox','nc','-w','3','10.0.2.2',str(port)],input_text='GET /health HTTP/1.0\r\n\r\n',timeout=10)
            if '200' in probe.stdout:break
            time.sleep(1)
        else:raise common.GateError('NETWORK_RESTORE_FAILED')
        time.sleep(18)
        if proxy.rejected < 1:raise common.GateError('RECONNECT_FAILURE_NOT_OBSERVED')
        result['rejectedReconnectAttempts']=proxy.rejected
        proxy.reconnect();time.sleep(22)
        for _ in range(2):
            status,reply=send('unity-reconnected-test')
            if status!=200 or reply.get('delivery')!='SIMULATED':raise common.GateError('RECONNECTED_SEND_FAILED')
            time.sleep(.4)
        wait('GB_PUSH_RECONNECTED_RECEIVED');wait('GB_PUSH_UNREGISTERED')
        status,_=send()
        if status!=403:raise common.GateError('UNREGISTERED_SEND_NOT_REJECTED')
        wait('GB_PUSH_B_READY')
        status,_=send('unity-push-test')
        if status!=403:raise common.GateError('PREVIOUS_SESSION_SEND_NOT_REJECTED')
        status,auth_b=post('/v1/dev/auth',{'subject':'B'},{'X-Development-Key':key})
        if status!=200 or 'accessToken' not in auth_b:raise common.GateError('HOST_AUTH_B_FAILED')
        bearer_b=auth_b['accessToken'];time.sleep(5)
        body['messageId']='unity-session-b'
        for _ in range(2):
            status,reply=post('/v1/dev/push/send',body,{'X-Admin-Key':admin,'Authorization':'Bearer '+bearer_b})
            if status!=200 or reply.get('delivery')!='SIMULATED':raise common.GateError('SESSION_B_SEND_FAILED')
            time.sleep(.4)
        text=wait('GB_PUSH_RESULT PASS LOCAL_MOCK');(out/'unity-push-markers.log').write_text(text+'\n')
        if text.count('GB_PUSH_RECEIVED 1')!=1 or 'GB_PUSH_RECEIVED 2' in text or 'GB_PUSH_STEP receive-deduplicate-main-thread PASS' not in text or 'GB_PUSH_STEP unregister-logout-no-late-event PASS' not in text or 'GB_PUSH_STEP background-foreground-main-thread PASS' not in text or 'GB_PUSH_STEP network-recovery-online-only PASS' not in text or 'GB_PUSH_STEP session-switch-no-stale-event PASS' not in text:raise common.GateError('PUSH_ASSERTIONS_MISSING')
        log.flush();trace=(out/'server.log').read_text()
        if any(secret in trace for secret in (key,password,admin,bearer,bearer_b)):raise common.GateError('SYNTHETIC_SECRET_IN_SERVER_LOG')
        dbcheck=must(['docker','exec','-i','gamebridge-sdk-local-postgres-1','psql','-X','-U','gamebridge','-d',db,'-t','-A','-v','ON_ERROR_STOP=1'],'PUSH_DB_QUERY',input_text='SELECT count(*) FROM device_tokens;\n')
        if dbcheck.strip()!='0':raise common.GateError('PUSH_TOKEN_NOT_DELETED')
        result.update(status='PASS',player='PASS',mockPush='PASS',deduplication='PASS',mainThread='PASS',unregisterLogout='PASS',background='PASS',networkRecovery='PASS',reconnectFailure='PASS',sessionSwitch='PASS',deviceTokens=0)
    except common.GateError as error:result.update(status=error.category,errorCode=str(error))
    except Exception as error:result['errorCode']=type(error).__name__
    finally:
        if network_changed and adb and serial:
            run([adb,'-s',serial,'shell','svc','wifi','enable'],timeout=15)
            run([adb,'-s',serial,'shell','svc','data','enable'],timeout=15)
        if proxy:proxy.shutdown();proxy.server_close()
        if server:
            server.terminate()
            try:server.wait(timeout=10)
            except subprocess.TimeoutExpired:server.kill();server.wait()
        if log:log.close()
        (out/'result.json').write_text(json.dumps(result,indent=2)+'\n')
    print('RESULT',result['status'],result.get('errorCode',''),'EVIDENCE',out.relative_to(ROOT));return 0 if result['status']=='PASS' else 2 if result['status']=='DEFERRED_ENV' else 1
if __name__=='__main__':raise SystemExit(main())
