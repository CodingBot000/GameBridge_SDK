#!/usr/bin/env python3
"""Run one isolated StoreKit product lookup on each of two fresh runtimes."""
import hashlib
import importlib.util
import json
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BUNDLE = 'invalid.gamebridge.storekit.isolation'
spec = importlib.util.spec_from_file_location('isolation',ROOT/'harness/run-storekit-isolation.py')
isolation = importlib.util.module_from_spec(spec); spec.loader.exec_module(isolation)


def main():
    if sys.argv[1:] != ['--run-local']:
        print('Usage: python3 harness/run-storekit-isolation-products.py --run-local'); return 2
    generator = ROOT/'artifacts/tools/xcodegen/2.46.0/bin/xcodegen'
    if not generator.is_file() or not shutil.which('xcodebuild') or not shutil.which('xcrun'):
        print('DEFERRED_ENV: Xcode or project generator unavailable'); return 2
    output = Path(tempfile.mkdtemp(prefix='storekit-isolation-products-',dir=ROOT/'artifacts'))
    project = output/'project'; shutil.copytree(ROOT/'tests/StoreKitIsolation',project)
    config = ROOT/'ios/StoreKit/GameBridge.storekit'
    shutil.copyfile(config,project/'Current.storekit')
    report={'sourceHead':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
            'sourceTrackedDirty':bool(subprocess.run(['git','diff','--quiet'],cwd=ROOT).returncode or subprocess.run(['git','diff','--cached','--quiet'],cwd=ROOT).returncode),
            'testSourceSHA256':hashlib.sha256((ROOT/'tests/StoreKitIsolation/SessionTests.swift').read_bytes()).hexdigest(),
            'configurationSHA256':hashlib.sha256(config.read_bytes()).hexdigest(),
            'scope':'independent XCTest StoreKit session and products only','results':[],'simulators':{}}
    try:
        code,_=isolation.command([str(generator),'generate','--spec',str(project/'project.yml')],output/'xcodegen.log',60)
        if code: report.update(status='DEFERRED_ENV',stage='project-generation',exitCode=code); return 2
        for runtime,suffix in [('26.5','26-5'),('18.6','18-6')]:
            created=subprocess.run(['xcrun','simctl','create','StoreKit-Products-'+suffix+'-'+str(time.time_ns()),
                                    'com.apple.CoreSimulator.SimDeviceType.iPhone-16',
                                    'com.apple.CoreSimulator.SimRuntime.iOS-'+suffix],cwd=ROOT,text=True,capture_output=True)
            if created.returncode:
                report['results'].append({'runtime':runtime,'status':'DEFERRED_ENV','stage':'simulator-create','exitCode':created.returncode});continue
            sim=created.stdout.strip();report['simulators'][runtime]=sim;print('Retained simulator:',runtime,sim,flush=True)
            try:
                code,_=isolation.command(['xcrun','simctl','boot',sim],output/f'boot-{suffix}.log',60)
                if code==0:code,_=isolation.command(['xcrun','simctl','bootstatus',sim,'-b'],output/f'bootstatus-{suffix}.log',180)
                if code:
                    report['results'].append({'runtime':runtime,'status':'DEFERRED_ENV','stage':'simulator-boot','exitCode':code});continue
                xcresult=output/f'{suffix}-products.xcresult'
                args=['xcodebuild','test','-project',str(project/'StoreKitIsolation.xcodeproj'),'-scheme','Isolation',
                      '-destination',f'platform=iOS Simulator,id={sim}','-derivedDataPath',str(output/'Derived'),
                      '-resultBundlePath',str(xcresult),'-parallel-testing-enabled','NO','-test-timeouts-enabled','YES',
                      '-default-test-execution-time-allowance','60','-maximum-test-execution-time-allowance','60',
                      '-only-testing:IsolationTests/SessionTests/testExistingConfigurationProducts',
                      'CODE_SIGN_IDENTITY=-','CODE_SIGNING_REQUIRED=YES','-quiet']
                print('Running independent session and products:',runtime,flush=True)
                code,timedout=isolation.command(args,output/f'{suffix}-products.log',150)
                summary={}
                if xcresult.exists():
                    r=subprocess.run(['xcrun','xcresulttool','get','test-results','summary','--path',str(xcresult),'--format','json'],capture_output=True,text=True)
                    if r.returncode==0:
                        try: summary=json.loads(r.stdout)
                        except ValueError: pass
                checkpoint={}
                container=subprocess.run(['xcrun','simctl','get_app_container',sim,BUNDLE,'data'],capture_output=True,text=True)
                if container.returncode==0:
                    file=Path(container.stdout.strip())/'Documents/isolation-products.json'
                    try: checkpoint=json.loads(file.read_text())
                    except (OSError,ValueError): pass
                stage=checkpoint.get('stage','no-checkpoint');ids=checkpoint.get('productIDs',[])
                session='PASS' if stage in ('session-created','products-returned','products-error') else 'FAIL' if stage=='session-before' else 'NOT_RUN'
                product='PASS' if stage=='products-returned' and sorted(ids)==['coins_100','premium_unlock'] else 'FAIL' if stage in ('products-returned','products-error') else 'NOT_RUN'
                passed=(code==0 and summary.get('totalTestCount')==1 and summary.get('failedTests')==0 and summary.get('skippedTests')==0 and session=='PASS' and product=='PASS')
                row={'runtime':runtime,'status':'PASS' if passed else 'FAIL','exitCode':code,'timedOut':timedout,
                     'tests':summary.get('totalTestCount'),'failures':summary.get('failedTests'),'skipped':summary.get('skippedTests'),
                     'stage':stage,'session':session,'products':product,'productIDs':ids,'result':str(xcresult.relative_to(ROOT))}
                report['results'].append(row);print('Result:',runtime,row['status'],'session',session,'products',product,'IDs',ids,'exit',code,flush=True)
            finally:
                isolation.command(['xcrun','simctl','shutdown',sim],output/f'shutdown-{suffix}.log',30)
        report['status']='FAIL' if any(x['status']=='FAIL' for x in report['results']) else 'DEFERRED_ENV' if len(report['results'])!=2 or any(x['status']!='PASS' for x in report['results']) else 'PASS'
        return 0 if report['status']=='PASS' else 1 if report['status']=='FAIL' else 2
    finally:
        (output/'result.json').write_text(json.dumps(report,indent=2)+'\n')
        print('Evidence directory:',output.relative_to(ROOT),flush=True)


if __name__ == '__main__': raise SystemExit(main())
