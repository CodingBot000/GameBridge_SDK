import importlib.util
import os
from pathlib import Path
import unittest
from unittest.mock import patch,Mock
spec=importlib.util.spec_from_file_location('pii_optin',Path(__file__).parent/'run-unity-pii-optin.py');module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
class PiiOptinTests(unittest.TestCase):
    def test_missing_optin_and_environment_defer(self):
        with patch.dict(os.environ,{},clear=True), patch.object(module.subprocess,'run') as run:
            self.assertEqual(module.main(),2);run.assert_not_called()
    def test_runs_fresh_nonce_and_propagates_result(self):
        env={'GAMEBRIDGE_RUN_UNITY_PII_E2E':'true','GAMEBRIDGE_UPM_STAGING':'/stage','GAMEBRIDGE_ANDROID_SERIAL':'emulator-1','GAMEBRIDGE_TEST_AVD_NAME':'GameBridge_V2_test','GAMEBRIDGE_UNITY_PACKAGE_CACHE':'/cache'}
        with patch.dict(os.environ,env,clear=True),patch.object(module.secrets,'token_hex',return_value='a'*32),patch.object(module.subprocess,'run',return_value=Mock(returncode=1)) as run:
            self.assertEqual(module.main(),1);command=run.call_args.args[0]
            self.assertIn('--run-local',command);self.assertIn('--nonce',command);self.assertIn('a'*32,command)
if __name__=='__main__':unittest.main()
