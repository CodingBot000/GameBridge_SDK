"""Validate measured monotonic samples; helpers/test counts are never timings."""
import math

def distribution(values, expected=100):
    if not isinstance(values,list) or len(values)!=expected or expected<100:raise ValueError('measurement sample count')
    if any(isinstance(v,bool) or not isinstance(v,(float,int)) or not math.isfinite(v) or v<0 for v in values):raise ValueError('invalid measured time')
    data=sorted(values);n=len(data)
    return dict(samples=n,unit='milliseconds',p50=data[math.ceil(n*.5)-1],p95=data[math.ceil(n*.95)-1],max=data[-1])

def managed_summary(data,head):
    if not isinstance(data,dict) or data.get('status')!='PASS' or data.get('sourceHead')!=head:raise ValueError('missing/current managed execution')
    if data.get('clock')!='Stopwatch monotonic' or type(data.get('clockFrequency')) is not int or data['clockFrequency']<=0 or data.get('build')!='Release/Optimize=true':raise ValueError('clock/build metadata')
    if data.get('warmup')!=20 or data.get('samples')!=100:raise ValueError('warmup/measurement separation')
    keys={'createInitialize','callbackProductQuery','shutdownDispose','registryEightInflightDuplicateCancelLate'}
    if set(data.get('timings',{}))!=keys:raise ValueError('measurement scopes missing')
    result={}
    for name,scope in data['timings'].items():
        actual=distribution(scope['samplesMilliseconds'])
        if any(scope.get(k)!=actual[k] for k in ('samples','unit','p50','p95','max')):raise ValueError('summary not derived from samples')
        result[name]=actual
    work=data.get('measuredWorkload',{})
    if any(type(work.get(k)) is not int or work[k]!=v for k,v in {'inFlightPerCycle':8,'successfulResponses':800,'expectedCancellations':100,'ignoredDuplicateResponses':100,'ignoredLateResponses':100,'finalPending':0,'liveClients':0,'liveTransports':0}.items()):raise ValueError('workload/cleanup mismatch')
    return {k:v for k,v in data.items() if k!='timings'}|{'timings':result}


def is_exact_coin_grant(body, purchase=None):
    if not isinstance(body,dict) or not isinstance(body.get('entitlements'),dict):return False
    # Wallet quantities are decimal strings in the existing API contract.
    return body['entitlements'].get('coinBalance')=='100' and isinstance(body.get('serverPurchaseId'),str) and (purchase is None or body['serverPurchaseId']==purchase)
