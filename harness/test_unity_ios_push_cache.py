import importlib.util
import json
import tempfile
from pathlib import Path
import unittest

spec=importlib.util.spec_from_file_location('ios_push',Path(__file__).parent/'run-unity-ios-mock-push-e2e.py');module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
class EmbeddedPackageTests(unittest.TestCase):
    def test_exact_versions_are_copied_without_modifying_source(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);cache=root/'cache';project=root/'project';(project/'Packages').mkdir(parents=True)
            for name,version in (('com.unity.mobile.notifications','2.5.0'),('com.unity.nuget.newtonsoft-json','3.2.2')):
                item=cache/(name+'@abc');item.mkdir(parents=True);(item/'package.json').write_text(json.dumps({'name':name,'version':version})); (item/'Tests').mkdir(); (item/'Tests/fixture.cs').write_text('test-only')
            result=module.embed_cached_packages(cache,project)
            self.assertEqual(result['com.unity.mobile.notifications'],'2.5.0')
            self.assertTrue((project/'Packages/com.unity.nuget.newtonsoft-json/package.json').is_file())
            self.assertFalse((project/'Packages/com.unity.mobile.notifications/Tests').exists())
            self.assertTrue((cache/'com.unity.mobile.notifications@abc/Tests/fixture.cs').exists())
            self.assertTrue((cache/'com.unity.mobile.notifications@abc/package.json').is_file())
    def test_missing_or_wrong_version_fails_closed(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);(root/'project/Packages').mkdir(parents=True);(root/'cache').mkdir()
            with self.assertRaises(module.common.GateError):module.embed_cached_packages(root/'cache',root/'project')
