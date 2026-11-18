#!/usr/bin/env python3
"""Read-only E1 inventory. Never provisions devices, servers or databases."""
import argparse, hashlib, json, os, shutil, subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def inspect(staging=None):
    def output(command):
        try:
            r=subprocess.run(command,cwd=ROOT,text=True,capture_output=True,timeout=15)
            return r.returncode,r.stdout.strip()
        except (OSError,subprocess.TimeoutExpired):return 2,''
    _,head=output(['git','rev-parse','HEAD']);_,dirty=output(['git','status','--porcelain','--untracked-files=no'])
    tools={name:bool(shutil.which(name)) for name in ['java','docker','xcrun','swift','dotnet']}
    docker,_=output(['docker','info','--format','{{.ServerVersion}}'])
    editor=Path(os.environ.get('UNITY_EDITOR_PATH','/Applications/Unity/Hub/Editor/6000.5.8f1/Unity.app/Contents/MacOS/Unity'))
    package={'status':'DEFERRED_ENV','reason':'Explicit current staging required'}
    if staging:
        code,_=output(['python3','harness/check-staging.py',str(staging)])
        package={'status':'PASS' if code==0 else 'FAIL','checksumCheckerExit':code,'sourceAttestation':'NOT_IMPLEMENTED'}
    return {'sourceHead':head,'trackedClean':not dirty,'tools':tools,'dockerDaemonReachable':docker==0,
        'unityExecutablePresent':editor.is_file() and os.access(editor,os.X_OK),'unityLicenseAndModules':'NOT_VERIFIED',
        'staging':package,'E1':'DEFERRED_ENV','E2':'NOT_RUN','strict':'NOT_RUN','exitCode':2,
        'missingContracts':['Complete required lane/environment inventory','Unity executable/license/modules runtime attestation',
          'Current package source attestation','ADB build/runtime executable PID and port ownership plan',
          'Distinct owned PII/Push AVD and serial/PID/console/ADB ports','Dedicated Simulator/StoreKit runtime ownership',
          'Dedicated PostgreSQL role and Testcontainers readiness','Backend port/secret scope attestation'],
        'resourceCreations':0,'note':'This inventory does not authorize full Strict. a83561a guard remains active.'}
def main():
    p=argparse.ArgumentParser();p.add_argument('--staging',type=Path);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    report=inspect(a.staging);a.output.write_text(json.dumps(report,indent=2)+'\n');print('DEFERRED_ENV: E1 inventory recorded; E2 and full Strict NOT_RUN');return 2
if __name__=='__main__':raise SystemExit(main())
