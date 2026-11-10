#!/usr/bin/env python3
"""Verify iOS static XCFramework slices and exported C ABI, without executing it."""
import plistlib
from pathlib import Path
import shutil
import subprocess
import sys

REQUIRED = {'_GB_ProtocolVersion','_GB_SetCallback','_GB_Dispatch','_GB_Shutdown'}

def main():
    if len(sys.argv) != 2: print('Usage: verify-xcframework.py XCFRAMEWORK',file=sys.stderr); return 2
    if not shutil.which('xcrun'): print('DEFERRED_ENV: xcrun required for Mach-O validation',file=sys.stderr); return 2
    root=Path(sys.argv[1]).resolve()
    try:
        manifest=plistlib.loads((root/'Info.plist').read_bytes()); found={}
        for item in manifest['AvailableLibraries']:
            if item.get('SupportedPlatform') != 'ios': continue
            variant=item.get('SupportedPlatformVariant','device')
            if variant not in ('device','simulator') or variant in found: raise ValueError('unexpected or duplicate iOS slice')
            path=(root/item['LibraryIdentifier']/item['LibraryPath']/'GameBridgeNative').resolve()
            if not path.is_relative_to(root) or not path.is_file(): raise ValueError(f'{variant} binary missing or unsafe')
            arches=set(subprocess.run(['xcrun','lipo','-archs',str(path)],stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,check=True,timeout=30).stdout.split())
            needed={'arm64'} if variant=='device' else {'arm64','x86_64'}
            if not needed.issubset(arches): raise ValueError(f'{variant} architectures missing')
            for arch in needed:
                result=subprocess.run(['xcrun','nm','-arch',arch,'-g',str(path)],stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,check=True,timeout=30)
                exported={line.split()[-1] for line in result.stdout.splitlines() if line.split() and ' T ' in line}
                if not REQUIRED.issubset(exported): raise ValueError(f'{variant}/{arch} C ABI symbols missing')
            found[variant]=True
        if set(found) != {'device','simulator'}: raise ValueError('required iOS slice missing')
    except (OSError,ValueError,KeyError,TypeError,plistlib.InvalidFileException,subprocess.SubprocessError) as error:
        print(f'XCFRAMEWORK_FAIL: {error}',file=sys.stderr); return 1
    print('XCFramework validation PASS: device arm64, simulator arm64/x86_64, four C ABI symbols per arch.'); return 0

if __name__=='__main__': raise SystemExit(main())
