"""A completed, correlated Editor method is required; license status is insufficient."""
import re


def observations(editor_log, client_log=''):
    return {
        'missingChannel': len(re.findall(r"Channel LicenseClient-[^\n]+doesn't exist", editor_log)),
        'ipcTimeouts': editor_log.count('Timed-out after 60.00s'),
        'clientMutexFailures': client_log.count('Failed to acquire global mutex'),
        'unsupportedProtocols': sorted(set(re.findall(r"Unsupported protocol version '(\d{1,3}\.\d{1,3}\.\d{1,3}(?:[-+][0-9A-Za-z.-]{1,30})?)'", client_log))),
        'compilerErrors': len(re.findall(r'error CS\d+', editor_log)),
    }


def evaluate(exit_code, editor_log, receipt, run_id, version, timed_out=False):
    observed = observations(editor_log)
    marker = 'GB_EDITOR_SMOKE PASS ' + run_id
    markers = sum(line.strip() == marker for line in editor_log.splitlines())
    expected = {'status': 'PASS', 'runId': run_id, 'unityVersion': version, 'batchMode': True}
    correlated = (type(receipt) is dict and receipt == expected and
                  type(receipt.get('batchMode')) is bool)
    if timed_out:
        status, reason = 'DEFERRED_ENV', 'PROCESS_TIMEOUT'
    elif observed['compilerErrors']:
        status, reason = 'FAIL', 'EDITOR_COMPILE_FAILURE'
    elif exit_code == 0 and correlated and markers == 1:
        status, reason = 'PASS', 'EDITOR_METHOD_COMPLETED'
    elif markers or receipt is not None:
        status, reason = 'FAIL', 'INCOMPLETE_OR_UNCORRELATED_VERDICT'
    elif exit_code != 0 and exit_code not in (6, 124) and not (observed['missingChannel'] or observed['ipcTimeouts']):
        status, reason = 'FAIL', 'EDITOR_PROCESS_FAILED_WITHOUT_VERDICT'
    else:
        status, reason = 'DEFERRED_ENV', 'NO_EDITOR_METHOD_VERDICT'
    return {'status': status, 'reason': reason, 'exitCode': exit_code,
            'timedOut': timed_out, 'receiptCorrelated': correlated,
            'markerCount': markers, 'observations': observed,
            'tests': 0, 'checks': 1, 'players': 0}
