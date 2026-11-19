import importlib.util,subprocess,unittest
from pathlib import Path
from unittest.mock import patch
spec=importlib.util.spec_from_file_location('push_guard_timing',Path(__file__).with_name('run-unity-android-mock-push-e2e.py'));m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)

class PushTimingGuardTests(unittest.TestCase):
    def test_gui_commands_still_attest_before_subprocess_without_legacy_queries(self):
        class Guard:
            adb=Path('/unit/adb').resolve()
            def attest(self,command):raise m.common._binding.BindingError('server changed')
        with patch.object(m.common,'_GUI_ADB_GUARD',Guard()),patch.object(m,'inspect_binding') as legacy,patch.object(m.common,'require_dedicated_identity') as inventory,patch.object(m.common.subprocess,'run') as process:
            with self.assertRaises(m.common.GateError):m.guarded_call(['/unit/adb','-s','emulator-5596','logcat','-d'],'/unit/adb','emulator-5596','GameBridge_V2_unit',expected_pid=42)
            legacy.assert_not_called();inventory.assert_not_called();process.assert_not_called()
    def test_legacy_path_retains_its_pid_and_identity_proofs(self):
        with patch.object(m.common,'_GUI_ADB_GUARD',None),patch.object(m,'inspect_binding') as binding,patch.object(m.common,'require_dedicated_identity') as identity,patch.object(m.common,'run',return_value=subprocess.CompletedProcess([],0)):
            m.guarded_call(['/unit/adb','-s','emulator-5596','logcat','-d'],'/unit/adb','emulator-5596','GameBridge_V2_unit',expected_pid=42)
            binding.assert_called_once_with('emulator-5596','GameBridge_V2_unit',42);identity.assert_called_once()
    def test_first_observed_rejection_finishes_fault_wait_without_changing_upper_bound(self):
        class Proxy:rejected=0
        proxy=Proxy();clock=[0.0]
        def sleep(seconds):
            clock[0]+=seconds
            if clock[0]>=2:proxy.rejected=1
        self.assertTrue(m.wait_for_reconnect_failure(proxy,18,now=lambda:clock[0],sleep=sleep));self.assertLess(clock[0],3)
    def test_missing_failure_stops_at_the_original_18_second_bound(self):
        class Proxy:rejected=0
        clock=[0.0]
        self.assertFalse(m.wait_for_reconnect_failure(Proxy(),18,now=lambda:clock[0],sleep=lambda seconds:clock.__setitem__(0,clock[0]+seconds)));self.assertEqual(clock[0],18)
    def test_existing_rejection_needs_no_extra_sleep(self):
        class Proxy:rejected=1
        self.assertTrue(m.wait_for_reconnect_failure(Proxy(),18,now=lambda:0,sleep=lambda seconds:self.fail('unnecessary sleep')))
if __name__=='__main__':unittest.main()
