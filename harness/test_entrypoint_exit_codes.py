import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
ROOT=Path(__file__).resolve().parent.parent
class EntrypointExitTests(unittest.TestCase):
    def test_missing_tools_are_deferred(self):
        with tempfile.TemporaryDirectory() as temp:
            env=os.environ.copy();env.update(PATH=temp,ANDROID_HOME=str(Path(temp)/'absent'))
            result=subprocess.run(['/bin/bash',str(ROOT/'scripts/doctor.sh')],env=env,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
            self.assertEqual(result.returncode,2);self.assertIn('unavailable',result.stdout)
    def test_build_failure_propagates_non_deferred_exit(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);(root/'scripts').mkdir();(root/'android').mkdir();shutil.copy2(ROOT/'scripts/build-android.sh',root/'scripts/build-android.sh')
            gradle=root/'android/gradlew';gradle.write_text('#!/bin/bash\nexit 7\n');gradle.chmod(0o755)
            env=os.environ.copy();env.update(GAMEBRIDGE_MAVEN_REPO=str(root/'maven'),ANDROID_HOME=str(root/'sdk'))
            result=subprocess.run(['/bin/bash',str(root/'scripts/build-android.sh'),'--mock'],env=env,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
            self.assertEqual(result.returncode,7)
if __name__=='__main__':unittest.main()
