"""Reused emulator serials must not receive another test's device commands."""
import importlib.util
import unittest
from pathlib import Path
from unittest.mock import patch
spec=importlib.util.spec_from_file_location('push_guard',Path(__file__).with_name('run-unity-android-mock-push-e2e.py'))
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)

class DeviceCommandGuardTests(unittest.TestCase):
    def test_serial_identity_changes_between_commands(self):
        error=module.common.GateError('NOT_THE_DEDICATED_GAMEBRIDGE_AVD','DEFERRED_ENV')
        with patch.object(module.common,'require_dedicated_identity',side_effect=[('emulator-5680','GameBridge_V2_fixture'),error]),patch.object(module.common,'run') as run:
            module.guarded_call(['adb','-s','emulator-5680','logcat'],'adb','emulator-5680','GameBridge_V2_fixture')
            with self.assertRaises(module.common.GateError):
                module.guarded_call(['adb','-s','emulator-5680','shell','svc','wifi','disable'],'adb','emulator-5680','GameBridge_V2_fixture')
            self.assertEqual(run.call_count,1)

    def test_unscoped_command_and_foreign_avd_rejected(self):
        with patch.object(module.common,'run') as run:
            with self.assertRaises(module.common.GateError):module.guarded_call(['adb','shell','svc','wifi','enable'],'adb','emulator-5680','GameBridge_V2_fixture')
            run.assert_not_called()
        responses=['List of devices attached\nemulator-5680\tdevice\n','Personal_AVD\nOK\n']
        with patch.object(module.common,'must',side_effect=responses):
            with self.assertRaises(module.common.GateError):module.common.require_dedicated_identity('adb','emulator-5680','GameBridge_V2_fixture')

if __name__=='__main__':unittest.main()
