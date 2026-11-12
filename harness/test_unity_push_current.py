import importlib.util, json, tempfile, unittest
from pathlib import Path
from unittest.mock import patch
spec=importlib.util.spec_from_file_location('push_current',Path(__file__).parent/'run-unity-push-current.py');module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
class UnityPushEvidenceTests(unittest.TestCase):
    def test_requires_fresh_clean_both_platform_evidence_and_all_markers(self):
        with tempfile.TemporaryDirectory() as temp, patch.object(module, 'ROOT', Path(temp)):
            directory=Path(temp)/'artifacts'/'unity-ios-push-test-fixture';directory.mkdir(parents=True);output='RESULT PASS  EVIDENCE '+directory.relative_to(module.ROOT).as_posix()+'\n'
            data={'status':'PASS','player':'PASS','sourceHead':'head','sourceTrackedDirty':False,'mockPush':'PASS','background':'PASS','networkRecovery':'PASS_LOCAL_TRANSPORT_FAULT','reconnectFailure':'PASS','rejectedReconnectAttempts':1,'deduplication':'PASS','mainThread':'PASS','sessionSwitch':'PASS','deviceTokens':0}
            (directory/'result.json').write_text(json.dumps(data));(directory/'unity-push-markers.log').write_text('\n'.join(module.REQUIRED))
            self.assertTrue(module.check_result(output,0,'head','ios'))
            for key,value in [('sourceHead','stale'),('sourceTrackedDirty',True),('player','NOT_RUN'),('rejectedReconnectAttempts',0),('deviceTokens',False),('networkRecovery','PASS')]:
                changed=data.copy();changed[key]=value;(directory/'result.json').write_text(json.dumps(changed));self.assertFalse(module.check_result(output,0,'head','ios'))
            (directory/'result.json').write_text(json.dumps(data));(directory/'unity-push-markers.log').write_text('\n'.join(module.REQUIRED[:-1]));self.assertFalse(module.check_result(output,0,'head','ios'))
            self.assertFalse(module.check_result(output,0,'head','android'));self.assertFalse(module.check_result(output,1,'head','ios'))
if __name__=='__main__':unittest.main()
