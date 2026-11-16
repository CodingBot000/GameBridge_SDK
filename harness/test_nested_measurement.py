"""Producer and parent unit contracts; external runtime execution is explicit elsewhere."""
import importlib.util
import tempfile
import unittest
from pathlib import Path
from measurement_contract import record_execution, counted_lane
from result_aggregator import summarize


def load(name):
    spec=importlib.util.spec_from_file_location(name,Path(__file__).with_name(name))
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module


class NestedMeasurementTests(unittest.TestCase):
    def setUp(self):
        temp=tempfile.TemporaryDirectory();self.addCleanup(temp.cleanup)
        self.log=Path(temp.name)/'run.log';self.log.write_text('fixture PASS')
        record_execution(['fixture'],0,'fixture PASS',self.log)

    def test_parent_preserves_every_measured_field(self):
        parent=load('verify-all.py')
        for unit,count in [('tests',7),('checker',1),('players',2),('samples',100)]:
            child=counted_lane('child',0,(count,0,0),0,'separate',unit)
            lane=parent.nested_lane('producer',child,['producer'],'result.json')
            for key in ('tests','checks','samples','players','failures','errors','skipped','exitCode','errorModel','measurement','checkerEvidence'):
                self.assertEqual(lane[key],child[key])
            self.assertEqual(summarize([lane])['exitCode'],0)
            if unit!='tests':self.assertEqual(lane['tests'],0)

    def test_missing_fields_are_not_filled_with_measured_zero(self):
        lane=load('verify-all.py').nested_lane('p',{'suite':'absent','status':'PASS'},['p'],'result.json')
        for key in ('tests','checks','failures','errors','skipped','measurement'):
            self.assertNotIn(key,lane)
        self.assertEqual(summarize([lane])['exitCode'],1)

    def test_self_check_has_no_checks_to_tests_compatibility(self):
        lane={'name':'checker','status':'PASS','required':True,'tests':0,'checks':1,'skipped':0,'exitCode':0}
        self.assertEqual(load('run-self-check.py').summarize_lanes([lane],{'checker'})['exitCode'],1)

    def test_marker_and_player_producers_do_not_claim_tests(self):
        common=load('run-auth-regression.py')
        checker=common.item('packaging',0,(1,0,0),error_model='checker-exit')
        players=common.item('players',0,(2,0,0),error_model='checker-exit',measurement='players')
        self.assertEqual((checker['tests'],checker['checks']),(0,1))
        self.assertEqual((players['tests'],players['players']),(0,2))

if __name__=='__main__':unittest.main()
