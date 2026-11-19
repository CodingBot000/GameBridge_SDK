"""Check aggregate exit behavior in disposable stub-only workspaces."""
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


class SmokeLocalExitTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.scripts = Path(self.temp.name) / 'scripts'
        self.scripts.mkdir()
        shutil.copy(ROOT / 'scripts/smoke-local.sh', self.scripts)
        for name in ('auth', 'purchase', 'device'):
            (self.scripts / f'smoke-{name}-local.py').write_text('raise SystemExit(0)\n')
        self.env = os.environ.copy()
        self.env['GAMEBRIDGE_DEV_AUTH_KEY'] = 'synthetic-key-for-test-only'
        self.env.pop('GAMEBRIDGE_LOCAL_SMOKE_OPT_IN', None)

    def tearDown(self):
        self.temp.cleanup()

    def run_smoke(self):
        return subprocess.run(['bash', str(self.scripts / 'smoke-local.sh')], env=self.env,
                              text=True, capture_output=True, check=False)

    def test_explicit_opt_in_is_required(self):
        self.assertEqual(self.run_smoke().returncode, 2)

    def test_failure_is_propagated_and_success_is_scoped(self):
        self.env['GAMEBRIDGE_LOCAL_SMOKE_OPT_IN'] = '1'
        (self.scripts / 'smoke-purchase-local.py').write_text('raise SystemExit(1)\n')
        failed = self.run_smoke()
        self.assertEqual(failed.returncode, 1)
        self.assertNotIn('backend smoke: PASS', failed.stdout)
        (self.scripts / 'smoke-purchase-local.py').write_text('raise SystemExit(0)\n')
        passed = self.run_smoke()
        self.assertEqual(passed.returncode, 0)
        self.assertIn('LOCAL_MOCK backend smoke: PASS', passed.stdout)
        self.assertIn('NOT_RUN: Unity player', passed.stdout)


if __name__ == '__main__':
    unittest.main()
