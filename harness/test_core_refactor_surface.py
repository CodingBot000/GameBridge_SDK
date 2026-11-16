import copy
import importlib.util
import unittest
from pathlib import Path
spec=importlib.util.spec_from_file_location('surface',Path(__file__).with_name('check-core-refactor-surface.py'))
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
class CoreSurfaceTests(unittest.TestCase):
    def setUp(self):
        self.base={'files':{module.TARGET:{'sha256':'old','declarations':['public class SdkException','internal RequestAsync']},'native.kt':{'sha256':'native'},'wire.json':{'sha256':'wire'}},'swiftCExports':['GB_Dispatch']}
    def test_only_private_managed_body_may_change(self):
        after=copy.deepcopy(self.base);after['files'][module.TARGET]['sha256']='new'
        self.assertEqual(module.check(self.base,after),[])
    def test_public_internal_and_wire_drift_rejected(self):
        for path in ('native.kt','wire.json',module.TARGET):
            after=copy.deepcopy(self.base)
            if path==module.TARGET:after['files'][path]['declarations'].append('public Changed')
            else:after['files'][path]['sha256']='changed'
            self.assertTrue(module.check(self.base,after))
    def test_export_or_file_set_drift_rejected(self):
        after=copy.deepcopy(self.base);after['swiftCExports']=[]
        self.assertTrue(module.check(self.base,after))
        after=copy.deepcopy(self.base);after['files'].pop('native.kt')
        self.assertTrue(module.check(self.base,after))
if __name__=='__main__':unittest.main()
