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
    versions={}
    for name,expected in [('com.unity.mobile.notifications','2.5.0'),('com.unity.nuget.newtonsoft-json','3.2.2')]:
        package=json.loads((project/'Packages'/name/'package.json').read_text())
        if package.get('name')!=name or package.get('version')!=expected: raise ValueError('GUI exact package mismatch')
        versions[name]=expected
    return {'apk':apk,'receipt':value,'logSegment':selected,'embeddedCachedPackages':versions}
