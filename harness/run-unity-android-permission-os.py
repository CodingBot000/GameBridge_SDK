#!/usr/bin/env python3
"""Opt-in real Android emulator notification denial; no remote Firebase use."""
import argparse
import importlib.util
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import time
import xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parent.parent
spec=importlib.util.spec_from_file_location('android_e2e',ROOT/'harness/run-unity-android-mock-e2e.py');common=importlib.util.module_from_spec(spec);spec.loader.exec_module(common)
REQUIRED=('GB_PERMISSION_FIRST_DENIED PASS','GB_PERMISSION_REGISTRATION_CODE PERMISSION_DENIED','GB_PERMISSION_REGISTRATION_BLOCKED PASS','GB_PERMISSION_SECOND_DENIED PASS','GB_PERMISSION_RESULT PASS ANDROID_OS_DENIED')


def button_center(xml, tutorial=False):
    try: root=ET.fromstring(xml[xml.index('<?xml'):])
    except (ValueError,ET.ParseError):return None
    matches=[]
    for node in root.iter('node'):
        resource=node.get('resource-id','');text=node.get('text','')
        allowed=(tutorial and text=='Got it') or (not tutorial and any(resource.endswith(':id/'+name) for name in ('permission_deny_button','permission_deny_and_dont_ask_again_button')))
        bounds=re.fullmatch(r'\[(\d+),(\d+)\]\[(\d+),(\d+)\]',node.get('bounds',''))
        if allowed and bounds:
            x1,y1,x2,y2=map(int,bounds.groups());matches.append(((x1+x2)//2,(y1+y2)//2))
    return matches[0] if len(matches)==1 else None


def markers_pass(text):
    return all(marker in text for marker in REQUIRED)


def main():
    p=argparse.ArgumentParser();p.add_argument('--run-local',required=True,action='store_true');p.add_argument('--staging',type=Path,required=True);p.add_argument('--serial',required=True);p.add_argument('--expected-avd',required=True);p.add_argument('--package-cache',type=Path,required=True);a=p.parse_args()
    artifacts=ROOT/'artifacts';artifacts.mkdir(exist_ok=True);out=Path(tempfile.mkdtemp(prefix='unity-android-permission-',dir=artifacts));result={'status':'FAIL','scope':'Android emulator real OS permission denial; not FCM','player':'NOT_RUN'}
    try:
        result['sourceHead']=common.must(['git','rev-parse','HEAD'],'GIT_HEAD').strip();result['sourceTrackedDirty']=bool(common.must(['git','status','--porcelain','--untracked-files=no'],'GIT_STATUS').strip())
        stage=a.staging.resolve();common.must(['python3','harness/check-staging.py',stage],'STAGING_INVALID');common.verify_staged_source_matches_checkout(stage)
        adb=common.locate_adb(None)
        if not adb:raise common.GateError('ADB_MISSING','DEFERRED_ENV')
        serial,avd=common.wait_for_dedicated_device(adb,a.serial,a.expected_avd);result['avd']=avd
        env=os.environ.copy();env['GAMEBRIDGE_UPM_STAGING']=str(stage)
        prepared=common.must(['bash','scripts/prepare-unity-android-mock.sh','--prepare'],'PREPARE_FAILED',env=env);match=re.search(r'^Prepared consumer: (/.+)$',prepared,re.M)
        if not match:raise common.GateError('CONSUMER_PATH_MISSING')
        project=Path(match.group(1));cache_spec=importlib.util.spec_from_file_location('cache',ROOT/'harness/run-unity-ios-mock-push-e2e.py');cache=importlib.util.module_from_spec(cache_spec);cache_spec.loader.exec_module(cache)
        try:cache.embed_cached_packages(a.package_cache.resolve(),project)
        except cache.common.GateError as error:raise common.GateError(str(error),error.category) from error
        shutil.copy2(ROOT/'tests/UnityAndroidPermissionConsumer/MockPlayerScenario.cs',project/'Assets/MockPlayerScenario.cs')
        shutil.copy2(ROOT/'tests/UnityAndroidPermissionConsumer/PermissionFirebaseDependency.cs',project/'Assets/Editor/PermissionFirebaseDependency.cs')
        manifest=project/'Assets/Plugins/Android/AndroidManifest.xml';text=manifest.read_text();
        if text.count('<application ')!=1 or text.count('</application>')!=1:raise common.GateError('MANIFEST_SHAPE')
        text=text.replace('<application ','<uses-permission android:name="android.permission.POST_NOTIFICATIONS"/><application ',1).replace('</application>','<meta-data android:name="unityplayer.SkipPermissionsDialog" android:value="true"/></application>',1);manifest.write_text(text)
        apk=out/'permission-test.apk';built=common.run(['bash','scripts/build-unity-android-mock.sh',project,apk],timeout=1200,env=env);(out/'unity-build.log').write_text(built.stdout)
        if built.returncode:raise common.GateError('UNITY_BUILD_FAILED','DEFERRED_ENV' if built.returncode==2 else 'FAIL')
        common.wait_for_dedicated_device(adb,serial,avd)
        install=common.must([adb,'-s',serial,'install',apk],'INSTALL_FAILED',timeout=120)
        if 'Success' not in install:raise common.GateError('INSTALL_RESULT_MISSING')
        common.must([adb,'-s',serial,'logcat','-c'],'LOGCAT_CLEAR');launch=common.must([adb,'-s',serial,'shell','am','start','-W','-n',common.PACKAGE+'/com.unity3d.player.UnityPlayerGameActivity'],'LAUNCH_FAILED',timeout=30)
        if not re.search(r'^Status:\s*ok\s*$',launch,re.M):raise common.GateError('LAUNCH_RESULT_MISSING')
        result['player']='LAUNCHED_PENDING';deadline=time.monotonic()+150;last_tap=0
        while time.monotonic()<deadline:
            raw=common.must([adb,'-s',serial,'logcat','-d','-v','brief','-s','Unity:I','*:S'],'LOGCAT_FAILED',timeout=20)
            lines=[line for line in raw.splitlines() if 'GB_PERMISSION_' in line];joined='\n'.join(lines)
            if 'GB_PERMISSION_RESULT FAIL' in joined:raise common.GateError('PLAYER_REPORTED_FAILURE')
            if 'GB_PERMISSION_RESULT PASS ANDROID_OS_DENIED' in joined:
                if not markers_pass(joined):raise common.GateError('PERMISSION_MARKERS_MISSING')
                (out/'permission-markers.log').write_text(joined+'\n');result.update(status='PASS',player='PASS',osDenial='PASS',registrationBlocked='PASS',rerequest='PASS');break
            if time.monotonic()-last_tap>2:
                focus=common.run([adb,'-s',serial,'shell','dumpsys','window'],timeout=15).stdout
                if 'ImmersiveModeConfirmation' in focus or 'permissioncontroller' in focus.lower():
                    dump=common.run([adb,'-s',serial,'shell','uiautomator','dump','/sdcard/gamebridge-permission.xml'],timeout=15)
                    if dump.returncode==0:
                        xml=common.run([adb,'-s',serial,'shell','cat','/sdcard/gamebridge-permission.xml'],timeout=15).stdout
                        point=button_center(xml,'ImmersiveModeConfirmation' in focus)
                        if point:common.must([adb,'-s',serial,'shell','input','tap',str(point[0]),str(point[1])],'DIALOG_TAP_FAILED');last_tap=time.monotonic()
            time.sleep(1)
        else:raise common.GateError('OS_DIALOG_OR_PLAYER_TIMEOUT','DEFERRED_ENV')
    except KeyboardInterrupt:result.update(status='INTERRUPTED',errorCode='USER_OR_ENV_INTERRUPTION')
    except common.GateError as error:result.update(status=error.category,errorCode=str(error))
    except (OSError,ValueError,subprocess.SubprocessError) as error:result['errorCode']=type(error).__name__
    finally:(out/'result.json').write_text(json.dumps(result,indent=2)+'\n')
    print('RESULT',result['status'],result.get('errorCode',''),'EVIDENCE',out.relative_to(ROOT));return 0 if result['status']=='PASS' else 2 if result['status']=='DEFERRED_ENV' else 130 if result['status']=='INTERRUPTED' else 1
if __name__=='__main__':raise SystemExit(main())
