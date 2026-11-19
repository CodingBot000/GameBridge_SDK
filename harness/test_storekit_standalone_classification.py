"""Ensure app exit cannot be misreported as StoreKit initialization timeout."""
import importlib.util
import unittest
from pathlib import Path

spec=importlib.util.spec_from_file_location('standalone',Path(__file__).with_name('run-storekit-standalone.py'))
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)


class StoreKitStandaloneClassificationTests(unittest.TestCase):
    def test_terminal_phases(self):
        before=['started','session-create-before']
        self.assertEqual(module.classify(before+['session-create-after'],False,False),('PASS','session-create-after',0))
        self.assertEqual(module.classify(before+['session-create-error'],False,False),('FAIL','session-create-error',1))
        self.assertEqual(module.classify(before,True,False),('FAIL','app-exited-during-session-create',1))
        self.assertEqual(module.classify(before,False,True),('FAIL','session-create-timeout',1))
        self.assertEqual(module.classify(before,False,False),('DEFERRED_ENV','session-create-result-unknown',2))
        self.assertEqual(module.classify(['started'],True,False),('DEFERRED_ENV','app-start-or-configuration',2))
        self.assertEqual(module.classify(['started','configuration-missing'],False,False),('FAIL','configuration-missing',1))


if __name__ == '__main__': unittest.main()
