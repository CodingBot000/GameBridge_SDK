#!/usr/bin/env python3
"""Required scenario deletion must be rejected using a new manifest copy."""
import json
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

def main() -> int:
    artifacts = ROOT / 'artifacts'; artifacts.mkdir(exist_ok=True)
    workspace = Path(tempfile.mkdtemp(prefix='negative-manifest-', dir=artifacts))
    manifest = json.loads((ROOT / 'harness/regression-manifest.json').read_text(encoding='utf-8'))
    manifest['scenarios'] = [entry for entry in manifest['scenarios'] if entry['id'] != 'R49']
    path = workspace / 'manifest.json'; path.write_text(json.dumps(manifest), encoding='utf-8')
    result = subprocess.run(['python3','harness/check-manifest.py','--manifest',str(path)], cwd=ROOT,
                            text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False)
    if result.returncode == 0 or 'scenario IDs must match' not in result.stdout:
        print('Missing required scenario was not detected'); return 1
    manifest = json.loads((ROOT / 'harness/regression-manifest.json').read_text(encoding='utf-8'))
    manifest['suites'].pop('contracts')
    suite_path = workspace / 'missing-suite.json'; suite_path.write_text(json.dumps(manifest), encoding='utf-8')
    suite_result = subprocess.run(['python3','harness/check-manifest.py','--manifest',str(suite_path)], cwd=ROOT,
                                  text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False)
    if suite_result.returncode == 0 or 'unknown suite contracts' not in suite_result.stdout:
        print('Missing required suite was not detected'); return 1
    manifest = json.loads((ROOT / 'harness/regression-manifest.json').read_text(encoding='utf-8'))
    manifest['scenarios'][0]['coverage'] = 'IMPLEMENTED'
    coverage_path = workspace / 'false-coverage.json'; coverage_path.write_text(json.dumps(manifest), encoding='utf-8')
    coverage_result = subprocess.run(['python3','harness/check-manifest.py','--manifest',str(coverage_path)], cwd=ROOT,
                                     text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False)
    if coverage_result.returncode == 0 or 'implemented requires assertion mapping' not in coverage_result.stdout:
        print('Unsubstantiated implemented coverage was not detected'); return 1
    print('Negative manifest: missing R49 rejected; required suite removal and false coverage rejected; original manifest unchanged.')
    return 0

if __name__ == '__main__': raise SystemExit(main())
