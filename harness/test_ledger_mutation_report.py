"""Ensure only fresh, expected ledger-invariant reports can pass the mutation gate."""
import importlib.util
import tempfile
import time
import unittest
from pathlib import Path

spec = importlib.util.spec_from_file_location('ledger_mutation', Path(__file__).with_name('check-ledger-mutation.py'))
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class LedgerReportTests(unittest.TestCase):
    def test_report_checks_expected_failure_and_freshness(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'report.xml'
            message = 'Expected an exception of class org.springframework.dao.DataIntegrityViolationException to be thrown, but was completed successfully.'
            def write(failures, body, errors=0, skipped=0, name=module.TEST_NAME):
                path.write_text(f'<testsuite tests="1" failures="{failures}" errors="{errors}" skipped="{skipped}"><testcase name="{name}">{body}</testcase></testsuite>')
            write(1, f'<failure message="{message}"/>')
            self.assertTrue(module.valid_report(path, 0, True))
            self.assertFalse(module.valid_report(path, time.time_ns() + 1_000_000_000, True))
            write(1, '<failure message="Expected an exception: unrelated"/>')
            self.assertFalse(module.valid_report(path, 0, True))
            write(1, f'<failure message="{message}"/>', skipped=1)
            self.assertFalse(module.valid_report(path, 0, True))
            write(1, f'<failure message="{message}"/>', name='other test')
            self.assertFalse(module.valid_report(path, 0, True))
            write(0, '')
            self.assertTrue(module.valid_report(path, 0, False))
            write(0, '', errors=1)
            self.assertFalse(module.valid_report(path, 0, False))


if __name__ == '__main__':
    unittest.main()
