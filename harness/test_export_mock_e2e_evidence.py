#!/usr/bin/env python3
"""Offline fail-closed checks for public LOCAL_MOCK evidence export."""
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parent.parent
SPEC = importlib.util.spec_from_file_location(
    "export_mock_e2e_evidence", ROOT / "harness" / "export-mock-e2e-evidence.py")
module = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(module)
SHA = "a" * 40
APK_SHA = "b" * 64


class EvidenceExportTests(unittest.TestCase):
    def setUp(self):
        (ROOT / "artifacts").mkdir(exist_ok=True)
        self.temporary = tempfile.TemporaryDirectory(dir=ROOT / "artifacts")
        self.addCleanup(self.temporary.cleanup)
        self.path = Path(self.temporary.name) / "result.json"
        self.unity = {
            "status": "PASS", "sourceTrackedDirty": False, "sourceHead": SHA,
            "ledgerCount": 1, "ledgerDelta": 100, "unityPlayer": "PASS",
            "unityApkSha256": APK_SHA, "unityMarkerCount": 12,
            "backendTraceCounts": {key: 1 for key in
                                   ("mock-auth", "catalog", "entitlements", "verify", "logout")},
        }
        for filename in ("unity-build.log", "unity-test-markers.log", "server.log"):
            (self.path.parent / filename).write_text("local testing only\n", encoding="utf-8")

    def check(self, data, kind="unity"):
        self.path.write_text(json.dumps(data), encoding="utf-8")
        return module.checked_result(self.path, kind, SHA)

    def test_clean_unity_pass_is_accepted_and_public_fields_are_limited(self):
        value = self.check(self.unity)
        summary = module.public_summary(value, "unity", "d" * 64)
        self.assertIn("Unity Android Player", summary)
        self.assertIn("100코인", summary)
        self.assertNotIn(str(self.path), summary)
        self.assertNotIn("emulator-", summary)

    def test_dirty_stale_and_unrun_results_are_rejected(self):
        for patch in ({"sourceTrackedDirty": True}, {"sourceHead": "f" * 40},
                      {"unityPlayer": "NOT_RUN"}, {"status": "DEFERRED_ENV"},
                      {"ledgerDelta": 200}, {"backendTraceCounts": {}}):
            with self.subTest(patch=patch), self.assertRaises(ValueError):
                self.check({**self.unity, **patch})

    def test_missing_raw_evidence_is_rejected(self):
        (self.path.parent / "unity-test-markers.log").unlink()
        with self.assertRaises(ValueError):
            self.check(self.unity)

    def test_native_results_cannot_be_exported_as_unity(self):
        native = {
            **self.unity, "unityPlayer": "NOT_RUN", "tests": 1, "skipped": 0,
            "nativeOperations": ["sdk.initialize", "auth.signIn", "store.products",
                                 "store.purchase", "store.entitlements", "auth.signOut"],
        }
        for filename in ("instrumentation.log", "native-requests.log"):
            (self.path.parent / filename).write_text("local testing only\n", encoding="utf-8")
        with self.assertRaises(ValueError):
            self.check(native, "unity")
        self.check(native, "native")


if __name__ == "__main__":
    unittest.main()
