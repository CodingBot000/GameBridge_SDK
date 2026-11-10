#!/usr/bin/env python3
"""Mutate only fresh local framework copies and require slice/symbol validation to fail."""
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

ROOT=Path(__file__).resolve().parent.parent

def main():
    raw=os.environ.get('GAMEBRIDGE_IOS_XCFRAMEWORK',''); source=Path(raw).resolve() if raw else None
    if source is None or not (source/'Info.plist').is_file() or not shutil.which('xcrun'):
        print('CONFIG_REQUIRED: built GAMEBRIDGE_IOS_XCFRAMEWORK and Xcode tools',file=sys.stderr); return 2
    artifacts=ROOT/'artifacts'; artifacts.mkdir(exist_ok=True); work=Path(tempfile.mkdtemp(prefix='ios-xcframework-negative-',dir=artifacts))
    def verify(path): return subprocess.run([sys.executable,'scripts/verify-xcframework.py',str(path)],cwd=ROOT,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=60)
    try:
        valid=verify(source)
        if valid.returncode != 0: raise ValueError('original framework validation failed')
        copy=work/'GameBridgeNative.xcframework'; shutil.copytree(source,copy)
        simulator=copy/'ios-arm64_x86_64-simulator/GameBridgeNative.framework/GameBridgeNative'; simulator.unlink()
        missing=verify(copy)
        if missing.returncode != 1 or 'binary missing' not in missing.stdout: raise ValueError('missing simulator slice not detected')
        shutil.copy2(source/'ios-arm64_x86_64-simulator/GameBridgeNative.framework/GameBridgeNative',simulator)
        cfile=work/'missing.c'; obj=work/'missing.o'; cfile.write_text('int GB_ProtocolVersion(void) { return 1; }\n')
        compile_result=subprocess.run(['xcrun','--sdk','iphoneos','clang','-target','arm64-apple-ios16.0','-c',str(cfile),'-o',str(obj)],stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,timeout=60)
        if compile_result.returncode != 0: raise ValueError('test archive compile failed')
        device=copy/'ios-arm64/GameBridgeNative.framework/GameBridgeNative'; device.unlink()
        archive=subprocess.run(['xcrun','libtool','-static','-o',str(device),str(obj)],stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,timeout=60)
        if archive.returncode != 0: raise ValueError('test archive creation failed')
        symbols=verify(copy)
        if symbols.returncode != 1 or 'C ABI symbols missing' not in symbols.stdout: raise ValueError('missing exported C symbols not detected')
    except (OSError,ValueError,subprocess.TimeoutExpired) as error:
        print(f'iOS framework negative failed: {error}; evidence: {work.relative_to(ROOT)}',file=sys.stderr); return 1
    print(f'iOS XCFramework negatives PASS: missing simulator binary and device symbols rejected; evidence directory: {work.relative_to(ROOT)}'); return 0

if __name__=='__main__': raise SystemExit(main())
