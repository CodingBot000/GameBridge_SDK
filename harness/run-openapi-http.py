#!/usr/bin/env python3
"""Opt-in loopback LOCAL_MOCK response validation; never contacts a provider."""
import argparse,copy,importlib.util,json,subprocess,tempfile,urllib.error,urllib.request,uuid
from pathlib import Path
from jsonschema import Draft4Validator, RefResolver
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('local_backend',ROOT/'harness/run-unity-android-mock-e2e.py');common=importlib.util.module_from_spec(spec);spec.loader.exec_module(common)
def compatible(value):
    if isinstance(value,list):return [compatible(x) for x in value]
    if not isinstance(value,dict):return value
    result={k:compatible(v) for k,v in value.items() if k!='nullable'}
    if value.get('nullable'):
        return {'anyOf':[result,{'type':'null'}]}
    return result

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--run-local',required=True,action='store_true');parser.parse_args()
    out=Path(tempfile.mkdtemp(prefix='openapi-http-',dir=ROOT/'artifacts'))
    doc=json.loads((ROOT/'contracts/openapi.yaml').read_text());converted=compatible(doc)
    observations=[]; server=log=None
    result={'sourceHead':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'sourceState':'HEAD plus working changes','scope':'LOCAL_MOCK loopback; no provider credentials or live calls','operations':[], 'observations':observations,'status':'FAIL'}
    build=subprocess.run(['backend/gradlew','-p','backend','bootJar'],cwd=ROOT,capture_output=True,text=True)
    (out/'build.log').write_text(build.stdout+build.stderr)
    if build.returncode:return 1
    db,password=common.create_isolated_database('gamebridge-sdk-local-postgres-1','gamebridge',54329)
    try:
        server,log,port,key=common.start_backend(ROOT/'backend/build/libs/gamebridge-backend.jar',out,db,password,54329)
        token=None
        def call(method,path,body=None,expected=200,route=None,extra=None,auth=True):
            headers={'Content-Type':'application/json'}
            if auth and token:headers['Authorization']='Bearer '+token
            headers.update(extra or {})
            request=urllib.request.Request('http://127.0.0.1:'+str(port)+path,method=method.upper(),headers=headers,data=None if body is None else json.dumps(body).encode())
            try: reply=urllib.request.urlopen(request,timeout=8)
            except urllib.error.HTTPError as error:reply=error
            with reply:
                status=reply.status;data=json.load(reply);rid=reply.headers.get('X-Request-Id')
            operation=doc['paths'][route or path][method]
            schema=operation['responses']['200' if status==200 else 'default']['content']['application/json']['schema']
            Draft4Validator(compatible(schema),resolver=RefResolver.from_schema(converted)).validate(data)
            result['lastResponse']={'method':method,'path':route or path,'actual':status,'expected':expected}
            assert status==expected, (method,path,status,expected)
            assert rid and str(uuid.UUID(rid))==rid
            if status!=200:assert data['requestId']==rid
            observations.append({'path':route or path,'method':method,'status':status,'schema':'PASS','requestIdCorrelation':'PASS' if status!=200 else 'HEADER_UUID_PASS'})
            return data
        call('get','/health');call('get','/v1/config');call('get','/v1/me',expected=401)
        call('post','/v1/dev/auth',{'subject':'A'},expected=403,auth=False)
        call('post','/v1/dev/auth',{},expected=400,extra={'X-Development-Key':key},auth=False)
        user=call('post','/v1/dev/auth',{'subject':'A'},extra={'X-Development-Key':key},auth=False);token=user['accessToken']
        call('get','/v1/me');call('get','/v1/catalog');call('get','/v1/entitlements');call('get','/v1/purchases/bindings')
        call('post','/v1/auth/challenges',{'appId':'no-provider-config','provider':'GOOGLE'},expected=404)
        call('post','/v1/auth/exchange',{'challengeId':str(uuid.uuid4()),'provider':'GOOGLE','idToken':'synthetic-invalid'},expected=404)
        payload={'productId':'coins_100','proof':'mock:'+user['userId']+':coins_100:'+str(uuid.uuid4()),'quantity':1}
        call('post','/v1/purchases/verify',payload,expected=400) # Required header failure must be a client error.
        idem={'Idempotency-Key':str(uuid.uuid4())}
        call('post','/v1/purchases/verify',payload,extra=idem);call('post','/v1/purchases/verify',payload,extra=idem)
        changed=dict(payload,proof='mock:'+user['userId']+':coins_100:'+str(uuid.uuid4()))
        call('post','/v1/purchases/verify',changed,extra=idem,expected=409)
        device=str(uuid.uuid4());route='/v1/devices/{installationId}/push-token';url='/v1/devices/'+device+'/push-token'
        call('put',url,{'token':'synthetic-local-token','provider':'MOCK','platform':'MOCK','appId':'gamebridge-sample'},route=route)
        call('post','/v1/dev/push/send',{'installationId':device,'messageId':'measurement','route':'home','title':'test','body':'test'},expected=503)
        # SSE successful handshake has a separate text/event-stream response schema.
        request=urllib.request.Request('http://127.0.0.1:'+str(port)+'/v1/dev/push/stream?installationId='+device,headers={'Authorization':'Bearer '+token})
        with urllib.request.urlopen(request,timeout=8) as reply:
            assert reply.status==200 and reply.headers.get('Content-Type','').startswith('text/event-stream')
            line=reply.readline().decode();assert 'ready' in line
        observations.append({'path':'/v1/dev/push/stream','method':'get','status':200,'schema':'SSE_READY_HANDSHAKE_ONLY'})
        call('delete',url,route=route);call('delete',url,route=route,expected=403)
        dev={'X-Development-Key':key};account=call('post','/v1/dev/xcode-storekit/account',extra=dev)
        call('post','/v1/dev/xcode-storekit/grant',{'productId':'coins_100','transactionId':'a'*64,'bindingId':account['bindingId'],'attemptId':str(uuid.uuid4())},extra=dev)
        call('post','/v1/dev/xcode-storekit/wallet',extra=dev)
        for platform in ('apple','google'):
            for operation in ('readiness','verify'):
                call('post',f'/v1/purchases/{platform}/{operation}',{'storeProductId':'synthetic'},expected=404)
        call('get','/v1/purchases/'+str(uuid.uuid4()),route='/v1/purchases/{purchaseId}',expected=404)
        refreshed=call('post','/v1/auth/refresh',{'refreshToken':user['refreshToken']},auth=False);token=refreshed['accessToken']
        call('post','/v1/auth/logout');token=None
        call('post','/v1/auth/refresh',{'refreshToken':refreshed['refreshToken']},expected=401,auth=False)
        for path,ops in doc['paths'].items():
            for method in ops:
                seen=[o for o in observations if o['path']==path and o['method']==method]
                result['operations'].append({'path':path,'method':method,'staticBinding':'PASS','localHttpStatuses':sorted({o['status'] for o in seen}),'runtimeScope':'LOCAL_MOCK_SUCCESS_AND_SELECTED_ERRORS' if any(o['status']==200 for o in seen) else 'PROFILE_ABSENCE_OR_SELECTED_ERRORS_ONLY','sandboxSuccess':'NOT_RUN','providerSuccess':'NOT_RUN'})
        result.update(status='PASS',database=db,observationsCount=len(observations))
        return 0
    except Exception as error:
        result['failureType']=type(error).__name__;print('HTTP contract FAIL:',type(error).__name__);return 1
    finally:
        if server:
            server.terminate();server.wait(timeout=15)
        if log:log.close()
        (out/'result.json').write_text(json.dumps(result,indent=2)+'\n');print('Evidence directory:',out.relative_to(ROOT))
if __name__=='__main__':raise SystemExit(main())
