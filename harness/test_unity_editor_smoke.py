import unittest

from unity_editor_smoke import evaluate, observations


class EditorSmokeContractTests(unittest.TestCase):
    run_id = 'test-invocation'
    version = '6000.5.8f1'

    def receipt(self):
        return dict(status='PASS', runId=self.run_id, unityVersion=self.version, batchMode=True)

    def marker(self):
        return 'GB_EDITOR_SMOKE PASS ' + self.run_id

    def test_active_or_initialized_license_is_not_a_method_verdict(self):
        for code in (0, 6, 124):
            self.assertEqual(evaluate(code, 'license active; Licensing is initialized', None,
                                      self.run_id, self.version)['status'], 'DEFERRED_ENV')

    def test_only_correlated_completed_method_can_pass(self):
        result = evaluate(0, self.marker(), self.receipt(), self.run_id, self.version)
        self.assertEqual(result['status'], 'PASS')
        self.assertEqual((result['tests'], result['checks'], result['players']), (0, 1, 0))

    def test_partial_output_or_nonzero_exit_cannot_override_failure(self):
        self.assertEqual(evaluate(6, self.marker(), self.receipt(), self.run_id, self.version)['status'], 'FAIL')
        self.assertEqual(evaluate(0, self.marker(), self.receipt(), self.run_id, self.version, True)['status'], 'DEFERRED_ENV')

    def test_foreign_or_duplicate_evidence_is_rejected(self):
        for key, value in (('runId', 'previous'), ('unityVersion', 'other'), ('batchMode', 1)):
            receipt = self.receipt(); receipt[key] = value
            self.assertEqual(evaluate(0, self.marker(), receipt, self.run_id, self.version)['status'], 'FAIL')
        self.assertEqual(evaluate(0, self.marker()+'\n'+self.marker(), self.receipt(), self.run_id, self.version)['status'], 'FAIL')

    def test_compile_error_is_not_environment_pending(self):
        self.assertEqual(evaluate(1, 'error CS1002: expected ;', None, self.run_id, self.version)['reason'], 'EDITOR_COMPILE_FAILURE')

    def test_observation_export_contains_no_log_payload_or_identity(self):
        value = observations("Channel LicenseClient-person doesn't exist\nTimed-out after 60.00s",
                             "secret arbitrary-person@example.invalid\nFailed to acquire global mutex\nUnsupported protocol version '1.19.0-rc.3'")
        self.assertEqual(value['missingChannel'], 1)
        self.assertEqual(value['clientMutexFailures'], 1)
        self.assertEqual(value['unsupportedProtocols'], ['1.19.0-rc.3'])
        self.assertNotIn('person', str(value))
        self.assertNotIn('secret', str(value))
