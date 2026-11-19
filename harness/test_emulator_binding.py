"""PID reuse and console collisions must stop before device commands."""
import importlib.util
import unittest
from pathlib import Path
from unittest.mock import patch
import emulator_binding as binding

class EmulatorBindingTests(unittest.TestCase):
    def check(self,argv=None,ports=None,pid='123'):
        args=argv or ['qemu-system-aarch64','-avd','GameBridge_V2_fixture','-port','5582']
        with patch.object(binding,'_process_arguments',return_value=args),patch.object(binding,'_port_owners',side_effect=ports or [{123},{123}]):
            return binding.inspect_binding('emulator-5582','GameBridge_V2_fixture',pid)
    def test_expected_process_owns_both_ports(self):
        self.assertEqual(self.check(),{'pid':123,'serial':'emulator-5582','avd':'GameBridge_V2_fixture','consolePort':5582,'adbPort':5583,'portsOwned':True})
    def test_collision_missing_half_or_multiple_owners_rejected(self):
        for ports in ([{999},{123}],[{123},set()],[{123,999},{123}]):
            with self.assertRaises(binding.BindingError):self.check(ports=ports)
    def test_reused_pid_or_different_requested_port_rejected(self):
        for args in (['qemu-system','-avd','foreign','-port','5582'],['qemu-system','-avd','GameBridge_V2_fixture','-port','5570']):
            with self.assertRaises(binding.BindingError):self.check(argv=args)
    def test_invalid_identity_does_not_query_process(self):
        for pid in ('',False,'0','-1'):
            with patch.object(binding,'_process_arguments') as read:
                with self.assertRaises(binding.BindingError):binding.inspect_binding('emulator-5582','GameBridge_V2_fixture',pid)
                read.assert_not_called()
    def test_mismatched_binding_prevents_mutation(self):
        spec=importlib.util.spec_from_file_location('push',Path(__file__).with_name('run-unity-android-mock-push-e2e.py'))
        module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
        with patch.object(module,'inspect_binding',side_effect=binding.BindingError('EMULATOR_PORT_OWNER_MISMATCH')),patch.object(module.common,'run') as run,patch.object(module.common,'require_dedicated_identity') as adb:
            with self.assertRaises(module.common.GateError):module.guarded_call(['adb','-s','emulator-5582','shell','svc','wifi','disable'],'adb','emulator-5582','GameBridge_V2_fixture',expected_pid=123)
            run.assert_not_called();adb.assert_not_called()

if __name__=='__main__':unittest.main()
