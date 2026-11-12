"""Bounded strict orchestration allows explicitly opted-in Player runs to finish."""
import importlib.util
from pathlib import Path
import unittest
spec=importlib.util.spec_from_file_location('strict_isolated',Path(__file__).parent/'run-strict-local-isolated.py')
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
class StrictTimeoutTests(unittest.TestCase):
    def test_only_explicit_unity_push_opt_in_extends_outer_limit(self):
        self.assertEqual(module.strict_timeout({}),900)
        self.assertEqual(module.strict_timeout({'GAMEBRIDGE_RUN_UNITY_PUSH_E2E':'false'}),900)
        self.assertEqual(module.strict_timeout({'GAMEBRIDGE_RUN_UNITY_PUSH_E2E':'true'}),5400)
if __name__=='__main__':unittest.main()
