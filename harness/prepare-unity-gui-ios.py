#!/usr/bin/env python3
"""Prepare a fresh GUI Simulator export consumer; never launches an Editor."""
import argparse, importlib.util, json, os, re, shutil, subprocess, uuid
from pathlib import Path
from gui_verification import file_hash, IOS_SCENARIOS, auxiliary_sources
ROOT=Path(__file__).resolve().parent.parent


def main():
    p=argparse.ArgumentParser();p.add_argument('--prepare',required=True,action='store_true')
    p.add_argument('--staging',required=True,type=Path);p.add_argument('--package-cache',required=True,type=Path)
    p.add_argument('--variant',choices=tuple(IOS_SCENARIOS),default='pii');p.add_argument('--project-label',default='GameBridgeGuiIosB29');a=p.parse_args();stage=a.staging.resolve()
    if not re.fullmatch(r'GameBridgeGuiIos[A-Za-z0-9_-]*',a.project_label):raise SystemExit('Owned GUI iOS project label required')
    subprocess.run(['python3','harness/check-staging.py',str(stage)],cwd=ROOT,check=True)
    spec=importlib.util.spec_from_file_location('source',ROOT/'harness/run-unity-android-mock-e2e.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);m.verify_staged_source_matches_checkout(stage)
    subprocess.run(['python3','scripts/verify-xcframework.py',str(stage/'com.gamebridge.sdk/Editor/GameBridgeArtifacts~/iOS/GameBridgeNative.xcframework')],cwd=ROOT,check=True)
    env=os.environ.copy();env['GAMEBRIDGE_UPM_STAGING']=str(stage)
    text=subprocess.check_output(['bash','scripts/prepare-unity-ios-mock.sh','--prepare'],cwd=ROOT,env=env,text=True)
    match=re.search(r'^Prepared consumer: (/.+)$',text,re.M)
    if not match:raise SystemExit('Prepared project path missing')
    old=Path(match.group(1)).resolve()
    if not old.is_relative_to(ROOT/'artifacts'):raise SystemExit('Owned artifact project required')
    project=old.with_name(a.project_label);old.rename(project)
    spec=importlib.util.spec_from_file_location('cache',ROOT/'harness/run-unity-ios-mock-push-e2e.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);packages=m.embed_cached_packages(a.package_cache.resolve(),project)
    shutil.copyfile(ROOT/'tests'/IOS_SCENARIOS[a.variant]/'MockIosPlayerScenario.cs',project/'Assets/MockIosPlayerScenario.cs')
    for target,source in auxiliary_sources(a.variant):shutil.copyfile(ROOT/source,project/'Assets'/target)
    for name in ('GameBridgeGuiVerification.cs','GuiIosExport.cs'):shutil.copyfile(ROOT/'tests/UnityGuiVerification'/name,project/'Assets/Editor'/name)
    shutil.copyfile(stage/'SHA256SUMS',project/'GameBridgeStaging.SHA256SUMS')
    c=dict(schemaVersion=1,operation='ios',runId=uuid.uuid4().hex,sourceHead=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),projectRoot=str(project),expectedUnityVersion='6000.5.8f1',variant=a.variant,
        outputPath=str(project.parent/'xcode-gui'),scriptSha256=file_hash(project/'Assets/Editor/GameBridgeGuiVerification.cs'),adapterSha256=file_hash(project/'Assets/Editor/GuiIosExport.cs'),
        buildScriptSha256=file_hash(project/'Assets/Editor/BuildMockIosPlayer.cs'),scenarioSha256=file_hash(project/'Assets/MockIosPlayerScenario.cs'),stagingManifestSha256=file_hash(stage/'SHA256SUMS'))
    (project/'GameBridgeGuiRun.json').write_text(json.dumps(c,indent=2)+'\n');(project.parent/'gui-preparation.json').write_text(json.dumps({'config':c,'embeddedCachedPackages':packages},indent=2)+'\n')
    print('Prepared GUI consumer:',project);print('GUI output:',c['outputPath']);print('NOT_RUN: open via Hub, Switch iOS Target, Export iOS Mock')


if __name__=='__main__':main()
