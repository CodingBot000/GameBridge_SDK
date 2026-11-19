#!/usr/bin/env python3
"""Compare StoreKitTest initialization in independent fresh iOS simulators."""
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


def command(args, log, timeout):
    with log.open('w') as stream:
        process = subprocess.Popen(args, cwd=ROOT, stdout=stream, stderr=subprocess.STDOUT, start_new_session=True)
        try:
            return process.wait(timeout=timeout), False
        except subprocess.TimeoutExpired:
            os.killpg(process.pid, signal.SIGTERM)
            try: process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                os.killpg(process.pid, signal.SIGKILL); process.wait()
            return 124, True


def main():
    if sys.argv[1:] != ['--run-local']:
        print('Usage: python3 harness/run-storekit-isolation.py --run-local'); return 2
    generator = ROOT/'artifacts/tools/xcodegen/2.46.0/bin/xcodegen'
    if not generator.is_file() or not shutil.which('xcodebuild') or not shutil.which('xcrun'):
        print('DEFERRED_ENV: Xcode or project generator unavailable'); return 2
    out = Path(tempfile.mkdtemp(prefix='storekit-isolation-', dir=ROOT/'artifacts'))
    project = out/'project'; shutil.copytree(ROOT/'tests/StoreKitIsolation', project)
    shutil.copyfile(ROOT/'ios/StoreKit/GameBridge.storekit', project/'Current.storekit')
    code, _ = command([str(generator), 'generate', '--spec', str(project/'project.yml')], out/'xcodegen.log', 60)
    if code != 0: print('FAIL: isolated project generation; evidence:', out.relative_to(ROOT)); return 1
    report = {'sourceHead':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
              'scope':'independent StoreKitTest session initialization only', 'results':[], 'simulators':{},
              'testTimeoutSeconds':60, 'commandTimeoutSeconds':150}
    for runtime, suffix in [('18.6','18-6'),('26.5','26-5')]:
        created = subprocess.run(['xcrun','simctl','create','StoreKit-Isolation-'+suffix+'-'+str(time.time_ns()),
                                 'com.apple.CoreSimulator.SimDeviceType.iPhone-16',
                                 'com.apple.CoreSimulator.SimRuntime.iOS-'+suffix],cwd=ROOT,text=True,capture_output=True)
        if created.returncode:
            report['results'].append({'runtime':runtime,'status':'DEFERRED_ENV','stage':'simulator-create','exitCode':created.returncode})
            continue
        device = created.stdout.strip(); report['simulators'][runtime] = device
        print('Retained dedicated simulator:', runtime, device, flush=True)
        try:
            code, _ = command(['xcrun','simctl','boot',device], out/f'boot-{suffix}.log', 60)
            if code == 0: code, _ = command(['xcrun','simctl','bootstatus',device,'-b'],out/f'bootstatus-{suffix}.log',180)
            if code != 0:
                report['results'].append({'runtime':runtime,'status':'DEFERRED_ENV','stage':'boot','exitCode':code}); continue
            for test, label in [('testMinimalConfiguration','minimal'),('testExistingConfiguration','existing')]:
                result = out/f'{suffix}-{label}.xcresult'
                args = ['xcodebuild','test','-project',str(project/'StoreKitIsolation.xcodeproj'),'-scheme','Isolation',
                        '-destination',f'platform=iOS Simulator,id={device}','-derivedDataPath',str(out/'Derived'),
                        '-resultBundlePath',str(result),'-parallel-testing-enabled','NO','-test-timeouts-enabled','YES',
                        '-default-test-execution-time-allowance','60','-maximum-test-execution-time-allowance','60',
                        '-only-testing:IsolationTests/SessionTests/'+test,'CODE_SIGN_IDENTITY=-','CODE_SIGNING_REQUIRED=YES','-quiet']
                print('Running:',runtime,label,flush=True)
                code, timed_out = command(args,out/f'{suffix}-{label}.log',150)
                summary = {}
                if result.exists():
                    read = subprocess.run(['xcrun','xcresulttool','get','test-results','summary','--path',str(result),'--format','json'],capture_output=True,text=True)
                    if read.returncode == 0:
                        try: summary = json.loads(read.stdout)
                        except ValueError: pass
                passed = code == 0 and summary.get('totalTestCount') == 1 and summary.get('failedTests') == 0 and summary.get('skippedTests') == 0
                value={'runtime':runtime,'configuration':label,'initializer':'test-bundle URL','status':'PASS' if passed else 'FAIL',
                       'exitCode':code,'timedOut':timed_out,'tests':summary.get('totalTestCount'),
                       'failures':summary.get('failedTests'),'skipped':summary.get('skippedTests'), 'result':str(result.relative_to(ROOT))}
                report['results'].append(value)
                print('Result:',runtime,label,value['status'],'exit',code,'tests',value['tests'],flush=True)
        finally:
            command(['xcrun','simctl','shutdown',device],out/f'shutdown-{suffix}.log',30)
    (out/'result.json').write_text(json.dumps(report,indent=2)+'\n')
    print('Evidence directory:',out.relative_to(ROOT),flush=True)
    if any(x['status']=='FAIL' for x in report['results']): return 1
    if len(report['results']) != 4 or any(x['status']!='PASS' for x in report['results']): return 2
    return 0


if __name__ == '__main__': raise SystemExit(main())
