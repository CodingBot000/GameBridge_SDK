#!/usr/bin/env bash
# Build only a freshly prepared local test consumer. Never modifies a user's Unity project.
set -euo pipefail
root="$(cd "$(dirname "$0")/.." && pwd)"
if [[ "$#" != 2 ]]; then echo 'Usage: build-unity-android-mock.sh PREPARED_PROJECT NEW_APK_PATH' >&2; exit 64; fi
project="$1"; apk="$2"
[[ "$project" == /* && "$apk" == /* && -f "$project/Assets/Editor/BuildMockPlayer.cs" && ! -e "$apk" ]] || { echo 'CONFIG_REQUIRED: prepared absolute project path and new absolute APK path' >&2; exit 2; }
if ! command -v unity >/dev/null 2>&1; then echo 'DEFERRED_ENV: Unity CLI missing' >&2; exit 2; fi
set +e
status="$(UNITY_NO_UPDATE_CHECK=1 unity license status --format json)"
license_exit=$?
set -e
license_state="$(python3 -c 'import json,sys
try:
 d=json.load(sys.stdin); print("active" if d.get("success") and d.get("data",{}).get("active") is True else "inactive" if d.get("success") and d.get("data",{}).get("active") is False else "unknown")
except (ValueError,TypeError): print("unknown")' <<< "$status")"
if [[ "$license_state" != active || "$license_exit" != 0 ]]; then echo "DEFERRED_ENV: Unity license $license_state; user activation or status check required" >&2; exit 2; fi
editor="${UNITY_EDITOR_PATH:-/Applications/Unity/Hub/Editor/6000.5.8f1/Unity.app/Contents/MacOS/Unity}"
contents="$(cd "$(dirname "$editor")/.." && pwd)"
# Unity Hub installations may place PlaybackEngines beside Unity.app, while
# other installs keep it under Contents. Check both without modifying either.
editor_parent="$(cd "$contents/../.." && pwd)"
if [[ ! -d "$contents/PlaybackEngines/AndroidPlayer" && ! -d "$editor_parent/PlaybackEngines/AndroidPlayer" ]]; then echo 'DEFERRED_ENV: Unity Android Build Support missing' >&2; exit 2; fi
export GAMEBRIDGE_UNITY_APK="$apk"
UNITY_NO_UPDATE_CHECK=1 unity run "$project" --editor-version "${UNITY_EDITOR_VERSION:-6000.5.8f1}" --timeout 900 --non-interactive -- -buildTarget Android -executeMethod BuildMockPlayer.Build
[[ -s "$apk" ]] || { echo 'FAILED: Unity returned without an APK' >&2; exit 1; }
echo 'BUILD PASS: Android test APK created; installation and execution not yet verified.'
