"""Offline checks: CI must not turn missing Unity or partial coverage into PASS."""
import os
from pathlib import Path
import subprocess
import tempfile
import shutil
import unittest
ROOT=Path(__file__).resolve().parent.parent

class CiGateTests(unittest.TestCase):
    def invoke(self, name, base=ROOT, **values):
        env=os.environ.copy(); env.update(values)
        for key in ('GAMEBRIDGE_UPM_STAGING','GAMEBRIDGE_ANDROID_SERIAL','GAMEBRIDGE_TEST_AVD_NAME'):
            env.pop(key,None)
        return subprocess.run(['bash',str(base/'scripts'/name)],cwd=ROOT,env=env,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
    def test_unity_preflight_refuses_missing_environment(self):
        result=self.invoke('ci-unity-e2e.sh');self.assertEqual(result.returncode,2);self.assertIn('DEFERRED_ENV',result.stdout)
    def test_unity_preflight_refuses_missing_editor_executable(self):
        env=os.environ.copy();env.update(UNITY_EDITOR_PATH='/nonexistent/gamebridge-unity-editor',GAMEBRIDGE_UPM_STAGING='/tmp',GAMEBRIDGE_UNITY_PACKAGE_CACHE='/tmp',
            GAMEBRIDGE_ANDROID_SERIAL='emulator-5580',GAMEBRIDGE_TEST_AVD_NAME='GameBridge_V2_baseline',
            GAMEBRIDGE_PUSH_ANDROID_SERIAL='emulator-5582',GAMEBRIDGE_PUSH_TEST_AVD_NAME='GameBridge_V2_push')
        result=subprocess.run(['bash',str(ROOT/'scripts/ci-unity-e2e.sh')],cwd=ROOT,env=env,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
        self.assertEqual(result.returncode,2);self.assertIn('UNITY_EDITOR_PATH',result.stdout)
    def test_unity_preflight_refuses_missing_package_cache(self):
        with tempfile.NamedTemporaryFile() as editor:
            env=os.environ.copy();env.update(UNITY_EDITOR_PATH=editor.name,GAMEBRIDGE_UPM_STAGING='/tmp',
                GAMEBRIDGE_UNITY_PACKAGE_CACHE='/nonexistent/gamebridge-package-cache',
                GAMEBRIDGE_ANDROID_SERIAL='emulator-5580',GAMEBRIDGE_TEST_AVD_NAME='GameBridge_V2_baseline',
                GAMEBRIDGE_PUSH_ANDROID_SERIAL='emulator-5582',GAMEBRIDGE_PUSH_TEST_AVD_NAME='GameBridge_V2_push')
            result=subprocess.run(['bash',str(ROOT/'scripts/ci-unity-e2e.sh')],cwd=ROOT,env=env,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
            self.assertEqual(result.returncode,2);self.assertIn('package cache',result.stdout)
    def test_release_gate_never_accepts_skipped_or_failed_unity(self):
        for status in ('skipped','failure','cancelled',''):
            result=self.invoke('ci-release-gate.sh',BASIC_RESULT='success',UNITY_RESULT=status)
            self.assertEqual(result.returncode,2);self.assertIn('DEFERRED_ENV',result.stdout)
    def test_release_rejects_basic_failure_and_partial_scenarios(self):
        self.assertEqual(self.invoke('ci-release-gate.sh',BASIC_RESULT='failure',UNITY_RESULT='success').returncode,1)
        # Use an isolated partial fixture so this test does not require the live
        # project to remain incomplete when future scenarios are implemented.
        with tempfile.TemporaryDirectory() as tmp:
            base=Path(tmp); (base/'scripts').mkdir(); (base/'harness').mkdir()
            shutil.copy2(ROOT/'scripts/ci-release-gate.sh',base/'scripts/ci-release-gate.sh')
            (base/'harness/check-required-coverage.py').write_text("import sys; print('INCOMPLETE: PARTIAL'); sys.exit(1)\n")
            result=self.invoke('ci-release-gate.sh',base=base,BASIC_RESULT='success',UNITY_RESULT='success')
            self.assertEqual(result.returncode,1);self.assertIn('PARTIAL',result.stdout)
if __name__=='__main__':unittest.main()
