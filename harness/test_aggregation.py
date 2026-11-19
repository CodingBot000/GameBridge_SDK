import unittest
import importlib.util
import tempfile
from pathlib import Path
from result_aggregator import summarize, runner_inconsistent

class AggregationTests(unittest.TestCase):
    def setUp(self):
        from measurement_contract import record_execution, counted_lane
        temp=tempfile.TemporaryDirectory();self.addCleanup(temp.cleanup)
        log=Path(temp.name)/'observed.log';log.write_text('fixture PASS')
        record_execution(['fixture'],0,'fixture PASS',log)
        self.base=counted_lane('fixture',0,(1,0,0),0,'separate')

    def lane(self, values):
        return {**self.base,**values}


    def test_pass(self):
        self.assertEqual(summarize([self.lane({'name': 'local', 'status': 'PASS', 'required': True, 'tests': 1, 'errors': 0})])['exitCode'], 0)

    def test_required_failure(self):
        self.assertEqual(summarize([self.lane({'name': 'local', 'status': 'FAIL', 'required': True, 'tests': 1, 'errors': 0})])['exitCode'], 1)

    def test_required_skip(self):
        self.assertEqual(summarize([self.lane({'name': 'local', 'status': 'PASS', 'required': True, 'tests': 1, 'errors': 0, 'skipped': 1})])['exitCode'], 2)

    def test_external_wait_does_not_claim_external_pass(self):
        lanes = [self.lane({'name': 'local', 'status': 'PASS', 'required': True, 'tests': 1, 'errors': 0}), self.lane({'name': 'external', 'status': 'WAITING_USER', 'required': False, 'tests': 0})]
        self.assertEqual(summarize(lanes)['exitCode'], 0)
        self.assertEqual(lanes[1]['status'], 'WAITING_USER')

    def test_zero_tests_is_not_pass(self):
        self.assertEqual(summarize([self.lane({'name': 'local', 'status': 'PASS', 'required': True, 'tests': 0})])['exitCode'], 1)

    def test_partial_is_not_pass(self):
        self.assertEqual(summarize([self.lane({'name': 'local', 'status': 'PARTIAL', 'required': True, 'tests': 0})])['exitCode'], 1)

    def test_unimplemented_is_not_pass(self):
        self.assertEqual(summarize([self.lane({'name': 'local', 'status': 'NOT_IMPLEMENTED', 'required': True, 'tests': 0})])['exitCode'], 1)

    def test_missing_required_is_not_pass(self):
        self.assertEqual(summarize([self.lane({'name': 'local', 'status': 'DEFERRED_ENV', 'required': True, 'tests': 0, 'exitCode':2})])['exitCode'], 2)

    def test_specific_missing_required_suite_is_not_pass(self):
        lanes = [self.lane({'name': 'present', 'status': 'PASS', 'required': True, 'tests': 1, 'errors': 0})]
        self.assertEqual(summarize(lanes, {'present', 'omitted'})['exitCode'], 1)
        self.assertEqual(summarize(lanes, {'present'})['exitCode'], 0)

    def test_no_required_lane_is_not_pass(self):
        self.assertEqual(summarize([self.lane({'name': 'external', 'status': 'WAITING_USER', 'required': False, 'tests': 0})])['exitCode'], 1)

    def test_pass_with_failed_exit_or_assertion_is_not_pass(self):
        self.assertEqual(summarize([self.lane({'name': 'x', 'status': 'PASS', 'required': True, 'tests': 1, 'errors': 0, 'exitCode': 1})])['exitCode'], 1)
        self.assertEqual(summarize([self.lane({'name': 'x', 'status': 'PASS', 'required': True, 'tests': 1, 'errors': 0, 'failures': 1})])['exitCode'], 1)

    def test_nested_runner_exit_must_match_report(self):
        self.assertTrue(runner_inconsistent(1, ['DEFERRED_ENV']))
        self.assertTrue(runner_inconsistent(-9, ['PASS']))
        self.assertFalse(runner_inconsistent(1, ['NOT_IMPLEMENTED']))
        self.assertFalse(runner_inconsistent(1, ['PARTIAL']))
        self.assertFalse(runner_inconsistent(2, ['DEFERRED_ENV']))

    def test_duplicate_lane_is_not_pass(self):
        self.assertEqual(summarize([self.lane({'name': 'x', 'status': 'PASS', 'required': True, 'tests': 1, 'errors': 0})] * 2)['exitCode'], 1)

class StaticMappingTests(unittest.TestCase):
    def test_static_checker_does_not_claim_execution(self):
        spec = importlib.util.spec_from_file_location('verify_all', Path(__file__).with_name('verify-all.py'))
        module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
        from execution_evidence import ROOT
        (ROOT/'artifacts').mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(dir=ROOT/'artifacts') as folder:
            root = Path(folder); (root/'checker.log').write_text('executed')
            from measurement_contract import measured_lane
            checker = measured_lane('manifest',['fixture'],0,'executed',root/'checker.log','executed')
            checker['evidence']=(root/'checker.log').relative_to(ROOT).as_posix()
            manifest = {'scenarios':[{'id':f'R{i:02}', 'required':True, 'coverage':'IMPLEMENTED'} for i in range(1,51)]}
            lane = module.scenario_mapping_lane(manifest, checker, ROOT)
            self.assertEqual((lane['status'],lane['tests'],lane['checks'],lane['mappedScenarios'],lane['executionStatus']), ('PASS',0,1,50,'NOT_RUN'))
            self.assertEqual(summarize([lane])['exitCode'],0)
            self.assertNotEqual(summarize([{**lane,'tests':50}])['exitCode'],0)
            self.assertNotEqual(summarize([{**lane,'evidence':''}])['exitCode'],0)
            self.assertNotEqual(module.scenario_mapping_lane(manifest, {**checker,'evidence':'missing.log'}, ROOT)['status'],'PASS')
            self.assertNotEqual(module.scenario_mapping_lane(manifest, None, ROOT)['status'],'PASS')
            self.assertNotEqual(module.scenario_mapping_lane(manifest, {**checker,'status':'FAIL'}, ROOT)['status'],'PASS')
            manifest['scenarios'][0]['coverage']='PARTIAL'
            self.assertEqual(module.scenario_mapping_lane(manifest, checker, ROOT)['status'],'PARTIAL')

if __name__ == '__main__': unittest.main()
