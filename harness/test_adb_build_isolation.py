import subprocess,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
import adb_build_isolation as m

class BuildAdbIsolationTests(unittest.TestCase):
    def test_runtime_port_invalid_ports_and_existing_owners_are_never_started_or_replaced(self):
        with tempfile.TemporaryDirectory() as tmp,patch.object(m.subprocess,'Popen') as start:
            for port in (5037,0,65536,True):
                with self.assertRaises(m.BindingError):
                    with m.isolated_build_endpoint('/sdk/adb',port,Path(tmp),{}):pass
            with patch.object(m,'_port_owners',return_value={99}),self.assertRaises(m.BindingError):
                with m.isolated_build_endpoint('/sdk/adb',5038,Path(tmp),{}):pass
            start.assert_not_called()
    def run_context(self,builder_kills=False):
        class Process:
            pid=77
            stopped=False
            def poll(self):return 0 if self.stopped else None
            def terminate(self):self.stopped=True
            def wait(self,timeout):return 0
        proc=Process();base={'UNCHANGED':'true'}
        with tempfile.TemporaryDirectory() as tmp,patch.object(m,'_port_owners',side_effect=[set(),{77},{77}]),patch.object(m.subprocess,'Popen',return_value=proc) as start,patch.object(m.subprocess,'run',return_value=subprocess.CompletedProcess([],0,stdout='n'+str(Path('/sdk/adb').resolve())+'\n')):
            with m.isolated_build_endpoint('/sdk/adb',5038,Path(tmp),base) as env:
                self.assertEqual(env['ADB_SERVER_SOCKET'],'tcp:5038');self.assertEqual(env['ANDROID_ADB_SERVER_PORT'],'5038');self.assertEqual(base,{'UNCHANGED':'true'})
                self.assertTrue((Path(tmp)/'build-adb-binding.json').is_file())
                if builder_kills:proc.stopped=True
            self.assertTrue(proc.stopped);self.assertEqual(start.call_args.args[0],[str(Path('/sdk/adb').resolve()),'-L','tcp:5038','server','nodaemon']);self.assertNotIn('kill-server',start.call_args.args[0])
    def test_only_owned_foreground_process_is_cleaned_and_environment_is_build_only(self):self.run_context()
    def test_builder_stopping_its_own_endpoint_is_handled_without_global_kill(self):self.run_context(True)
    def test_wrong_executable_fails_and_terminates_only_the_created_process(self):
        class Process:
            pid=77
            stopped=False
            def poll(self):return 0 if self.stopped else None
            def terminate(self):self.stopped=True
            def wait(self,timeout):return 0
        proc=Process()
        with tempfile.TemporaryDirectory() as tmp,patch.object(m,'_port_owners',side_effect=[set(),{77},{77}]),patch.object(m.subprocess,'Popen',return_value=proc),patch.object(m.subprocess,'run',return_value=subprocess.CompletedProcess([],0,stdout='n/other/adb\n')),self.assertRaises(m.BindingError):
            with m.isolated_build_endpoint('/sdk/adb',5038,Path(tmp),{}):pass
        self.assertTrue(proc.stopped)
if __name__=='__main__':unittest.main()
