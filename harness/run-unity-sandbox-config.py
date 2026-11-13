#!/usr/bin/env python3
"""Opt-in sandbox missing-configuration Player test; no real provider calls."""
import argparse
import importlib.util
import json
import os
from pathlib import Path
import re
import secrets
import shutil
import subprocess
import tempfile
import threading
import time
ROOT=Path(__file__).resolve().parent.parent
spec=importlib.util.spec_from_file_location('android_e2e',ROOT/'harness/run-unity-android-mock-e2e.py');common=importlib.util.module_from_spec(spec);spec.loader.exec_module(common)


def markers_pass(text,platform):
    return all(marker in text for marker in ('GB_SANDBOX_CONFIG_CAPABILITIES PASS','GB_SANDBOX_CONFIG_NO_FALLBACK PASS','GB_SANDBOX_CONFIG_RESULT PASS '+platform.upper()))


def main():
    p=argparse.ArgumentParser();p.add_argument('--run-local',required=True,action='store_true');p.add_argument('--platform',choices=('android','ios'),required=True);p.add_argument('--staging',type=Path,required=True);p.add_argument('--package-cache',type=Path,required=True);p.add_argument('--serial');p.add_argument('--expected-avd');a=p.parse_args()
    artifacts=ROOT/'artifacts';artifacts.mkdir(exist_ok=True);out=Path(tempfile.mkdtemp(prefix='unity-sandbox-config-'+a.platform+'-',dir=artifacts));result={'status':'FAIL','scope':'sandbox configuration only; no account or remote service','platform':a.platform,'player':'NOT_RUN'};player=None;markers=[]
    try:
        result['sourceHead']=common.must(['git','rev-parse','HEAD'],'GIT_HEAD').strip();result['sourceTrackedDirty']=bool(common.must(['git','status','--porcelain','--untracked-files=no'],'GIT_STATUS').strip())
        stage=a.staging.resolve();common.must(['python3','harness/check-staging.py',stage],'STAGING_INVALID');common.verify_staged_source_matches_checkout(stage)
        env=os.environ.copy();env['GAMEBRIDGE_UPM_STAGING']=str(stage)
        if a.platform=='android':
            if not a.serial or not a.expected_avd:raise common.GateError('DEDICATED_AVD_REQUIRED','DEFERRED_ENV')
            adb=common.locate_adb(None)
            if not adb:raise common.GateError('ADB_MISSING','DEFERRED_ENV')
            serial,avd=common.wait_for_dedicated_device(adb,a.serial,a.expected_avd);result['avd']=avd
        prepare='scripts/prepare-unity-'+a.platform+'-mock.sh';prepared=common.must(['bash',prepare,'--prepare'],'PREPARE_FAILED',env=env);match=re.search(r'^Prepared consumer: (/.+)$',prepared,re.M)
        if not match:raise common.GateError('CONSUMER_PATH_MISSING')
        project=Path(match.group(1));cache_spec=importlib.util.spec_from_file_location('cache',ROOT/'harness/run-unity-ios-mock-push-e2e.py');cache=importlib.util.module_from_spec(cache_spec);cache_spec.loader.exec_module(cache)
        try:cache.embed_cached_packages(a.package_cache.resolve(),project)
        except cache.common.GateError as error:raise common.GateError(str(error),error.category) from error
        if a.platform=='android':
            shutil.copy2(ROOT/'tests/UnitySandboxConfig/Android/MockPlayerScenario.cs',project/'Assets/MockPlayerScenario.cs');apk=out/'config-test.apk'
            build=common.run(['bash','scripts/build-unity-android-mock.sh',project,apk],timeout=1200,env=env);(out/'unity-build.log').write_text(build.stdout)
            if build.returncode:raise common.GateError('UNITY_BUILD_FAILED','DEFERRED_ENV' if build.returncode==2 else 'FAIL')
            common.wait_for_dedicated_device(adb,serial,avd);installed=common.must([adb,'-s',serial,'install',apk],'INSTALL_FAILED',timeout=120)
            if 'Success' not in installed:raise common.GateError('INSTALL_RESULT_MISSING')
            common.must([adb,'-s',serial,'logcat','-c'],'LOGCAT_CLEAR');launched=common.must([adb,'-s',serial,'shell','am','start','-W','-n',common.PACKAGE+'/com.unity3d.player.UnityPlayerGameActivity'],'LAUNCH_FAILED',timeout=30)
            if not re.search(r'^Status:\s*ok\s*$',launched,re.M):raise common.GateError('LAUNCH_RESULT_MISSING')
            result['player']='LAUNCHED_PENDING';deadline=time.monotonic()+120
            while time.monotonic()<deadline:
                raw=common.must([adb,'-s',serial,'logcat','-d','-v','brief','-s','Unity:I','*:S'],'LOGCAT_FAILED',timeout=20);markers=[line for line in raw.splitlines() if 'GB_SANDBOX_CONFIG_' in line];text='\n'.join(markers)
                if 'GB_SANDBOX_CONFIG_RESULT FAIL' in text:raise common.GateError('PLAYER_REPORTED_FAILURE')
                if 'GB_SANDBOX_CONFIG_RESULT PASS ANDROID' in text:break
                time.sleep(1)
            else:raise common.GateError('PLAYER_TIMEOUT','DEFERRED_ENV')
        else:
            shutil.copy2(ROOT/'tests/UnitySandboxConfig/iOS/MockIosPlayerScenario.cs',project/'Assets/MockIosPlayerScenario.cs');xcode=out/'xcode'
            export=common.run(['bash','scripts/build-unity-ios-mock.sh',project,xcode],timeout=1200,env=env);(out/'unity-export.log').write_text(export.stdout)
            if export.returncode:raise common.GateError('UNITY_EXPORT_FAILED','DEFERRED_ENV' if export.returncode==2 else 'FAIL')
            derived=out/'Derived';build=common.run(['xcodebuild','-project',xcode/'Unity-iPhone.xcodeproj','-scheme','Unity-iPhone','-configuration','Debug','-sdk','iphonesimulator','-derivedDataPath',derived,'ARCHS=arm64','CODE_SIGN_IDENTITY=-','CODE_SIGNING_REQUIRED=YES','build','-quiet'],timeout=600);(out/'xcodebuild.log').write_text(build.stdout)
            if build.returncode:raise common.GateError('XCODE_BUILD_FAILED')
            app=next((derived/'Build/Products/Debug-iphonesimulator').glob('*.app'),None)
            if app is None:raise common.GateError('SIMULATOR_APP_MISSING')
            sim=common.must(['xcrun','simctl','create','GameBridge-iOS-Config-'+secrets.token_hex(5),'com.apple.CoreSimulator.SimDeviceType.iPhone-16','com.apple.CoreSimulator.SimRuntime.iOS-18-6'],'SIMULATOR_CREATE',category='DEFERRED_ENV').strip();result['simulator']=sim
            for command in (['boot',sim],['bootstatus',sim,'-b'],['install',sim,app]):common.must(['xcrun','simctl']+command,'SIMULATOR_'+command[0].upper(),timeout=180)
            player=subprocess.Popen(['xcrun','simctl','launch','--console',sim,'com.gamebridge.sdk.mockiosconsumer'],cwd=ROOT,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,bufsize=1)
            def collect():
                for line in player.stdout:
                    if 'GB_SANDBOX_CONFIG_' in line:markers.append(line.strip())
            threading.Thread(target=collect,daemon=True).start();result['player']='LAUNCHED_PENDING';deadline=time.monotonic()+120
            while time.monotonic()<deadline:
                text='\n'.join(markers)
                if 'GB_SANDBOX_CONFIG_RESULT FAIL' in text:raise common.GateError('PLAYER_REPORTED_FAILURE')
                if 'GB_SANDBOX_CONFIG_RESULT PASS IOS' in text:break
                if player.poll() is not None:raise common.GateError('PLAYER_EXITED')
                time.sleep(1)
            else:raise common.GateError('PLAYER_TIMEOUT','DEFERRED_ENV')
        if not markers_pass('\n'.join(markers),a.platform):raise common.GateError('CONFIG_MARKERS_MISSING')
        (out/'config-markers.log').write_text('\n'.join(markers)+'\n');result.update(status='PASS',player='PASS',missingKeys='PASS',noFallback='PASS')
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
