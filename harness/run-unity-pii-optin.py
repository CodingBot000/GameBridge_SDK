#!/usr/bin/env python3
"""Explicit opt-in entry for a fresh two-platform synthetic PII regression."""
import os
from pathlib import Path
import secrets
import subprocess
import sys
ROOT=Path(__file__).resolve().parent.parent

def main():
    names=('GAMEBRIDGE_UPM_STAGING','GAMEBRIDGE_ANDROID_SERIAL','GAMEBRIDGE_TEST_AVD_NAME','GAMEBRIDGE_UNITY_PACKAGE_CACHE')
    if os.environ.get('GAMEBRIDGE_RUN_UNITY_PII_E2E')!='true' or not all(os.environ.get(name) for name in names):
        print('DEFERRED_ENV: explicit PII Player opt-in and isolated environment required');return 2
    command=[sys.executable,'harness/run-unity-pii-current.py','--run-local','--staging',os.environ[names[0]],
             '--serial',os.environ[names[1]],'--expected-avd',os.environ[names[2]],'--package-cache',os.environ[names[3]],
             '--nonce',secrets.token_hex(16)]
    try:return subprocess.run(command,cwd=ROOT,check=False,timeout=3200).returncode
    except (OSError,subprocess.TimeoutExpired):print('DEFERRED_ENV: PII Player runner unavailable or timed out');return 2
if __name__=='__main__':raise SystemExit(main())
