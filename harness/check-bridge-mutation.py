#!/usr/bin/env python3
"""Remove the duplicate-response guard in a disposable copy and require smoke failure."""
import os
import hashlib
import json
import subprocess
import tempfile
from pathlib import Path
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parent.parent
OLD = 'if (!pending.TryGetValue(id, out entry)) { Interlocked.Increment(ref ignored); return; }'
NEW = 'if (!pending.TryGetValue(id, out entry)) { Interlocked.Increment(ref ignored); }'

def main() -> int:
    editor = os.environ.get('UNITY_EDITOR_PATH')
    if not editor or not Path(editor).is_file(): print('DEFERRED_ENV: UNITY_EDITOR_PATH'); return 2
    dotnet = Path(editor).parent.parent / 'Resources/Scripting/DotNetSdk/dotnet'
    newtonsoft = Path(os.environ.get('NEWTONSOFT_DLL', str(ROOT / 'artifacts/unity-newtonsoft/package/Runtime/Newtonsoft.Json.dll')))
    if not dotnet.is_file() or not newtonsoft.is_file(): print('DEFERRED_ENV: .NET or Newtonsoft'); return 2
    source = ROOT / 'unity/Packages/com.gamebridge.sdk/Runtime/Core/RequestRegistry.cs'
    text = source.read_text(encoding='utf-8')
    original_hash=hashlib.sha256(source.read_bytes()).hexdigest()
    if text.count(OLD) != 1: print('Mutation target changed; no test performed'); return 1
    artifacts = ROOT / 'artifacts'; artifacts.mkdir(exist_ok=True)
    workspace = Path(tempfile.mkdtemp(prefix='bridge-mutation-', dir=artifacts))
    mutated = workspace / 'RequestRegistry.cs'; mutated.write_text(text.replace(OLD, NEW), encoding='utf-8')
    files = [mutated, ROOT/'unity/Packages/com.gamebridge.sdk/Runtime/Core/WireModels.cs',
             ROOT/'unity/Packages/com.gamebridge.sdk/Runtime/Core/IWireTransport.cs',
             ROOT/'unity/Packages/com.gamebridge.sdk/Runtime/Core/EditorOfflineTransport.cs',
             ROOT/'unity/Packages/com.gamebridge.sdk/Runtime/Models.cs', ROOT/'unity/Packages/com.gamebridge.sdk/Runtime/GameBridgeConfig.cs',
             ROOT/'unity/Packages/com.gamebridge.sdk/Runtime/GameBridgeClient.cs', ROOT/'scripts/registry-smoke.cs']
    includes = '\n'.join(f'<Compile Include="{escape(str(path))}" />' for path in files)
    project = workspace / 'Mutation.csproj'
    project.write_text(f'''<Project Sdk="Microsoft.NET.Sdk"><PropertyGroup><OutputType>Exe</OutputType><TargetFramework>net8.0</TargetFramework><EnableDefaultCompileItems>false</EnableDefaultCompileItems><DefineConstants>GAMEBRIDGE_TEST_OFFLINE</DefineConstants></PropertyGroup><ItemGroup>{includes}<Reference Include="Newtonsoft.Json"><HintPath>{escape(str(newtonsoft))}</HintPath></Reference></ItemGroup></Project>''', encoding='utf-8')
    env = os.environ.copy(); env['GAMEBRIDGE_ROOT'] = str(ROOT); env['DOTNET_GENERATE_ASPNET_CERTIFICATE'] = 'false'
    env['GAMEBRIDGE_MUTATION_DUPLICATE_ONLY']='true'
    env['DOTNET_CLI_HOME'] = str(ROOT/'artifacts/dotnet-home'); env['DOTNET_CLI_TELEMETRY_OPTOUT'] = '1'; env['DOTNET_SKIP_FIRST_TIME_EXPERIENCE'] = '1'; env['DOTNET_NOLOGO'] = '1'
    normal_project=workspace/'NormalProbe.csproj'
    normal_project.write_text(project.read_text().replace(escape(str(mutated)),escape(str(source))))
    normal=subprocess.run([str(dotnet),'run','--project',str(normal_project),'--nologo'],cwd=ROOT,env=env,text=True,
                          stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=180,check=False)
    (workspace/'normal-probe.log').write_text(normal.stdout)
    if normal.returncode or 'GB_DUPLICATE_PROBE PASS' not in normal.stdout:
        print('Normal duplicate completion probe failed');return 1
    try:
        run = subprocess.run([str(dotnet),'run','--project',str(project),'--nologo'], cwd=ROOT, env=env, text=True,
                             stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=180, check=False)
    except (OSError, subprocess.TimeoutExpired): print('Mutation execution unavailable'); return 2
    (workspace/'mutation.log').write_text(run.stdout, encoding='utf-8')
    if run.returncode == 0 or 'NullReferenceException' not in run.stdout or 'RequestRegistry.HandleMessage' not in run.stdout:
        print('Duplicate guard mutation was not detected by the expected runtime assertion path'); return 1
    unchanged=hashlib.sha256(source.read_bytes()).hexdigest()==original_hash
    report={'status':'PASS' if unchanged else 'FAIL','normalProbeExitCode':normal.returncode,'probe':'duplicate-completion-only','mutatedProcessExitCode':run.returncode,'expectedProcessFailures':1,
            'sourceUnchanged':unchanged,'originalSha256':original_hash,'mutationOnlyInDisposableCopy':True}
    (workspace/'result.json').write_text(json.dumps(report,indent=2)+'\n')
    if not unchanged:print('FAIL: original mutation target changed');return 1
    print('Duplicate response guard mutation: detected; original source unchanged.')
    print('Evidence directory:',workspace.relative_to(ROOT))
    return 0

if __name__ == '__main__': raise SystemExit(main())
