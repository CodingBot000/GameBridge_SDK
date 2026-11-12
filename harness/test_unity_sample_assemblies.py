"""Unity asmdef references are not transitive like .NET project references."""
import json
from pathlib import Path
import unittest
ROOT=Path(__file__).resolve().parent.parent
class UnitySampleAssemblyTests(unittest.TestCase):
    def test_ios_host_sample_directly_references_used_runtime_assemblies(self):
        path=ROOT/'unity/Packages/com.gamebridge.sdk/Samples~/Native Demo/iOS/GameBridge.NativeDemo.iOS.asmdef'
        assembly=json.loads(path.read_text())
        self.assertEqual(assembly['includePlatforms'],['iOS'])
        self.assertTrue({'GameBridge.NativeDemo','GameBridge.iOSHost','GameBridge.Runtime'} <= set(assembly['references']))
if __name__=='__main__':unittest.main()
