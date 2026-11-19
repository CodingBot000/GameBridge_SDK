"""Exercise scenario execution with disposable manifests and marker commands."""
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


class ManifestExecutionGuardTests(unittest.TestCase):
    def test_invalid_commands_never_execute(self):
        (ROOT / 'artifacts').mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(prefix='p09-marker-') as external:
            marker = Path(external) / 'executed'
            program = Path(external) / 'write_marker.py'
            program.write_text('from pathlib import Path\nPath(' + repr(str(marker)) + ').write_text("executed")\n')
            with tempfile.TemporaryDirectory(prefix='p09-path-', dir=ROOT / 'artifacts') as local:
                link = Path(local) / 'outside.py'; link.symlink_to(program)
                rel_link = str(link.relative_to(ROOT))
                escape = os.path.relpath(program, ROOT)
                attacks = [
                    ['python3', str(program)],
                    ['python3', escape],
                    ['python3', rel_link],
                    ['sh', '-c', f'touch {marker}'],
                    ['bash', '-c', f'touch {marker}'],
                    ['python3', '-c', f'open({str(marker)!r}, "w").close()'],
                    ['python3', 'harness/run-contracts.py', '--unreviewed'],
                    ['android/gradlew', '-p', 'android', '--init-script', str(program)],
                ]
                original = json.loads((ROOT / 'harness/regression-manifest.json').read_text())
                for index, command in enumerate(attacks):
                    with self.subTest(index=index):
                        manifest = json.loads(json.dumps(original))
                        manifest['suites']['contracts']['command'] = command
                        path = Path(local) / f'manifest-{index}.json'
                        path.write_text(json.dumps(manifest))
                        result = subprocess.run([sys.executable, 'harness/run-scenario.py', 'R01', '--manifest', str(path)],
                                                cwd=ROOT, text=True, capture_output=True, timeout=30, check=False)
                        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
                        self.assertIn('no suites executed', result.stderr)
                        self.assertFalse(marker.exists(), 'untrusted command executed')
                # The complete manifest must be checked before even an unrelated valid suite runs.
                result = subprocess.run([sys.executable, 'harness/run-scenario.py', 'R50', '--manifest', str(path)],
                                        cwd=ROOT, text=True, capture_output=True, timeout=30, check=False)
                self.assertEqual(result.returncode, 1)
                self.assertIn('no suites executed', result.stderr)
                self.assertNotIn('R50 /', result.stdout)
                self.assertFalse(marker.exists())

    def test_malformed_manifest_never_runs_a_suite(self):
        with tempfile.TemporaryDirectory(prefix='p09-malformed-') as temp:
            path = Path(temp) / 'manifest.json'
            for value in ('{', '[]', '{}', 'null'):
                with self.subTest(value=value):
                    path.write_text(value)
                    result = subprocess.run([sys.executable, 'harness/run-scenario.py', 'R50', '--manifest', str(path)],
                                            cwd=ROOT, text=True, capture_output=True, timeout=30, check=False)
                    self.assertEqual(result.returncode, 1)
                    self.assertIn('Manifest validation failed', result.stderr)
                    self.assertNotIn('R50 /', result.stdout)

    def test_valid_scenario_runs(self):
        result = subprocess.run([sys.executable, 'harness/run-scenario.py', 'R50'], cwd=ROOT,
                                text=True, capture_output=True, timeout=60, check=False)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn('R50 PASS:', result.stdout)
        self.assertIn('R50 / r50-negative: exit 0', result.stdout)


if __name__ == '__main__':
    unittest.main()
