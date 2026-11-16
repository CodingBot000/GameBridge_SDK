"""Disposable measurement contracts; no Player, DB or product regression runs."""
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from measurement_contract import measured_lane
from result_aggregator import summarize

ROOT=Path(__file__).resolve().parent.parent

class MeasurementTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.log=Path(self.temp.name)/'fixture.log'

    def lane(self,name='checker',text='PASS marker',code=0,marker='PASS marker'):
        self.log.write_text(text)
        return measured_lane(name,['fixture-checker'],code,text,self.log,marker)

    def test_checker_counts_no_test_cases(self):
        lane=self.lane()
        self.assertEqual((lane['tests'],lane['checks'],lane['samples'],lane['players']),(0,1,0,0))
        self.assertEqual(summarize([lane])['exitCode'],0)
        self.assertIsNone(lane['errors'])

    def test_missing_marker_and_failed_exit(self):
        for text,code in [('absent',0),('PASS marker',1)]:
            lane=self.lane(text=text,code=code)
            self.assertEqual(summarize([lane])['exitCode'],1)

    def test_unexecuted_or_unsubstantiated_checker_rejected(self):
        fake={'name':'fake','status':'PASS','required':True,'tests':0,'checks':1,'errors':None,'errorModel':'checker-exit','measurement':'checker','exitCode':0,'skipped':0}
        self.assertEqual(summarize([fake])['exitCode'],1)
        lane=self.lane()
        for changes in ({'checks':0},{'checkerEvidence':None},{'command':[]}):
            self.assertEqual(summarize([{**lane,**changes}])['exitCode'],1)

    def test_missing_modified_evidence_and_errors_rejected(self):
        lane=self.lane();self.log.write_text('different')
        self.assertEqual(summarize([lane])['exitCode'],1)
        lane=self.lane();self.log.unlink()
        self.assertEqual(summarize([lane])['exitCode'],1)
        lane=self.lane()
        self.assertEqual(summarize([{**lane,'errors':1}])['exitCode'],1)

    def test_required_missing_and_skip(self):
        lane=self.lane()
        self.assertEqual(summarize([lane],{'checker','missing'})['exitCode'],1)
        self.assertNotEqual(summarize([{**lane,'skipped':1}])['exitCode'],0)

    def test_actual_unittest_count(self):
        run=subprocess.run([sys.executable,'-m','unittest','discover','-s','harness','-p','test_aggregation.py','-v'],cwd=ROOT,text=True,capture_output=True)
        self.assertEqual(run.returncode,0)
        lane=self.lane('aggregation-self',run.stdout+run.stderr,run.returncode,'OK')
        self.assertEqual(lane['tests'],14)
        self.assertEqual(summarize([lane])['exitCode'],0)

    def test_samples_are_not_tests(self):
        lane=self.lane('lifecycle-stress','{"samples": 100, "liveClients": 0, "liveTransports": 0}',0,'"samples": 100')
        self.assertEqual((lane['samples'],lane['tests']),(100,0))
        self.assertEqual(summarize([lane])['exitCode'],0)

    def test_player_validator_count_is_not_xctest_count(self):
        lane=self.lane('unity-pii-e2e','Unity PII current-run PASS: Android and iOS LOCAL_MOCK Players, 2 tests',0,'Unity PII current-run PASS:')
        self.assertEqual((lane['players'],lane['tests']),(2,0))
        self.assertEqual(summarize([lane])['exitCode'],0)

    def test_test_measurement_without_count_is_not_pass(self):
        lane=self.lane('aggregation-self','OK',0,'OK')
        self.assertEqual(summarize([lane])['exitCode'],1)

    def test_json_and_markdown_preserve_units(self):
        spec=importlib.util.spec_from_file_location('verify_all',ROOT/'harness/verify-all.py')
        module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
        lane=self.lane('lifecycle-stress','{"samples": 100, "liveClients": 0, "liveTransports": 0}',0,'"samples": 100')
        text=json.dumps(lane);self.assertEqual(json.loads(text)['tests'],0)
        self.assertIn('| 0 | 1 | 100 | 0 |',module.lane_row(lane))

if __name__=='__main__':unittest.main()
