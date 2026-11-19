import importlib.util
from pathlib import Path
import subprocess
import sys
import unittest
spec=importlib.util.spec_from_file_location('ios_permission',Path(__file__).parent/'run-unity-ios-permission-os.py');module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
class IosPermissionOsTests(unittest.TestCase):
    def test_all_os_markers_required(self):
        self.assertTrue(module.markers_pass('\n'.join(module.REQUIRED)))
        for marker in module.REQUIRED:self.assertFalse(module.markers_pass('\n'.join(x for x in module.REQUIRED if x!=marker)))
    def test_explicit_optin_required(self):
        result=subprocess.run([sys.executable,str(Path(__file__).parent/'run-unity-ios-permission-os.py')],capture_output=True,text=True)
        self.assertEqual(result.returncode,2)
if __name__=='__main__':unittest.main()
