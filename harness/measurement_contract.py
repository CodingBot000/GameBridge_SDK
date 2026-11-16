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


# A producer attaches the invocation observed by its own subprocess wrapper.
# This is process-local; it is never loaded from a supplied result.json.
_last_execution = None


def record_execution(command, code, text, log):
    global _last_execution
    path = Path(log).resolve()
    _last_execution = dict(path=str(path), sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
                           marker=text.strip().splitlines()[-1] if text.strip() else '',
                           exitCode=code, command=list(command))
    return _last_execution


def attach_execution(lane, execution=None):
    receipt = execution if execution is not None else _last_execution
    if receipt is not None and receipt.get('exitCode') == lane.get('exitCode'):
        lane['command'] = receipt['command']
        lane['evidence'] = receipt['path']
        lane['checkerEvidence'] = dict(receipt)
    return lane


def counted_lane(name, code, counts, errors=None, error_model='included-in-failures', measurement='tests', execution=None):
    tests, failures, skipped = counts
    checker = measurement in ('checker', 'players', 'samples')
    count = tests
    lane = {'suite': name, 'tests': 0 if checker else tests, 'checks': 1 if count > 0 else 0,
            'samples': count if measurement == 'samples' else 0,
            'players': count if measurement == 'players' else 0,
            'measurement': measurement, 'failures': failures, 'errors': errors,
            'errorModel': error_model, 'skipped': skipped, 'exitCode': code}
    good = (type(code) is int and code == 0 and type(count) is int and count > 0 and
            type(failures) is int and failures == 0 and (errors is None or type(errors) is int and errors == 0) and
            type(skipped) is int and skipped == 0)
    lane['status'] = 'PASS' if good else ('DEFERRED_ENV' if code == 2 else 'FAIL')
    return attach_execution(lane, execution)
