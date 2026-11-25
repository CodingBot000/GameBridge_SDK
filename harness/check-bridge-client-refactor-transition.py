#!/usr/bin/env python3
"""Verify the fixed SDK refactor delta and run the original guard at its baseline."""
from collections import Counter
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import stat
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
BASE = '6ff2cafa1c54863720ffccd17c2164c30a119bfd'
RECORD = 'contracts/bridge-client-refactor-transition.json'
BRIDGE = 'android/sdk-unity-bridge/src/main/kotlin/com/gamebridge/bridge/'
UPM = 'unity/Packages/com.gamebridge.sdk/'
MANAGED = UPM + 'Runtime/'
REFACTOR_FILES = {
    BRIDGE + 'BridgeFacade.kt', BRIDGE + 'BridgeStoreLifecycle.kt', BRIDGE + 'BridgeFcmRegistration.kt',
    MANAGED + 'GameBridgeClient.cs', MANAGED + 'SdkStatusModels.cs', MANAGED + 'SdkStatusModels.cs.meta',
    MANAGED + 'Core/DiagnosticDecoder.cs', MANAGED + 'Core/DiagnosticDecoder.cs.meta',
    MANAGED + 'Core/CapabilityDecoder.cs', MANAGED + 'Core/CapabilityDecoder.cs.meta',
}
VERSION_FILES = {
    'VERSION',
    'android/sdk-core/src/main/kotlin/com/gamebridge/Version.kt',
    'ios/Sources/GameBridgeCore/Version.swift',
    MANAGED + 'Core/EditorOfflineTransport.cs',
    UPM + 'package.json',
}
VERSION = '0.1.2-dev'
SCOPES = ('VERSION', 'android', 'ios', 'unity', 'backend', 'contracts', 'config', 'infra')
BRIDGE_TESTS = 'android/sdk-unity-bridge/src/test/'
ORIGINAL_GUARDS = (
    'harness/check-social-auth-transition.py', 'harness/check-api-baseline.py',
    'harness/check-core-refactor-surface.py', 'harness/check-feature-refactor-transition.py',
)


def git(root, *args):
    return subprocess.check_output(['git', *args], cwd=root)


def safe_path(root, name):
    relative = PurePosixPath(name)
    if relative.is_absolute() or '..' in relative.parts or name != relative.as_posix() or not relative.parts:
        raise ValueError('invalid path: ' + name)
    path = root
    for part in relative.parts:
        path = path / part
        if path.is_symlink():
            raise ValueError('symlink refused: ' + name)
    return path


def collect(root, baseline=None):
    if baseline is not None:
        raw = git(root, 'ls-tree', '-r', '-z', baseline, '--name-only', '--', *SCOPES)
    else:
        raw = git(root, 'ls-files', '-z', '--cached', '--', *SCOPES)
        # Gradle creates these compiler sessions during a concurrent Native build.
        # A tracked file there still participates in the shipping inventory.
        raw += git(root, 'ls-files', '-z', '--others', '--exclude-standard', '--', *SCOPES,
                   ':(exclude,glob)**/.kotlin/sessions/*.salive')
    files = {}
    for name in sorted(set(os.fsdecode(raw).split('\0')) - {'', RECORD}):
        if name.startswith(BRIDGE_TESTS):
            continue
        if baseline is not None:
            files[name] = git(root, 'show', baseline + ':' + name)
        else:
            path = safe_path(root, name)
            if path.exists():
                if not stat.S_ISREG(path.stat().st_mode):
                    raise ValueError('non-file shipping path: ' + name)
                files[name] = path.read_bytes()
    return files


def sha256(data):
    return None if data is None else hashlib.sha256(data).hexdigest()


def managed_surface(files):
    signatures = Counter()
    for name, data in files.items():
        if name.startswith(MANAGED) and name.endswith('.cs'):
            signatures.update(
                ' '.join(line.split()) for line in data.decode().splitlines()
                if re.match(r'^\s*(public|protected)\s+', line)
            )
    return signatures


def c_exports(files):
    return sorted(
        match for name, data in files.items() if name.startswith('ios/UnityBridge/') and name.endswith('.swift')
        for match in re.findall(rb'@_cdecl\("([^"]+)"\)', data)
    )


def verify_version(files):
    if files['VERSION'].decode().strip() != VERSION or json.loads(files[UPM + 'package.json'])['version'] != VERSION:
        raise ValueError('VERSION and UPM metadata differ from candidate version')
    for name in (VERSION_FILES - {'VERSION', UPM + 'package.json'}) | {MANAGED + 'SdkStatusModels.cs'}:
        if files[name].count(f'"{VERSION}"'.encode()) != 1:
            raise ValueError('candidate Native/managed version mismatch: ' + name)


def verify_transition(before, after, record):
    if record['baselineSourceCommit'] != BASE or record['sdkVersion'] != VERSION:
        raise ValueError('fixed baseline or SDK version changed')
    allowed = REFACTOR_FILES | VERSION_FILES
    entries = record['changes']
    paths = [entry['path'] for entry in entries]
    if len(paths) != len(set(paths)) or set(paths) != allowed:
        raise ValueError('invalid or duplicate reviewed path')
    delta = {name for name in before.keys() | after.keys() if before.get(name) != after.get(name)}
    if delta != allowed:
        raise ValueError('shipping delta differs from reviewed paths: ' + ', '.join(sorted(delta ^ allowed)))
    for item in entries:
        name = item['path']
        old = sha256(before.get(name))
        new = sha256(after.get(name))
        if new is None or item['beforeSha256'] != old or item['afterSha256'] != new:
            raise ValueError('reviewed preimage/postimage mismatch: ' + name)
    if managed_surface(before) != managed_surface(after):
        raise ValueError('managed public declarations changed')
    if c_exports(before) != c_exports(after):
        raise ValueError('Swift C ABI names changed')
    for files in (before, after):
        enum = re.search(rb'public enum AuthProvider\s*\{([^}]+)\}', files[MANAGED + 'GameBridgeClient.cs'])
        if enum is None or enum[1].replace(b' ', b'').split(b',') != [b'MOCK', b'GOOGLE', b'APPLE', b'FACEBOOK']:
            raise ValueError('AuthProvider ordinal drift')
    verify_version(after)


def verify_original_guards(root):
    for name in ORIGINAL_GUARDS:
        if safe_path(root, name).read_bytes() != git(root, 'show', BASE + ':' + name):
            raise ValueError('original guard changed: ' + name)
    with tempfile.TemporaryDirectory(prefix='bridge-refactor-baseline-') as directory:
        historical = Path(directory) / 'source'
        git(root, 'clone', '--quiet', '--shared', '--no-checkout', '--', str(root), str(historical))
        git(historical, 'checkout', '--quiet', '--detach', BASE)
        subprocess.run(
            [sys.executable, str(historical / ORIGINAL_GUARDS[0])],
            cwd=historical, check=True,
            env={**os.environ, 'PYTHONDONTWRITEBYTECODE': '1'},
        )


def main():
    try:
        git(ROOT, 'merge-base', '--is-ancestor', BASE, 'HEAD')
        record = json.loads(safe_path(ROOT, RECORD).read_text())
        verify_transition(collect(ROOT, BASE), collect(ROOT), record)
        verify_original_guards(ROOT)
    except (OSError, ValueError, KeyError, TypeError, subprocess.SubprocessError) as error:
        print('Bridge/client refactor transition FAIL:', error, file=sys.stderr)
        return 1
    print('Bridge/client refactor transition PASS: reviewed shipping paths, version and source surfaces')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
