import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
spec=importlib.util.spec_from_file_location('consumer_e2e',Path(__file__).parent/'run-unity-consumer-e2e.py');module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
class ConsumerEvidenceTests(unittest.TestCase):
    def test_rejects_missing_nonpass_and_stale_results(self):
        self.assertFalse(module.check_result('RESULT PASS EVIDENCE artifacts/unity-android-e2e-missing\n',0,'head','android'))
        self.assertFalse(module.check_result('',0,'head','ios'))
        self.assertFalse(module.check_result('RESULT PASS EVIDENCE artifacts/unity-ios-e2e-x\n',1,'head','ios'))
    def test_accepts_only_fresh_clean_real_player_result(self):
        with tempfile.TemporaryDirectory(dir=module.ROOT/'artifacts',prefix='unity-android-e2e-test-') as tmp:
            path=Path(tmp); result=path/'result.json'; marker='RESULT PASS  EVIDENCE '+path.relative_to(module.ROOT).as_posix()+'\n'
            data={'status':'PASS','unityPlayer':'PASS','sourceHead':'head','sourceTrackedDirty':False,'ledgerCount':1,'ledgerDelta':100}
            result.write_text(json.dumps(data));self.assertTrue(module.check_result(marker,0,'head','android'))
            for key,value in [('sourceHead','stale'),('sourceTrackedDirty',True),('unityPlayer','NOT_RUN'),('ledgerDelta',0)]:
                altered=data.copy();altered[key]=value;result.write_text(json.dumps(altered));self.assertFalse(module.check_result(marker,0,'head','android'))
if __name__=='__main__':unittest.main()
