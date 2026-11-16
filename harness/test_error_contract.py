"""Disposable error-count contracts; no product suites or databases are executed."""
import importlib.util
import json
import tempfile
import unittest
from unittest.mock import patch
import os
from pathlib import Path
from result_aggregator import summarize
from measurement_contract import record_execution

ROOT=Path(__file__).resolve().parent.parent

def module(file):
    spec=importlib.util.spec_from_file_location(file,ROOT/'harness'/file)
    value=importlib.util.module_from_spec(spec);spec.loader.exec_module(value);return value

class ErrorContractTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.fixture_log=Path(self.temp.name)/'observed.log'
        self.fixture_log.write_text('fixture complete')
        record_execution(['fixture'],0,'fixture complete',self.fixture_log)
        self.base={'name':'lane','status':'PASS','required':True,'tests':1,'failures':0,'errors':0,'skipped':0,'exitCode':0}

    def test_separate_normal_and_error_despite_success_exit(self):
        self.assertEqual(summarize([self.base])['exitCode'],0)
        self.assertEqual(summarize([{**self.base,'errors':1}])['exitCode'],1)

    def test_invalid_and_missing_errors(self):
        for value in (-1,'0',False,True,None):
            with self.subTest(value=value):self.assertEqual(summarize([{**self.base,'errors':value}])['exitCode'],1)
        value=self.base.copy();value.pop('errors')
        self.assertEqual(summarize([value])['exitCode'],1)

    def test_combined_compatibility_is_explicit(self):
        value={**self.base,'errors':None,'errorModel':'included-in-failures'}
        self.assertEqual(summarize([value])['exitCode'],0)
        self.assertEqual(summarize([{**value,'failures':1}])['exitCode'],1)
        self.assertEqual(summarize([{**value,'errors':1}])['exitCode'],1)
        self.assertEqual(summarize([{**value,'errors':'0'}])['exitCode'],1)
        value.pop('errors');self.assertEqual(summarize([value])['exitCode'],0)

    def test_nested_parent_and_saved_reports_preserve_errors(self):
        parent=module('verify-all.py')
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp);child={**self.base,'suite':'child','errors':1}
            lane=parent.nested_lane('parent',child,['fixture'],'fixture.json')
            (path/'result.json').write_text(json.dumps({'lanes':[lane],'summary':summarize([lane])}))
            (path/'summary.md').write_text(parent.lane_row(lane))
            report=json.loads((path/'result.json').read_text())
            self.assertEqual(report['lanes'][0]['errors'],1);self.assertEqual(report['summary']['exitCode'],1)
            self.assertIn('| 1 | UNSPECIFIED |',(path/'summary.md').read_text())
            lane=parent.nested_lane('parent',{'suite':'child','status':'PASS','tests':1,'exitCode':0},[],'fixture')
            self.assertNotIn('errors',lane);self.assertEqual(summarize([lane])['exitCode'],1)

    def test_junit_does_not_double_count_errors(self):
        common=module('run-auth-regression.py')
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/'report.xml';path.write_text('<testsuite tests="2" failures="0" errors="1" skipped="0"/>')
            counts=common.junit_counts([path],0)
            self.assertEqual(tuple(counts),(2,0,0));self.assertEqual(counts.errors,1)
            result=common.item('fixture',0,counts)
            self.assertEqual(result['status'],'FAIL');self.assertEqual(result['failures'],0);self.assertEqual(result['errors'],1)
            self.assertEqual(summarize([{**result,'name':'fixture','required':True,'status':'PASS'}])['exitCode'],1)

    def test_non_junit_producers_and_checker_compatibility(self):
        common=module('run-auth-regression.py')
        for file in ('run-purchase-regression.py','run-push-regression.py'):
            producer=module(file);counts=producer.swift_counts('Executed 3 tests, with 0 failures')
            value=common.item('swift',0,counts)
            self.assertEqual(value['errorModel'],'included-in-failures');self.assertIsNone(value['errors'])
            self.assertEqual(summarize([{**value,'name':'swift','required':True}])['exitCode'],0)
        value=common.item('marker',0,(1,0,0),error_model='checker-exit')
        self.assertIsNone(value['errors']);self.assertEqual(summarize([{**value,'name':'marker','required':True}])['exitCode'],0)

    def test_emitted_nested_producers_with_stubbed_commands(self):
        # Execute the actual producer main functions, replacing external commands only.
        output_text = ('Executed 3 tests, with 0 failures\n'
                       'PASS: mock permission denied, registration blocked, re-request denied (standalone managed test)\n'
                       'Staging integrity PASS: fixture\nPackage negatives PASS: fixture\n')
        for file in ('run-auth-regression.py','run-purchase-regression.py','run-push-regression.py'):
            producer=module(file)
            common=producer if file=='run-auth-regression.py' else producer.common
            with tempfile.TemporaryDirectory() as temp:
                root=Path(temp)
                def fake_run(command,env,log,**kwargs):
                    log.write_text(output_text);record_execution(command,0,output_text,log)
                    return 0,output_text,0
                with patch.object(producer,'ROOT',root), patch.object(common,'run',side_effect=fake_run), \
                     patch.object(common,'junit_counts',return_value=common.JUnitCounts(1,0,0,0)), \
                     patch.object(producer.shutil,'which',return_value='/fixture'), patch.dict(os.environ,{'GAMEBRIDGE_UPM_STAGING':temp},clear=True):
                    producer.main()
                report=json.loads(next((root/'artifacts').glob('*/result.json')).read_text())
                passed=[x for x in report['suites'] if x['status']=='PASS']
                self.assertTrue(passed)
                for value in passed:
                    self.assertIn('errors',value);self.assertIn('errorModel',value)
                    self.assertEqual(summarize([{**value,'name':value['suite'],'required':True}])['exitCode'],0)

    def test_contract_producer_emits_separate_and_compatible_errors(self):
        producer=module('run-contracts.py')
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);(root/'android').mkdir();(root/'android/gradlew').touch()
            editor=root/'editor';editor.touch()
            def fake_run(command,log,env):
                if log.name=='kotlin.log':
                    folder=root/'android/sdk-core/build/test-results/test';folder.mkdir(parents=True)
                    for cls in ('BridgeProtocolTest','ModelFixtureTest','SdkCoordinatorTest','BridgeDispatcherTest'):
                        (folder/('TEST-com.gamebridge.'+cls+'.xml')).write_text('<testsuite tests="1" failures="0" errors="0" skipped="0"/>')
                text='Executed 3 tests, with 0 failures\nRegistry, facade and offline fake smoke passed'
                log.write_text(text);record_execution(command,0,text,log)
                return 0,text
            with patch.object(producer,'ROOT',root),patch.object(producer,'run',side_effect=fake_run), \
                 patch.object(producer.shutil,'which',return_value='/fixture'),patch.dict(os.environ,{'UNITY_EDITOR_PATH':str(editor)},clear=True):
                self.assertEqual(producer.main(),0)
            report=json.loads(next((root/'artifacts').glob('*/result.json')).read_text())
            for value in report['suites']:
                self.assertIn('errors',value)
                self.assertEqual(summarize([{**value,'name':value['suite'],'required':True}])['exitCode'],0)

    def test_required_missing_zero_and_skip(self):
        self.assertEqual(summarize([self.base],{'lane','missing'})['exitCode'],1)
        self.assertEqual(summarize([{**self.base,'tests':0}])['exitCode'],1)
        self.assertNotEqual(summarize([{**self.base,'skipped':1}])['exitCode'],0)

if __name__=='__main__':unittest.main()
