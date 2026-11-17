#!/usr/bin/env python3
"""Prepare test-only menu in an existing owned GUI project; never launches an Editor."""
import argparse
import json
from pathlib import Path
import shutil
import subprocess
import uuid

from gui_verification import file_hash

ROOT = Path(__file__).resolve().parent.parent


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--prepare', required=True, action='store_true')
    parser.add_argument('--project', required=True, type=Path)
    args = parser.parse_args()
    project = args.project.resolve()
    if not project.is_relative_to((ROOT/'artifacts').resolve()) or not (project/'ProjectSettings/ProjectVersion.txt').is_file():
        raise SystemExit('Owned existing artifact project required')
    config_path = project/'GameBridgeGuiRun.json'
    if config_path.exists():
        raise SystemExit('Existing GUI run configuration preserved; use another owned project')
    source = ROOT/'tests/UnityGuiVerification/GameBridgeGuiVerification.cs'
    target = project/'Assets/Editor/GameBridgeGuiVerification.cs'
    if target.exists():
        raise SystemExit('Existing GUI script preserved')
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, target)
    config = dict(schemaVersion=1, runId=uuid.uuid4().hex, operation='probe',
                  sourceHead=subprocess.check_output(['git','rev-parse','HEAD'], cwd=ROOT, text=True).strip(),
                  projectRoot=str(project), expectedUnityVersion='6000.5.8f1', scriptSha256=file_hash(target))
    config_path.write_text(json.dumps(config, indent=2)+'\n')
    print('Prepared GUI probe:', project.relative_to(ROOT), 'nonce:', config['runId'])
    print('NOT_RUN: use GameBridge Verification/Run GUI Probe in this GUI project')


if __name__ == '__main__':
    main()
