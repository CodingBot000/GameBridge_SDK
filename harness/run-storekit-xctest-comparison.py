#!/usr/bin/env python3
"""Run existing StoreKit purchase/pending XCTest sequentially on fresh simulators."""
import hashlib
import json
import os
import shutil
import signal
import subprocess
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BUNDLE = 'com.gamebridge.sdk.sample.dev20261110'
TESTS = [('purchase', 'testLocalVerifiedPurchaseReceivesFakeGrantAndFinishes'),
         ('pending', 'testAskToBuyPendingNeverRequestsGrant')]


def command(args, logfile, timeout):
    with logfile.open('w') as output:
        process = subprocess.Popen(args, cwd=ROOT, stdout=output, stderr=subprocess.STDOUT, start_new_session=True)
        try: return process.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            os.killpg(process.pid, signal.SIGTERM)
            try: process.wait(timeout=10)
            except subprocess.TimeoutExpired: os.killpg(process.pid, signal.SIGKILL); process.wait()
            return 124


def main():
    if sys.argv[1:] != ['--run-local']:
        print('Usage: python3 harness/run-storekit-xctest-comparison.py --run-local'); return 2
    if not shutil.which('xcodebuild') or not shutil.which('xcrun'):
        print('DEFERRED_ENV: Xcode simulator tools required'); return 2
    output = Path(tempfile.mkdtemp(prefix='storekit-xctest-comparison-',dir=ROOT/'artifacts'))
    generated=subprocess.run(['bash','scripts/generate-ios-project.sh'],cwd=ROOT,text=True,capture_output=True,check=False)
    (output/'project-generation.log').write_text(generated.stderr)
    if generated.returncode:
        print('DEFERRED_ENV: Xcode project generation failed; evidence:',output.relative_to(ROOT));return 2
    project=generated.stdout.strip().splitlines()[-1]
    test_file=ROOT/'ios/StoreKitTests/XcodeStoreKitPurchaseTests.swift'
    report={'sourceHead':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
            'sourceTrackedDirty':bool(subprocess.run(['git','diff','--quiet'],cwd=ROOT).returncode or subprocess.run(['git','diff','--cached','--quiet'],cwd=ROOT).returncode),
            'testSourceSHA256':hashlib.sha256(test_file.read_bytes()).hexdigest(),'scope':'Xcode local StoreKit, fake backend, XCTest only',
            'results':[],'simulators':{}}
    def run_runtime(version,suffix):
        created=subprocess.run(['xcrun','simctl','create','GameBridge-XCTest-'+suffix+'-'+str(time.time_ns()),
                                'com.apple.CoreSimulator.SimDeviceType.iPhone-16','com.apple.CoreSimulator.SimRuntime.iOS-'+suffix],
                                cwd=ROOT,text=True,capture_output=True,check=False)
        if created.returncode:
            report['results'].append({'runtime':version,'status':'DEFERRED_ENV','stage':'simulator-create','exitCode':created.returncode});return
        sim=created.stdout.strip();report['simulators'][version]=sim;print('Retained simulator:',version,sim,flush=True)
        try:
            code=command(['xcrun','simctl','boot',sim],output/f'boot-{suffix}.log',60)
            if code==0: code=command(['xcrun','simctl','bootstatus',sim,'-b'],output/f'bootstatus-{suffix}.log',180)
            if code:
                report['results'].append({'runtime':version,'status':'DEFERRED_ENV','stage':'boot','exitCode':code});return
            for label,test in TESTS:
                result=output/f'{suffix}-{label}.xcresult'
                print('Running:',version,label,flush=True)
                args=['xcodebuild','test','-project',project,'-scheme','GameBridgeStoreKit','-configuration','Debug',
                      '-destination',f'platform=iOS Simulator,id={sim}','-derivedDataPath',str(output/'Derived'),
                      '-resultBundlePath',str(result),'-parallel-testing-enabled','NO','-test-timeouts-enabled','YES',
                      '-default-test-execution-time-allowance','90','-maximum-test-execution-time-allowance','90',
                      '-only-testing:GameBridgeStoreKitTests/XcodeStoreKitPurchaseTests/'+test,
                      'CODE_SIGN_IDENTITY=-','CODE_SIGNING_REQUIRED=YES','-quiet']
                code=command(args,output/f'{suffix}-{label}.log',240)
                summary={}
                if result.exists():
                    value=subprocess.run(['xcrun','xcresulttool','get','test-results','summary','--path',str(result),'--format','json'],capture_output=True,text=True)
                    if value.returncode==0:
                        try: summary=json.loads(value.stdout)
                        except ValueError: pass
                container=subprocess.run(['xcrun','simctl','get_app_container',sim,BUNDLE,'data'],capture_output=True,text=True)
                checkpoint={}
                if container.returncode==0:
                    path=Path(container.stdout.strip())/'Documents'/('storekit-xctest-'+label+'.json')
                    try: checkpoint=json.loads(path.read_text())
                    except (OSError,ValueError): pass
                passed=(code==0 and summary.get('totalTestCount')==1 and summary.get('failedTests')==0 and
                        summary.get('skippedTests')==0 and checkpoint.get('test')==label and checkpoint.get('stage')=='complete')
                row={'runtime':version,'test':test,'status':'PASS' if passed else 'FAIL','exitCode':code,
                     'timedOut':code==124,'tests':summary.get('totalTestCount'),'failures':summary.get('failedTests'),
                     'skipped':summary.get('skippedTests'),'stage':checkpoint.get('stage','no-checkpoint'),
                     'productIDs':checkpoint.get('productIDs') if checkpoint.get('stage') in ('purchase-and-grant-before','purchase-before') else None,
                     'result':str(result.relative_to(ROOT))}
                report['results'].append(row);print('Result:',version,label,row['status'],'exit',code,'stage',row['stage'],flush=True)
        finally:
            command(['xcrun','simctl','shutdown',sim],output/f'shutdown-{suffix}.log',30)
    try:
        run_runtime('26.5','26-5')
        if len(report['results'])!=2 or any(x['status']!='PASS' for x in report['results']):
            print('26.5 not fully passing; running 18.6 control.',flush=True)
            run_runtime('18.6','18-6')
        good=len(report['results'])>=2 and all(x['status']=='PASS' for x in report['results'][:2])
        report['status']='PASS' if good else 'FAIL'
        if any(x['status']=='DEFERRED_ENV' for x in report['results'][:2]): report['status']='DEFERRED_ENV'
        return 0 if report['status']=='PASS' else 2 if report['status']=='DEFERRED_ENV' else 1
    finally:
        (output/'result.json').write_text(json.dumps(report,indent=2)+'\n')
        print('Evidence directory:',output.relative_to(ROOT),flush=True)


if __name__ == '__main__': raise SystemExit(main())
