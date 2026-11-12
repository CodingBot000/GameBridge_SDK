#!/usr/bin/env bash
# Run only inside a newly prepared isolated consumer project.
set -euo pipefail
root="$(cd "$(dirname "$0")/.." && pwd)"
if [[ $# != 2 || ! -d "$1/Assets/Editor" || ! -d "$1/Packages/com.gamebridge.sdk" || -e "$2" ]]; then echo 'CONFIG_REQUIRED: prepared consumer and new marker file' >&2; exit 2; fi
project="$1"; markers="$2"
python3 - "$root" "$project" "$markers" <<'PYPATH'
import sys
from pathlib import Path
root, project, marker = map(Path, sys.argv[1:])
if not project.is_absolute() or not marker.is_absolute() or not project.resolve().is_relative_to((root/'artifacts').resolve()) or not marker.resolve().is_relative_to((root/'artifacts').resolve()):
    raise SystemExit('CONFIG_REQUIRED: isolated artifacts paths only')
PYPATH
cp "$root/tests/UnityOfflineSample/Setup/ImportSamples.cs" "$project/Assets/Editor/ImportSamples.cs"
set +e
UNITY_NO_UPDATE_CHECK=1 UNITY_NO_CONSENT_PROMPT=1 unity run "$project" --editor-version "${UNITY_EDITOR_VERSION:-6000.5.8f1}" --timeout 300 --non-interactive -- -executeMethod GameBridgeSampleImporter.Import
code=$?
set -e
if [[ "$code" != 0 || ! -f "$project/Logs/Editor.log" ]]; then echo 'FAIL: Unity sample import did not complete' >&2; exit 1; fi
grep -E '^GB_SAMPLE_IMPORT PASS (Editor Offline Demo|Native Mock and Sandbox Demo)$' "$project/Logs/Editor.log" > "$markers"
if [[ "$(grep -Fxc 'GB_SAMPLE_IMPORT PASS Editor Offline Demo' "$markers")" != 1 || "$(grep -Fxc 'GB_SAMPLE_IMPORT PASS Native Mock and Sandbox Demo' "$markers")" != 1 ]]; then
  echo 'FAIL: Unity sample import markers missing or duplicated' >&2; exit 1
fi
echo 'Unity Package Manager sample import PASS'
