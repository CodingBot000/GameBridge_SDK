import copy
import unittest
from gui_verification import validate_probe


class GuiProbeReceiptTests(unittest.TestCase):
    def fixtures(self):
        config = dict(runId='a'*32, sourceHead='b'*40, scriptSha256='c'*64,
                      expectedUnityVersion='6000.5.8f1', projectRoot='/tmp/gamebridge-gui-owned/project')
        value = dict(config, schemaVersion=1, status='PASS', operation='probe', isBatchMode=False,
                     unityVersion='6000.5.8f1', method='GameBridgeGuiVerification.RunProbe',
                     assemblyName='Assembly-CSharp-Editor', editorPid=123, engineObjectId=-42,
                     checksExecuted=7, engineObjectCreated=True, engineObjectDestroyed=True,
                     startedUtc='2026-11-17T10:00:00Z', finishedUtc='2026-11-17T10:00:01Z')
        return value, config

    def test_complete_receipt_is_gui_only(self):
        value, config = self.fixtures(); result = validate_probe(value, config)
        self.assertEqual((result['tests'], result['checks'], result['players']), (0, 1, 0))
        self.assertEqual(result['batchAutomation'], 'NOT_RUN')

    def test_pass_text_without_runtime_proof_rejected(self):
        value, config = self.fixtures()
        for key in ('method', 'assemblyName', 'engineObjectId', 'engineObjectDestroyed'):
            changed = copy.deepcopy(value); changed.pop(key)
            with self.assertRaises(ValueError): validate_probe(changed, config)

    def test_stale_nonce_source_and_script_rejected(self):
        value, config = self.fixtures()
        for key in ('runId', 'sourceHead', 'scriptSha256'):
            changed = copy.deepcopy(value); changed[key] = 'stale'
            with self.assertRaises(ValueError): validate_probe(changed, config)

    def test_other_project_version_or_batch_mode_rejected(self):
        value, config = self.fixtures()
        for key, replacement in (('projectRoot', '/tmp/other-project'), ('unityVersion', 'other'), ('isBatchMode', True)):
            changed = copy.deepcopy(value); changed[key] = replacement
            with self.assertRaises(ValueError): validate_probe(changed, config)

    def test_partial_failed_and_bad_timestamp_rejected(self):
        value, config = self.fixtures()
        for key, replacement in (('status', 'FAIL'), ('checksExecuted', 6), ('editorPid', True), ('finishedUtc', '2026-11-16T00:00:00Z')):
            changed = copy.deepcopy(value); changed[key] = replacement
            with self.assertRaises(ValueError): validate_probe(changed, config)
