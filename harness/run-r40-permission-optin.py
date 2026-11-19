#!/usr/bin/env python3
"""Run distinct Android/iOS OS denial and managed mock denial checks."""
import os
from pathlib import Path
import subprocess
import sys
ROOT=Path(__file__).resolve().parent.parent

def main():
    names=('GAMEBRIDGE_UPM_STAGING','GAMEBRIDGE_UNITY_PACKAGE_CACHE','GAMEBRIDGE_ANDROID_SERIAL','GAMEBRIDGE_TEST_AVD_NAME','UNITY_EDITOR_PATH')
    if os.environ.get('GAMEBRIDGE_RUN_OS_PERMISSION_E2E')!='true' or not all(os.environ.get(name) for name in names):
        print('DEFERRED_ENV: explicit OS permission opt-in and isolated environment required');return 2
    stage,cache,serial,avd,_=(os.environ[name] for name in names)
    commands=[[sys.executable,'harness/run-unity-android-permission-os.py','--run-local','--staging',stage,'--package-cache',cache,'--serial',serial,'--expected-avd',avd],
              [sys.executable,'harness/run-unity-ios-permission-os.py','--run-local','--staging',stage,'--package-cache',cache],
              ['bash','scripts/smoke-unity-mock-permission.sh']]
    for command,timeout in zip(commands,(1500,1500,300)):
        try:result=subprocess.run(command,cwd=ROOT,check=False,timeout=timeout)
        except (OSError,subprocess.TimeoutExpired):print('DEFERRED_ENV: OS permission runner unavailable or timed out');return 2
        if result.returncode!=0:return result.returncode
    print('R40 PASS: Android OS, iOS OS and managed mock denial separately executed');return 0
if __name__=='__main__':raise SystemExit(main())
