"""Read-only, test-only liveness observations; never credentials or payloads."""
import hashlib
import json
import subprocess
import time
from pathlib import Path


def configuration_hash(path):
    try:return hashlib.sha256(Path(path).read_bytes()).hexdigest()
    except OSError:return None


def toolchain():
    try:
        result=subprocess.run(['xcodebuild','-version'],text=True,capture_output=True,timeout=10)
        return {'exitCode':result.returncode,'version':result.stdout.strip() if result.returncode==0 else 'UNMEASURED'}
    except (OSError,subprocess.SubprocessError):return {'exitCode':None,'version':'UNMEASURED'}


def simulator_state(device):
    try:
        result=subprocess.run(['xcrun','simctl','list','devices','--json'],text=True,capture_output=True,timeout=10)
        data=json.loads(result.stdout) if result.returncode==0 else {}
        for runtime,devices in data.get('devices',{}).items():
            for item in devices:
                if item.get('udid')==device:return {'udid':device,'runtime':runtime,'state':item.get('state','UNMEASURED')}
    except (OSError,ValueError,subprocess.SubprocessError):pass
    return {'udid':device,'state':'UNMEASURED'}


class Timeline:
    def __init__(self):self.started=time.monotonic();self.events=[]
    def mark(self,stage,device=None):
        item={'stage':stage,'elapsedMs':round((time.monotonic()-self.started)*1000,3)}
        if device:item['simulator']=simulator_state(device)
        self.events.append(item)
        return item
