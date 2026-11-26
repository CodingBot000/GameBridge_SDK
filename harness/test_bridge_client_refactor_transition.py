import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

spec = importlib.util.spec_from_file_location('bridge_refactor', Path(__file__).with_name('check-bridge-client-refactor-transition.py'))
guard = importlib.util.module_from_spec(spec)
spec.loader.exec_module(guard)


class TransitionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.baseline = guard.collect(guard.ROOT, guard.BASE)
        cls.candidate = guard.collect(guard.ROOT)
        cls.reviewed = json.loads((guard.ROOT / guard.RECORD).read_text())

    def setUp(self):
        self.before = self.baseline.copy()
        self.after = self.candidate.copy()
        self.record = copy.deepcopy(self.reviewed)

    def test_exact_candidate_passes(self):
        guard.verify_transition(self.before, self.after, self.record)

    def test_missing_duplicate_and_outside_reviewed_paths_fail(self):
        for behavior in ('missing', 'duplicate', 'outside'):
            with self.subTest(behavior=behavior):
                record = copy.deepcopy(self.record)
                if behavior == 'missing':
                    record['changes'].pop()
                elif behavior == 'duplicate':
                    record['changes'].append(record['changes'][0])
                else:
                    record['changes'][0]['path'] = '../outside.kt'
                with self.assertRaisesRegex(ValueError, 'reviewed path'):
                    guard.verify_transition(self.before, self.after, record)

    def test_preimage_and_postimage_are_independently_verified(self):
        for field in ('beforeSha256', 'afterSha256'):
            with self.subTest(field=field):
                record = copy.deepcopy(self.record)
                record['changes'][0][field] = 'malformed'
                with self.assertRaisesRegex(ValueError, 'preimage/postimage'):
                    guard.verify_transition(self.before, self.after, record)
        name = guard.BRIDGE + 'BridgeStoreLifecycle.kt'
        self.after[name] += b'// changed body'
        with self.assertRaisesRegex(ValueError, 'postimage'):
            guard.verify_transition(self.before, self.after, self.record)

    def test_new_unreviewed_file_removed_file_and_contract_drift_fail(self):
        for name in ('contracts/bridge.schema.json', 'backend/src/extra.kt', 'ios/UnityBridge/Bridge.swift'):
            with self.subTest(name=name):
                after = self.after | {name: b'drift'}
                with self.assertRaisesRegex(ValueError, 'shipping delta'):
                    guard.verify_transition(self.before, after, self.record)
        self.after.pop(guard.BRIDGE + 'BridgeFacade.kt')
        with self.assertRaises(ValueError):
            guard.verify_transition(self.before, self.after, self.record)

    def revise_postimage(self, name, old, new):
        self.after[name] = self.after[name].replace(old, new)
        for entry in self.record['changes']:
            if entry['path'] == name:
                entry['afterSha256'] = guard.sha256(self.after[name])
                return
        self.fail('missing changed test file')

    def test_public_declaration_and_enum_drift_fail_even_with_matching_hash(self):
        self.revise_postimage(guard.MANAGED + 'GameBridgeClient.cs', b'MOCK, GOOGLE', b'GOOGLE, MOCK')
        with self.assertRaisesRegex(ValueError, 'managed public declarations'):
            guard.verify_transition(self.before, self.after, self.record)

    def test_version_disagreement_fails_even_with_matching_hash(self):
        self.revise_postimage(guard.MANAGED + 'SdkStatusModels.cs', guard.VERSION.encode(), b'9.9.9-dev')
        with self.assertRaisesRegex(ValueError, 'version mismatch'):
            guard.verify_transition(self.before, self.after, self.record)

    def test_symlink_and_path_traversal_are_refused(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'outside').symlink_to(root.parent, target_is_directory=True)
            for name in ('../outside', '/absolute', 'outside/file'):
                with self.subTest(name=name), self.assertRaises(ValueError):
                    guard.safe_path(root, name)

    def test_nonancestor_and_previous_guard_fail_closed(self):
        with patch.object(guard, 'git', side_effect=subprocess.CalledProcessError(1, 'merge-base')):
            self.assertEqual(1, guard.main())
        with patch.object(guard, 'git'), patch.object(guard, 'collect'), patch.object(guard, 'verify_transition'), \
                patch.object(guard, 'verify_original_guards', side_effect=subprocess.CalledProcessError(1, 'old guard')):
            self.assertEqual(1, guard.main())
