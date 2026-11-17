"""GUI receipts prove GUI scope only, never batch automation or Player execution."""
from datetime import datetime
import hashlib
import json
from pathlib import Path
import re


def file_hash(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def validate_probe(value, config):
    for key in ('runId', 'sourceHead', 'scriptSha256'):
        if value.get(key) != config[key]:
            raise ValueError('GUI receipt correlation mismatch: ' + key)
    if type(value.get('schemaVersion')) is not int or value['schemaVersion'] != 1 or value.get('status') != 'PASS' or value.get('operation') != 'probe':
        raise ValueError('GUI probe did not pass')
    if value.get('isBatchMode') is not False or value.get('unityVersion') != config['expectedUnityVersion']:
        raise ValueError('GUI receipt mode/version mismatch')
    if Path(value.get('projectRoot', '')).resolve() != Path(config['projectRoot']).resolve():
        raise ValueError('GUI receipt project mismatch')
    if value.get('method') != 'GameBridgeGuiVerification.RunProbe' or value.get('assemblyName') != 'Assembly-CSharp-Editor':
        raise ValueError('GUI compiled method identity missing')
    for key in ('editorPid', 'engineObjectId', 'checksExecuted'):
        if type(value.get(key)) is not int or value[key] == 0:
            raise ValueError('GUI runtime observations missing')
    if value['editorPid'] < 0:
        raise ValueError('GUI Editor PID invalid')
    if value['checksExecuted'] != 7 or value.get('engineObjectCreated') is not True or value.get('engineObjectDestroyed') is not True:
        raise ValueError('GUI engine object lifecycle incomplete')
    start = datetime.fromisoformat(value['startedUtc'].replace('Z', '+00:00'))
    end = datetime.fromisoformat(value['finishedUtc'].replace('Z', '+00:00'))
    if start.tzinfo is None or end.tzinfo is None or end < start:
        raise ValueError('GUI receipt timestamps invalid')
    return {'status': 'PASS', 'scope': 'GUI Editor compiled method and engine probe',
            'tests': 0, 'checks': 1, 'engineChecksExecuted': 7, 'players': 0,
            'batchAutomation': 'NOT_RUN'}


def read_probe(project, source_head):
    project = Path(project).resolve()
    config_path = project / 'GameBridgeGuiRun.json'
    config = json.loads(config_path.read_text())
    if not re.fullmatch(r'[0-9a-f]{32}', config.get('runId', '')):
        raise ValueError('GUI nonce invalid')
    if config['sourceHead'] != source_head or Path(config['projectRoot']).resolve() != project:
        raise ValueError('stale checkout/project config')
    if file_hash(project / 'Assets/Editor/GameBridgeGuiVerification.cs') != config['scriptSha256']:
        raise ValueError('GUI script source changed')
    path = project / 'GameBridgeGuiResults' / (config['runId'] + '.json')
    if path.stat().st_mtime_ns < config_path.stat().st_mtime_ns:
        raise ValueError('stale GUI receipt')
    value = json.loads(path.read_text(encoding='utf-8-sig'))
    return validate_probe(value, config), value
