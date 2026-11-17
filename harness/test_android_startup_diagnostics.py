from pathlib import Path
import json
import subprocess
import tempfile
import unittest
from android_startup_diagnostics import analyze, last_confirmed, Collector, DiagnosticsUnavailable

PACKAGE='com.gamebridge.sdk.mockconsumer'


class AndroidStartupDiagnosticsTests(unittest.TestCase):
    def sample(self, log='', pids='123', ui=None):
        return analyze(log,pids,'mResumedActivity: '+PACKAGE,'mCurrentFocus= '+PACKAGE,'',ui,PACKAGE)

    def test_post_initialize_marker_absence_cannot_prove_start_absence(self):
        value=self.sample('GB_BOOT point=awake sceneIndex=0 t=1\nGB_BOOT point=start_enter t=2\nGB_BOOT point=initialize_call t=3')
        self.assertEqual(value['lastBusinessPoint'],'initialize_call')
        self.assertEqual(last_confirmed(value),'INITIALIZE_CALLED_NO_RETURN_OBSERVED')
        self.assertNotIn('status',value)

    def test_missing_managed_points_are_unmeasured_and_never_pass(self):
        value=self.sample('Initialize engine version: 6000.5.8f1',pids='')
        self.assertEqual(value['lastBusinessPoint'],'UNMEASURED');self.assertEqual(value['appPids'],[])
        self.assertTrue(value['unityEngineInitializationObserved'])
        self.assertEqual(last_confirmed(value),'NO_MANAGED_ENTRY_OBSERVED')

    def test_crash_and_anr_are_package_scoped(self):
        value=self.sample('FATAL EXCEPTION\nProcess: '+PACKAGE+', PID: 123\njava.lang.UnsatisfiedLinkError')
        self.assertTrue(value['appCrashObserved']);self.assertEqual(last_confirmed(value),'APP_CRASH_OBSERVED')
        other=self.sample('FATAL EXCEPTION\nProcess: com.android.other, PID: 42')
        self.assertFalse(other['appCrashObserved'])
        self.assertTrue(self.sample('ANR in '+PACKAGE)['appAnrObserved'])

    def test_only_observed_known_systemui_guide_is_reported(self):
        xml='<hierarchy><node package="com.android.systemui" text="Viewing full screen"/><node package="com.android.systemui" text="Got it"/></hierarchy>'
        self.assertTrue(self.sample(ui=xml)['knownFullscreenGuideObserved'])
        self.assertEqual(self.sample()['knownFullscreenGuideObserved'],'UNMEASURED')
        self.assertFalse(self.sample(ui=xml.replace('com.android.systemui',PACKAGE))['knownFullscreenGuideObserved'])

    def test_public_analysis_does_not_export_raw_configuration_or_credentials(self):
        raw='private-token-123\nGB_BOOT point=intent_checked urlPresent=1 keyPresent=1 keyValid=1 t=1\nGB_BOOT point=unknown_secret t=2'
        value=self.sample(raw)
        self.assertEqual(value['bootPoints'],['intent_checked']);self.assertNotIn('private-token',json.dumps(value))

    def fake_runner(self, command, timeout):
        args=command[3:]
        if args[:1]==['logcat']:text='system log\nGB_BOOT point=awake t=1\nsecret-key secret-password'
        elif args[:2]==['shell','pidof']:text='123'
        elif 'uiautomator' in args:text='UI hierarchy dumped'
        elif args[:2]==['shell','cat']:text='<hierarchy/>'
        else:text='diagnostic fixture'
        return subprocess.CompletedProcess(command,0,text)

    def test_collection_redacts_known_secrets_and_detects_observed_process_exit(self):
        with tempfile.TemporaryDirectory() as tmp:
            out=Path(tmp)/'diag';collector=Collector(self.fake_runner,'/sdk/adb','emulator-5592',PACKAGE,out,('secret-key','secret-password'))
            first=collector.capture('launched',ui=True);self.assertEqual(first['appPids'],[123])
            saved=''.join(p.read_text() for p in out.iterdir());self.assertNotIn('secret-key',saved);self.assertNotIn('secret-password',saved)
            def exited(command,timeout):
                if command[3:5]==['shell','pidof']:return subprocess.CompletedProcess(command,1,'')
                return self.fake_runner(command,timeout)
            collector.run=exited;collector.capture('later')
            self.assertTrue(json.loads((out/'summary.json').read_text())['processExitObserved'])

    def test_unavailable_all_buffer_log_is_not_normal(self):
        with tempfile.TemporaryDirectory() as tmp:
            def missing(command,timeout):return subprocess.CompletedProcess(command,1,'unavailable')
            collector=Collector(missing,'/sdk/adb','emulator-5592',PACKAGE,Path(tmp)/'diag')
            with self.assertRaises(DiagnosticsUnavailable):collector.capture('failure')

    def test_backend_first_trace_is_observation_not_invented_time_zero(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);log=root/'server.log';log.write_text('healthy only')
            c=Collector(self.fake_runner,'/sdk/adb','emulator-5592',PACKAGE,root/'diag')
            c.capture('ready',backend_log=log);self.assertIsNone(c.first_http)
            log.write_text('LOCAL_MOCK_TRACE operation=mock-auth method=POST requestId=dc9a46f4-8e20-4880-bcbb-ac45033157ca status=200')
            c.capture('requested',backend_log=log);self.assertIsNotNone(c.first_http)
