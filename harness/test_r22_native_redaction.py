import importlib.util
from pathlib import Path
import tempfile
import unittest
spec=importlib.util.spec_from_file_location("r22_native",Path(__file__).parent/"run-r22-native-redaction.py")
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
class RedactionMarkerTests(unittest.TestCase):
    def test_mock_credential_pattern_is_detected_without_exposing_values(self):
        self.assertTrue(module.has_mock_credential("mock:00000000-0000-4000-8000-000000000001"))
        self.assertFalse(module.has_mock_credential("MOCK provider and ordinary message"))
    def test_environment_deferral_is_not_reported_as_success(self):
        class Deferred(Exception): category="DEFERRED_ENV"
        self.assertEqual(module.error_status(Deferred()),"DEFERRED_ENV")
        self.assertEqual(module.error_status(RuntimeError()),"FAIL")
    def test_requires_exact_current_marker(self):
        with tempfile.TemporaryDirectory() as temp:
            path=Path(temp)/"marker"
            self.assertFalse(module.marker_pass(path))
            for value in ("", "FAIL\n", "PASS", "PASS\nextra\n"):
                path.write_text(value);self.assertFalse(module.marker_pass(path))
            path.write_text("PASS\n");self.assertTrue(module.marker_pass(path))
if __name__=="__main__":unittest.main()
