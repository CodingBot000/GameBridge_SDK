"""Invocation provenance owned by the running orchestrator, never a user result file.

This detects stale/mismatched evidence, not a hostile process with local write access.
"""
import hashlib
import copy
import json
import os
import subprocess
import time
import uuid
from pathlib import Path

ROOT=Path(__file__).resolve().parent.parent
RUN_ID=os.environ.get('GAMEBRIDGE_HARNESS_RUN_ID') or uuid.uuid4().hex
_OBSERVED={}


def source_identity():
    head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    diff=subprocess.check_output(['git','diff','--binary','HEAD'],cwd=ROOT)
    return {'sourceHead':head,'sourceDigest':hashlib.sha256(head.encode()+diff).hexdigest()}


def metadata():
    return {**source_identity(),'runId':RUN_ID}


def observe(command,code,text,log,started=None,invocation_id=None):
    path=Path(log).resolve()
    data=path.read_bytes()
    if data.decode('utf-8')!=text:raise ValueError('captured output differs from log')
    receipt={**metadata(),'path':str(path),'sha256':hashlib.sha256(data).hexdigest(),
            'command':list(command),'exitCode':code,'startedNs':started or path.stat().st_mtime_ns,
            'finishedNs':time.time_ns(),'invocationId':invocation_id or uuid.uuid4().hex}
    _OBSERVED[receipt['invocationId']]=copy.deepcopy(receipt)
    return receipt


def valid_observation(receipt,run_id=None,source=None):
    if not isinstance(receipt,dict):return False
    try:
        if run_id is None:
            observed=_OBSERVED.get(receipt.get('invocationId'))
            if not observed or any(receipt.get(k)!=v for k,v in observed.items()):return False
        path=Path(receipt['path'])
        if not path.is_absolute() or path.is_symlink() or path.resolve()!=path:return False
        if receipt['runId'] != (run_id or RUN_ID):return False
        source=source or source_identity()
        if any(receipt.get(k)!=source[k] for k in ('sourceHead','sourceDigest')):return False
        if (type(receipt['exitCode']) is not int or type(receipt['startedNs']) is not int or
            type(receipt['finishedNs']) is not int or receipt['startedNs']>receipt['finishedNs'] or
            not receipt['startedNs']<=path.stat().st_mtime_ns<=receipt['finishedNs']):return False
        if not isinstance(receipt['command'],list) or not receipt['command'] or not all(type(x) is str and x for x in receipt['command']):return False
        return hashlib.sha256(path.read_bytes()).hexdigest()==receipt['sha256']
    except (OSError,KeyError,ValueError,TypeError):return False


def valid_parent(lane):
    parent=lane.get('parentExecution')
    if parent is None:return None
    if not valid_observation(parent):return False
    try:
        report=Path(lane['producerEvidence'])
        if report.is_symlink() or not report.is_absolute() or not report.parent.resolve().is_relative_to(ROOT/'artifacts'):return False
        if not parent['startedNs']<=report.stat().st_mtime_ns<=parent['finishedNs']:return False
        text=Path(parent['path']).read_text()
        if f"Evidence directory: {report.parent.relative_to(ROOT).as_posix()}" not in text:return False
        raw=report.read_bytes()
        if hashlib.sha256(raw).hexdigest()!=lane.get('producerSha256'):return False
        data=json.loads(raw)
        if data.get('runId')!=parent['invocationId']:return False
        if any(data.get(k)!=parent[k] for k in ('sourceHead','sourceDigest')):return False
        child_name=lane['name'].split('/',1)[1]
        items=data.get('suites',data.get('lanes',[]))
        matches=[x for x in items if isinstance(x,dict) and x.get('suite',x.get('name'))==child_name]
        if len(matches)!=1:return False
        child=matches[0]
        fields=('tests','checks','samples','players','failures','errors','skipped','exitCode','errorModel','measurement','checkerEvidence','command','evidence','status')
        if any((key in child)!=(key in lane) or child.get(key)!=lane.get(key) for key in fields):return False
        return parent
    except (OSError,ValueError,TypeError,KeyError):return False
