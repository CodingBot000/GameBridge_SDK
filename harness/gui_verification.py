"""GUI receipts prove GUI scope only, never batch automation or Player execution."""
from datetime import datetime
import hashlib
import json
from pathlib import Path
import re
import subprocess


def file_hash(path):
    digest = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(block)
    return digest.hexdigest()


def validate_probe(value, config):
    for key in ('runId', 'sourceHead', 'scriptSha256'):
        if value.get(key) != config[key]:
            raise ValueError('GUI receipt correlation mismatch: ' + key)
    if type(value.get('schemaVersion')) is not int or value['schemaVersion'] != 1 or value.get('status') != 'PASS' or value.get('operation') != 'probe':
        raise ValueError('GUI probe did not pass')
    if value.get('isBatchMode') is not False or value.get('unityVersion') != config['expectedUnityVersion']:
        raise ValueError('GUI receipt mode/version mismatch')
    if Path(value.get('projectRoot', '')).resolve() != Path(config['projectRoot']).resolve():
        raise ValueError('GUI receipt project mismatch')
    if value.get('method') != 'GameBridgeGuiVerification.RunProbe' or value.get('assemblyName') != 'Assembly-CSharp-Editor':
        raise ValueError('GUI compiled method identity missing')
    for key in ('editorPid', 'checksExecuted'):
        if type(value.get(key)) is not int or value[key] == 0:
            raise ValueError('GUI runtime observations missing')
    if value.get('engineObjectName') != 'GameBridgeGuiProbe-' + config['runId']:
        raise ValueError('GUI engine object identity missing')
    if value['editorPid'] < 0:
        raise ValueError('GUI Editor PID invalid')
    if value['checksExecuted'] != 7 or value.get('engineObjectCreated') is not True or value.get('engineObjectDestroyed') is not True:
        raise ValueError('GUI engine object lifecycle incomplete')
    start = datetime.fromisoformat(value['startedUtc'].replace('Z', '+00:00'))
    end = datetime.fromisoformat(value['finishedUtc'].replace('Z', '+00:00'))
    if start.tzinfo is None or end.tzinfo is None or end < start:
        raise ValueError('GUI receipt timestamps invalid')
    return {'status': 'PASS', 'scope': 'GUI Editor compiled method and engine probe',
            'tests': 0, 'checks': 1, 'engineChecksExecuted': 7, 'players': 0,
            'batchAutomation': 'NOT_RUN'}


def read_probe(project, source_head):
    project = Path(project).resolve()
    config_path = project / 'GameBridgeGuiRun.json'
    config = json.loads(config_path.read_text())
    if not re.fullmatch(r'[0-9a-f]{32}', config.get('runId', '')):
        raise ValueError('GUI nonce invalid')
    if config['sourceHead'] != source_head or Path(config['projectRoot']).resolve() != project:
        raise ValueError('stale checkout/project config')
    if file_hash(project / 'Assets/Editor/GameBridgeGuiVerification.cs') != config['scriptSha256']:
        raise ValueError('GUI script source changed')
    path = project / 'GameBridgeGuiResults' / (config['runId'] + '.json')
    if path.stat().st_mtime_ns < config_path.stat().st_mtime_ns:
        raise ValueError('stale GUI receipt')
    value = json.loads(path.read_text(encoding='utf-8-sig'))
    return validate_probe(value, config), value


def validate_android_receipt(value, config):
    keys = ('runId', 'sourceHead', 'scriptSha256', 'adapterSha256', 'buildScriptSha256',
            'scenarioSha256', 'stagingManifestSha256', 'variant')
    if any(value.get(k) != config[k] for k in keys):
        raise ValueError('GUI Android build correlation mismatch')
    if (value.get('status') != 'PASS' or value.get('operation') != 'android' or
            type(value.get('schemaVersion')) is not int or value['schemaVersion'] != 1 or
            value.get('isBatchMode') is not False or value.get('unityVersion') != config['expectedUnityVersion'] or
            value.get('method') != 'GuiAndroidBuild.Build' or value.get('originalBuilderReturned') is not True or
            type(value.get('packageFilesVerified')) is not int or value['packageFilesVerified'] != 147):
        raise ValueError('GUI Android build incomplete')
    for k in ('projectRoot', 'outputPath'):
        if Path(value.get(k, '')).resolve() != Path(config[k]).resolve():
            raise ValueError('GUI Android build path mismatch')
    if type(value.get('artifactSize')) is not int or value['artifactSize'] <= 0 or not re.fullmatch(r'[0-9a-f]{64}', value.get('artifactSha256', '')):
        raise ValueError('GUI APK artifact proof missing')
    if type(value.get('editorPid')) is not int or value['editorPid'] <= 0:
        raise ValueError('GUI Editor PID missing')


def build_log_segment(text, nonce):
    start = 'GB_GUI_ANDROID_STARTED ' + nonce
    end = 'GB_GUI_ANDROID_PASS ' + nonce
    lines = text.splitlines()
    a = [i for i, l in enumerate(lines) if l.strip() == start]
    b = [i for i, l in enumerate(lines) if l.strip() == end]
    if len(a) != 1 or len(b) != 1 or a[0] >= b[0]:
        raise ValueError('GUI build log correlation missing/duplicate')
    selected = lines[a[0]:b[0]+1]
    if sum(l.strip() == 'GB_MOCK_BUILD PASS' for l in selected) != 1:
        raise ValueError('Original BuildMockPlayer verdict missing')
    return '\n'.join(selected) + '\n'


def validate_apk(path, value, config_mtime_ns):
    path = Path(path)
    if path.is_symlink() or not path.is_file() or path.stat().st_mtime_ns < config_mtime_ns:
        raise ValueError('GUI APK absent/stale/symlink')
    if path.stat().st_size != value['artifactSize'] or file_hash(path) != value['artifactSha256']:
        raise ValueError('GUI APK bytes changed')


def embedded_versions(project):
    versions={}
    for name,expected in [('com.unity.mobile.notifications','2.5.0'),('com.unity.nuget.newtonsoft-json','3.2.2')]:
        value=json.loads((Path(project)/'Packages'/name/'package.json').read_text())
        if value.get('name')!=name or value.get('version')!=expected:
            raise ValueError('GUI exact embedded package mismatch')
        versions[name]=expected
    return versions


def load_android_build(project, receipt_path, staging, current_head, variant):
    root = Path(__file__).resolve().parent.parent
    project, staging = Path(project).resolve(), Path(staging).resolve()
    if not project.is_relative_to((root/'artifacts').resolve()):
        raise ValueError('Owned GUI artifact project required')
    config_path = project/'GameBridgeGuiRun.json'; config = json.loads(config_path.read_text())
    if not re.fullmatch(r'[0-9a-f]{32}', config.get('runId', '')) or not re.fullmatch(r'[0-9a-f]{40}', config.get('sourceHead', '')):
        raise ValueError('GUI source/nonce invalid')
    expected_receipt = project/'GameBridgeGuiResults'/(config['runId']+'.json')
    if Path(receipt_path).resolve() != expected_receipt or expected_receipt.stat().st_mtime_ns < config_path.stat().st_mtime_ns:
        raise ValueError('GUI receipt path/freshness mismatch')
    value = json.loads(expected_receipt.read_text(encoding='utf-8-sig'))
    validate_android_receipt(value, config)
    if Path(config['projectRoot']).resolve() != project or config['variant'] != variant or config['operation'] != 'android':
        raise ValueError('GUI project/scenario mismatch')
    # A documentation/harness-only descendant may consume the same exact SDK build.
    # Changes to shipping Native/managed or any build/scenario source reject reuse.
    protected = ['unity/Packages/com.gamebridge.sdk', 'android/sdk-core/src/main', 'android/sdk-android/src/main',
                 'android/sdk-unity-bridge/src/main', 'ios/Sources', 'ios/UnityBridge', 'contracts',
                 'tests/UnityGuiVerification/GameBridgeGuiVerification.cs', 'tests/UnityGuiVerification/GuiAndroidBuild.cs', 'tests/UnityAndroidMockConsumer', 'tests/UnityAndroidPiiConsumer',
                 'tests/UnityAndroidUtf8Consumer', 'tests/UnityPiiProbe', 'tests/UnityLateCallbackPlayer']
    if subprocess.run(['git','merge-base','--is-ancestor',config['sourceHead'],current_head],cwd=root,capture_output=True).returncode:
        raise ValueError('GUI build source is not current checkout ancestor')
    for args in ([config['sourceHead'], current_head], ['HEAD']):
        if subprocess.run(['git','diff','--quiet',*args,'--',*protected],cwd=root,capture_output=True).returncode:
            raise ValueError('GUI build SDK/scenario source differs from checkout')
    checks = [('Assets/Editor/GameBridgeGuiVerification.cs', 'scriptSha256'),
              ('Assets/Editor/GuiAndroidBuild.cs','adapterSha256'), ('Assets/Editor/BuildMockPlayer.cs','buildScriptSha256'),
              ('Assets/MockPlayerScenario.cs','scenarioSha256')]
    for relative, key in checks:
        if file_hash(project/relative) != config[key]: raise ValueError('GUI build source file changed')
    for relative, source in [('Assets/Editor/GameBridgeGuiVerification.cs','tests/UnityGuiVerification/GameBridgeGuiVerification.cs'),
                             ('Assets/Editor/GuiAndroidBuild.cs','tests/UnityGuiVerification/GuiAndroidBuild.cs'),
                             ('Assets/Editor/BuildMockPlayer.cs','tests/UnityAndroidMockConsumer/BuildMockPlayer.cs')]:
        if file_hash(project/relative) != file_hash(root/source): raise ValueError('GUI build helper differs from checkout')
    folder={'standard':'UnityAndroidMockConsumer','pii':'UnityAndroidPiiConsumer','utf8':'UnityAndroidUtf8Consumer'}[variant]
    if file_hash(project/'Assets/MockPlayerScenario.cs') != file_hash(root/'tests'/folder/'MockPlayerScenario.cs'):
        raise ValueError('GUI scenario differs from checkout')
    if file_hash(staging/'SHA256SUMS') != config['stagingManifestSha256'] or file_hash(project/'GameBridgeStaging.SHA256SUMS') != config['stagingManifestSha256']:
        raise ValueError('GUI staging manifest differs')
    records=(staging/'SHA256SUMS').read_text().splitlines()
    if len(records)!=147: raise ValueError('Unexpected GUI package manifest count')
    for line in records:
        digest, relative=line.split('  ',1); candidate=(project/'Packages'/relative).resolve()
        if not candidate.is_relative_to(project/'Packages/com.gamebridge.sdk') or file_hash(candidate)!=digest:
            raise ValueError('GUI packaged SDK changed')
    apk=Path(config['outputPath'])
    if not apk.resolve().is_relative_to(project.parent) or apk.suffix!='.apk': raise ValueError('GUI APK outside owned output')
    validate_apk(apk,value,config_path.stat().st_mtime_ns)
    logfile=Path(value['editorLogPath']).resolve()
    if logfile not in ((project/'Logs/Editor.log').resolve(), (Path.home()/'Library/Logs/Unity/Editor.log').resolve()):
        raise ValueError('Unexpected GUI Editor log path')
    selected=build_log_segment(logfile.read_text(errors='replace'),config['runId'])
    versions=embedded_versions(project)
    return {'apk':apk,'receipt':value,'logSegment':selected,'embeddedCachedPackages':versions}


def export_tree_hash(directory):
    root=Path(directory).resolve();digest=hashlib.sha256();count=0
    entries=sorted(root.rglob('*'),key=lambda p:p.relative_to(root).as_posix())
    for path in entries:
        if path.is_symlink():raise ValueError('GUI export symlink rejected')
        if not path.is_file():continue
        digest.update((path.relative_to(root).as_posix()+'\0'+file_hash(path)+'\n').encode());count+=1
    return digest.hexdigest(),count


def validate_ios_receipt(value,config):
    for key in ('runId','sourceHead','scriptSha256','adapterSha256','buildScriptSha256','scenarioSha256','stagingManifestSha256','variant'):
        if value.get(key)!=config[key]:raise ValueError('GUI iOS source/nonce correlation mismatch')
    if (value.get('status')!='PASS' or value.get('operation')!='ios' or type(value.get('schemaVersion')) is not int or value['schemaVersion']!=1 or
        value.get('isBatchMode') is not False or value.get('unityVersion')!=config['expectedUnityVersion'] or
        value.get('method')!='GuiIosExport.Export' or value.get('originalBuilderReturned') is not True or
        type(value.get('packageFilesVerified')) is not int or value['packageFilesVerified']!=147):raise ValueError('GUI iOS export incomplete')
    for key in ('projectRoot','outputPath'):
        if Path(value.get(key,'')).resolve()!=Path(config[key]).resolve():raise ValueError('GUI iOS path mismatch')
    if type(value.get('artifactFileCount')) is not int or value['artifactFileCount']<=0:raise ValueError('GUI export files missing')
    for key in ('artifactSha256','pbxprojSha256'):
        if not re.fullmatch(r'[0-9a-f]{64}',value.get(key,'')):raise ValueError('GUI export digest missing')


def load_ios_export(project, receipt_path, staging, current_head, variant):
    root=Path(__file__).resolve().parent.parent;project=Path(project).resolve();staging=Path(staging).resolve()
    if not project.is_relative_to(root/'artifacts'):raise ValueError('Owned GUI iOS project required')
    cfgpath=project/'GameBridgeGuiRun.json';c=json.loads(cfgpath.read_text())
    if not re.fullmatch(r'[0-9a-f]{32}',c.get('runId','')) or not re.fullmatch(r'[0-9a-f]{40}',c.get('sourceHead','')):raise ValueError('GUI nonce/source invalid')
    expected=project/'GameBridgeGuiResults'/(c['runId']+'.json')
    if Path(receipt_path).resolve()!=expected or expected.stat().st_mtime_ns<cfgpath.stat().st_mtime_ns:raise ValueError('GUI iOS receipt stale/path mismatch')
    v=json.loads(expected.read_text(encoding='utf-8-sig'));validate_ios_receipt(v,c)
    if c['operation']!='ios' or c['variant']!=variant or Path(c['projectRoot']).resolve()!=project:raise ValueError('GUI iOS variant/project mismatch')
    protected=['unity/Packages/com.gamebridge.sdk','ios/Sources','ios/UnityBridge','ios/Framework','contracts',
        'tests/UnityIosMockConsumer','tests/UnityIosPiiConsumer','tests/UnityPiiProbe','tests/UnityLateCallbackPlayer',
        'tests/UnityGuiVerification/GameBridgeGuiVerification.cs','tests/UnityGuiVerification/GuiIosExport.cs']
    if subprocess.run(['git','merge-base','--is-ancestor',c['sourceHead'],current_head],cwd=root,capture_output=True).returncode:raise ValueError('GUI export source not checkout ancestor')
    for args in ([c['sourceHead'],current_head],['HEAD']):
        if subprocess.run(['git','diff','--quiet',*args,'--',*protected],cwd=root,capture_output=True).returncode:raise ValueError('GUI export protected source changed')
    pairs=[('Assets/Editor/GameBridgeGuiVerification.cs','scriptSha256','tests/UnityGuiVerification/GameBridgeGuiVerification.cs'),
           ('Assets/Editor/GuiIosExport.cs','adapterSha256','tests/UnityGuiVerification/GuiIosExport.cs'),
           ('Assets/Editor/BuildMockIosPlayer.cs','buildScriptSha256','tests/UnityIosMockConsumer/BuildMockIosPlayer.cs'),
           ('Assets/MockIosPlayerScenario.cs','scenarioSha256','tests/'+('UnityIosPiiConsumer' if variant=='pii' else 'UnityIosMockConsumer')+'/MockIosPlayerScenario.cs')]
    for relative,key,source in pairs:
        if file_hash(project/relative)!=c[key] or c[key]!=file_hash(root/source):raise ValueError('GUI iOS builder/scenario differs')
    if file_hash(staging/'SHA256SUMS')!=c['stagingManifestSha256'] or file_hash(project/'GameBridgeStaging.SHA256SUMS')!=c['stagingManifestSha256']:raise ValueError('GUI iOS manifest mismatch')
    lines=(staging/'SHA256SUMS').read_text().splitlines()
    if len(lines)!=147:raise ValueError('Unexpected GUI package count')
    for line in lines:
        digest,relative=line.split('  ',1);p=(project/'Packages'/relative).resolve()
        if not p.is_relative_to(project/'Packages/com.gamebridge.sdk') or file_hash(p)!=digest:raise ValueError('GUI iOS packaged SDK changed')
    output=Path(c['outputPath']).resolve()
    if not output.is_relative_to(project.parent) or not output.is_dir():raise ValueError('GUI export outside owned directory')
    digest,count=export_tree_hash(output)
    if digest!=v['artifactSha256'] or count!=v['artifactFileCount'] or file_hash(output/'Unity-iPhone.xcodeproj/project.pbxproj')!=v['pbxprojSha256']:raise ValueError('GUI export bytes changed')
    log=Path(v['editorLogPath']).resolve()
    if log not in ((project/'Logs/Editor.log').resolve(),(Path.home()/'Library/Logs/Unity/Editor.log').resolve()):raise ValueError('Unexpected GUI log path')
    text=log.read_text(errors='replace');a='GB_GUI_IOS_STARTED '+c['runId'];b='GB_GUI_IOS_PASS '+c['runId'];ls=text.splitlines()
    start=[i for i,l in enumerate(ls) if l.strip()==a];end=[i for i,l in enumerate(ls) if l.strip()==b]
    if len(start)!=1 or len(end)!=1 or start[0]>=end[0]:raise ValueError('GUI iOS log correlation invalid')
    segment=ls[start[0]:end[0]+1]
    if sum(l.strip()=='GB_IOS_MOCK_EXPORT PASS' for l in segment)!=1:raise ValueError('Original iOS builder verdict missing')
    return {'output':output,'receipt':v,'logSegment':'\n'.join(segment)+'\n','embeddedCachedPackages':embedded_versions(project)}
