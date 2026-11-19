#!/usr/bin/env python3
"""Explicit fresh Editor diagnostic. No activation, retries, or user-project mutation."""
import argparse
import json
import os
from pathlib import Path
import signal
import subprocess
import tempfile
import time
import uuid

from unity_editor_smoke import evaluate

ROOT = Path(__file__).resolve().parent.parent


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--run-local', required=True, action='store_true')
    parser.add_argument('--mode', required=True, choices=('cli', 'direct'))
    args = parser.parse_args()
    version = '6000.5.8f1'
    editor = Path(os.environ.get('UNITY_EDITOR_PATH', '/Applications/Unity/Hub/Editor/' + version + '/Unity.app/Contents/MacOS/Unity'))
    if not editor.is_file():
        print('DEFERRED_ENV: installed Editor required')
        return 2
    artifacts = ROOT / 'artifacts'
    artifacts.mkdir(exist_ok=True)
    out = Path(tempfile.mkdtemp(prefix='unity-editor-smoke-', dir=artifacts))
    project = out / 'project'
    for directory in ('Assets/Editor', 'Packages', 'ProjectSettings'):
        (project / directory).mkdir(parents=True)
    run_id = uuid.uuid4().hex
    receipt = {'status': 'PASS', 'runId': run_id, 'unityVersion': version, 'batchMode': True}
    literal = json.dumps(json.dumps(receipt))
    # Executed only after normal Editor initialization and its built-in license checks.
    (project / 'Assets/Editor/EditorSmoke.cs').write_text('''using System; using System.IO; using UnityEngine;
public static class EditorSmoke { public static void Run() {
 if (!Application.isBatchMode || Application.unityVersion != "6000.5.8f1") throw new Exception("Unexpected Editor");
 var path = Environment.GetEnvironmentVariable("GAMEBRIDGE_EDITOR_SMOKE_RESULT");
 if (String.IsNullOrEmpty(path) || File.Exists(path)) throw new Exception("Fresh result required");
 File.WriteAllText(path, ''' + literal + ''');
 Debug.Log("GB_EDITOR_SMOKE PASS ''' + run_id + '''");
} }
''')
    (project / 'Packages/manifest.json').write_text('{"dependencies":{}}\n')
    (project / 'ProjectSettings/ProjectVersion.txt').write_text('m_EditorVersion: ' + version + '\n')
    log = out / 'editor.log'
    result = out / 'receipt.json'
    extra = ['-executeMethod', 'EditorSmoke.Run', '-logFile', str(log)]
    command = ([str(editor), '-batchmode', '-quit', '-projectPath', str(project), *extra]
               if args.mode == 'direct' else
               ['unity', 'run', str(project), '--editor-version', version, '--timeout', '180', '--non-interactive', '--', *extra])
    env = os.environ.copy()
    env.update(GAMEBRIDGE_EDITOR_SMOKE_RESULT=str(result), UNITY_NO_UPDATE_CHECK='1', UNITY_NO_CONSENT_PROMPT='1')
    timed_out = False
    started = time.monotonic()
    with (out / 'launcher.log').open('w') as output:
        try:
            process = subprocess.Popen(command, env=env, stdout=output, stderr=subprocess.STDOUT, start_new_session=True)
        except OSError:
            print('DEFERRED_ENV: diagnostic launcher unavailable; evidence:', out.relative_to(ROOT))
            return 2
        try:
            code = process.wait(timeout=210)
        except subprocess.TimeoutExpired:
            timed_out, code = True, 124
            # This fresh session contains only this diagnostic and its children.
            try:
                os.killpg(process.pid, signal.SIGTERM)
            except ProcessLookupError:
                pass
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                try:
                    os.killpg(process.pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass
                process.wait()
    text = log.read_text(errors='replace') if log.exists() else ''
    try:
        value = json.loads(result.read_text()) if result.exists() else None
    except (OSError, ValueError):
        value = {'invalidReceipt': True}
    report = evaluate(code, text, value, run_id, version, timed_out)
    report.update(mode=args.mode, runId=run_id, elapsedSeconds=round(time.monotonic()-started, 2),
                  sourceHead=subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip())
    (out / 'result.json').write_text(json.dumps(report, indent=2) + '\n')
    print('Editor diagnostic:', report['status'], report['reason'], 'Evidence:', out.relative_to(ROOT))
    return 0 if report['status'] == 'PASS' else 1 if report['status'] == 'FAIL' else 2


if __name__ == '__main__':
    raise SystemExit(main())
