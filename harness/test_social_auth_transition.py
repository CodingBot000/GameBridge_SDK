import copy
import importlib.util
from pathlib import Path
import unittest
spec=importlib.util.spec_from_file_location('social',Path(__file__).with_name('check-social-auth-transition.py'))
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)

class SocialTransitionTests(unittest.TestCase):
    def setUp(self):
        self.before={'files':{'core.cs':{'sha256':'core'},'native.swift':{'sha256':'old'}},'swiftCExports':['GB_Dispatch']}
        self.approved={'files':{'core.cs':{'sha256':'core'},'native.swift':{'sha256':'new'},'social.kt':{'sha256':'added'}},'swiftCExports':['GB_Dispatch','GB_HandleAuthURL']}
        self.record={'changes':[{'path':'native.swift','beforeSha256':'old','afterSha256':'new'},{'path':'social.kt','beforeSha256':None,'afterSha256':'added'}]}
    def check(self,current=None,record=None,approved=None):
        return m.check_transition(self.before,approved or self.approved,current or self.approved,record or self.record)
    def test_exact_authorized_extension_accepted(self):
        self.assertEqual(self.check(),[])
    def test_core_new_file_or_native_drift_rejected(self):
        for name in ['core.cs','native.swift','social.kt','unapproved.cs']:
            current=copy.deepcopy(self.approved);current['files'][name]={'sha256':'modified'}
            self.assertTrue(self.check(current=current))
    def test_omission_duplicate_and_unapproved_record_rejected(self):
        for mutate in ['omit','duplicate','extra','before','after']:
            record=copy.deepcopy(self.record)
            if mutate=='omit':record['changes'].pop()
            elif mutate=='duplicate':record['changes'].append(record['changes'][0])
            elif mutate=='extra':record['changes'].append({'path':'core.cs','beforeSha256':'core','afterSha256':'modified'})
            else:record['changes'][0][mutate+'Sha256']='wrong'
            self.assertTrue(self.check(record=record))
    def test_legacy_export_removal_or_unapproved_addition_rejected(self):
        for exports in [[],['GB_HandleAuthURL'],['GB_Dispatch','GB_HandleAuthURL','GB_Extra']]:
            approved=copy.deepcopy(self.approved);approved['swiftCExports']=exports
            self.assertTrue(self.check(approved=approved,current=approved))
    def test_csharp_declaration_drift_rejected(self):
        current=copy.deepcopy(self.approved);current['files']['core.cs']['declarations']=['public changed']
        self.assertTrue(self.check(current=current))

class LogoutTransitionTests(unittest.TestCase):
    def test_only_reviewed_postimages_and_unchanged_wire_are_accepted(self):
        closed = {'files': {p: {'sha256': 'a'*64} for p in m.LOGOUT_FILES}, 'swiftCExports': ['GB_Dispatch']}
        closed['files']['core.cs'] = {'sha256': 'c'*64}
        record = {'before': m.LOGOUT_BASE, 'files': {p: {'before': 'a'*64, 'after': 'b'*64} for p in m.LOGOUT_FILES}}
        current = copy.deepcopy(closed)
        for name in m.LOGOUT_FILES:
            current['files'][name]['sha256'] = 'b'*64
        self.assertEqual([], m.check_logout_transition(closed, current, record))
        for name in current['files']:
            drift = copy.deepcopy(current)
            drift['files'][name]['sha256'] = 'd'*64
            self.assertTrue(m.check_logout_transition(closed, drift, record))
        drift = dict(current, swiftCExports=[])
        self.assertTrue(m.check_logout_transition(closed, drift, record))

if __name__=='__main__':unittest.main()
