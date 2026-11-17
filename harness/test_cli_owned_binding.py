import argparse,contextlib,importlib.util,io,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
spec=importlib.util.spec_from_file_location('cli_owned_input',Path(__file__).with_name('run-unity-android-mock-e2e.py'));m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)

class CliOwnedBindingTests(unittest.TestCase):
    def args(self,**kw):return argparse.Namespace(**dict(dict(serial='emulator-5600',expected_avd='GameBridge_V2_unit',expected_emulator_pid=42,expected_adb_server_pid=43),**kw))
    def test_cli_and_gui_use_the_same_strong_binding_guard(self):
        for gui in (False,True):
            with patch.object(m._binding,'GuiAdbGuard',return_value='guard') as factory:
                self.assertEqual(m.owned_device_guard(self.args(),'/unity/adb',gui),'guard');factory.assert_called_once_with('/unity/adb',43,'emulator-5600','GameBridge_V2_unit',42)
    def test_partial_explicit_binding_is_rejected_and_legacy_ackless_path_remains(self):
        for key in ('serial','expected_avd','expected_emulator_pid','expected_adb_server_pid'):
            with self.assertRaises(m.GateError):m.owned_device_guard(self.args(**{key:None}),'/unity/adb')
        self.assertIsNone(m.owned_device_guard(self.args(expected_emulator_pid=None,expected_adb_server_pid=None),'/unity/adb'))
        with self.assertRaises(m.GateError):m.owned_device_guard(self.args(expected_emulator_pid=None,expected_adb_server_pid=None),'/unity/adb',True)
    def test_cli_notice_opt_in_is_accepted_only_with_all_scoping_before_missing_staging_defer(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);(root/'artifacts').mkdir()
            def must(cmd,*a,**kw):return 'head' if cmd[:3]==['git','rev-parse','HEAD'] else ''
            argv=['probe','--run-local','--staging',str(root/'absent'),'--serial','emulator-5600','--expected-avd','GameBridge_V2_unit','--expected-emulator-pid','42','--expected-adb-server-pid','43','--startup-diagnostics','--ack-known-fullscreen-notice']
            with patch.object(m,'ROOT',root),patch('sys.argv',argv),patch.object(m,'must',side_effect=must),patch.object(m,'locate_adb') as adb,contextlib.redirect_stdout(io.StringIO()):self.assertEqual(m.main(),2);adb.assert_not_called()
if __name__=='__main__':unittest.main()
