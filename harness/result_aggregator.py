"""Pure fail-closed status classification; external waits are reported separately."""
VALID = {'PASS', 'FAIL', 'PARTIAL', 'NOT_IMPLEMENTED', 'DEFERRED_ENV', 'NOT_RUN', 'SKIP', 'WAITING_USER'}

def summarize(lanes):
    if not lanes: return {'status':'FAIL', 'exitCode':1, 'reason':'no required lanes'}
    names = set(); failure = False; deferred = False; required_count = 0
    for lane in lanes:
        name = lane.get('name'); status = lane.get('status'); required = lane.get('required')
        if not name or name in names or status not in VALID or not isinstance(required, bool): failure = True; continue
        names.add(name)
        if not required: continue
        required_count += 1
        if status == 'WAITING_USER': failure = True
        elif status in ('FAIL','PARTIAL','NOT_IMPLEMENTED'): failure = True
        elif status in ('DEFERRED_ENV','NOT_RUN','SKIP'): deferred = True
        elif status == 'PASS':
            count = lane.get('tests', 0); skipped = lane.get('skipped', 0)
            if (not isinstance(count, int) or isinstance(count, bool) or count <= 0 or not isinstance(skipped, int) or skipped < 0 or
                lane.get('exitCode', 0) != 0 or lane.get('failures', 0) != 0): failure = True
            elif skipped: deferred = True
    if required_count == 0: failure = True
    if failure: return {'status':'FAIL', 'exitCode':1, 'reason':'required failure, partial/unimplemented coverage, or invalid evidence'}
    if deferred: return {'status':'DEFERRED_ENV', 'exitCode':2, 'reason':'required lane not executed or skipped'}
    return {'status':'PASS', 'exitCode':0, 'reason':'all required local lanes executed and passed'}

def runner_inconsistent(code, statuses):
    if code not in (0, 1, 2) or not statuses: return True
    if code == 0: return any(status != 'PASS' for status in statuses)
    if code == 1: return not any(status in ('FAIL', 'PARTIAL', 'NOT_IMPLEMENTED') for status in statuses)
    return all(status == 'PASS' for status in statuses)
