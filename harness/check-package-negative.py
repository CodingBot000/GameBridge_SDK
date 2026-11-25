#!/usr/bin/env python3
"""Check missing artifact and existing-output rejection using new fake-only fixtures."""
import plistlib
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

VERSION=(ROOT/"VERSION").read_text().strip()

def main() -> int:
    artifacts = ROOT/'artifacts'; artifacts.mkdir(exist_ok=True)
    workspace = Path(tempfile.mkdtemp(prefix='package-negative-', dir=artifacts)); maven = workspace/'maven'; ios = workspace/'ios'
    for module, ext in (('sdk-core','jar'),('sdk-android','aar'),('sdk-unity-bridge','aar')):
        folder = maven/'com/gamebridge'/module/VERSION; folder.mkdir(parents=True)
        (folder/f'{module}-{VERSION}.pom').write_text('test-only')
        if module != 'sdk-unity-bridge': (folder/f'{module}-{VERSION}.{ext}').write_text('test-only')
    info = {'GameBridgeSDKVersion': VERSION, 'AvailableLibraries':[{'SupportedPlatform':'ios','LibraryIdentifier':'device','LibraryPath':'GameBridgeNative.framework'},
                                  {'SupportedPlatform':'ios','SupportedPlatformVariant':'simulator','LibraryIdentifier':'sim','LibraryPath':'GameBridgeNative.framework'}]}
    ios.mkdir(); (ios/'Info.plist').write_bytes(plistlib.dumps(info))
    device = ios/'device/GameBridgeNative.framework'; device.mkdir(parents=True); (device/'GameBridgeNative').write_text('test-only')
    script = ROOT/'scripts/package-sdk.sh'
    def attempt(output): return subprocess.run(['bash',str(script),str(maven),str(ios),str(output)],cwd=ROOT,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,check=False)
    output = workspace/'output'; missing_android = attempt(output)
    if missing_android.returncode == 0 or 'Missing sdk-unity-bridge binary' not in missing_android.stdout or output.exists(): return 1
    folder = maven/f'com/gamebridge/sdk-unity-bridge/{VERSION}'; (folder/f'sdk-unity-bridge-{VERSION}.aar').write_text('test-only')
    missing_ios = attempt(output)
    if missing_ios.returncode == 0 or 'Missing XCFramework device/simulator slices' not in missing_ios.stdout or output.exists(): return 1
    simulator = ios/'sim/GameBridgeNative.framework'; simulator.mkdir(parents=True); (simulator/'GameBridgeNative').write_text('test-only')
    info['GameBridgeSDKVersion'] = '0.0.0-dev'
    (ios/'Info.plist').write_bytes(plistlib.dumps(info))
    wrong_version = attempt(output)
    if wrong_version.returncode == 0 or 'SDK version mismatch' not in wrong_version.stdout or output.exists(): return 1
    info['GameBridgeSDKVersion'] = VERSION
    (ios/'Info.plist').write_bytes(plistlib.dumps(info))
    output.mkdir(); sentinel = output/'sentinel'; sentinel.write_text('preserve')
    existing = attempt(output)
    if existing.returncode == 0 or 'Output already exists' not in existing.stdout or sentinel.read_text() != 'preserve': return 1
    print('Package negatives PASS: missing Android/iOS artifacts, mixed SDK versions and existing output rejected; fixtures only.')
    return 0

if __name__ == '__main__': raise SystemExit(main())
