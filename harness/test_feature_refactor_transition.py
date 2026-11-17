import copy,contextlib,importlib.util,io,json,tempfile,unittest
from unittest.mock import patch
from pathlib import Path
spec=importlib.util.spec_from_file_location('feature_transition',Path(__file__).with_name('check-feature-refactor-transition.py'));m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)

class FeatureTransitionTests(unittest.TestCase):
    def fixture(self):
        modified={x for x in m.ALLOWED if x.endswith(('GoogleAuthProvider.kt','AppleHttpProofSink.swift'))}
        before=dict(files={**{x:{'sha256':'a'*64} for x in modified},'Core.cs':{'sha256':'b'*64},'wire.json':{'sha256':'c'*64}},swiftCExports=['GB_Dispatch'])
        after=copy.deepcopy(before);record={'changes':[]}
        for path in sorted(m.ALLOWED):
            record['changes'].append(dict(path=path,beforeSha256=before['files'].get(path,{}).get('sha256'),afterSha256='d'*64));after['files'][path]={'sha256':'d'*64}
        return before,after,record
    def test_only_exact_four_reviewed_native_changes_are_accepted(self):
        self.assertEqual(m.check_transition(*self.fixture()),[])
    def test_unscoped_native_core_private_body_wire_and_file_set_changes_rejected(self):
        for kind in ('Core.cs','wire.json','new','removed'):
            a,b,r=self.fixture()
            if kind=='new':b['files']['new.kt']={'sha256':'f'*64}
            elif kind=='removed':b['files'].pop('Core.cs')
            else:b['files'][kind]['sha256']='f'*64
            self.assertTrue(m.check_transition(a,b,r))
    def test_approved_paths_do_not_permit_any_future_content_drift(self):
        a,b,r=self.fixture();b['files'][next(iter(m.ALLOWED))]['sha256']='f'*64
        self.assertTrue(m.check_transition(a,b,r))
    def test_missing_duplicate_foreign_or_forged_transition_record_rejected(self):
        for kind in ('missing','duplicate','foreign','preimage','hash'):
            a,b,r=self.fixture()
            if kind=='missing':r['changes'].pop()
            elif kind=='duplicate':r['changes'][1]=r['changes'][0]
            elif kind=='foreign':r['changes'][0]['path']='another.kt'
            elif kind=='preimage':r['changes'][0]['beforeSha256']='wrong'
            else:r['changes'][0]['afterSha256']='not-a-digest'
            self.assertTrue(m.check_transition(a,b,r))
    def test_export_drift_rejected(self):
        a,b,r=self.fixture();b['swiftCExports']=[];self.assertTrue(m.check_transition(a,b,r))
    def test_original_core_guard_still_rejects_native_edits(self):
        a,b,r=self.fixture();a['files'][m.core.TARGET]={'sha256':'a','declarations':['internal old']};b['files'][m.core.TARGET]={'sha256':'a','declarations':['internal old']}
        self.assertTrue(m.core.check(a,b))
    def test_changed_original_baseline_digest_cannot_be_hidden(self):
        value=json.loads(m.RECORD.read_text());value['originalCoreBaselineSha256']='0'*64
        with tempfile.TemporaryDirectory() as tmp:
            record=Path(tmp)/'transition.json';record.write_text(json.dumps(value))
            with patch.object(m,'RECORD',record),contextlib.redirect_stdout(io.StringIO()):self.assertEqual(m.main(),1)
    def test_missing_or_unrelated_closed_commit_fails_closed(self):
        value=json.loads(m.RECORD.read_text());value['coreCompletedSourceHead']='f'*40
        with tempfile.TemporaryDirectory() as tmp:
            record=Path(tmp)/'transition.json';record.write_text(json.dumps(value))
            with patch.object(m,'RECORD',record),contextlib.redirect_stdout(io.StringIO()):self.assertEqual(m.main(),1)

if __name__=='__main__':unittest.main()
