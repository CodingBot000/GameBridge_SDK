"""A checksum-valid staging from an older private implementation is still stale."""
import importlib.util
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
spec=importlib.util.spec_from_file_location('stage_compare',Path(__file__).with_name('run-unity-android-mock-e2e.py'))
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
class CoreStagingSourceTests(unittest.TestCase):
    def test_private_managed_change_requires_fresh_staging(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);source=root/'unity/Packages/com.gamebridge.sdk/Runtime/Core';source.mkdir(parents=True)
            stage=root/'stage';pack=stage/'com.gamebridge.sdk/Runtime/Core';pack.mkdir(parents=True)
            (source/'RequestRegistry.cs').write_text('current implementation')
            (pack/'RequestRegistry.cs').write_text('older implementation')
            with patch.object(module,'ROOT',root):
                with self.assertRaises(module.GateError):module.verify_staged_source_matches_checkout(stage)
                (pack/'RequestRegistry.cs').write_bytes((source/'RequestRegistry.cs').read_bytes())
                module.verify_staged_source_matches_checkout(stage)
if __name__=='__main__':unittest.main()
