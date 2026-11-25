#!/usr/bin/env python3
"""Run frozen P08/P10 guards on their closed source, then verify doc37's exact social delta.

No frozen manifest/snapshot or legacy guard is rewritten. This source lock does not
claim binary ABI, real OAuth, Unity Player or release readiness.
"""
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
BEFORE = 'dc3ed4224d1c676e33ee92e8aa7aa6ceaa3c7855'
APPROVED = '23536d22ed5a11c919c65b411c8807ff07e42b37'
LOGOUT_BASE = '09db0706f0e53693d9fd44df290d9da4c49aba6b'
LOGOUT_FILES = {'ios/UnityBridge/AppleAuthBridgeHandler.swift', 'ios/UnityBridge/PlatformAuthBridgeHandler.swift'}
VERSION_BASE = '3d9d5b8e6e906c78affd4d53444c544b762afe30'
VERSION_FILES = (
    'android/sdk-core/src/main/kotlin/com/gamebridge/Version.kt',
    'ios/Sources/GameBridgeCore/Version.swift',
    'unity/Packages/com.gamebridge.sdk/Runtime/GameBridgeClient.cs',
    'unity/Packages/com.gamebridge.sdk/Runtime/Core/EditorOfflineTransport.cs',
)
RECORD = ROOT / 'contracts/social-auth-transition.json'
spec = importlib.util.spec_from_file_location('feature_closed_transition', ROOT/'harness/check-feature-refactor-transition.py')
legacy = importlib.util.module_from_spec(spec)
spec.loader.exec_module(legacy)


def check_transition(before, approved, current, record):
    errors = []
    delta = {p for p in set(before['files']) | set(approved['files']) if before['files'].get(p) != approved['files'].get(p)}
    changes = record.get('changes', [])
    if not isinstance(changes, list) or any(not isinstance(v, dict) for v in changes):
        return ['invalid social transition entries']
    indexed = {v.get('path'): v for v in changes}
    if len(indexed) != len(changes) or set(indexed) != delta:
        return ['social transition path set mismatch']
    if set(current['files']) != set(approved['files']):
        errors.append('shipping file set drift outside approved social source')
    for path in set(before['files']) | set(approved['files']):
        old = before['files'].get(path)
        new = approved['files'].get(path)
        if path in delta:
            item = indexed[path]
            if item.get('beforeSha256') != (old or {}).get('sha256') or item.get('afterSha256') != (new or {}).get('sha256'):
                errors.append('reviewed preimage/postimage mismatch: ' + path)
        if current['files'].get(path) != new:
            errors.append('unapproved source/declaration change: ' + path)
    if not set(before['swiftCExports']).issubset(approved['swiftCExports']):
        errors.append('legacy C ABI export removed')
    if sorted(approved['swiftCExports']) != sorted(before['swiftCExports'] + ['GB_HandleAuthURL']):
        errors.append('unexpected approved C ABI addition')
    if current['swiftCExports'] != approved['swiftCExports']:
        errors.append('current C ABI export drift')
    return errors


def check_logout_transition(closed, current, transition):
    if transition.get('before') != LOGOUT_BASE or set(transition.get('files', {})) != LOGOUT_FILES:
        return ['iOS logout transition scope mismatch']
    expected = dict(closed['files'])
    for name, hashes in transition['files'].items():
        if hashes.get('before') != closed['files'][name]['sha256'] or not re.fullmatch('[a-f0-9]{64}', hashes.get('after', '')):
            return ['invalid reviewed logout transition: ' + name]
        expected[name] = dict(expected[name], sha256=hashes['after'])
    if current['files'] != expected or current['swiftCExports'] != closed['swiftCExports']:
        return ['shipping source, public contract or C ABI drift outside reviewed iOS logout transition']
    return []


def main():
    try:
        record = json.loads(RECORD.read_text())
        if record.get('before') != BEFORE or record.get('approvedSource') != APPROVED:
            raise ValueError('fixed social authorization source mismatch')
        for ref in (BEFORE, APPROVED, LOGOUT_BASE, VERSION_BASE):
            subprocess.run(['git', 'merge-base', '--is-ancestor', ref, 'HEAD'], cwd=ROOT, check=True, capture_output=True)
        # Frozen guards and every frozen baseline file must remain byte-identical.
        frozen = subprocess.check_output(['git', 'ls-tree', '-r', '--name-only', BEFORE, '--', 'contracts/baseline'], cwd=ROOT, text=True).splitlines()
        frozen += ['harness/check-api-baseline.py', 'harness/check-core-refactor-surface.py', 'harness/check-feature-refactor-transition.py']
        for name in frozen:
            expected = subprocess.check_output(['git', 'show', BEFORE+':'+name], cwd=ROOT)
            path = ROOT/name
            if path.is_symlink() or path.read_bytes() != expected:
                raise ValueError('frozen guard/baseline altered: '+name)
        before = legacy.snapshot_at(BEFORE)
        approved = legacy.snapshot_at(APPROVED)
        current = legacy.core.snapshot()
        closed = legacy.snapshot_at(LOGOUT_BASE)
        errors = check_transition(before, approved, closed, record)
        transition = json.loads((ROOT/'contracts/ios-logout-transition.json').read_text())
        version_base = legacy.snapshot_at(VERSION_BASE)
        errors += check_logout_transition(closed, version_base, transition)
        version = (ROOT/'VERSION').read_text().strip()
        expected = dict(version_base['files'])
        for name in VERSION_FILES:
            old = subprocess.check_output(['git', 'show', VERSION_BASE+':'+name], cwd=ROOT)
            if old.count(b'"0.1.0-dev"') != 1 or not re.fullmatch(r'[0-9]+\.[0-9]+\.[0-9]+-dev', version):
                raise ValueError('invalid SDK version transition')
            data = old.replace(b'"0.1.0-dev"', ('"' + version + '"').encode())
            expected[name] = dict(expected[name], sha256=hashlib.sha256(data).hexdigest())
        if current['files'] != expected or current['swiftCExports'] != version_base['swiftCExports']:
            errors.append('shipping source, public contract or C ABI drift outside reviewed SDK version files')
        for name in current['files']:
            if (ROOT/name).is_symlink():
                errors.append('shipping source symlink refused: '+name)
        enum_path = 'unity/Packages/com.gamebridge.sdk/Runtime/GameBridgeClient.cs'
        old_cs = subprocess.check_output(['git', 'show', BEFORE+':'+enum_path], cwd=ROOT, text=True)
        new_cs = (ROOT/enum_path).read_text()
        def members(text):
            return [x.strip() for x in re.search(r'public enum AuthProvider\s*\{([^}]+)\}', text)[1].split(',')]
        if members(old_cs) != ['MOCK', 'GOOGLE', 'APPLE'] or members(new_cs) != members(old_cs) + ['FACEBOOK']:
            errors.append('AuthProvider legacy ordinal/addition drift')
        if errors:
            for error in errors:
                print(error)
            return 1
        # Run the unmodified guards in an owned historical checkout so Git path
        # discovery and byte comparisons use the original repository root.
        (ROOT/'artifacts').mkdir(exist_ok=True)
        destination = Path(tempfile.mkdtemp(prefix='social-closed-', dir=ROOT/'artifacts'))/'source'
        subprocess.run(['git', 'worktree', 'add', '--detach', str(destination), BEFORE], cwd=ROOT, check=True, stdout=subprocess.DEVNULL)
        for guard in ['check-api-baseline.py', 'check-feature-refactor-transition.py']:
            subprocess.run([sys.executable, str(destination/'harness'/guard)], cwd=destination, check=True)
        print('Frozen P08/P10 guards PASS at closed source; reviewed social and iOS logout source/API/export transitions PASS')
        return 0
    except (OSError, ValueError, KeyError, TypeError, AttributeError, subprocess.SubprocessError) as error:
        print('Social transition FAIL:', type(error).__name__)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
