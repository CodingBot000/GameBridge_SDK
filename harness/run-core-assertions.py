#!/usr/bin/env python3
"""R01-R12 measurement ledger: executed tests/helpers and declared coverage are distinct."""
import argparse
import hashlib
import importlib.util
import json
import os
import re
import shutil
import sys
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path
from assertion_contract import records,totals,stress_assertions
from execution_evidence import metadata
from measurement_contract import last_execution
ROOT=Path(__file__).resolve().parent.parent
spec=importlib.util.spec_from_file_location('assert_common',ROOT/'harness/run-auth-regression.py')
common=importlib.util.module_from_spec(spec);spec.loader.exec_module(common)
KOTLIN=('BridgeProtocolTest','ModelFixtureTest','SdkCoordinatorTest','BridgeDispatcherTest')


def evidence_directory(text):
    matches=re.findall(r'^Evidence directory: (.+)$',text,re.M)
    if len(matches)!=1:raise ValueError('ambiguous evidence')
    path=Path(matches[0]);path=path if path.is_absolute() else ROOT/path
    path=path.resolve()
    if not path.is_relative_to((ROOT/'artifacts').resolve()):raise ValueError('external evidence')
    return path


def native_scopes(rid, kotlin, swift):
    names={
      'R01':('initialization joins','testRequireReadyBeforeInitializationFails'),
      'R02':('initialization joins','testConcurrentInitializeAndShutdown'),
      'R03':('initialization joins','testConcurrentInitializeAndShutdown'),
      'R07':('rejects invalid envelopes','testRejectsMalformedInputs'),
      'R08':('status returns correlated','testInvalidLengthsAreRejectedWithoutReadingAndBridgeSurvives'),
      'R09':('', 'testCopiedUTF8AndCorrelatedResponse'),
      'R10':('shutdown cancels','testShutdownDuringInitialization')}
    k,s=names.get(rid,('',''))
    return {'kotlin':[x for x in kotlin if k and k in x['test']], 'swift':[x for x in swift if s and s in x['test']]}


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--run-local',action='store_true',required=True);parser.add_argument('--include-editor',action='store_true');a=parser.parse_args()
    (ROOT/'artifacts').mkdir(exist_ok=True);out=Path(tempfile.mkdtemp(prefix='core-assertions-',dir=ROOT/'artifacts'))
    env=os.environ.copy();env['PYTHONDONTWRITEBYTECODE']='1';env.pop('GAMEBRIDGE_TEST_CONFIG_JSON',None);report={**metadata(),'scope':'test-only helper invocation measurement','status':'FAIL','executions':[]}
    try:
        code,text,started=common.run(['python3','harness/run-contracts.py'],env,out/'contracts.log')
        directory=evidence_directory(text);data=json.loads((directory/'result.json').read_text())
        observed=last_execution()
        if code!=0 or data.get('sourceHead')!=report['sourceHead'] or data.get('runId')!=observed['invocationId']:raise ValueError('contracts failed/stale')
        suites={x['suite']:x for x in data['suites']}
        if set(suites)!={'kotlin','swift','csharp'} or any(x['status']!='PASS' for x in suites.values()):raise ValueError('missing contract platform')
        kotlin=[]
        for name in KOTLIN:
            xml=ROOT/f'android/sdk-core/build/test-results/test/TEST-com.gamebridge.{name}.xml'
            if xml.stat().st_mtime_ns<started:raise ValueError('stale JUnit')
            root=ET.parse(xml).getroot();kotlin+=records(''.join(x.text or '' for x in root.findall('system-out')),'kotlin-jvm',int(root.attrib['tests']))
            shutil.copyfile(xml,out/xml.name)
        swift=records((directory/'swift.log').read_text(),'swift-xctest',suites['swift']['tests'])
        managed=records((directory/'csharp.log').read_text(),'csharp-managed',1)
        for platform,items in [('kotlin',kotlin),('swift',swift),('csharp',managed)]:
            report['executions'].append({'name':platform,'tests':suites[platform]['tests'],'checks':suites[platform]['checks'],**{k:suites[platform][k] for k in ('status','exitCode','failures','errors','errorModel','skipped')},**totals(items),'records':items,'assertionOutcomes':'UNMEASURED'})
        code,text,_=common.run(['bash','scripts/stress-csharp-lifecycle.sh'],env,out/'stress.log')
        if code:raise ValueError('stress failed')
        stress_path=evidence_directory(text)/'result.json';stress=json.loads(stress_path.read_text());counts=stress_assertions(stress)
        report['executions'].append({'name':'lifecycle-stress','tests':0,'checks':1,'samples':stress['samples'],'assertions':counts,'evidence':str(stress_path.relative_to(ROOT))})
        target=ROOT/'unity/Packages/com.gamebridge.sdk/Runtime/Core/RequestRegistry.cs';before=hashlib.sha256(target.read_bytes()).hexdigest()
        code,text,_=common.run(['python3','harness/check-bridge-mutation.py'],env,out/'mutation.log')
        mutation_path=evidence_directory(text);mutation=json.loads((mutation_path/'result.json').read_text())
        if code or mutation.get('status')!='PASS' or mutation.get('sourceUnchanged') is not True or not mutation.get('mutatedProcessExitCode') or hashlib.sha256(target.read_bytes()).hexdigest()!=before:raise ValueError('mutation/restore failed')
        partial=records((mutation_path/'mutation.log').read_text(),'csharp-managed',1,allow_partial=True)
        report['executions'].append({'name':'duplicate-guard-mutation','tests':0,'checks':1,'expectedProcessFailures':1,'mutatedProcessExitCode':mutation['mutatedProcessExitCode'],'partialAssertions':totals(partial),'normalProbeExitCode':mutation['normalProbeExitCode'],'normalProbeAssertions':totals(records((mutation_path/'normal-probe.log').read_text(),'csharp-managed',1)),'probe':mutation['probe'],'sourceUnchanged':True})
        code,text,_=common.run(['bash','scripts/smoke-csharp-registry.sh'],env,out/'normal-after-mutation.log')
        if code or 'Registry, facade and offline fake smoke passed' not in text:raise ValueError('normal restoration failed')
        restored=records(text,'csharp-managed',1)
        report['executions'].append({'name':'normal-after-mutation','tests':0,'checks':1,**totals(restored),'sourceUnchanged':hashlib.sha256(target.read_bytes()).hexdigest()==before})
        branch_env=env.copy()
        branch_env['GAMEBRIDGE_TEST_CONFIG_JSON']=json.dumps({'revision':'1','maintenanceEnabled':False,'message':None,'expiresAt':'2026-12-31T00:00:00Z','source':'NETWORK'})
        code,text,_=common.run(['bash','scripts/smoke-csharp-registry.sh'],branch_env,out/'conditional-branch.log')
        if code:raise ValueError('conditional branch control failed')
        branch=records(text,'csharp-managed',1)
        before_sites=[x for x in managed[0]['sites'] if x['label']=='actual local config decoded']
        branch_sites=[x for x in branch[0]['sites'] if x['label']=='actual local config decoded']
        if before_sites or len(branch_sites)!=1 or branch_sites[0]['count']!=1 or branch[0]['assertionsExecuted']!=managed[0]['assertionsExecuted']+1:raise ValueError('unexecuted branch counted or unstable controls')
        report['executions'].append({'name':'conditional-branch-control','tests':0,'checks':1,**totals(branch),'branchOffExecutions':0,'branchOnExecutions':1})
        editor=[]
        if a.include_editor:
            code,text,editor_started=common.run(['bash','scripts/build-unity.sh','--editor-smoke'],env,out/'editor.log')
            directory=evidence_directory(text)
            if code or 'Unity consumer tests PASS: 2 executed' not in text:raise ValueError('editor failed')
            xml=directory/'results.xml'
            if xml.stat().st_mtime_ns<editor_started:raise ValueError('stale Editor result')
            document=ET.parse(xml).getroot()
            editor=records('\n'.join(x.text or '' for x in document.findall('.//output')),'csharp-unity-editor',2)
            report['executions'].append({'name':'unity-editor','tests':2,'checks':1,**totals(editor),'records':editor})
        manifest=json.loads((ROOT/'harness/regression-manifest.json').read_text())
        labels={'R04':['duplicate response ignored exactly once'],'R05':['late timed-out response ignored','purchase event accepted after timeout','verified purchase event'],'R06':['stale session must be ignored','stale event ignored'],'R07':['malformed JSON ignored safely','trailing JSON must be ignored'],'R10':['race error','cancel shutdown race completes once']}
        coverage=[]
        for scenario in manifest['scenarios'][:12]:
            rid=scenario['id'];scopes=native_scopes(rid,kotlin,swift)
            selected=[x for x in managed[0]['sites'] if x['label'] in labels.get(rid,[])]
            if rid=='R01':selected=[x for x in managed[0]['sites'] if x['label']=='expected NOT_INITIALIZED' and 'facade.GetProductsAsync()' in (ROOT/'scripts/registry-smoke.cs').read_text().splitlines()[x['line']-1]]
            if rid=='R02':selected=[x for x in managed[0]['sites'] if x['label'] in ('same config sends one init','same config identical ready results','same configuration joins initialization')]
            if rid=='R03':selected=[x for x in managed[0]['sites'] if x['label'] in ('different config','expected ALREADY_INITIALIZED_DIFFERENT_CONFIG')]
            coverage.append({'id':rid,'declaredPlatform':scenario['platform'],'managedSmokeExecution':'EXECUTED','jniPlayerExecution':'NOT_RUN_BY_THIS_LEDGER' if rid=='R09' else None,'editorExecution':('EXECUTED' if editor else 'NOT_RUN') if rid=='R11' else None,'declaredManifestAssertions':scenario['assertions'],'declarationKind':'STATIC_MAPPING_NOT_EXECUTIONS',
                'nativeTestScopes':scopes,'nativeAttribution':'entire shared test scope; not per-R assertion totals',
                'managedLabelSelectedSites':selected,'managedLabelSelectedAssertions':sum(x['count'] for x in selected) if selected else 'UNMEASURED',
                'unityEditorScopes':editor if rid=='R11' else [],'stressExecution':counts if rid=='R12' else None,
                'jniPlayerAssertionCount':'UNMEASURED' if rid=='R09' else None,
                'limits':'Unwrapped implicit failure signals and unselected scopes remain UNMEASURED; no test-count substitution'})
        report.update(status='PASS',scenarioCoverage=coverage,assertionOutcomes='UNMEASURED',sourceCallSiteCount='UNMEASURED',
                      limitation='Counts are test-helper invocations, not boolean operands or all framework internals. Shared test scope totals are not additive per scenario.')
    except (OSError,ValueError,KeyError,ET.ParseError) as error:
        report['failure']=type(error).__name__+': '+str(error)
    (out/'result.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    for item in report['executions']:print(item['name'],'tests',item.get('tests'),'checks',item.get('checks'),'assertions',item.get('assertionsExecuted',item.get('assertions',item.get('partialAssertions'))))
    print('Assertion ledger',report['status'],'Evidence directory:',out.relative_to(ROOT))
    return 0 if report['status']=='PASS' else 1

if __name__=='__main__':raise SystemExit(main())
