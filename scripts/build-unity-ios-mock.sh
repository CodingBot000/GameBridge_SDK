#!/usr/bin/env bash
# Export a fresh test-only Unity iOS Simulator Xcode project.
set -euo pipefail
if [[ "$#" != 2 ]]; then echo 'Usage: build-unity-ios-mock.sh PREPARED_PROJECT NEW_XCODE_PROJECT_PATH' >&2; exit 64; fi
project="$1"; output="$2"
[[ "$project" == /* && "$output" == /* && -f "$project/Assets/Editor/BuildMockIosPlayer.cs" && ! -e "$output" ]] || { echo 'CONFIG_REQUIRED: prepared absolute project and new absolute output path' >&2; exit 2; }
if ! command -v unity >/dev/null 2>&1; then echo 'DEFERRED_ENV: Unity CLI missing' >&2; exit 2; fi
export GAMEBRIDGE_UNITY_IOS_OUTPUT="$output"
UNITY_NO_UPDATE_CHECK=1 unity run "$project" --editor-version "${UNITY_EDITOR_VERSION:-6000.5.8f1}" --timeout 900 --non-interactive -- -buildTarget iOS -executeMethod BuildMockIosPlayer.Build
[[ -f "$output/Unity-iPhone.xcodeproj/project.pbxproj" ]] || { echo 'FAILED: Unity returned without Xcode project' >&2; exit 1; }
echo 'EXPORT PASS: iOS Simulator Xcode project; build and execution remain unverified.'
