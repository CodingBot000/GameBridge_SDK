import importlib.util
import os
from pathlib import Path
import unittest
from unittest.mock import patch,Mock
spec=importlib.util.spec_from_file_location('r40_optin',Path(__file__).parent/'run-r40-permission-optin.py');module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
class R40OptinTests(unittest.TestCase):
    def test_missing_optin_defers_without_running(self):
        with patch.dict(os.environ,{},clear=True),patch.object(module.subprocess,'run') as run:
            self.assertEqual(module.main(),2);run.assert_not_called()
    def test_requires_all_three_and_stops_on_deferred(self):
        env={'GAMEBRIDGE_RUN_OS_PERMISSION_E2E':'true','GAMEBRIDGE_UPM_STAGING':'/stage','GAMEBRIDGE_UNITY_PACKAGE_CACHE':'/cache','GAMEBRIDGE_ANDROID_SERIAL':'emulator-1','GAMEBRIDGE_TEST_AVD_NAME':'GameBridge_V2_test','UNITY_EDITOR_PATH':'/editor'}
        with patch.dict(os.environ,env,clear=True),patch.object(module.subprocess,'run',side_effect=[Mock(returncode=0),Mock(returncode=2)]) as run:
            self.assertEqual(module.main(),2);self.assertEqual(run.call_count,2)
        with patch.dict(os.environ,env,clear=True),patch.object(module.subprocess,'run',side_effect=[Mock(returncode=0),Mock(returncode=0),Mock(returncode=0)]) as run:
            self.assertEqual(module.main(),0);self.assertEqual(run.call_count,3)
if __name__=='__main__':unittest.main()
