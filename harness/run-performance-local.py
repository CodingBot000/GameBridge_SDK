#!/usr/bin/env python3
"""Opt-in pre-P10-T03 local measurements. Never store/FCM/APNs or Unity performance."""
import argparse,datetime,hashlib,importlib.util,json,os,platform,re,subprocess,tempfile,time,urllib.error,urllib.request,uuid
from pathlib import Path
from performance_contract import distribution,managed_summary,is_exact_coin_grant
ROOT=Path(__file__).resolve().parent.parent
spec=importlib.util.spec_from_file_location('performance_local_backend',ROOT/'harness/run-unity-android-mock-e2e.py');common=importlib.util.module_from_spec(spec);spec.loader.exec_module(common)

def main():
    p=argparse.ArgumentParser();p.add_argument('--run-local',required=True,action='store_true');p.add_argument('--backend-only',action='store_true');args=p.parse_args()
    out=Path(tempfile.mkdtemp(prefix='performance-local-',dir=ROOT/'artifacts'));head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    report=dict(status='FAIL',sourceHead=head,sourceTrackedDirty=bool(subprocess.check_output(['git','status','--porcelain','--untracked-files=no'],cwd=ROOT,text=True).strip()),scope='preliminary P10-T03 standalone managed fake + loopback LOCAL_MOCK HTTP/PostgreSQL; not full task completion',startedUtc=datetime.datetime.now(datetime.timezone.utc).isoformat(),os=platform.platform(),warmup=20,samples=100,managed='NOT_RUN',backend='NOT_RUN',realProviders='NOT_RUN',unityPlayerPerformance='NOT_RUN',nativeMemoryAndUiJank='NOT_RUN')
    report['selection']='backend-only' if args.backend_only else 'managed-and-backend'
    if args.backend_only:report['scope']='preliminary P10-T03 loopback LOCAL_MOCK HTTP/PostgreSQL only; managed not executed in this invocation'
    server=log=None;phase='managed'
    try:
        if not args.backend_only:
            r=subprocess.run(['bash','scripts/measure-managed-performance.sh'],cwd=ROOT,text=True,capture_output=True,timeout=180);(out/'managed.log').write_text(r.stdout+r.stderr)
            match=re.search(r'^Evidence directory: (.+)$',r.stdout,re.M)
            if r.returncode or not match:raise ValueError('MANAGED_MEASUREMENT_FAILED')
            directory=Path(match.group(1)).resolve()
            if not directory.is_relative_to(ROOT/'artifacts'):raise ValueError('MEASUREMENT_EVIDENCE_OUTSIDE_ARTIFACTS')
            raw=json.loads((directory/'result.json').read_text());report['managed']=managed_summary(raw,head);report['managedEvidence']=str(directory.relative_to(ROOT))
        phase='backend-build';build=subprocess.run(['backend/gradlew','-p','backend','bootJar'],cwd=ROOT,capture_output=True,text=True,timeout=240);(out/'backend-build.log').write_text(build.stdout+build.stderr)
        if build.returncode:raise ValueError('BACKEND_BUILD_FAILED')
        # The shared creator requires the owned local Compose container and creates a fresh role/DB.
        phase='isolated-database'
        endpoint=os.environ.get('DOCKER_HOST','')
        if not endpoint:
            context=subprocess.run(['docker','context','inspect','--format','{{.Endpoints.docker.Host}}'],cwd=ROOT,capture_output=True,text=True)
            if context.returncode:raise ValueError('LOCAL_DOCKER_CONTEXT_UNAVAILABLE')
            endpoint=context.stdout.strip()
        if not endpoint.startswith('unix://'):raise ValueError('LOCAL_DOCKER_UNIX_SOCKET_REQUIRED')
        db,password=common.create_isolated_database('gamebridge-sdk-local-postgres-1','gamebridge',54329)
        server,log,port,key=common.start_backend(ROOT/'backend/build/libs/gamebridge-backend.jar',out,db,password,54329)
        def call(method,path,body=None,token=None,idem=None,dev=False):
            headers={'Content-Type':'application/json'}
            if dev:headers['X-Development-Key']=key
            if token:headers['Authorization']='Bearer '+token
            if idem:headers['Idempotency-Key']=idem
            req=urllib.request.Request(f'http://127.0.0.1:{port}'+path,data=None if body is None else json.dumps(body).encode(),headers=headers,method=method)
            before=time.perf_counter_ns()
            try:
                with urllib.request.urlopen(req,timeout=10) as reply:code=reply.status;data=json.load(reply)
            except urllib.error.HTTPError as error:code=error.code;data=json.load(error)
            return code,data,(time.perf_counter_ns()-before)/1_000_000
        java=subprocess.run(['java','-version'],capture_output=True,text=True);report['javaVersion']=(java.stderr+java.stdout).splitlines()[:2]
        report['backend']={'status':'STARTED_NO_MEASUREMENTS'}
        phase='auth';code,user,_=call('POST','/v1/dev/auth',{'subject':'A'},dev=True)
        if code!=200:raise ValueError('MOCK_AUTH_FAILED')
        token=user['accessToken'];uid=user['userId'];phase='backend-measurements';timings={}
        report['backend']={'status':'PARTIAL','timings':timings}
        def measure(name,operation,accept):
            nonlocal phase
            phase='backend-'+name
            values=[]
            for index in range(120):
                code,body,elapsed=operation()
                if not accept(code,body):raise ValueError('MEASUREMENT_RESPONSE_INVARIANT')
                if index>=20:values.append(elapsed)
            timings[name]=distribution(values)
        measure('catalogLoopback',lambda:call('GET','/v1/catalog',token=token),lambda code,body:code==200 and {x['productId'] for x in body}=={'coins_100','premium_unlock'})
        idem=str(uuid.uuid4());proof={'productId':'coins_100','proof':f'mock:{uid}:coins_100:{uuid.uuid4()}','quantity':1}
        code,first,_=call('POST','/v1/purchases/verify',proof,token,idem)
        if code!=200 or not is_exact_coin_grant(first):raise ValueError('INITIAL_GRANT_INVARIANT')
        purchase=first['serverPurchaseId']
        measure('idempotentVerifyLoopback',lambda:call('POST','/v1/purchases/verify',proof,token,idem),lambda code,body:code==200 and is_exact_coin_grant(body,purchase))
        conflict={**proof,'proof':f'mock:{uid}:coins_100:{uuid.uuid4()}'}
        measure('conflictingVerifyLoopback',lambda:call('POST','/v1/purchases/verify',conflict,token,idem),lambda code,body:code==409 and body['code']=='IDEMPOTENCY_CONFLICT')
        common.assert_wallet_ledger('gamebridge-sdk-local-postgres-1','gamebridge',db)
        log.flush();text=(out/'server.log').read_text()
        if any(secret in text for secret in (key,password,token)) or common._redaction.contains_mock_credential(text):raise ValueError('SECRET_IN_SERVER_LOG')
        report.update(status='PASS',backend=dict(status='PASS',scope='single sequential loopback JVM/HTTP + PostgreSQL actual local-mock responses',clock='perf_counter_ns monotonic',clockResolutionSeconds=time.get_clock_info('perf_counter').resolution,build='Spring Boot bootJar; normal local JVM, no throughput or production claim',timings=timings,ledgerCount=1,ledgerDelta=100,duplicateMeasuredRequests=100,expectedConflictResponses=100,warmupDuplicateRequests=20,warmupConflictResponses=20,retainsIsolatedDatabase=True),backendJarSha256=hashlib.sha256((ROOT/'backend/build/libs/gamebridge-backend.jar').read_bytes()).hexdigest())
    except Exception as error:
        report.update(errorStage=phase,errorType=type(error).__name__)
        if re.fullmatch(r'[A-Z_]{1,80}',str(error)):report['errorCode']=str(error)
    finally:
        if server:
            server.terminate()
            try:server.wait(timeout=10)
            except subprocess.TimeoutExpired:server.kill();server.wait()
        if log:log.close()
        (out/'result.json').write_text(json.dumps(report,indent=2)+'\n')
    print('PERFORMANCE',report['status'],'evidence:',out.relative_to(ROOT));return 0 if report['status']=='PASS' else 1
if __name__=='__main__':raise SystemExit(main())
