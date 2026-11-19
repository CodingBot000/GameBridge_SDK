import importlib.util
from pathlib import Path
import tempfile
import unittest
spec=importlib.util.spec_from_file_location('meta_check',Path(__file__).parent/'check-unity-meta.py')
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
class UnityMetaTests(unittest.TestCase):
    def test_missing_duplicate_and_orphan_are_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);(root/'a.cs').write_text('a');(root/'b.cs').write_text('b')
            guid='1'*32;(root/'a.cs.meta').write_text('fileFormatVersion: 2\nguid: '+guid+'\n')
            self.assertTrue(any('missing metadata' in e for e in module.check(root)))
            (root/'b.cs.meta').write_text('fileFormatVersion: 2\nguid: '+guid+'\n')
            self.assertTrue(any('duplicate GUID' in e for e in module.check(root)))
            (root/'b.cs.meta').write_text('fileFormatVersion: 2\nguid: '+'2'*32+'\n');self.assertEqual(module.check(root),[])
            (root/'ghost.meta').write_text('fileFormatVersion: 2\nguid: '+'3'*32+'\n')
            self.assertTrue(any('orphan metadata' in e for e in module.check(root)))
    def test_directory_requires_folder_metadata(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);(root/'folder').mkdir();(root/'folder.meta').write_text('fileFormatVersion: 2\nguid: '+'4'*32+'\n')
            self.assertTrue(any('folder metadata mismatch' in e for e in module.check(root)))
if __name__=='__main__':unittest.main()
