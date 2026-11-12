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
    def test_unity_gate_calls_isolated_strict_and_propagates_failure(self):
        with tempfile.TemporaryDirectory() as tmp:
            base=Path(tmp);(base/'scripts').mkdir();(base/'bin').mkdir();(base/'cache').mkdir()
            shutil.copy2(ROOT/'scripts/ci-unity-e2e.sh',base/'scripts/ci-unity-e2e.sh')
            for name in ('build-unity.sh','smoke-unity-offline-sample.sh','smoke-unity-android-hook-repeat.sh','smoke-unity-ios-hook-repeat.sh'):
                (base/'scripts'/name).write_text('#!/bin/bash\nprintf "%s\\n" "$0" >> "$GB_TEST_CALLS"\nexit 0\n')
            unity=base/'bin/unity';unity.write_text('#!/bin/bash\necho mocked\n');unity.chmod(0o755)
            python=base/'bin/python3';python.write_text('#!/bin/bash\nif [[ "$1" == "-c" ]]; then exit 0; fi\nprintf "%s\\n" "$*" >> "$GB_TEST_CALLS"\nif [[ "$1" == "harness/run-strict-local-isolated.py" ]]; then printf "%s\\n%s\\n" "$GAMEBRIDGE_MAVEN_REPO" "$GAMEBRIDGE_IOS_XCFRAMEWORK" >> "$GB_TEST_CALLS"; exit 1; fi\nexit 0\n');python.chmod(0o755)
            editor=base/'editor';editor.touch();calls=base/'calls'
            env=os.environ.copy();env.update(PATH=str(base/'bin')+os.pathsep+env['PATH'],GB_TEST_CALLS=str(calls),
                UNITY_EDITOR_PATH=str(editor),GAMEBRIDGE_UPM_STAGING=str(base),GAMEBRIDGE_UNITY_PACKAGE_CACHE=str(base/'cache'),
                GAMEBRIDGE_ANDROID_SERIAL='emulator-5580',GAMEBRIDGE_TEST_AVD_NAME='GameBridge_V2_baseline',
                GAMEBRIDGE_PUSH_ANDROID_SERIAL='emulator-5582',GAMEBRIDGE_PUSH_TEST_AVD_NAME='GameBridge_V2_push')
            result=subprocess.run(['bash',str(base/'scripts/ci-unity-e2e.sh')],cwd=base,env=env,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
            self.assertEqual(result.returncode,1);captured=calls.read_text()
            self.assertIn('harness/run-strict-local-isolated.py',captured)
            self.assertIn('harness/run-unity-android-mock-e2e.py --run-local --pii-probe',captured)
            self.assertIn('harness/run-unity-ios-mock-e2e.py --run-local --adhoc --pii-probe',captured)
            for script in ('build-unity.sh','smoke-unity-offline-sample.sh','smoke-unity-android-hook-repeat.sh','smoke-unity-ios-hook-repeat.sh'): self.assertIn('scripts/'+script,captured)
            self.assertIn(str(base/'com.gamebridge.sdk/Editor/GameBridgeArtifacts~/Android/maven-repo'),captured)
            self.assertIn(str(base/'com.gamebridge.sdk/Editor/GameBridgeArtifacts~/iOS/GameBridgeNative.xcframework'),captured)
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
