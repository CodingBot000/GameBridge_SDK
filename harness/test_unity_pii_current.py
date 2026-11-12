import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
spec=importlib.util.spec_from_file_location('pii_evidence',Path(__file__).parent/'check-unity-pii-evidence.py')
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
class PiiEvidenceTests(unittest.TestCase):
    def test_requires_both_current_clean_players_nonce_and_markers(self):
        with tempfile.TemporaryDirectory() as temp, patch.object(module,'ROOT',Path(temp)):
            root=Path(temp);artifacts=root/'artifacts';artifacts.mkdir();nonce='a'*32;head='source-head';children={}
            data={'status':'PASS','sourceHead':head,'sourceTrackedDirty':False,'piiProbe':True,'unityPlayer':'PASS','ledgerCount':1,'ledgerDelta':100}
            for platform in ('android','ios'):
                directory=artifacts/f'unity-{platform}-e2e-fixture';directory.mkdir();(directory/'result.json').write_text(json.dumps(data));(directory/'unity-test-markers.log').write_text('GB_PII_PROBE PASS\nGB_MOCK_RESULT PASS LOCAL_MOCK\n');children[platform]=f'artifacts/{directory.name}/result.json'
            gate=artifacts/'unity-pii-current-fixture';gate.mkdir();path=gate/'result.json';report={'status':'PASS','sourceHead':head,'nonce':nonce,'suites':children};path.write_text(json.dumps(report));relative='artifacts/unity-pii-current-fixture/result.json'
            self.assertTrue(module.check(relative,nonce,head))
            self.assertFalse(module.check(relative,'b'*32,head));self.assertFalse(module.check(relative,nonce,'stale'));self.assertFalse(module.check('../outside',nonce,head))
            child=artifacts/'unity-android-e2e-fixture/result.json'
            for key,value in [('sourceTrackedDirty',True),('sourceHead','old'),('piiProbe',False),('unityPlayer','NOT_RUN'),('ledgerCount',True),('ledgerDelta',0)]:
                changed=data.copy();changed[key]=value;child.write_text(json.dumps(changed));self.assertFalse(module.check(relative,nonce,head))
            child.write_text(json.dumps(data));(child.parent/'unity-test-markers.log').write_text('GB_MOCK_RESULT PASS LOCAL_MOCK\n');self.assertFalse(module.check(relative,nonce,head))
            report['suites'].pop('ios');path.write_text(json.dumps(report));self.assertFalse(module.check(relative,nonce,head))
if __name__=='__main__':unittest.main()
