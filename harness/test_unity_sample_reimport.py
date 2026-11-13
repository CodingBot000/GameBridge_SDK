import importlib.util
from pathlib import Path
import tempfile
import unittest
spec=importlib.util.spec_from_file_location('reimport_check',Path(__file__).parent/'check-unity-sample-reimport.py');module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
class SampleReimportTests(unittest.TestCase):
    def test_requires_exact_unique_stable_markers_and_success(self):
        with tempfile.TemporaryDirectory() as temp:
            path=Path(temp)/'markers';self.assertFalse(module.passed(path,0))
            valid='\n'.join(module.REQUIRED)+'\n';path.write_text(valid)
            self.assertTrue(module.passed(path,0));self.assertFalse(module.passed(path,1))
            for text in (valid.replace(module.REQUIRED[0],''),valid+module.REQUIRED[1]+'\n',valid.replace('ROOT=STABLE','ROOT=CHANGED',1)):
                path.write_text(text);self.assertFalse(module.passed(path,0))
if __name__=='__main__':unittest.main()
