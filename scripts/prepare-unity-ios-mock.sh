#!/usr/bin/env bash
# Create a new isolated Simulator consumer; do not alter user projects or publish.
set -euo pipefail
root="$(cd "$(dirname "$0")/.." && pwd)"
if [[ "$#" != 1 || "$1" != --prepare ]]; then echo 'Usage: prepare-unity-ios-mock.sh --prepare' >&2; exit 64; fi
if [[ -z "${GAMEBRIDGE_UPM_STAGING:-}" || ! -d "$GAMEBRIDGE_UPM_STAGING/com.gamebridge.sdk" ]]; then echo 'CONFIG_REQUIRED: GAMEBRIDGE_UPM_STAGING' >&2; exit 2; fi
python3 "$root/harness/check-staging.py" "$GAMEBRIDGE_UPM_STAGING"
mkdir -p "$root/artifacts"; output="$(mktemp -d "$root/artifacts/unity-ios-mock.XXXXXX")"; project="$output/project"
mkdir -p "$project/Assets/Editor" "$project/Packages" "$project/ProjectSettings"
cp -R "$GAMEBRIDGE_UPM_STAGING/com.gamebridge.sdk" "$project/Packages/com.gamebridge.sdk"
cp "$root/tests/UnityIosMockConsumer/MockIosPlayerScenario.cs" "$project/Assets/MockIosPlayerScenario.cs"
cp "$root/tests/UnityIosMockConsumer/BuildMockIosPlayer.cs" "$project/Assets/Editor/BuildMockIosPlayer.cs"
printf '%s\n' '{"dependencies":{}}' > "$project/Packages/manifest.json"
printf 'm_EditorVersion: %s\n' "${UNITY_EDITOR_VERSION:-6000.5.8f1}" > "$project/ProjectSettings/ProjectVersion.txt"
printf 'Prepared consumer: %s\n' "$project"
printf '%s\n' 'NOT_RUN: Unity iOS export, Simulator build and Player execution.'
