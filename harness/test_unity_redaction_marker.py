import importlib.util
from pathlib import Path
import unittest
from unittest.mock import patch
spec=importlib.util.spec_from_file_location("android_e2e",Path(__file__).parent/"run-unity-android-mock-e2e.py")
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
class UnityRedactionMarkerTests(unittest.TestCase):
    def test_pending_waits_and_completed_without_redaction_fails(self):
        self.assertFalse(module.check_player_markers(["GB_MOCK_STEP initialize PASS"]))
        with self.assertRaisesRegex(module.GateError,"UNITY_RESULT_REDACTION_MISSING"):
            module.check_player_markers(["GB_MOCK_RESULT PASS LOCAL_MOCK"])
    def test_shared_runner_consumers_have_redaction_probe(self):
        root=Path(__file__).resolve().parent.parent
        for name in ("UnityAndroidMockConsumer/MockPlayerScenario.cs", "UnityAndroidUtf8Consumer/MockPlayerScenario.cs",
                     "UnityIosMockConsumer/MockIosPlayerScenario.cs", "UnityIosHostCallbackConsumer/MockIosPlayerScenario.cs"):
            source=(root/"tests"/name).read_text()
            for assertion in ("RejectSecret(profile, syntheticKey)", "RejectSecret(purchase, syntheticKey)",
                              "RejectSecret(events, syntheticKey)", "GB_MOCK_REDACTION PASS"):
                with self.subTest(consumer=name, assertion=assertion): self.assertIn(assertion,source)
    def test_log_filter_keeps_native_demo_marker(self):
        with patch.object(module,"must",return_value="I/Unity: GB_NATIVE_DEMO_FLOW PASS\n"):
            self.assertEqual(len(module.scan_unity_log("adb","serial","synthetic-key","synthetic-password")),1)
    def test_synthetic_pii_in_raw_unity_log_is_rejected_when_enabled(self):
        with patch.object(module,"must",return_value="I/Unity: synthetic-person@example.invalid\n"):
            with self.assertRaisesRegex(module.GateError,"SYNTHETIC_SECRET_IN_PLAYER_LOG"):
                module.scan_unity_log("adb","serial","synthetic-key","synthetic-password",True)
    def test_mock_credential_in_raw_unity_log_is_rejected(self):
        with patch.object(module,"must",return_value="I/Unity: mock:00000000-0000-4000-8000-000000000001\n"):
            with self.assertRaisesRegex(module.GateError,"SYNTHETIC_SECRET_IN_PLAYER_LOG"):
                module.scan_unity_log("adb","serial","synthetic-key","synthetic-password")
    def test_log_filter_keeps_redaction_marker(self):
        with patch.object(module,"must",return_value="I/Unity: GB_MOCK_REDACTION PASS\n"):
            self.assertEqual(len(module.scan_unity_log("adb","serial","synthetic-key","synthetic-password")),1)
if __name__=="__main__":unittest.main()
