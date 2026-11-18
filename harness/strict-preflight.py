#!/usr/bin/env python3
"""Read-only E1 inventory. Never provisions devices, servers or databases."""
import argparse, hashlib, json, os, shutil, subprocess
from strict_environment_contract import REQUIREMENTS, assess_e1, required_lanes
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
    report = {'sourceHead':head,'trackedClean':not dirty,'tools':tools,'dockerDaemonReachable':docker==0,
        'unityExecutablePresent':editor.is_file() and os.access(editor,os.X_OK),'unityLicenseAndModules':'NOT_VERIFIED',
        'staging':package,'E1':'DEFERRED_ENV','E2':'NOT_RUN','strict':'NOT_RUN','exitCode':2,
        'missingContracts':['Complete required lane/environment inventory','Unity executable/license/modules runtime attestation',
          'Current package source attestation','ADB build/runtime executable PID and port ownership plan',
          'Distinct owned PII/Push AVD and serial/PID/console/ADB ports','Dedicated Simulator/StoreKit runtime ownership',
          'Dedicated PostgreSQL role and Testcontainers readiness','Backend port/secret scope attestation'],
        'resourceCreations':0,'note':'This inventory does not authorize full Strict. a83561a guard remains active.'}
    lanes=required_lanes((ROOT/'harness/verify-all.py').read_text())
    checks={name:None for name in REQUIREMENTS}
    checks.update(sourceClean=not dirty, stagingIntegrity=package.get('status')=='PASS', unityExecutable=editor.is_file() and os.access(editor,os.X_OK),
        unityAndroidModule=(editor.parents[3]/'PlaybackEngines/AndroidPlayer').is_dir(), unityIosModule=(editor.parents[3]/'PlaybackEngines/iOSSupport').is_dir(),
        adbEndpointsSeparate=True, postgresAvailable=docker==0)
    module_root=editor.parents[3]/'PlaybackEngines'
    adb=module_root/'AndroidPlayer/SDK/platform-tools/adb'
    checks['adbExecutable']=adb.is_file() and os.access(adb,os.X_OK)
    owners={}
    for port in (5037,5038,18080):
        code,value=output(['lsof','-nP','-t',f'-iTCP:{port}','-sTCP:LISTEN'])
        owners[str(port)]=[int(pid) for pid in value.splitlines() if pid.isdigit()] if code in (0,1) else None
    checks['adbPortsAvailable']=all(owners[str(port)]==[] for port in (5037,5038))
    checks['backendPortsAvailable']=owners['18080']==[]
    code,value=output(['xcrun','simctl','list','runtimes','-j'])
    try:
        available=any(r.get('isAvailable') and r['identifier']=='com.apple.CoreSimulator.SimRuntime.iOS-18-6' for r in json.loads(value)['runtimes']) if code==0 else False
    except (ValueError,KeyError):available=False
    checks['simulatorRuntime']=available; checks['storekitRuntime']=available
    if staging and package.get('status')=='PASS':
        source=ROOT/'unity/Packages/com.gamebridge.sdk'; packaged=staging.resolve()/'com.gamebridge.sdk'
        checks['stagingSourceMatch']=all((packaged/p.relative_to(source)).is_file() and hashlib.sha256(p.read_bytes()).digest()==hashlib.sha256((packaged/p.relative_to(source)).read_bytes()).digest() for p in source.rglob('*') if p.is_file())
        checks['requiredArtifacts']=(packaged/'Editor/GameBridgeArtifacts~/iOS/GameBridgeNative.xcframework/Info.plist').is_file()
        code,value=output(['git','diff','a83561a','--','android','ios','unity'])
        checks['nativeSourceAttestation']=code==0 and not value
    report.update(requiredLanes=lanes, requiredLaneCount=len(lanes), checks=checks, portOwners=owners,
        E2='NOT_IMPLEMENTED_OR_EXECUTED', resourceCreations=0,
        note='E1 decision and E2 identity validator are implemented; E2 provisioning and all live ownership observations are incomplete. Full Strict guard remains active.')
    decision=assess_e1(report,lanes);report.update(E1=decision['status'],exitCode=decision['exitCode'],missingContracts=decision['missing'])
    return report

def main():
    p=argparse.ArgumentParser();p.add_argument('--staging',type=Path);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    report=inspect(a.staging);a.output.write_text(json.dumps(report,indent=2)+'\n');print(report['E1']+': E1 evaluated; E2 and full Strict NOT_RUN');return report['exitCode']
if __name__=='__main__':raise SystemExit(main())
