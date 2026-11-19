import subprocess
import importlib.util
from pathlib import Path
import unittest
from unittest.mock import patch
import emulator_binding as m


class GuiAdbGuardTests(unittest.TestCase):
    def check(self, command, owners={42}, executable='/opt/unity/sdk/adb'):
        guard=m.GuiAdbGuard('/opt/unity/sdk/adb',42,'emulator-5590','GameBridge_V2_B29',43)
        result=subprocess.CompletedProcess([],0,stdout='n'+executable+'\n',stderr='')
        with patch.object(m,'inspect_binding') as binding,patch.object(m,'_port_owners',return_value=owners),patch.object(m.subprocess,'run',return_value=result):
            guard.attest(command)
            binding.assert_called_once_with('emulator-5590','GameBridge_V2_B29',43)

    def test_scoped_device_and_readonly_inventory_allowed(self):
        self.check(['/opt/unity/sdk/adb','-s','emulator-5590','shell','getprop','sys.boot_completed'])
        self.check(['/opt/unity/sdk/adb','devices'])

    def test_server_or_sdk_change_rejected(self):
        for owners,exe in [({99},'/opt/unity/sdk/adb'),({42},'/opt/other-sdk/adb')]:
            with self.assertRaises(m.BindingError):self.check(['/opt/unity/sdk/adb','devices'],owners,exe)

    def test_other_device_server_commands_and_other_client_rejected(self):
        for command in (['/opt/unity/sdk/adb','-s','emulator-5554','shell','getprop'],
                        ['/opt/unity/sdk/adb','kill-server'],['/opt/other-sdk/adb','devices']):
            with self.assertRaises(m.BindingError):self.check(command)

    def test_renamed_configured_client_still_dispatches_guard_before_subprocess(self):
        spec=importlib.util.spec_from_file_location('renamed_gui_client',Path(__file__).with_name('run-unity-android-mock-e2e.py'))
        module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
        class Guard:
            adb=Path('/tmp/renamed-client').resolve()
            def attest(self,command):raise module._binding.BindingError('wrong SDK')
        with patch.object(module,'_GUI_ADB_GUARD',Guard()),patch.object(module.subprocess,'run') as execute:
            with self.assertRaises(module.GateError):module.run(['/tmp/renamed-client','devices'])
            execute.assert_not_called()
