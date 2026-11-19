"""A real timed-out subprocess must preserve partial evidence without becoming PASS."""
import importlib.util
import os
import sys
import tempfile
import unittest
from pathlib import Path
from result_aggregator import summarize

spec=importlib.util.spec_from_file_location('auth_diagnostics',Path(__file__).with_name('run-auth-regression.py'))
common=importlib.util.module_from_spec(spec);spec.loader.exec_module(common)


class RuntimeDiagnosticsTests(unittest.TestCase):
    def test_partial_output_survives_real_timeout_but_never_passes(self):
        with tempfile.TemporaryDirectory() as folder:
            log=Path(folder)/'timeout.log'
            command=[sys.executable,'-u','-c',"import time;print('partial PASS marker',flush=True);time.sleep(30)"]
            code,text,_=common.run(command,os.environ.copy(),log,timeout=1)
            self.assertEqual(code,2)
            self.assertIn('partial PASS marker',text)
            self.assertEqual(log.read_text(),text)
            lane=common.item('partial',code,(1,0,0),error_model='checker-exit')
            lane.update(name='partial',required=True)
            self.assertNotEqual(summarize([lane])['exitCode'],0)

if __name__=='__main__':unittest.main()
