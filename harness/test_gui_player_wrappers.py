import argparse, contextlib, importlib.util, io, json, subprocess, tempfile, unittest
from pathlib import Path
from unittest.mock import patch
ROOT=Path(__file__).resolve().parent.parent

def module(name):
    spec=importlib.util.spec_from_file_location(name,ROOT/'harness'/('run-'+name+'.py'));m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m

def arguments(**kw):
    return argparse.Namespace(**dict(dict(gui_project=None,gui_build_receipt=None,expected_emulator_pid=None,expected_adb_server_pid=None,adb=None,startup_diagnostics=False,platform='both'),**kw))

class GuiPlayerWrapperTests(unittest.TestCase):
    def test_r09_gui_requires_utf8_and_exact_owned_binding_no_batch_fallback(self):
        m=module('r09-utf8');a=arguments(gui_project=Path('/owned/project'),gui_build_receipt=Path('/owned/receipt'),expected_emulator_pid=42,expected_adb_server_pid=43,adb='/unity/adb',startup_diagnostics=True)
        cmd=m.android_command(a,'/stage','emulator-5596','GameBridge_V2_fixture','/cache')
        for flag,value in [('--gui-project','/owned/project'),('--gui-build-receipt','/owned/receipt'),('--expected-emulator-pid','42'),('--expected-adb-server-pid','43'),('--adb','/unity/adb')]:self.assertEqual(cmd[cmd.index(flag)+1],value)
        self.assertIn('--utf8-probe',cmd);self.assertIn('--startup-diagnostics',cmd);self.assertNotIn('--package-cache',cmd);self.assertNotIn('--ack-known-fullscreen-notice',cmd)
        legacy=m.android_command(arguments(),'/stage','emulator-5596','GameBridge_V2_fixture','/cache');self.assertIn('--package-cache',legacy);self.assertNotIn('--gui-project',legacy)

    def test_r09_missing_pair_binding_or_fresh_identity_rejected(self):
        m=module('r09-utf8')
        for a in (arguments(gui_project=Path('/owned')),arguments(gui_build_receipt=Path('/receipt')),arguments(gui_project=Path('/owned'),gui_build_receipt=Path('/receipt'))):
            with self.assertRaises(ValueError):m.android_command(a,'/stage','emulator-5596','GameBridge_V2_fixture',None)
        with self.assertRaises(ValueError):m.android_command(arguments(),'/stage','emulator-5596','personal',None)

    def test_r09_android_requires_current_clean_utf8_player_and_marker(self):
        m=module('r09-utf8')
        with tempfile.TemporaryDirectory() as tmp,patch.object(m,'ROOT',Path(tmp)),patch.object(m.consumer,'ROOT',Path(tmp)):
            root=Path(tmp);out=root/'artifacts/r09';out.mkdir(parents=True);child=root/'artifacts/unity-android-e2e-fixture';child.mkdir();markers=child/'unity-test-markers.log'
            text='RESULT PASS EVIDENCE artifacts/unity-android-e2e-fixture\n';value=dict(status='PASS',unityPlayer='PASS',sourceHead='head',sourceTrackedDirty=False,ledgerCount=1,ledgerDelta=100,utf8Probe=True)
            def execute(data,marker='GB_UTF8_JNI_ROUNDTRIP PASS'):
                (child/'result.json').write_text(json.dumps(data));markers.write_text(marker)
                with patch.object(m.subprocess,'run',return_value=subprocess.CompletedProcess([],0,stdout=text)),contextlib.redirect_stdout(io.StringIO()):return m.run_android([], 'head',out)
            self.assertEqual(execute(value)['status'],'PASS')
            for key,val in [('sourceHead','stale'),('sourceTrackedDirty',True),('utf8Probe',False),('ledgerDelta',0),('unityPlayer','NOT_RUN')]:self.assertEqual(execute(dict(value,**{key:val}))['status'],'FAIL')
            self.assertEqual(execute(value,'GB_MOCK_RESULT PASS LOCAL_MOCK')['status'],'FAIL')
            for invalid in ([],None,dict(value,ledgerCount=True),dict(value,ledgerDelta=True)):self.assertEqual(execute(invalid)['status'],'FAIL')

    def test_r09_platform_results_independent_after_android_failure(self):
        m=module('r09-utf8')
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);(root/'artifacts').mkdir()
            env={'GAMEBRIDGE_RUN_R09':'true','GAMEBRIDGE_UPM_STAGING':'/stage','GAMEBRIDGE_ANDROID_SERIAL':'emulator-5596','GAMEBRIDGE_TEST_AVD_NAME':'GameBridge_V2_unit'}
            with patch.object(m,'ROOT',root),patch.dict(m.os.environ,env),patch('sys.argv',['r09']),patch.object(m.subprocess,'check_output',return_value='head\n'),patch.object(m,'run_android',return_value=dict(status='FAIL',exitCode=1,errorCode='marker')) as android,patch.object(m,'run_ios',return_value=dict(status='PASS',exitCode=0,tests=1)) as ios,contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(m.main(),1);android.assert_called_once();ios.assert_called_once()
            result=json.loads(next((root/'artifacts').glob('*/result.json')).read_text());self.assertEqual(result['android']['status'],'FAIL');self.assertEqual(result['ios']['status'],'PASS')

    def test_r09_android_only_never_infers_ios_execution(self):
        m=module('r09-utf8')
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);(root/'artifacts').mkdir()
            env={'GAMEBRIDGE_RUN_R09':'true','GAMEBRIDGE_UPM_STAGING':'/stage','GAMEBRIDGE_ANDROID_SERIAL':'emulator-5596','GAMEBRIDGE_TEST_AVD_NAME':'GameBridge_V2_unit'}
            with patch.object(m,'ROOT',root),patch.dict(m.os.environ,env),patch('sys.argv',['r09','--platform','android']),patch.object(m.subprocess,'check_output',return_value='head\n'),patch.object(m,'run_android',return_value=dict(status='PASS',exitCode=0)),patch.object(m,'run_ios') as ios,contextlib.redirect_stdout(io.StringIO()):self.assertEqual(m.main(),0);ios.assert_not_called()
            result=json.loads(next((root/'artifacts').glob('*/result.json')).read_text());self.assertEqual(result['ios']['status'],'NOT_RUN')

    def test_r09_ios_timeout_shuts_down_only_created_simulator_without_deletion(self):
        m=module('r09-utf8');device='00000000-0000-0000-0000-000000000001'
        commands=[]
        def run(cmd,**kw):
            commands.append(cmd)
            if cmd[0]=='bash':return subprocess.CompletedProcess([],0,stdout='/owned/project')
            if cmd[:3]==['xcrun','simctl','create']:return subprocess.CompletedProcess([],0,stdout=device+'\n')
            if cmd[0]=='xcodebuild':raise subprocess.TimeoutExpired(cmd,240)
            self.assertEqual(cmd,['xcrun','simctl','shutdown',device]);return subprocess.CompletedProcess([],0)
        with tempfile.TemporaryDirectory() as tmp,patch.object(m.subprocess,'run',side_effect=run):
            result=m.run_ios(Path(tmp));self.assertEqual(result['status'],'DEFERRED_ENV');self.assertEqual(result['ownedSimulatorShutdownExitCode'],0)
        self.assertFalse(any('delete' in cmd or 'erase' in cmd for cmd in commands))

    def test_r09_already_shutdown_uuid_comparison_ignores_simctl_letter_case(self):
        m=module('r09-utf8');device='AAAABBBB-0000-0000-0000-000000000001'
        def run(cmd,**kw):
            if cmd[0]=='bash':return subprocess.CompletedProcess([],0,stdout='/owned/project')
            if cmd[:3]==['xcrun','simctl','create']:return subprocess.CompletedProcess([],0,stdout=device)
            if cmd[0]=='xcodebuild':raise subprocess.TimeoutExpired(cmd,240)
            if cmd[:3]==['xcrun','simctl','shutdown']:return subprocess.CompletedProcess([],149)
            self.assertEqual(cmd,['xcrun','simctl','list','devices','-j']);return subprocess.CompletedProcess([],0,stdout=json.dumps({'devices':{'runtime':[{'udid':device,'state':'Shutdown'}]}}))
        with tempfile.TemporaryDirectory() as tmp,patch.object(m.subprocess,'run',side_effect=run):value=m.run_ios(Path(tmp))
        self.assertEqual(value['status'],'DEFERRED_ENV');self.assertEqual(value['errorCode'],'IOS_COMMAND_UNAVAILABLE_OR_TIMEOUT');self.assertEqual(value['ownedSimulatorShutdownExitCode'],149)

    def test_r09_ios_malformed_summary_fails_closed_and_preserves_cleanup(self):
        m=module('r09-utf8');device='00000000-0000-0000-0000-000000000001'
        with tempfile.TemporaryDirectory() as tmp:
            out=Path(tmp)
            def run(cmd,**kw):
                if cmd[0]=='bash':return subprocess.CompletedProcess([],0,stdout='/owned/project')
                if cmd[:3]==['xcrun','simctl','create']:return subprocess.CompletedProcess([],0,stdout=device)
                if cmd[0]=='xcodebuild':(out/'result.xcresult').mkdir();return subprocess.CompletedProcess([],0,stdout='')
                if cmd[:3]==['xcrun','xcresulttool','get']:return subprocess.CompletedProcess([],0,stdout='[]')
                self.assertEqual(cmd,['xcrun','simctl','shutdown',device]);return subprocess.CompletedProcess([],0)
            with patch.object(m.subprocess,'run',side_effect=run):
                value=m.run_ios(out)
            self.assertEqual(value['status'],'FAIL');self.assertEqual(value['errorCode'],'IOS_RESULT_UNAVAILABLE');self.assertEqual(value['ownedSimulatorShutdownExitCode'],0)

    def test_push_gui_forwarding_and_legacy_both_are_separate(self):
        m=module('unity-push-current');env={'GAMEBRIDGE_UPM_STAGING':'/stage','GAMEBRIDGE_PUSH_ANDROID_SERIAL':'emulator-5596','GAMEBRIDGE_PUSH_TEST_AVD_NAME':'GameBridge_V2_unit','GAMEBRIDGE_PUSH_EMULATOR_PID':'42'}
        a=arguments(gui_project=Path('/owned'),gui_build_receipt=Path('/receipt'),expected_adb_server_pid=43,adb='/unity/adb')
        commands=m.commands_for(a,env);self.assertEqual([x for x,_ in commands],['android','ios']);self.assertIn('--gui-build-receipt',commands[0][1]);self.assertNotIn('--gui-project',commands[1][1]);self.assertNotIn('--ack-known-fullscreen-notice',commands[0][1])
        self.assertEqual(len(m.commands_for(arguments(),env)),2);self.assertNotIn('--gui-project',m.commands_for(arguments(),env)[0][1])
        self.assertEqual([x for x,_ in m.commands_for(arguments(platform='android'),env)],['android'])

    def test_push_unpaired_gui_or_missing_server_rejected_before_child(self):
        m=module('unity-push-current');env={'GAMEBRIDGE_UPM_STAGING':'/stage','GAMEBRIDGE_PUSH_ANDROID_SERIAL':'emulator-5596','GAMEBRIDGE_PUSH_TEST_AVD_NAME':'GameBridge_V2_unit','GAMEBRIDGE_PUSH_EMULATOR_PID':'42'}
        for a in (arguments(gui_project=Path('/owned')),arguments(gui_project=Path('/owned'),gui_build_receipt=Path('/receipt')),arguments(platform='ios',gui_project=Path('/owned'),gui_build_receipt=Path('/receipt'))):
            with self.assertRaises(ValueError):m.commands_for(a,env)

if __name__=='__main__':unittest.main()
