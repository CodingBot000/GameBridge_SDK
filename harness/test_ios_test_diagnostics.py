import hashlib
import json
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import ios_test_diagnostics as module
class IosTestDiagnosticTests(unittest.TestCase):
    def test_only_requested_device_is_recorded(self):
        raw={'devices':{'runtime':[{'udid':'foreign','name':'private','state':'Booted'},{'udid':'owned','name':'test','state':'Shutdown'}]}}
        with patch.object(module.subprocess,'run',return_value=subprocess.CompletedProcess([],0,json.dumps(raw),'')):
            self.assertEqual(module.simulator_state('owned'),{'udid':'owned','runtime':'runtime','state':'Shutdown'})
            self.assertEqual(module.simulator_state('missing')['state'],'UNMEASURED')
    def test_monotonic_stage_times_not_wall_clock_or_zero_defaults(self):
        with patch.object(module.time,'monotonic',side_effect=[100.0,100.25,101.0]):
            trace=module.Timeline();self.assertEqual(trace.mark('before')['elapsedMs'],250);self.assertEqual(trace.mark('after')['elapsedMs'],1000)
    def test_hash_and_unavailable_toolchain(self):
        with tempfile.TemporaryDirectory() as temp:
            path=Path(temp)/'config';path.write_bytes(b'configuration')
            self.assertEqual(module.configuration_hash(path),hashlib.sha256(b'configuration').hexdigest())
            self.assertIsNone(module.configuration_hash(path/'missing'))
        with patch.object(module.subprocess,'run',side_effect=OSError('unavailable')):
            self.assertEqual(module.toolchain()['version'],'UNMEASURED')
if __name__=='__main__':unittest.main()
