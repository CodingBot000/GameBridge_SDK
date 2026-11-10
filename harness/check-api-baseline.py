#!/usr/bin/env python3
"""Compare P08 source snapshots; this is not a binary/Unity compatibility test."""
import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

def declarations(data: bytes) -> list[str]:
    text = data.decode('utf-8')
    return [re.sub(r'\s+', ' ', line.strip()) for line in text.splitlines()
            if re.match(r'^\s*(?:\[[^]]+\]\s*)?public\s+', line)]

def check(current_root: Path = ROOT) -> list[str]:
    errors = []
    try:
        manifest = json.loads((ROOT/'contracts/baseline/manifest.json').read_text(encoding='utf-8'))
        files = manifest['files']
        if not files: return ['baseline has no files']
        for item in files:
            source = Path(item['source']); snapshot = Path(item['snapshot'])
            if source.is_absolute() or snapshot.is_absolute() or '..' in source.parts or '..' in snapshot.parts:
                errors.append('unsafe baseline path'); continue
            before = (ROOT/snapshot).read_bytes(); after = (current_root/source).read_bytes()
            if hashlib.sha256(before).hexdigest() != item['sha256']:
                errors.append(f'baseline hash mismatch: {source}'); continue
            if source.suffix == '.cs':
                old, new = declarations(before), declarations(after)
                if not old or old != new: errors.append(f'C# public declaration changed: {source}')
            elif before != after: errors.append(f'non-C# snapshot changed: {source}')
    except (OSError, UnicodeError, ValueError, KeyError, TypeError) as exc:
        errors.append(f'baseline read failed: {exc}')
    return errors

def main() -> int:
    errors = check()
    if errors:
        for error in errors: print(error, file=sys.stderr)
        return 1
    print('Baseline source comparison PASS; binary and Unity compatibility not tested.')
    return 0

if __name__ == '__main__': raise SystemExit(main())
