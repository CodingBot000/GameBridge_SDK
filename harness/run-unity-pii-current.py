#!/usr/bin/env python3
"""Run both fresh LOCAL_MOCK PII Players for one explicit local gate."""
import argparse
import importlib.util
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
spec=importlib.util.spec_from_file_location('pii_evidence',ROOT/'harness/check-unity-pii-evidence.py');validator=importlib.util.module_from_spec(spec);spec.loader.exec_module(validator)

def main():
    p=argparse.ArgumentParser();p.add_argument('--run-local',action='store_true',required=True);p.add_argument('--staging',required=True);p.add_argument('--serial',required=True);p.add_argument('--expected-avd',required=True);p.add_argument('--nonce',required=True);p.add_argument('--package-cache');a=p.parse_args()
    if not re.fullmatch(r'[0-9a-f]{32}',a.nonce) or not a.expected_avd.startswith('GameBridge_V2_'):
        print('DEFERRED_ENV: valid run nonce and dedicated AVD required');return 2
    head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    (ROOT/'artifacts').mkdir(exist_ok=True)
    output=Path(tempfile.mkdtemp(prefix='unity-pii-current-',dir=ROOT/'artifacts'));report={'status':'FAIL','sourceHead':head,'nonce':a.nonce,'suites':{}}
    commands=[('android',[sys.executable,'harness/run-unity-android-mock-e2e.py','--run-local','--pii-probe','--staging',a.staging,'--serial',a.serial,'--expected-avd',a.expected_avd]),
              ('ios',[sys.executable,'harness/run-unity-ios-mock-e2e.py','--run-local','--adhoc','--pii-probe','--staging',a.staging])]
    try:
        for platform,command in commands:
            if a.package_cache:command += ['--package-cache',a.package_cache]
            print('Running fresh Unity '+platform+' synthetic PII Player...',flush=True)
            result=subprocess.run(command,cwd=ROOT,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,timeout=1500)
            print(result.stdout,end='',flush=True)
            if result.returncode==2:report['status']='DEFERRED_ENV';break
            match=re.search(r'^RESULT PASS\s+EVIDENCE (artifacts/unity-'+platform+r'-e2e-[A-Za-z0-9_.-]+)\s*$',result.stdout,re.M)
            if result.returncode!=0 or not match:break
            report['suites'][platform]=match.group(1)+'/result.json'
        else:
            report['status']='PASS';(output/'result.json').write_text(json.dumps(report,indent=2)+'\n')
            if not validator.check((output/'result.json').relative_to(ROOT).as_posix(),a.nonce,head):report['status']='FAIL'
    except (OSError,subprocess.TimeoutExpired): report['status']='DEFERRED_ENV'
    (output/'result.json').write_text(json.dumps(report,indent=2)+'\n')
    print('PII gate result:',report['status'],'Evidence directory:',output.relative_to(ROOT),flush=True)
    return 0 if report['status']=='PASS' else 2 if report['status']=='DEFERRED_ENV' else 1
if __name__=='__main__':raise SystemExit(main())
