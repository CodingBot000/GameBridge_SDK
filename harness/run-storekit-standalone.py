#!/usr/bin/env python3
"""Compare standalone app StoreKitTest initialization on fresh simulators."""
import argparse
import json
import re
import os
import shutil
import signal
import subprocess
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BUNDLE = 'invalid.gamebridge.storekit.isolation'


def command(args, log, timeout, env=None):
    with log.open('w') as stream:
        p = subprocess.Popen(args, cwd=ROOT, env=env, stdout=stream, stderr=subprocess.STDOUT, start_new_session=True)
        try:
            return p.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            os.killpg(p.pid, signal.SIGTERM)
            try: p.wait(timeout=10)
            except subprocess.TimeoutExpired: os.killpg(p.pid, signal.SIGKILL); p.wait()
            return 124


def process_alive(pid):
    result = subprocess.run(['ps','-p',str(pid),'-o','stat='],capture_output=True,text=True,check=False)
    return result.returncode == 0 and bool(result.stdout.strip()) and not result.stdout.strip().startswith('Z')


def classify(checkpoints, exited, timed_out):
    if all(x in checkpoints for x in ('started','session-create-before','session-create-after')):
        return 'PASS', 'session-create-after', 0
    if 'session-create-error' in checkpoints:
        return 'FAIL', 'session-create-error', 1
    if 'configuration-missing' in checkpoints:
        return 'FAIL', 'configuration-missing', 1
    if 'session-create-before' in checkpoints:
        if exited: return 'FAIL', 'app-exited-during-session-create', 1
        if timed_out: return 'FAIL', 'session-create-timeout', 1
        return 'DEFERRED_ENV', 'session-create-result-unknown', 2
    return 'DEFERRED_ENV', 'app-start-or-configuration', 2


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--run-local',action='store_true',required=True)
    parser.add_argument('--runtime',choices=('18.6','26.5'),help='single-runtime diagnostic; default compares both')
    args=parser.parse_args()
    generator = ROOT/'artifacts/tools/xcodegen/2.46.0/bin/xcodegen'
    if not generator.is_file() or not shutil.which('xcodebuild') or not shutil.which('xcrun'):
        print('DEFERRED_ENV: Xcode or project generator unavailable'); return 2
    out = Path(tempfile.mkdtemp(prefix='storekit-standalone-', dir=ROOT/'artifacts'))
    project = out/'project'; shutil.copytree(ROOT/'tests/StoreKitIsolation', project)
    shutil.copyfile(ROOT/'ios/StoreKit/GameBridge.storekit', project/'Current.storekit')
    report = {'sourceHead':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
              'scope':'independent app-bundle StoreKitTest session initialization only', 'results':[],
              'simulators':{}, 'checkpointTimeoutSeconds':75}
    try:
        code = command([str(generator),'generate','--spec',str(project/'project.yml')],out/'xcodegen.log',60)
        if code != 0: report.update(status='DEFERRED_ENV',stage='project-generation',exitCode=code); return 2
        code = command(['xcodebuild','build','-project',str(project/'StoreKitIsolation.xcodeproj'),'-scheme','Isolation',
                        '-destination','generic/platform=iOS Simulator','-derivedDataPath',str(out/'Derived'),
                        'CODE_SIGN_IDENTITY=-','CODE_SIGNING_REQUIRED=YES','-quiet'],out/'build.log',180)
        report['buildExitCode']=code
        if code != 0: report.update(status='DEFERRED_ENV',stage='build-or-framework',exitCode=code); return 2
        app=out/'Derived/Build/Products/Debug-iphonesimulator/IsolationHost.app'
        if not (app/'Current.storekit').is_file(): report.update(status='FAIL',stage='app-bundle-resource'); return 1
        selected=[(v,s) for v,s in [('18.6','18-6'),('26.5','26-5')] if not args.runtime or args.runtime == v]
        for version,suffix in selected:
            created=subprocess.run(['xcrun','simctl','create','StoreKit-Standalone-'+suffix+'-'+str(time.time_ns()),
                                    'com.apple.CoreSimulator.SimDeviceType.iPhone-16',
                                    'com.apple.CoreSimulator.SimRuntime.iOS-'+suffix],cwd=ROOT,text=True,capture_output=True)
            if created.returncode:
                report['results'].append({'runtime':version,'status':'DEFERRED_ENV','stage':'simulator-create','exitCode':created.returncode});continue
            device=created.stdout.strip();report['simulators'][version]=device
            print('Retained dedicated simulator:',version,device,flush=True)
            row={'runtime':version,'status':'DEFERRED_ENV','stage':'boot','buildExitCode':report['buildExitCode'],
                 'launchExitCode':None,'timedOut':False,'checkpoints':[]}
            try:
                code=command(['xcrun','simctl','boot',device],out/f'boot-{suffix}.log',60)
                if code == 0: code=command(['xcrun','simctl','bootstatus',device,'-b'],out/f'bootstatus-{suffix}.log',180)
                if code != 0: row['exitCode']=code; continue
                row['stage']='install'
                code=command(['xcrun','simctl','install',device,str(app)],out/f'install-{suffix}.log',60)
                if code != 0: row['exitCode']=code; continue
                container=subprocess.run(['xcrun','simctl','get_app_container',device,BUNDLE,'data'],cwd=ROOT,capture_output=True,text=True,timeout=30)
                if container.returncode: row['stage']='container';row['exitCode']=container.returncode;continue
                documents=Path(container.stdout.strip())/'Documents'
                env=os.environ.copy();env['SIMCTL_CHILD_STOREKIT_ISOLATION_STANDALONE']='true'
                row['stage']='launch'
                code=command(['xcrun','simctl','launch',device,BUNDLE],out/f'launch-{suffix}.log',30,env)
                row['launchExitCode']=code
                if code != 0: row['exitCode']=code; continue
                match=re.search(r'^'+re.escape(BUNDLE)+r':\s*(\d+)\s*$',(out/f'launch-{suffix}.log').read_text(),re.M)
                if not match: row.update(status='DEFERRED_ENV',stage='launch-pid-missing',exitCode=2);continue
                pid=int(match.group(1));row['launchPID']=pid
                deadline=time.monotonic()+75
                exited=False
                while time.monotonic()<deadline:
                    row['checkpoints']=[name for name in ('started','configuration-missing','session-create-before','session-create-after','session-create-error') if (documents/('isolation-'+name+'.json')).is_file()]
                    if 'session-create-after' in row['checkpoints'] or 'session-create-error' in row['checkpoints'] or 'configuration-missing' in row['checkpoints']: break
                    if not process_alive(pid): exited=True;break
                    time.sleep(.25)
                else: row['timedOut']=True
                row['processExited']=exited
                row['status'],row['stage'],row['exitCode']=classify(row['checkpoints'],exited,row['timedOut'])
                print('Result:',version,row['status'],row['stage'],'launch',row['launchExitCode'],flush=True)
            finally:
                report['results'].append(row)
                command(['xcrun','simctl','terminate',device,BUNDLE],out/f'terminate-{suffix}.log',30)
                command(['xcrun','simctl','shutdown',device],out/f'shutdown-{suffix}.log',30)
        status='FAIL' if any(r['status']=='FAIL' for r in report['results']) else 'DEFERRED_ENV' if len(report['results']) != len(selected) or any(r['status']!='PASS' for r in report['results']) else 'PASS'
        report['status']=status
        return 0 if status=='PASS' else 1 if status=='FAIL' else 2
    finally:
        (out/'result.json').write_text(json.dumps(report,indent=2)+'\n')
        print('Evidence directory:',out.relative_to(ROOT),flush=True)


if __name__ == '__main__': raise SystemExit(main())
