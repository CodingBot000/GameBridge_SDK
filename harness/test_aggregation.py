import unittest
from result_aggregator import summarize, runner_inconsistent

class AggregationTests(unittest.TestCase):
    def test_pass(self): self.assertEqual(summarize([{'name':'local','status':'PASS','required':True,'tests':1}])['exitCode'],0)
    def test_required_failure(self): self.assertEqual(summarize([{'name':'local','status':'FAIL','required':True,'tests':1}])['exitCode'],1)
    def test_required_skip(self): self.assertEqual(summarize([{'name':'local','status':'PASS','required':True,'tests':1,'skipped':1}])['exitCode'],2)
    def test_external_wait_does_not_claim_external_pass(self):
        lanes = [{'name':'local','status':'PASS','required':True,'tests':1},{'name':'external','status':'WAITING_USER','required':False,'tests':0}]
        self.assertEqual(summarize(lanes)['exitCode'],0); self.assertEqual(lanes[1]['status'],'WAITING_USER')
    def test_zero_tests_is_not_pass(self): self.assertEqual(summarize([{'name':'local','status':'PASS','required':True,'tests':0}])['exitCode'],1)
    def test_unimplemented_is_not_pass(self): self.assertEqual(summarize([{'name':'local','status':'NOT_IMPLEMENTED','required':True,'tests':0}])['exitCode'],1)
    def test_missing_required_is_not_pass(self): self.assertEqual(summarize([{'name':'local','status':'DEFERRED_ENV','required':True,'tests':0}])['exitCode'],2)
    def test_no_required_lane_is_not_pass(self): self.assertEqual(summarize([{'name':'external','status':'WAITING_USER','required':False,'tests':0}])['exitCode'],1)
    def test_pass_with_failed_exit_or_assertion_is_not_pass(self):
        self.assertEqual(summarize([{'name':'x','status':'PASS','required':True,'tests':1,'exitCode':1}])['exitCode'],1)
        self.assertEqual(summarize([{'name':'x','status':'PASS','required':True,'tests':1,'failures':1}])['exitCode'],1)
    def test_nested_runner_exit_must_match_report(self):
        self.assertTrue(runner_inconsistent(1, ['DEFERRED_ENV']))
        self.assertTrue(runner_inconsistent(-9, ['PASS']))
        self.assertFalse(runner_inconsistent(1, ['NOT_IMPLEMENTED']))
        self.assertFalse(runner_inconsistent(2, ['DEFERRED_ENV']))
    def test_duplicate_lane_is_not_pass(self): self.assertEqual(summarize([{'name':'x','status':'PASS','required':True,'tests':1}]*2)['exitCode'],1)

if __name__ == '__main__': unittest.main()
