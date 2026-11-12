import importlib.util
from pathlib import Path
import tempfile
import unittest
spec=importlib.util.spec_from_file_location('sample_result',Path(__file__).parent/'check-unity-offline-sample-result.py')
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
class OfflineSampleResultTests(unittest.TestCase):
    def test_rejects_missing_incomplete_skipped_failure_and_missing_marker(self):
        with tempfile.TemporaryDirectory() as temp:
            path=Path(temp)/'result.xml';self.assertFalse(module.passed(path,0))
            xml='<test-run result="Passed" total="1" passed="1" failed="0" skipped="0" inconclusive="0"><test-case fullname="OfflineSampleTests.SampleInitializesAndCompletesMockPurchase" result="Passed"><output>GB_OFFLINE_SAMPLE_FLOW PASS GB_NATIVE_SAMPLE_EDITOR_GUARD PASS</output></test-case></test-run>'
            path.write_text(xml);self.assertTrue(module.passed(path,0));self.assertFalse(module.passed(path,1))
            for old,new in [('total="1"','total="0"'),('skipped="0"','skipped="1"'),('result="Passed"','result="Failed"'),('GB_OFFLINE_SAMPLE_FLOW PASS','missing'),('GB_NATIVE_SAMPLE_EDITOR_GUARD PASS','missing')]:
                path.write_text(xml.replace(old,new));self.assertFalse(module.passed(path,0))
if __name__=='__main__':unittest.main()
