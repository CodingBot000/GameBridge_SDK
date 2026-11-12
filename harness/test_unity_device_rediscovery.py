import importlib.util
from pathlib import Path
import unittest
from unittest.mock import patch

SPEC = importlib.util.spec_from_file_location("unity_e2e", Path(__file__).parent / "run-unity-android-mock-e2e.py")
module = importlib.util.module_from_spec(SPEC); SPEC.loader.exec_module(module)

class DeviceRediscoveryTests(unittest.TestCase):
    def test_waits_for_offline_device_then_revalidates(self):
        with patch.object(module, "find_dedicated_device", side_effect=[module.GateError("TARGET_NOT_AN_ONLINE_EMULATOR", "DEFERRED_ENV"), ("emulator-5584", "GameBridge_V2_test")]) as probe, patch.object(module.time, "sleep"):
            self.assertEqual(module.wait_for_dedicated_device("adb", "emulator-5584", "GameBridge_V2_test"), ("emulator-5584", "GameBridge_V2_test"))
            self.assertEqual(probe.call_count, 2)
    def test_does_not_retry_wrong_device_or_existing_app(self):
        for code in ("NOT_THE_DEDICATED_GAMEBRIDGE_AVD", "TEST_APP_ALREADY_INSTALLED_PRESERVE_EXISTING"):
            with patch.object(module, "find_dedicated_device", side_effect=module.GateError(code, "DEFERRED_ENV")) as probe:
                with self.assertRaises(module.GateError): module.wait_for_dedicated_device("adb", "emulator-5584", "GameBridge_V2_test")
                self.assertEqual(probe.call_count, 1)
