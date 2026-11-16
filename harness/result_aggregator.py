from error_contract import valid_error_evidence
from measurement_contract import valid_checker
"""Pure fail-closed status classification; external waits are reported separately."""
VALID = {'PASS', 'FAIL', 'PARTIAL', 'NOT_IMPLEMENTED', 'DEFERRED_ENV', 'NOT_RUN', 'SKIP', 'WAITING_USER'}

def summarize(lanes, required_names=None):
    if not lanes: return {'status':'FAIL', 'exitCode':1, 'reason':'no required lanes'}
    names = set(); failure = False; deferred = False; required_count = 0
    for lane in lanes:
        name = lane.get('name'); status = lane.get('status'); required = lane.get('required')
        if not name or name in names or status not in VALID or not isinstance(required, bool): failure = True; continue
        names.add(name)
        if not required: continue
        required_count += 1
        if 'errors' in lane and lane['errors'] is not None and not valid_error_evidence(lane): failure = True
        if any(k in lane and (type(lane[k]) is not int or lane[k]<0) for k in ('tests','checks','samples','players','failures','skipped')):failure=True
        if 'exitCode' in lane and type(lane['exitCode']) is not int:failure=True
        if type(lane.get('failures')) is int and lane['failures']>0:failure=True
        if status in ('DEFERRED_ENV','NOT_RUN','SKIP') and lane.get('exitCode',2)!=2:failure=True
        if status == 'WAITING_USER': failure = True
        elif status in ('FAIL','PARTIAL','NOT_IMPLEMENTED'): failure = True
        elif status in ('DEFERRED_ENV','NOT_RUN','SKIP'): deferred = True
        elif status == 'PASS':
            count=lane.get('tests');skipped=lane.get('skipped')
            counters=('tests','checks','samples','players','failures','skipped')
            valid_counts=all(type(lane.get(k)) is int and lane[k]>=0 for k in counters)
            measurement=lane.get('measurement')
            if measurement=='tests':
                valid_count=valid_counts and count>0 and lane['samples']==lane['players']==0
            elif measurement in ('checker','samples','players'):
                valid_count=valid_counts and count==0
                if measurement=='checker':valid_count=valid_count and lane['samples']==lane['players']==0
                elif measurement=='samples':valid_count=valid_count and lane['samples']>0 and lane['players']==0
                else:valid_count=valid_count and lane['players']>0 and lane['samples']==0
            else:valid_count=False
            if lane.get('evidenceKind')=='static-mapping':
                valid_count=(valid_count and measurement=='checker' and type(lane.get('mappedScenarios')) is int and
                             lane['mappedScenarios']==50 and lane.get('executionStatus')=='NOT_RUN')
            if (not valid_count or not valid_error_evidence(lane) or not valid_checker(lane) or
                type(lane.get('exitCode')) is not int or lane['exitCode']!=0 or lane['failures']!=0): failure=True
            elif skipped: deferred = True
    if required_count == 0: failure = True
    if required_names is not None:
        expected = set(required_names)
        actual_required = {lane.get('name') for lane in lanes if lane.get('required') is True}
        if not expected or not expected.issubset(actual_required): failure = True
    if failure: return {'status':'FAIL', 'exitCode':1, 'reason':'required failure, partial/unimplemented coverage, or invalid evidence'}
    if deferred: return {'status':'DEFERRED_ENV', 'exitCode':2, 'reason':'required lane not executed or skipped'}
    return {'status':'PASS', 'exitCode':0, 'reason':'all required local lanes executed and passed'}

def runner_inconsistent(code, statuses):
    if type(code) is not int or code not in (0, 1, 2) or not statuses: return True
    if code == 0: return any(status != 'PASS' for status in statuses)
    if code == 1: return not any(status in ('FAIL', 'PARTIAL', 'NOT_IMPLEMENTED') for status in statuses)
    return all(status == 'PASS' for status in statuses)
