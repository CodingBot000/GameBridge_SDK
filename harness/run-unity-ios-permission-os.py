#!/usr/bin/env python3
"""Opt-in real iOS Simulator denial; GUI denial is required, never APNs."""
import argparse
import importlib.util
import json
import os
from pathlib import Path
import re
import secrets
import shutil
import subprocess
import sys
import tempfile
import threading
import time
ROOT=Path(__file__).resolve().parent.parent
spec=importlib.util.spec_from_file_location('android_e2e',ROOT/'harness/run-unity-android-mock-e2e.py');common=importlib.util.module_from_spec(spec);spec.loader.exec_module(common)
REQUIRED=('GB_IOS_PERMISSION_FIRST_DENIED PASS','GB_IOS_PERMISSION_REGISTRATION_CODE PERMISSION_DENIED','GB_IOS_PERMISSION_REGISTRATION_BLOCKED PASS','GB_IOS_PERMISSION_SECOND_DENIED PASS','GB_IOS_PERMISSION_RESULT PASS IOS_OS_DENIED')

def markers_pass(text):return all(marker in text for marker in REQUIRED)

def main():
    p=argparse.ArgumentParser();p.add_argument('--run-local',required=True,action='store_true');p.add_argument('--staging',type=Path,required=True);p.add_argument('--package-cache',type=Path,required=True);a=p.parse_args()
    artifacts=ROOT/'artifacts';artifacts.mkdir(exist_ok=True);out=Path(tempfile.mkdtemp(prefix='unity-ios-permission-',dir=artifacts));result={'status':'FAIL','scope':'iOS Simulator real OS permission denial; not APNs','player':'NOT_RUN'};player=None;markers=[]
    try:
        result['sourceHead']=common.must(['git','rev-parse','HEAD'],'GIT_HEAD').strip();result['sourceTrackedDirty']=bool(common.must(['git','status','--porcelain','--untracked-files=no'],'GIT_STATUS').strip())
        stage=a.staging.resolve();common.must(['python3','harness/check-staging.py',stage],'STAGING_INVALID');common.verify_staged_source_matches_checkout(stage)
        env=os.environ.copy();env['GAMEBRIDGE_UPM_STAGING']=str(stage)
        prepared=common.must(['bash','scripts/prepare-unity-ios-mock.sh','--prepare'],'PREPARE_FAILED',env=env);match=re.search(r'^Prepared consumer: (/.+)$',prepared,re.M)
        if not match:raise common.GateError('CONSUMER_PATH_MISSING')
        project=Path(match.group(1));cache_spec=importlib.util.spec_from_file_location('cache',ROOT/'harness/run-unity-ios-mock-push-e2e.py');cache=importlib.util.module_from_spec(cache_spec);cache_spec.loader.exec_module(cache)
        try:cache.embed_cached_packages(a.package_cache.resolve(),project)
        except cache.common.GateError as error:raise common.GateError(str(error),error.category) from error
        shutil.copy2(ROOT/'tests/UnityIosPermissionConsumer/MockIosPlayerScenario.cs',project/'Assets/MockIosPlayerScenario.cs')
        xcode=out/'xcode';export=common.run(['bash','scripts/build-unity-ios-mock.sh',project,xcode],timeout=1200,env=env);(out/'unity-export.log').write_text(export.stdout)
        if export.returncode:raise common.GateError('UNITY_EXPORT_FAILED','DEFERRED_ENV' if export.returncode==2 else 'FAIL')
        derived=out/'Derived';build=common.run(['xcodebuild','-project',xcode/'Unity-iPhone.xcodeproj','-scheme','Unity-iPhone','-configuration','Debug','-sdk','iphonesimulator','-derivedDataPath',derived,'ARCHS=arm64','CODE_SIGN_IDENTITY=-','CODE_SIGNING_REQUIRED=YES','build','-quiet'],timeout=600);(out/'xcodebuild.log').write_text(build.stdout)
        if build.returncode:raise common.GateError('XCODE_BUILD_FAILED')
        app=next((derived/'Build/Products/Debug-iphonesimulator').glob('*.app'),None)
        if app is None:raise common.GateError('SIMULATOR_APP_MISSING')
        sim=common.must(['xcrun','simctl','create','GameBridge-iOS-Permission-'+secrets.token_hex(5),'com.apple.CoreSimulator.SimDeviceType.iPhone-16','com.apple.CoreSimulator.SimRuntime.iOS-18-6'],'SIMULATOR_CREATE',category='DEFERRED_ENV').strip();result['simulator']=sim
        for command in (['boot',sim],['bootstatus',sim,'-b'],['install',sim,app]):common.must(['xcrun','simctl']+command,'SIMULATOR_'+command[0].upper(),timeout=180)
        player=subprocess.Popen(['xcrun','simctl','launch','--console',sim,'com.gamebridge.sdk.mockiosconsumer'],cwd=ROOT,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,bufsize=1)
        def collect():
            for line in player.stdout:
                if 'GB_IOS_PERMISSION_' in line:markers.append(line.strip())
        threading.Thread(target=collect,daemon=True).start();result['player']='LAUNCHED_PENDING';deadline=time.monotonic()+150;announced=False
        while time.monotonic()<deadline:
            text='\n'.join(markers)
            if 'GB_IOS_PERMISSION_RESULT FAIL' in text:raise common.GateError('PLAYER_REPORTED_FAILURE')
            if 'GB_IOS_PERMISSION_REQUEST_FIRST' in text and not announced:
                print('AWAITING_IOS_OS_DENIAL simulator='+sim,flush=True);announced=True
            if 'GB_IOS_PERMISSION_RESULT PASS IOS_OS_DENIED' in text:
                if not markers_pass(text):raise common.GateError('PERMISSION_MARKERS_MISSING')
                (out/'permission-markers.log').write_text(text+'\n');result.update(status='PASS',player='PASS',osDenial='PASS',registrationBlocked='PASS',rerequest='PASS');break
            if player.poll() is not None:raise common.GateError('PLAYER_EXITED')
            time.sleep(1)
        else:raise common.GateError('OS_DIALOG_OR_PLAYER_TIMEOUT','DEFERRED_ENV')
    except KeyboardInterrupt:result.update(status='INTERRUPTED',errorCode='USER_OR_ENV_INTERRUPTION')
    except common.GateError as error:result.update(status=error.category,errorCode=str(error))
    except (OSError,ValueError,subprocess.SubprocessError) as error:result['errorCode']=type(error).__name__
    finally:
        if player and player.poll() is None:
            player.terminate()
            try:player.wait(timeout=10)
            except subprocess.TimeoutExpired:player.kill();player.wait()
        (out/'result.json').write_text(json.dumps(result,indent=2)+'\n')
    print('RESULT',result['status'],result.get('errorCode',''),'EVIDENCE',out.relative_to(ROOT));return 0 if result['status']=='PASS' else 2 if result['status']=='DEFERRED_ENV' else 130 if result['status']=='INTERRUPTED' else 1
if __name__=='__main__':raise SystemExit(main())
