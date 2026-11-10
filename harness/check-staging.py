#!/usr/bin/env python3
"""Verify a specified local UPM staging tree; no Unity execution is implied."""
import argparse
import hashlib
import json
import plistlib
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

def main() -> int:
    parser = argparse.ArgumentParser(); parser.add_argument('staging', type=Path); args = parser.parse_args()
    root = args.staging.resolve()
    try:
        if not root.is_dir(): raise ValueError('staging directory missing')
        lines = (root/'SHA256SUMS').read_text(encoding='utf-8').splitlines()
        expected = {}
        for line in lines:
            digest, rel = line.split('  ', 1)
            path = Path(rel)
            if not re.fullmatch(r'[0-9a-f]{64}', digest) or path.is_absolute() or '..' in path.parts or rel in expected:
                raise ValueError('invalid checksum entry')
            target = root/path
            if target.is_symlink() or not target.is_file() or not target.resolve().is_relative_to(root): raise ValueError('missing or unsafe file')
            if hashlib.sha256(target.read_bytes()).hexdigest() != digest: raise ValueError('checksum mismatch')
            expected[rel] = digest
        actual = {p.relative_to(root).as_posix() for p in root.rglob('*') if p.is_file() and p.relative_to(root).as_posix() != 'SHA256SUMS'}
        if not expected or set(expected) != actual: raise ValueError('checksum inventory differs')
        package = root/'com.gamebridge.sdk'; metadata = json.loads((package/'package.json').read_text(encoding='utf-8'))
        version = (ROOT/'VERSION').read_text(encoding='utf-8').strip()
        if metadata['version'] != version: raise ValueError('version mismatch')
        for sample in metadata['samples']:
            path = Path(sample['path'])
            if path.is_absolute() or '..' in path.parts or not (package/path).is_dir(): raise ValueError('sample missing')
        maven = package/'Editor/GameBridgeArtifacts~/Android/maven-repo/com/gamebridge'
        for module, ext in (('sdk-core','jar'),('sdk-android','aar'),('sdk-unity-bridge','aar')):
            folder = maven/module/version
            for suffix in ('pom', ext):
                if not (folder/f'{module}-{version}.{suffix}').is_file(): raise ValueError(f'{module} {suffix} missing')
        framework = package/'Editor/GameBridgeArtifacts~/iOS/GameBridgeNative.xcframework'
        info = plistlib.loads((framework/'Info.plist').read_bytes()); found = set()
        for library in info['AvailableLibraries']:
            if library.get('SupportedPlatform') == 'ios' and (framework/library['LibraryIdentifier']/library['LibraryPath']/'GameBridgeNative').is_file():
                found.add(library.get('SupportedPlatformVariant','device'))
        if not {'device','simulator'} <= found: raise ValueError('iOS slice missing')
    except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError, plistlib.InvalidFileException) as exc:
        print(f'STAGING_FAIL: {exc}', file=sys.stderr); return 1
    print(f'Staging integrity PASS: {len(expected)} files; Unity import/export not tested.')
    return 0

if __name__ == '__main__': raise SystemExit(main())
