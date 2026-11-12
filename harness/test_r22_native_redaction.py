import importlib.util
from pathlib import Path
import tempfile
import unittest
spec=importlib.util.spec_from_file_location("r22_native",Path(__file__).parent/"run-r22-native-redaction.py")
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
class RedactionMarkerTests(unittest.TestCase):
    def test_requires_exact_current_marker(self):
        with tempfile.TemporaryDirectory() as temp:
            path=Path(temp)/"marker"
            self.assertFalse(module.marker_pass(path))
            for value in ("", "FAIL\n", "PASS", "PASS\nextra\n"):
                path.write_text(value);self.assertFalse(module.marker_pass(path))
            path.write_text("PASS\n");self.assertTrue(module.marker_pass(path))
if __name__=="__main__":unittest.main()
