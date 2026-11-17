import copy
from pathlib import Path
import tempfile
import unittest
from gui_verification import validate_ios_receipt, export_tree_hash, embedded_versions
import json


class GuiIosExportTests(unittest.TestCase):
    def fixture(self):
        c=dict(runId='a'*32,sourceHead='b'*40,scriptSha256='c'*64,adapterSha256='d'*64,
               buildScriptSha256='e'*64,scenarioSha256='f'*64,stagingManifestSha256='1'*64,
               variant='pii',projectRoot='/tmp/owned/project',outputPath='/tmp/owned/xcode',expectedUnityVersion='6000.5.8f1')
        v=dict(c,schemaVersion=1,status='PASS',operation='ios',isBatchMode=False,unityVersion='6000.5.8f1',
               method='GuiIosExport.Export',originalBuilderReturned=True,packageFilesVerified=147,
               artifactFileCount=12,artifactSha256='2'*64,pbxprojSha256='3'*64)
        return v,c

    def test_completed_export_is_not_player_or_batch_claim(self):
        v,c=self.fixture();validate_ios_receipt(v,c)

    def test_wrong_source_nonce_hash_project_and_variant_rejected(self):
        v,c=self.fixture()
        for key in ('runId','sourceHead','scriptSha256','adapterSha256','buildScriptSha256','scenarioSha256','stagingManifestSha256','projectRoot','outputPath','variant'):
            x=copy.deepcopy(v);x[key]='foreign'
            with self.assertRaises(ValueError):validate_ios_receipt(x,c)

    def test_partial_or_wrong_mode_export_rejected(self):
        v,c=self.fixture()
        for key,value in [('status','FAIL'),('isBatchMode',True),('originalBuilderReturned',False),('artifactFileCount',0),('pbxprojSha256','missing'),('packageFilesVerified',146)]:
            x=copy.deepcopy(v);x[key]=value
            with self.assertRaises(ValueError):validate_ios_receipt(x,c)

    def test_export_tree_digest_catches_mutation_extra_files_and_symlinks(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);(root/'a').write_bytes(b'unit fixture')
            before,count=export_tree_hash(root);self.assertEqual(count,1)
            (root/'a').write_bytes(b'changed');self.assertNotEqual(export_tree_hash(root)[0],before)
            (root/'b').write_bytes(b'extra');self.assertEqual(export_tree_hash(root)[1],2)
            (root/'link').symlink_to(root/'a')
            with self.assertRaises(ValueError):export_tree_hash(root)

    def test_gui_export_requires_exact_embedded_runtime_dependencies(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            for name,version in [('com.unity.mobile.notifications','2.5.0'),('com.unity.nuget.newtonsoft-json','3.2.2')]:
                folder=root/'Packages'/name;folder.mkdir(parents=True)
                (folder/'package.json').write_text(json.dumps(dict(name=name,version=version)))
            self.assertEqual(embedded_versions(root)['com.unity.mobile.notifications'],'2.5.0')
            (root/'Packages/com.unity.mobile.notifications/package.json').write_text(json.dumps(dict(name='com.unity.mobile.notifications',version='other')))
            with self.assertRaises(ValueError):embedded_versions(root)
