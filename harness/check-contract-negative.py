#!/usr/bin/env python3
"""Corrupt only a new fixture copy and require the contract runner to detect it."""
import json
import os
import shutil
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

def main() -> int:
    artifacts = ROOT / 'artifacts'; artifacts.mkdir(exist_ok=True)
    workspace = Path(tempfile.mkdtemp(prefix='negative-contract-', dir=artifacts))
    contracts = workspace / 'contracts'; contracts.mkdir()
    shutil.copytree(ROOT / 'contracts/fixtures', contracts / 'fixtures')
    request = contracts / 'fixtures/bridge/request.json'
    value = json.loads(request.read_text()); value['protocolVersion'] = 99
    request.write_text(json.dumps(value) + '\n')
    env = os.environ.copy(); env['GAMEBRIDGE_CONTRACT_ROOT'] = str(contracts)
    try:
        run = subprocess.run(['python3','harness/run-contracts.py'], cwd=ROOT, env=env, text=True,
                             stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=600, check=False)
    except (OSError, subprocess.TimeoutExpired): print('Negative contract run unavailable'); return 2
    (workspace / 'negative.log').write_text(run.stdout, encoding='utf-8')
    if run.returncode != 1 or 'kotlin: FAIL' not in run.stdout or 'swift: FAIL' not in run.stdout or 'csharp: PASS' not in run.stdout:
        print('Negative contract mutation was not detected by both Kotlin and Swift'); return 1
    print('Negative contract: Kotlin and Swift rejected invalid copied request; original fixtures unchanged.')
    print('Negative evidence directory:', workspace.relative_to(ROOT))
    return 0

if __name__ == '__main__': raise SystemExit(main())
