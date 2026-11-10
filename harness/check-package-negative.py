#!/usr/bin/env python3
"""Check missing artifact and existing-output rejection using new fake-only fixtures."""
import plistlib
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

def main() -> int:
    artifacts = ROOT/'artifacts'; artifacts.mkdir(exist_ok=True)
    workspace = Path(tempfile.mkdtemp(prefix='package-negative-', dir=artifacts)); maven = workspace/'maven'; ios = workspace/'ios'
    for module, ext in (('sdk-core','jar'),('sdk-android','aar'),('sdk-unity-bridge','aar')):
        folder = maven/'com/gamebridge'/module/'0.1.0-dev'; folder.mkdir(parents=True)
        (folder/f'{module}-0.1.0-dev.pom').write_text('test-only')
        if module != 'sdk-unity-bridge': (folder/f'{module}-0.1.0-dev.{ext}').write_text('test-only')
    info = {'AvailableLibraries':[{'SupportedPlatform':'ios','LibraryIdentifier':'device','LibraryPath':'GameBridgeNative.framework'},
                                  {'SupportedPlatform':'ios','SupportedPlatformVariant':'simulator','LibraryIdentifier':'sim','LibraryPath':'GameBridgeNative.framework'}]}
    ios.mkdir(); (ios/'Info.plist').write_bytes(plistlib.dumps(info))
    device = ios/'device/GameBridgeNative.framework'; device.mkdir(parents=True); (device/'GameBridgeNative').write_text('test-only')
    script = ROOT/'scripts/package-sdk.sh'
    def attempt(output): return subprocess.run(['bash',str(script),str(maven),str(ios),str(output)],cwd=ROOT,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,check=False)
    output = workspace/'output'; missing_android = attempt(output)
    if missing_android.returncode == 0 or 'Missing sdk-unity-bridge binary' not in missing_android.stdout or output.exists(): return 1
    folder = maven/'com/gamebridge/sdk-unity-bridge/0.1.0-dev'; (folder/'sdk-unity-bridge-0.1.0-dev.aar').write_text('test-only')
    missing_ios = attempt(output)
    if missing_ios.returncode == 0 or 'Missing XCFramework device/simulator slices' not in missing_ios.stdout or output.exists(): return 1
    simulator = ios/'sim/GameBridgeNative.framework'; simulator.mkdir(parents=True); (simulator/'GameBridgeNative').write_text('test-only')
    output.mkdir(); sentinel = output/'sentinel'; sentinel.write_text('preserve')
    existing = attempt(output)
    if existing.returncode == 0 or 'Output already exists' not in existing.stdout or sentinel.read_text() != 'preserve': return 1
    print('Package negatives PASS: missing Android/iOS artifacts and existing output rejected; fixtures only.')
    return 0

if __name__ == '__main__': raise SystemExit(main())
