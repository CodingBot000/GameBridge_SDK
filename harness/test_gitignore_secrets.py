"""Check ignore policy using synthetic names only; never read secret files."""
from pathlib import Path
import subprocess
import unittest
ROOT=Path(__file__).resolve().parent.parent
class GitignoreSecretsTests(unittest.TestCase):
    def ignored(self,path):
        return subprocess.run(['git','check-ignore','--no-index','-q',path],cwd=ROOT,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL).returncode==0
    def test_secret_and_build_names_are_ignored(self):
        for path in ('.env','config/.env.production','config/.env.local','temp/license.ulf','temp/signing.p12','temp/key.p8','temp/sample.mobileprovision','temp/test.apk','temp/test.aab','temp/test.ipa','temp/google-services.json','temp/GoogleService-Info.plist'):
            with self.subTest(path=path):self.assertTrue(self.ignored(path))
    def test_example_names_can_be_versioned(self):
        for path in ('.env.example','config/.env.production.example'):
            with self.subTest(path=path):self.assertFalse(self.ignored(path))
if __name__=='__main__':unittest.main()
