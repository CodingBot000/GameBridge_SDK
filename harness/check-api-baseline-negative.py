#!/usr/bin/env python3
"""Verify a public declaration change is detected in a new source copy."""
import importlib.util
import json
import shutil
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.dont_write_bytecode = True
spec = importlib.util.spec_from_file_location('baseline_checker', ROOT/'harness/check-api-baseline.py')
checker = importlib.util.module_from_spec(spec); spec.loader.exec_module(checker)

def main() -> int:
    artifacts = ROOT/'artifacts'; artifacts.mkdir(exist_ok=True)
    workspace = Path(tempfile.mkdtemp(prefix='api-negative-',dir=artifacts))
    manifest = json.loads((ROOT/'contracts/baseline/manifest.json').read_text(encoding='utf-8'))
    for item in manifest['files']:
        source = ROOT/item['source']; target = workspace/item['source']; target.parent.mkdir(parents=True,exist_ok=True); shutil.copyfile(source,target)
    client = workspace/'unity/Packages/com.gamebridge.sdk/Runtime/GameBridgeClient.cs'
    text = client.read_text(encoding='utf-8'); old = 'public event Action<PushUpdate> PushReceived;'
    if text.count(old) != 1: print('Mutation target changed'); return 1
    client.write_text(text.replace(old,'public event Action<PushUpdate> RenamedPushReceived;'),encoding='utf-8')
    errors = checker.check(workspace)
    if not any('C# public declaration changed' in error for error in errors): print('Public API mutation not detected'); return 1
    print('Public API mutation detected in isolated copy; original unchanged.')
    return 0

if __name__ == '__main__': raise SystemExit(main())
