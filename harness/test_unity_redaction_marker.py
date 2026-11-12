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
    def test_log_filter_keeps_redaction_marker(self):
        with patch.object(module,"must",return_value="I/Unity: GB_MOCK_REDACTION PASS\n"):
            self.assertEqual(len(module.scan_unity_log("adb","serial","synthetic-key","synthetic-password")),1)
if __name__=="__main__":unittest.main()
