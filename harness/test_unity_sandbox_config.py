import importlib.util
from pathlib import Path
import subprocess
import sys
import unittest
spec=importlib.util.spec_from_file_location('sandbox_config',Path(__file__).parent/'run-unity-sandbox-config.py');module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
class SandboxConfigRunnerTests(unittest.TestCase):
    def test_requires_each_platform_specific_marker(self):
        base='GB_SANDBOX_CONFIG_CAPABILITIES PASS\nGB_SANDBOX_CONFIG_NO_FALLBACK PASS\n'
        self.assertTrue(module.markers_pass(base+'GB_SANDBOX_CONFIG_RESULT PASS ANDROID','android'))
        self.assertFalse(module.markers_pass(base+'GB_SANDBOX_CONFIG_RESULT PASS ANDROID','ios'))
        self.assertFalse(module.markers_pass('GB_SANDBOX_CONFIG_RESULT PASS IOS','ios'))
    def test_explicit_optin_required(self):
        result=subprocess.run([sys.executable,str(Path(__file__).parent/'run-unity-sandbox-config.py')],capture_output=True,text=True)
        self.assertEqual(result.returncode,2)
if __name__=='__main__':unittest.main()
