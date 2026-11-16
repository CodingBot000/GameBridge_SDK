"""Real child processes producing disposable reports exercise the collector boundary."""
import copy
import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import time
import unittest
import uuid
from pathlib import Path
from execution_evidence import ROOT, observe
from measurement_contract import measured_lane
from result_aggregator import summarize

spec=importlib.util.spec_from_file_location('verify_all',ROOT/'harness/verify-all.py')
parent=importlib.util.module_from_spec(spec);spec.loader.exec_module(parent)

CHILD='''
import json,os,sys
from pathlib import Path
sys.path.insert(0,str(Path.cwd()/'harness'))
from execution_evidence import metadata
from measurement_contract import measured_lane
folder=Path(sys.argv[1]);log=folder/'checker.log';log.write_text('child PASS')
lane=measured_lane('required',['child-fixture'],0,'child PASS',log,'child PASS')
lane['suite']='required'
mode=sys.argv[2]
if mode=='zero':lane.update(measurement='tests',tests=0)
if mode=='error':lane['errors']=1
if mode=='deferred':lane.update(status='DEFERRED_ENV',exitCode=2,checks=0)
if mode=='skip':lane['skipped']=1
if mode=='missing-unit':lane.pop('measurement')
items=[] if mode=='missing' else [lane]
if mode=='duplicate':items*=2
report={**metadata(),'suites':items}
if mode=='wrong-source':report['sourceHead']='0'*40
if mode=='wrong-digest':report['sourceDigest']='f'*64
if mode=='wrong-run':report['runId']='past-run'
(folder/'result.json').write_text(json.dumps(report))
print('Evidence directory:',folder.relative_to(Path.cwd()))
raise SystemExit(2 if mode=='deferred' else 0)
'''


class ExecutionEvidenceTests(unittest.TestCase):
    def setUp(self):
        (ROOT/'artifacts').mkdir(exist_ok=True)
        self.temp=tempfile.TemporaryDirectory(prefix='collector-fixture-',dir=ROOT/'artifacts');self.addCleanup(self.temp.cleanup)
        self.folder=Path(self.temp.name)

    def collect(self,mode='normal',parent_code=None):
        invocation=uuid.uuid4().hex;env=os.environ.copy();env['GAMEBRIDGE_HARNESS_RUN_ID']=invocation
        command=[sys.executable,'-c',CHILD,str(self.folder),mode];started=time.time_ns()
        process=subprocess.run(command,cwd=ROOT,env=env,text=True,capture_output=True)
        self.assertEqual(process.stderr,'')
        log=self.folder/'parent.log';log.write_text(process.stdout)
        code=process.returncode if parent_code is None else parent_code
        observed=observe(command,code,process.stdout,log,started,invocation)
        lanes=parent.collect_nested('parent',command,code,process.stdout,observed,{'required'})
        return lanes,summarize(lanes,{'parent/required'}),observed,process.stdout

    def test_real_process_exits_0_1_2(self):
        # The subprocess executes the collector and returns its decision itself.
        script=("import sys;sys.path.insert(0,'harness');from test_execution_evidence import ExecutionEvidenceTests;"
                "t=ExecutionEvidenceTests();t.setUp();code=t.collect(sys.argv[1])[1]['exitCode'];t.doCleanups();raise SystemExit(code)")
        for mode,expected in [('normal',0),('error',1),('deferred',2)]:
            process=subprocess.run([sys.executable,'-c',script,mode],cwd=ROOT,text=True,capture_output=True)
            self.assertEqual(process.returncode,expected,process.stderr)

    def test_missing_duplicate_zero_and_error_children(self):
        for mode in ('missing','duplicate','zero','error','missing-unit'):
            self.assertEqual(self.collect(mode)[1]['exitCode'],1,mode)

    def test_source_run_and_digest_mismatch(self):
        for mode in ('wrong-source','wrong-digest','wrong-run'):
            self.assertEqual(self.collect(mode)[1]['exitCode'],1,mode)

    def test_invalid_all_count_types(self):
        lanes,_,_,_=self.collect()
        for key in ('tests','checks','samples','players','failures','skipped','exitCode'):
            for value in ('0',False,True,-1):
                changed=copy.deepcopy(lanes);changed[0][key]=value
                self.assertEqual(summarize(changed)['exitCode'],1,(key,value))

    def test_all_required_measurements_missing(self):
        lanes,_,_,_=self.collect()
        for key in ('tests','checks','samples','players','failures','skipped','exitCode','measurement','checkerEvidence'):
            changed=copy.deepcopy(lanes);changed[0].pop(key)
            self.assertEqual(summarize(changed)['exitCode'],1,key)

    def test_checker_missing_tampered_unrelated_or_old(self):
        for mode in ('missing','tampered','unrelated','old'):
            lanes,_,_,_=self.collect();child=Path(lanes[0]['checkerEvidence']['path'])
            if mode=='missing':child.unlink()
            elif mode=='tampered':child.write_text('new content')
            elif mode=='old':
                past=lanes[0]['parentExecution']['startedNs']-1_000_000_000
                os.utime(child,ns=(past,past))
            else:
                arbitrary=self.folder/'unrelated.log';arbitrary.write_text('child PASS')
                lanes[0]['checkerEvidence']['path']=str(arbitrary)
            self.assertEqual(summarize(lanes)['exitCode'],1,mode)

    def test_same_sha_past_report_cannot_be_replayed(self):
        lanes,_,observed,text=self.collect()
        invocation=uuid.uuid4().hex;log=self.folder/'second.log';started=time.time_ns();log.write_text(text)
        new=observe(observed['command'],0,text,log,started,invocation)
        result=parent.collect_nested('parent',observed['command'],0,text,new,{'required'})
        self.assertEqual(summarize(result,{'parent/required'})['exitCode'],1)

    def test_unobserved_arbitrary_receipt_and_changed_command(self):
        log=self.folder/'loose.log';log.write_text('PASS')
        lane=measured_lane('loose',['fixture'],0,'PASS',log,'PASS')
        for change in ({'command':['other']},{'evidence':str(self.folder/'other.log')}):
            self.assertEqual(summarize([{**lane,**change}])['exitCode'],1)
        lane['checkerEvidence']['invocationId']=uuid.uuid4().hex
        self.assertEqual(summarize([lane])['exitCode'],1)

    def test_parent_exit_and_child_status_must_agree(self):
        for mode,code in [('normal',1),('normal',2),('deferred',0),('error',0)]:
            self.assertEqual(self.collect(mode,code)[1]['exitCode'],1)

    def test_skipped_and_deferred_cannot_be_promoted(self):
        self.assertNotEqual(self.collect('skip')[1]['exitCode'],0)
        lanes,_,_,_=self.collect('deferred');lanes[0]['status']='PASS'
        self.assertEqual(summarize(lanes)['exitCode'],1)

    def test_parent_cannot_change_valid_positive_counts_or_promote_status(self):
        lanes,_,_,_=self.collect()
        for changes in ({'measurement':'tests','tests':7},{'checks':2},{'players':2}):
            self.assertEqual(summarize([{**lanes[0],**changes}])['exitCode'],1)
        lanes,_,_,_=self.collect('deferred')
        lanes[0].update(status='PASS',exitCode=0,checks=1)
        self.assertEqual(summarize(lanes)['exitCode'],1)

    def test_result_json_modification_invalidates_parent_binding(self):
        lanes,_,_,_=self.collect()
        path=Path(lanes[0]['producerEvidence']);path.write_text('{}')
        self.assertEqual(summarize(lanes)['exitCode'],1)

if __name__=='__main__':unittest.main()
