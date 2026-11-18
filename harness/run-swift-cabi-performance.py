#!/usr/bin/env python3
"""Opt-in dedicated Simulator measurement. Retains its device and shuts down only its UUID."""
import json, platform, subprocess, uuid
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def main():
    import argparse
    parser=argparse.ArgumentParser();parser.add_argument('--run-local',required=True,action='store_true');parser.parse_args()
    out=ROOT/'artifacts'/('swift-cabi-performance-'+uuid.uuid4().hex);out.mkdir()
    def run(args):return subprocess.run(args,cwd=ROOT,text=True,capture_output=True,timeout=180,check=True)
    runtime='com.apple.CoreSimulator.SimRuntime.iOS-18-6'
    runtimes=json.loads(run(['xcrun','simctl','list','runtimes','-j']).stdout)['runtimes']
    if not any(r['identifier']==runtime and r['isAvailable'] for r in runtimes):
        print('DEFERRED_ENV: iOS18.6 unavailable');return 2
    sdk=run(['xcrun','--sdk','iphonesimulator','--show-sdk-path']).stdout.strip()
    binary=out/'coordinator'
    run(['xcrun','swiftc','-O','-parse-as-library','-sdk',sdk,'-target','arm64-apple-ios18.0-simulator',
         'harness/performance/SwiftCAbi.swift','-F',str(ROOT/'artifacts/batch33/ios/GameBridgeNative.xcframework/ios-arm64_x86_64-simulator'),'-framework','GameBridgeNative','-o',str(binary)])
    name='GameBridge-Perf-'+uuid.uuid4().hex
    device=run(['xcrun','simctl','create',name,'com.apple.CoreSimulator.SimDeviceType.iPhone-16',runtime]).stdout.strip()
    owned=False
    try:
        devices=json.loads(run(['xcrun','simctl','list','devices','-j']).stdout)['devices'].get(runtime,[])
        owned=any(d['udid']==device and d['name']==name for d in devices)
        if not owned:raise ValueError('Simulator ownership mismatch')
        run(['xcrun','simctl','boot',device]);run(['xcrun','simctl','bootstatus',device,'-b'])
        raw=run(['xcrun','simctl','spawn',device,str(binary)])
        (out/'stdout.log').write_text(raw.stdout);(out/'stderr.log').write_text(raw.stderr)
        result=json.loads(raw.stdout.strip().splitlines()[-1])
        result.update(sourceHead=run(['git','rev-parse','HEAD']).stdout.strip(),simulatorUUID=device,simulatorName=name,runtime=runtime,host=platform.platform(),swiftVersion=run(['xcrun','swiftc','--version']).stdout.strip(),status='PASS' if result['harnessOutstandingCallbacks']==0 and result['callbacks']==360 else 'FAIL')
        (out/'result.json').write_text(json.dumps(result,indent=2)+'\n');print('Evidence directory:',out.relative_to(ROOT))
        return 0 if result['status']=='PASS' else 1
    finally:
        if owned:run(['xcrun','simctl','shutdown',device])
if __name__=='__main__':raise SystemExit(main())
