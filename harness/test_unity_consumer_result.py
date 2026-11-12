import subprocess
import tempfile
from pathlib import Path
import unittest
ROOT=Path(__file__).resolve().parent.parent
class UnityConsumerResultTests(unittest.TestCase):
    def check(self, xml):
        with tempfile.TemporaryDirectory() as tmp:
            report=Path(tmp)/'result.xml';report.write_text(xml)
            return subprocess.run(['python3',str(ROOT/'scripts/check-unity-test-result.py'),str(report)],stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True)
    def test_requires_both_test_markers(self):
        good='<test-run><test-case name="DomainReloadEnabled" result="Passed"><output>GB_CONSUMER_RELOAD_ENABLED_COMPLETE</output></test-case><test-case name="DomainReloadDisabled" result="Passed"><output>GB_CONSUMER_RELOAD_DISABLED_COMPLETE</output></test-case></test-run>'
        self.assertEqual(self.check(good).returncode,0)
        self.assertEqual(self.check(good.replace('GB_CONSUMER_RELOAD_ENABLED_COMPLETE','')).returncode,1)
        self.assertEqual(self.check(good.replace('result="Passed"','result="Skipped"',1)).returncode,1)
        self.assertEqual(self.check(good.replace('DomainReloadEnabled','DomainReloadDisabled',1)).returncode,1)
if __name__=='__main__':unittest.main()
