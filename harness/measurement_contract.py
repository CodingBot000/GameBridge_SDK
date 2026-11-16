"""Evidence-backed measurements for simple checker invocations."""
import hashlib
import re
from pathlib import Path


def valid_checker(lane):
    receipt=lane.get('checkerEvidence')
    if not isinstance(receipt,dict) or type(lane.get('checks')) is not int or lane['checks']!=1:
        return False
    if type(lane.get('exitCode')) is not int or lane['exitCode']!=0 or type(receipt.get('exitCode')) is not int or receipt['exitCode']!=0 or not isinstance(lane.get('command'),list) or not lane['command'] or not all(isinstance(x,str) and x for x in lane['command']):
        return False
    try:
        data=Path(receipt['path']).read_bytes()
        return (isinstance(receipt.get('marker'),str) and bool(receipt['marker']) and
                receipt['marker'] in data.decode('utf-8') and
                hashlib.sha256(data).hexdigest()==receipt.get('sha256'))
    except (OSError,KeyError,TypeError,ValueError):return False


def measured_lane(name, command, code, text, log, marker):
    lane={'name':name,'status':'FAIL','required':True,'tests':0,'checks':0,'samples':0,'players':0,
          'measurement':'checker','errors':None,'errorModel':'checker-exit','skipped':0,'exitCode':code,
          'command':command,'evidence':str(log)}
    path=Path(log)
    try:
        data=path.read_bytes()
        if data.decode('utf-8')!=text: return lane
    except (OSError,ValueError):return lane
    passed=code==0 and marker in text
    if code==2:lane['status']='DEFERRED_ENV'
    if not passed:return lane
    lane['checks']=1
    lane['checkerEvidence']={'path':str(path.resolve()),'sha256':hashlib.sha256(data).hexdigest(),'marker':marker,'exitCode':code}
    if name=='aggregation-self':
        lane['measurement']='tests';match=re.search(r'Ran (\d+) tests?',text)
        lane['tests']=int(match.group(1)) if match else 0
        skips=re.search(r'skipped=(\d+)',text);lane['skipped']=int(skips.group(1)) if skips else 0
        passed=lane['tests']>0 and 'FAILED' not in text
    elif name in ('unity-editor-runtime','purchase-verifier'):
        lane['measurement']='tests'
        pattern=r'Unity consumer tests PASS: (\d+) executed' if name=='unity-editor-runtime' else r'Purchase verifier PASS: (\d+) synthetic tests'
        match=re.search(pattern,text);lane['tests']=int(match.group(1)) if match else 0
        passed=lane['tests']>0
    elif name=='lifecycle-stress':
        lane['measurement']='samples';match=re.search(r'"samples"\s*:\s*(\d+)',text)
        lane['samples']=int(match.group(1)) if match else 0
        passed=lane['samples']==100 and bool(re.search(r'"liveClients"\s*:\s*0',text)) and bool(re.search(r'"liveTransports"\s*:\s*0',text))
    elif name=='unity-pii-e2e':
        lane['measurement']='players';lane['players']=2 if 'Android and iOS LOCAL_MOCK Players, 2 tests' in text else 0
        passed=lane['players']==2
    lane['status']='PASS' if passed else 'FAIL'
    return lane
