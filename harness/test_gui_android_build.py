import copy
from pathlib import Path
import os
import tempfile
import unittest
import contextlib
import importlib.util
import io
from unittest.mock import patch
from gui_verification import validate_android_receipt, validate_apk, build_log_segment, file_hash


class GuiAndroidBuildTests(unittest.TestCase):
    def fixture(self):
        c = dict(runId='a'*32, sourceHead='b'*40, scriptSha256='c'*64, adapterSha256='d'*64,
                 buildScriptSha256='e'*64, scenarioSha256='f'*64, stagingManifestSha256='1'*64,
                 projectRoot='/tmp/owned/project', outputPath='/tmp/owned/test.apk', variant='pii',
                 expectedUnityVersion='6000.5.8f1')
        v = dict(c, schemaVersion=1, status='PASS', operation='android', isBatchMode=False,
                 unityVersion='6000.5.8f1', method='GuiAndroidBuild.Build', originalBuilderReturned=True,
                 packageFilesVerified=147, artifactSize=100, artifactSha256='2'*64, editorPid=123)
        return v, c

    def test_actual_build_receipt_shape_accepted(self):
        v,c=self.fixture();validate_android_receipt(v,c)

    def test_wrong_nonce_source_variant_or_any_source_hash_rejected(self):
        v,c=self.fixture()
        for k in ('runId','sourceHead','variant','scriptSha256','adapterSha256','buildScriptSha256','scenarioSha256','stagingManifestSha256'):
            x=copy.deepcopy(v);x[k]='foreign'
            with self.assertRaises(ValueError):validate_android_receipt(x,c)

    def test_wrong_project_output_or_editor_rejected(self):
        v,c=self.fixture()
        for k,r in [('projectRoot','/tmp/other'),('outputPath','/tmp/other.apk'),('isBatchMode',True),('unityVersion','other')]:
            x=copy.deepcopy(v);x[k]=r
            with self.assertRaises(ValueError):validate_android_receipt(x,c)

    def test_incomplete_original_builder_cannot_claim_pass(self):
        v,c=self.fixture()
        for k,r in [('status','FAIL'),('originalBuilderReturned',False),('packageFilesVerified',146),('artifactSize',0),('artifactSize',True),('editorPid',0)]:
            x=copy.deepcopy(v);x[k]=r
            with self.assertRaises(ValueError):validate_android_receipt(x,c)

    def test_log_requires_exact_nonce_original_build_and_order(self):
        nonce='a'*32
        text='GB_GUI_ANDROID_STARTED '+nonce+'\nGB_MOCK_BUILD PASS\nGB_GUI_ANDROID_PASS '+nonce+'\n'
        self.assertEqual(build_log_segment(text,nonce),text)
        for broken in (text.replace('GB_MOCK_BUILD PASS',''),text+text,text.replace(nonce,'foreign'), '\n'.join(reversed(text.splitlines()))):
            with self.assertRaises(ValueError):build_log_segment(broken,nonce)

    def test_apk_hash_size_freshness_and_symlink_are_verified(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/'test.apk';p.write_bytes(b'unit fixture only, not a real APK')
            v=dict(artifactSize=p.stat().st_size,artifactSha256=file_hash(p))
            validate_apk(p,v,0)
            p.write_bytes(b'changed')
            with self.assertRaises(ValueError):validate_apk(p,v,0)
            v=dict(artifactSize=p.stat().st_size,artifactSha256=file_hash(p))
            with self.assertRaises(ValueError):validate_apk(p,v,p.stat().st_mtime_ns+1)
            link=Path(tmp)/'link.apk';link.symlink_to(p)
            with self.assertRaises(ValueError):validate_apk(link,v,0)

    def test_invalid_gui_input_fails_before_any_adb_or_backend_action(self):
        spec=importlib.util.spec_from_file_location('gui_consumer_gate',Path(__file__).with_name('run-unity-android-mock-e2e.py'))
        m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);stage=root/'stage';stage.mkdir();(stage/'SHA256SUMS').write_text('unit fixture')
            def command(parts,*args,**kw):
                if parts[:3]==['git','rev-parse','HEAD']:return 'b'*40
                if parts[:2]==['git','status']:return ''
                return 'fixture validation only'
            argv=['probe','--run-local','--staging',str(stage),'--gui-project',str(root/'project'),
                  '--gui-build-receipt',str(root/'receipt.json')]
            with patch.object(m,'ROOT',root),patch('sys.argv',argv),patch.object(m,'must',side_effect=command), \
                 patch.object(m,'verify_staged_source_matches_checkout'),patch.object(m,'load_android_build',side_effect=ValueError('mutated APK')), \
                 patch.object(m,'locate_adb') as adb,patch.object(m,'start_backend') as backend,contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(m.main(),1)
                adb.assert_not_called();backend.assert_not_called()
