"""Guard independent sandbox evidence and fail-closed self-check aggregation."""
import importlib.util
import tempfile
import unittest
from pathlib import Path

spec = importlib.util.spec_from_file_location('self_check', Path(__file__).with_name('run-self-check.py'))
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class SelfCheckReportTests(unittest.TestCase):
    def test_named_sandbox_case_is_required(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / 'junit.xml'
            def write(name, failure='', skips=0):
                path.write_text(f'<testsuite tests="1" failures="0" errors="0" skipped="{skips}"><testcase name="{name}">{failure}</testcase></testsuite>')
            name = 'sandbox rejects mock identity token with 401()'
            write(name)
            self.assertEqual(module.sandbox_report(path, 0, 0)['status'], 'PASS')
            self.assertEqual(module.sandbox_report(path, path.stat().st_mtime_ns + 1, 0)['status'], 'FAIL')
            write('unrelated test')
            self.assertEqual(module.sandbox_report(path, 0, 0)['status'], 'FAIL')
            write(name, '<failure message="wrong"/>')
            self.assertEqual(module.sandbox_report(path, 0, 0)['status'], 'FAIL')
            write(name, '<skipped/>', 1)
            self.assertNotEqual(module.sandbox_report(path, 0, 0)['status'], 'PASS')
            write(name)
            self.assertNotEqual(module.sandbox_report(path, 0, 1)['status'], 'PASS')

    def test_checks_are_not_test_counts_and_gate_is_fail_closed(self):
        lanes = [{'name':'check','status':'PASS','required':True,'tests':0,'checks':1,'skipped':0,'exitCode':0}]
        self.assertEqual(module.summarize_lanes(lanes, {'check'})['exitCode'],0)
        self.assertEqual(lanes[0]['tests'],0)
        for changes in ({'checks':0}, {'skipped':1}, {'exitCode':1}, {'status':'FAIL'}):
            self.assertNotEqual(module.summarize_lanes([{**lanes[0], **changes}], {'check'})['exitCode'],0)
        self.assertNotEqual(module.summarize_lanes(lanes, {'check','missing'})['exitCode'],0)


if __name__ == '__main__':
    unittest.main()
