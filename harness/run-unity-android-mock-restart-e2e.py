#!/usr/bin/env python3
"""Opt-in Unity Android process restart / LOCAL_MOCK pending purchase test."""
import argparse, http.client, http.server, importlib.util, json, os, re, shutil, subprocess, threading, time
from pathlib import Path
import tempfile
ROOT=Path(__file__).resolve().parent.parent
spec=importlib.util.spec_from_file_location('android_e2e',ROOT/'harness/run-unity-android-mock-e2e.py');common=importlib.util.module_from_spec(spec);spec.loader.exec_module(common)

class FaultProxy(http.server.ThreadingHTTPServer):
    daemon_threads=True
    def __init__(self, upstream): super().__init__(('127.0.0.1',0),Handler); self.upstream=upstream; self.faults=0; self.lock=threading.Lock()
class Handler(http.server.BaseHTTPRequestHandler):
    def log_message(self, *args): pass
    def do_GET(self): self.forward()
    def do_POST(self): self.forward()
    def forward(self):
        length=int(self.headers.get('Content-Length','0'))
        if length<0 or length>262144: self.send_error(413);return
        body=self.rfile.read(length); headers={k:v for k,v in self.headers.items() if k.lower() not in ('host','connection','content-length','transfer-encoding')}
        conn=http.client.HTTPConnection('127.0.0.1',self.server.upstream,timeout=30)
        try:
            conn.request(self.command,self.path,body=body if length else None,headers=headers);response=conn.getresponse();data=response.read(262145)
            if len(data)>262144:self.send_error(502);return
            fault=False
            with self.server.lock:
                if self.command=='POST' and self.path=='/v1/purchases/verify' and response.status==200 and self.server.faults==0: self.server.faults+=1;fault=True
            if fault:
                self.send_response(503);self.send_header('Content-Type','application/json');data=b'{"code":"NETWORK_UNAVAILABLE","retryable":true}'
            else:
                self.send_response(response.status)
                if response.getheader('Content-Type'):self.send_header('Content-Type',response.getheader('Content-Type'))
                if response.getheader('X-Request-Id'):self.send_header('X-Request-Id',response.getheader('X-Request-Id'))
            self.send_header('Content-Length',str(len(data)));self.end_headers();self.wfile.write(data)
        finally: conn.close()

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--run-local',required=True,action='store_true');ap.add_argument('--staging',type=Path,required=True);ap.add_argument('--serial',required=True);ap.add_argument('--expected-avd',required=True);args=ap.parse_args()
    out=Path(tempfile.mkdtemp(prefix='unity-android-restart-',dir=ROOT/'artifacts'));must=common.must;run=common.run;server=log=proxy=None
    head=must(['git','rev-parse','HEAD'],'GIT_HEAD').strip();dirty=bool(must(['git','status','--porcelain','--untracked-files=no'],'GIT_STATUS').strip());result={'status':'FAIL','scope':'Unity Android LOCAL_MOCK process restart; not Play Billing','sourceHead':head,'sourceTrackedDirty':dirty,'player':'NOT_RUN'}
    try:
        stage=args.staging.resolve();must(['python3','harness/check-staging.py',stage],'STAGING_INVALID');common.verify_staged_source_matches_checkout(stage);adb=common.locate_adb(None)
        if not adb:raise common.GateError('ADB_MISSING','DEFERRED_ENV')
        serial,avd=common.find_dedicated_device(adb,args.serial,args.expected_avd)
        env=os.environ.copy();env['GAMEBRIDGE_UPM_STAGING']=str(stage);prepared=must(['bash','scripts/prepare-unity-android-mock.sh','--prepare'],'PREPARE_FAILED',env=env);match=re.search(r'^Prepared consumer: (/.+)$',prepared,re.M)
        if not match:raise common.GateError('CONSUMER_PATH')
        project=Path(match.group(1));shutil.copy2(ROOT/'tests/UnityAndroidRestartConsumer/MockPlayerScenario.cs',project/'Assets/MockPlayerScenario.cs');apk=out/'restart-consumer.apk'
        build=run(['bash','scripts/build-unity-android-mock.sh',project,apk],timeout=1200,env=env);(out/'unity-build.log').write_text(build.stdout)
        if build.returncode:raise common.GateError('UNITY_BUILD_FAILED')
        result['apkSha256']=common.sha256(apk);must(['backend/gradlew','-p','backend','bootJar'],'BACKEND_BUILD',timeout=240)
        db,password=common.create_isolated_database('gamebridge-sdk-local-postgres-1','gamebridge',54329);result['database']=db
        server,log,port,key=common.start_backend(ROOT/'backend/build/libs/gamebridge-backend.jar',out,db,password,54329)
        proxy=FaultProxy(port);threading.Thread(target=proxy.serve_forever,daemon=True).start();proxyport=proxy.server_address[1]
        common.wait_for_dedicated_device(adb,serial,avd);install=run([adb,'-s',serial,'install',apk],timeout=120);(out/'adb-install.log').write_text(install.stdout)
        if install.returncode or 'Success' not in install.stdout:raise common.GateError('INSTALL_FAILED')
        must([adb,'-s',serial,'logcat','-c'],'LOGCAT_CLEAR')
        def launch(phase):
            p=run([adb,'-s',serial,'shell','am','start','-W','-n',common.PACKAGE+'/com.unity3d.player.UnityPlayerGameActivity','--es','gamebridge_mock_url',f'http://10.0.2.2:{proxyport}','--es','gamebridge_mock_key',key,'--es','gamebridge_phase',phase],timeout=30)
            if p.returncode or not re.search(r'^Status:\s*ok\s*$',p.stdout,re.M):raise common.GateError('LAUNCH_FAILED_'+phase)
        def wait(marker,seconds=120):
            deadline=time.monotonic()+seconds
            while time.monotonic()<deadline:
                text=must([adb,'-s',serial,'logcat','-d','-v','brief','-s','Unity:I','*:S'],'LOGCAT_FAILED',timeout=20)
                if key in text or password in text:raise common.GateError('SYNTHETIC_SECRET_IN_LOG')
                markers='\n'.join(line for line in text.splitlines() if 'GB_RESTART_' in line)
                (out/'markers.log').write_text(markers+'\n')
                if 'GB_RESTART_RESULT FAIL' in markers:raise common.GateError('PLAYER_REPORTED_FAILURE')
                if marker in markers:return
                time.sleep(.5)
            raise common.GateError('TIMEOUT_'+marker)
        def pid():return must([adb,'-s',serial,'shell','pidof',common.PACKAGE],'PID_UNAVAILABLE').strip()
        def ledger():return must(['docker','exec','-i','gamebridge-sdk-local-postgres-1','psql','-X','-U','gamebridge','-d',db,'-t','-A','-v','ON_ERROR_STOP=1'],'LEDGER_QUERY',input_text='SELECT count(*),coalesce(sum(delta),0) FROM wallet_ledger;\n').strip()
        launch('prepare');wait('GB_RESTART_PENDING PASS')
        if proxy.faults!=1 or ledger()!='1|100':raise common.GateError('FIRST_COMMIT_NOT_CONFIRMED')
        first=pid();must([adb,'-s',serial,'shell','am','force-stop',common.PACKAGE],'FORCE_STOP_FAILED');launch('recover');second=pid()
        if first==second or not first or not second:raise common.GateError('PROCESS_NOT_RESTARTED')
        wait('GB_RESTART_RESULT PASS LOCAL_MOCK MAIN_THREAD')
        if ledger()!='1|100':raise common.GateError('DUPLICATE_LEDGER')
        log.flush();trace=(out/'server.log').read_text()
        if key in trace or password in trace:raise common.GateError('SECRET_IN_SERVER_LOG')
        result.update(status='PASS',player='PASS',processRestart='PASS',sessionRestore='PASS',pendingRecovery='PASS',ledgerCount=1,ledgerDelta=100,firstPid=first,secondPid=second)
    except common.GateError as error:result.update(status=error.category,errorCode=str(error))
    except Exception as error:result['errorCode']=type(error).__name__
    finally:
        if proxy:proxy.shutdown();proxy.server_close()
        if server:
            server.terminate()
            try:server.wait(timeout=10)
            except subprocess.TimeoutExpired:server.kill();server.wait()
        if log:log.close()
        (out/'result.json').write_text(json.dumps(result,indent=2)+'\n')
    print('RESULT',result['status'],result.get('errorCode',''),'EVIDENCE',out.relative_to(ROOT));return 0 if result['status']=='PASS' else 2 if result['status']=='DEFERRED_ENV' else 1
if __name__=='__main__':raise SystemExit(main())
