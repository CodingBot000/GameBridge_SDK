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
    print('Negative manifest: missing R49 rejected; original manifest unchanged.')
    return 0

if __name__ == '__main__': raise SystemExit(main())
