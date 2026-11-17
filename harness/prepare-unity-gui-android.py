#!/usr/bin/env python3
"""Fresh GUI Android consumer using existing prepare/build sources; never launches Unity."""
import argparse
import importlib.util
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import uuid
from gui_verification import file_hash

ROOT = Path(__file__).resolve().parent.parent


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--prepare', required=True, action='store_true')
    p.add_argument('--staging', required=True, type=Path)
    p.add_argument('--package-cache', required=True, type=Path)
    p.add_argument('--variant', choices=('standard', 'pii', 'utf8'), default='pii')
    p.add_argument('--project-label', default='GameBridgeGuiAndroidB29')
    a = p.parse_args(); stage = a.staging.resolve()
    if not re.fullmatch(r'GameBridgeGuiAndroid[A-Za-z0-9_-]*',a.project_label):raise SystemExit('Owned test project label required')
    subprocess.run(['python3','harness/check-staging.py',str(stage)], cwd=ROOT, check=True)
    spec=importlib.util.spec_from_file_location('consumer',ROOT/'harness/run-unity-android-mock-e2e.py')
    common=importlib.util.module_from_spec(spec); spec.loader.exec_module(common)
    common.verify_staged_source_matches_checkout(stage)
    env=os.environ.copy(); env['GAMEBRIDGE_UPM_STAGING']=str(stage)
    text=subprocess.check_output(['bash','scripts/prepare-unity-android-mock.sh','--prepare'], cwd=ROOT, env=env, text=True)
    match=re.search(r'^Prepared consumer: (/.+)$',text,re.M)
    if not match: raise SystemExit('Prepared consumer path missing')
    source=Path(match.group(1)).resolve()
    if not source.is_relative_to(ROOT/'artifacts'): raise SystemExit('Unexpected consumer path')
    project=source.with_name(a.project_label); source.rename(project)
    spec=importlib.util.spec_from_file_location('cache',ROOT/'harness/run-unity-ios-mock-push-e2e.py')
    cache=importlib.util.module_from_spec(spec); spec.loader.exec_module(cache)
    packages=cache.embed_cached_packages(a.package_cache.resolve(),project)
    if a.variant!='standard':
        folder='UnityAndroidPiiConsumer' if a.variant=='pii' else 'UnityAndroidUtf8Consumer'
        shutil.copyfile(ROOT/'tests'/folder/'MockPlayerScenario.cs',project/'Assets/MockPlayerScenario.cs')
    if a.variant=='pii':
        shutil.copyfile(ROOT/'tests/UnityPiiProbe/PiiProbe.cs',project/'Assets/PiiProbe.cs')
        shutil.copyfile(ROOT/'tests/UnityLateCallbackPlayer/link.xml',project/'Assets/link.xml')
    for name in ('GameBridgeGuiVerification.cs','GuiAndroidBuild.cs'):
        shutil.copyfile(ROOT/'tests/UnityGuiVerification'/name,project/'Assets/Editor'/name)
    shutil.copyfile(stage/'SHA256SUMS',project/'GameBridgeStaging.SHA256SUMS')
    config=dict(schemaVersion=1,runId=uuid.uuid4().hex,operation='android',
        sourceHead=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        projectRoot=str(project),expectedUnityVersion='6000.5.8f1',variant=a.variant,
        outputPath=str(project.parent/'gamebridge-gui-mock.apk'),
        scriptSha256=file_hash(project/'Assets/Editor/GameBridgeGuiVerification.cs'),
        adapterSha256=file_hash(project/'Assets/Editor/GuiAndroidBuild.cs'),
        buildScriptSha256=file_hash(project/'Assets/Editor/BuildMockPlayer.cs'),
        scenarioSha256=file_hash(project/'Assets/MockPlayerScenario.cs'),stagingManifestSha256=file_hash(stage/'SHA256SUMS'))
    (project/'GameBridgeGuiRun.json').write_text(json.dumps(config,indent=2)+'\n')
    (project.parent/'gui-preparation.json').write_text(json.dumps({'config':config,'embeddedCachedPackages':packages},indent=2)+'\n')
    print('Prepared GUI consumer:',project)
    print('GUI output:',config['outputPath'])
    print('NOT_RUN: open via Hub, Switch Android Target, then Build Android Mock')


if __name__=='__main__':main()
