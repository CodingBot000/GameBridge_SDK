#!/usr/bin/env python3
"""Run common Kotlin/Swift/C# fixture checks and reject missing or zero-test lanes."""
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

def run(command: list[str], log: Path, env: dict[str, str]) -> tuple[int, str]:
    try:
        result = subprocess.run(command, cwd=ROOT, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                text=True, errors='replace', timeout=600, check=False)
        output = result.stdout; code = result.returncode
    except (OSError, subprocess.TimeoutExpired) as exc:
        output = f'{type(exc).__name__}: command unavailable or timed out\n'; code = 2
    log.write_text(output, encoding='utf-8')
    return code, output

def main() -> int:
    artifacts = ROOT / 'artifacts'; artifacts.mkdir(exist_ok=True)
    output = Path(tempfile.mkdtemp(prefix='contracts-', dir=artifacts)); env = os.environ.copy()
    env.setdefault('ANDROID_HOME', str(Path.home() / 'Library/Android/sdk'))
    results = []
    gradle = ROOT / 'android/gradlew'
    if not gradle.is_file(): results.append({'suite':'kotlin', 'status':'DEFERRED_ENV', 'exitCode':2, 'tests':0})
    else:
        started_ns = time.time_ns()
        code, _ = run([str(gradle), '-p', 'android', ':sdk-core:test', '--rerun-tasks', '--tests', 'com.gamebridge.BridgeProtocolTest', '--tests', 'com.gamebridge.ModelFixtureTest', '--tests', 'com.gamebridge.SdkCoordinatorTest'], output / 'kotlin.log', env)
        tests = failures = skipped = 0
        try:
            for cls in ('BridgeProtocolTest', 'ModelFixtureTest', 'SdkCoordinatorTest'):
                report = ROOT / f'android/sdk-core/build/test-results/test/TEST-com.gamebridge.{cls}.xml'
                if report.stat().st_mtime_ns < started_ns: raise ValueError('stale report')
                root = ET.parse(report).getroot()
                tests += int(root.attrib['tests']); failures += int(root.attrib['failures']) + int(root.attrib['errors']); skipped += int(root.attrib['skipped'])
        except (OSError, ET.ParseError, KeyError, ValueError): tests = 0
        status = 'PASS' if code == 0 and tests > 0 and failures == 0 and skipped == 0 else ('DEFERRED_ENV' if code == 2 else 'FAIL')
        results.append({'suite':'kotlin','status':status,'exitCode':code,'tests':tests,'failures':failures,'skipped':skipped})
    if not shutil.which('swift'): results.append({'suite':'swift','status':'DEFERRED_ENV','exitCode':2,'tests':0})
    else:
        code, text = run(['swift','test','--package-path','ios','--filter','BridgeProtocolTests|ModelFixtureTests|SdkCoordinatorTests'], output / 'swift.log', env)
        counts = [(int(a), int(b)) for a,b in re.findall(r'Executed (\d+) tests?, with (\d+) failures?', text)]
        tests, failures = max(counts, default=(0,0), key=lambda item:item[0])
        skipped = max((int(v) for v in re.findall(r'with (\d+) tests? skipped', text)), default=0)
        status = 'PASS' if code == 0 and tests > 0 and failures == 0 and skipped == 0 else ('DEFERRED_ENV' if code == 2 else 'FAIL')
        results.append({'suite':'swift','status':status,'exitCode':code,'tests':tests,'failures':failures,'skipped':skipped})
    editor = env.get('UNITY_EDITOR_PATH')
    if not editor or not Path(editor).is_file(): results.append({'suite':'csharp','status':'DEFERRED_ENV','exitCode':2,'tests':0})
    else:
        code, text = run(['bash','scripts/smoke-csharp-registry.sh'], output / 'csharp.log', env)
        tests = 1 if 'Registry, facade and offline fake smoke passed' in text else 0
        status = 'PASS' if code == 0 and tests == 1 else ('DEFERRED_ENV' if code == 2 else 'FAIL')
        results.append({'suite':'csharp','status':status,'exitCode':code,'tests':tests})
    head = subprocess.run(['git','rev-parse','HEAD'], cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, check=False).stdout.strip()
    report = {'scope':'shared-contract-fixtures-only','sourceHead':head,'workingTree':'HEAD plus uncommitted changes may be present',
              'timestampUtc':time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),'suites':results}
    (output / 'result.json').write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8')
    for item in results: print(f"{item['suite']}: {item['status']} (tests={item['tests']}, exit={item['exitCode']})")
    print('Evidence directory:', output.relative_to(ROOT))
    if any(x['status'] == 'FAIL' for x in results): return 1
    if any(x['status'] != 'PASS' for x in results): return 2
    return 0

if __name__ == '__main__': raise SystemExit(main())
