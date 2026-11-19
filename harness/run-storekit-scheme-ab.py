#!/usr/bin/env python3
"""Compare only XcodeGen RunAction StoreKit configuration on fresh iOS 26.5 simulators."""
import hashlib
import importlib.util
import json
import shutil
import subprocess
import sys
import tempfile
import time
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT=Path(__file__).resolve().parent.parent
BUNDLE='invalid.gamebridge.storekit.isolation'
spec=importlib.util.spec_from_file_location('isolation',ROOT/'harness/run-storekit-isolation.py')
isolation=importlib.util.module_from_spec(spec);spec.loader.exec_module(isolation)


def normalized_scheme(path):
    root=ET.parse(path).getroot(); refs=[]
    for parent in root.iter():
        for child in list(parent):
            if child.tag == 'StoreKitConfigurationFileReference':
                refs.append(child.attrib.get('identifier'));parent.remove(child)
    def normalize(node):
        return (node.tag,tuple(sorted(node.attrib.items())),tuple(normalize(x) for x in node))
    return normalize(root),refs


def main():
    if sys.argv[1:] != ['--run-local']:
        print('Usage: python3 harness/run-storekit-scheme-ab.py --run-local');return 2
    generator=ROOT/'artifacts/tools/xcodegen/2.46.0/bin/xcodegen'
    if not generator.is_file() or not shutil.which('xcodebuild') or not shutil.which('xcrun'):
        print('DEFERRED_ENV: Xcode or project generator unavailable');return 2
    out=Path(tempfile.mkdtemp(prefix='storekit-scheme-ab-',dir=ROOT/'artifacts'))
    report={'sourceHead':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
            'sourceTrackedDirty':bool(subprocess.run(['git','diff','--quiet'],cwd=ROOT).returncode or subprocess.run(['git','diff','--cached','--quiet'],cwd=ROOT).returncode),
            'testSourceSHA256':hashlib.sha256((ROOT/'tests/StoreKitIsolation/SessionTests.swift').read_bytes()).hexdigest(),
            'configurationSHA256':hashlib.sha256((ROOT/'ios/StoreKit/GameBridge.storekit').read_bytes()).hexdigest(),
            'runtime':'iOS 26.5','configurationActive':'NOT_CONFIRMED','results':[],'simulators':{}}
    try:
        for label in ('A','B'):
            project=out/label;shutil.copytree(ROOT/'tests/StoreKitIsolation',project)
            shutil.copyfile(ROOT/'ios/StoreKit/GameBridge.storekit',project/'Current.storekit')
            if label=='B':
                yml=project/'project.yml';text=yml.read_text();needle='    test:\n      targets:\n        - IsolationTests\n'
                if text.count(needle)!=1: report.update(status='FAIL',stage='scheme-input-shape');return 1
                yml.write_text(text.replace(needle,'    run:\n      storeKitConfiguration: Current.storekit\n'+needle))
            code,_=isolation.command([str(generator),'generate','--spec',str(project/'project.yml')],out/f'{label}-xcodegen.log',60)
            if code:report.update(status='DEFERRED_ENV',stage='project-generation',exitCode=code);return 2
        for file in ('App.swift','SessionTests.swift','Minimal.storekit','Current.storekit'):
            if (out/'A'/file).read_bytes() != (out/'B'/file).read_bytes():
                report.update(status='FAIL',stage='source-mismatch');return 1
        scheme='StoreKitIsolation.xcodeproj/xcshareddata/xcschemes/Isolation.xcscheme'
        # XcodeGen emits an empty argument list when an explicit run stanza is present.
        # Remove that no-op element so the actual schemes differ only in StoreKit reference.
        bscheme=out/'B'/scheme; xml=bscheme.read_text()
        empty='      <CommandLineArguments>\n      </CommandLineArguments>\n      <StoreKitConfigurationFileReference'
        if xml.count(empty)!=1: report.update(status='FAIL',stage='unexpected-run-arguments');return 1
        bscheme.write_text(xml.replace(empty,'      <StoreKitConfigurationFileReference'))
        a,arefs=normalized_scheme(out/'A'/scheme);b,brefs=normalized_scheme(bscheme)
        report['schemeComparison']={'identicalAfterRemovingStoreKitReference':a==b,'A':arefs,'B':brefs}
        if a!=b or arefs or len(brefs)!=1 or not brefs[0].endswith('/Current.storekit'):
            report.update(status='FAIL',stage='scheme-difference');return 1
        print('Scheme comparison PASS: only StoreKit reference differs',flush=True)
        for label in ('A','B'):
            created=subprocess.run(['xcrun','simctl','create','StoreKit-Scheme-'+label+'-'+str(time.time_ns()),
                                    'com.apple.CoreSimulator.SimDeviceType.iPhone-16',
                                    'com.apple.CoreSimulator.SimRuntime.iOS-26-5'],cwd=ROOT,text=True,capture_output=True)
            if created.returncode:
                report['results'].append({'variant':label,'status':'DEFERRED_ENV','stage':'simulator-create','exitCode':created.returncode});continue
            sim=created.stdout.strip();report['simulators'][label]=sim;print('Retained simulator:',label,sim,flush=True)
            try:
                code,_=isolation.command(['xcrun','simctl','boot',sim],out/f'{label}-boot.log',60)
                if code==0:code,_=isolation.command(['xcrun','simctl','bootstatus',sim,'-b'],out/f'{label}-bootstatus.log',180)
                if code:
                    report['results'].append({'variant':label,'status':'DEFERRED_ENV','stage':'boot','exitCode':code});continue
                result=out/f'{label}.xcresult';project=out/label
                args=['xcodebuild','test','-project',str(project/'StoreKitIsolation.xcodeproj'),'-scheme','Isolation',
                      '-destination',f'platform=iOS Simulator,id={sim}','-derivedDataPath',str(out/f'Derived-{label}'),
                      '-resultBundlePath',str(result),'-parallel-testing-enabled','NO','-test-timeouts-enabled','YES',
                      '-default-test-execution-time-allowance','60','-maximum-test-execution-time-allowance','60',
                      '-only-testing:IsolationTests/SessionTests/testExistingConfigurationProducts',
                      'CODE_SIGN_IDENTITY=-','CODE_SIGNING_REQUIRED=YES','-quiet']
                print('Running variant:',label,flush=True)
                code,timedout=isolation.command(args,out/f'{label}-test.log',150);summary={}
                if result.exists():
                    r=subprocess.run(['xcrun','xcresulttool','get','test-results','summary','--path',str(result),'--format','json'],capture_output=True,text=True)
                    if r.returncode==0:
                        try:summary=json.loads(r.stdout)
                        except ValueError:pass
                checkpoint={};container=subprocess.run(['xcrun','simctl','get_app_container',sim,BUNDLE,'data'],capture_output=True,text=True)
                if container.returncode==0:
                    try:checkpoint=json.loads((Path(container.stdout.strip())/'Documents/isolation-products.json').read_text())
                    except (OSError,ValueError):pass
                stage=checkpoint.get('stage','no-checkpoint');ids=checkpoint.get('productIDs',[])
                session='PASS' if stage in ('session-created','products-returned','products-error') else 'FAIL' if stage=='session-before' else 'NOT_RUN'
                product='PASS' if stage=='products-returned' and sorted(ids)==['coins_100','premium_unlock'] else 'FAIL' if stage in ('products-returned','products-error') else 'NOT_RUN'
                passed=(code==0 and summary.get('totalTestCount')==1 and summary.get('failedTests')==0 and summary.get('skippedTests')==0 and session=='PASS' and product=='PASS')
                row={'variant':label,'status':'PASS' if passed else 'FAIL','exitCode':code,'timedOut':timedout,
                     'tests':summary.get('totalTestCount'),'failures':summary.get('failedTests'),'skipped':summary.get('skippedTests'),
                     'stage':stage,'session':session,'products':product,'productIDs':ids,'activeConfiguration':'NOT_CONFIRMED',
                     'result':str(result.relative_to(ROOT))}
                report['results'].append(row);print('Result:',label,row['status'],'session',session,'products',product,'IDs',ids,'exit',code,flush=True)
            finally:isolation.command(['xcrun','simctl','shutdown',sim],out/f'{label}-shutdown.log',30)
        report['status']='FAIL' if any(x['status']=='FAIL' for x in report['results']) else 'DEFERRED_ENV' if len(report['results'])!=2 or any(x['status']!='PASS' for x in report['results']) else 'PASS'
        return 0 if report['status']=='PASS' else 1 if report['status']=='FAIL' else 2
    finally:
        (out/'result.json').write_text(json.dumps(report,indent=2)+'\n')
        print('Evidence directory:',out.relative_to(ROOT),flush=True)


if __name__=='__main__':raise SystemExit(main())
