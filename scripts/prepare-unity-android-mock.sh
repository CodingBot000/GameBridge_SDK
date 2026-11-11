#!/usr/bin/env bash
# Creates only a new isolated LOCAL_MOCK consumer; does not run Unity or publish.
set -euo pipefail
root="$(cd "$(dirname "$0")/.." && pwd)"
if [[ "$#" != 1 || "$1" != --prepare ]]; then echo 'Usage: prepare-unity-android-mock.sh --prepare' >&2; exit 64; fi
if [[ -z "${GAMEBRIDGE_UPM_STAGING:-}" || ! -d "$GAMEBRIDGE_UPM_STAGING/com.gamebridge.sdk" ]]; then echo 'CONFIG_REQUIRED: GAMEBRIDGE_UPM_STAGING must identify packaged SDK staging' >&2; exit 2; fi
python3 "$root/harness/check-staging.py" "$GAMEBRIDGE_UPM_STAGING"
mkdir -p "$root/artifacts"
output="$(mktemp -d "$root/artifacts/unity-android-mock.XXXXXX")"
project="$output/project"
mkdir -p "$project/Assets/Editor" "$project/Assets/Plugins/Android" "$project/Packages" "$project/ProjectSettings"
cp -R "$GAMEBRIDGE_UPM_STAGING/com.gamebridge.sdk" "$project/Packages/com.gamebridge.sdk"
cp "$root/tests/UnityAndroidMockConsumer/MockPlayerScenario.cs" "$project/Assets/MockPlayerScenario.cs"
cp "$root/tests/UnityAndroidMockConsumer/BuildMockPlayer.cs" "$project/Assets/Editor/BuildMockPlayer.cs"
cat > "$project/Assets/Plugins/Android/AndroidManifest.xml" <<'MANIFEST'
<manifest xmlns:android="http://schemas.android.com/apk/res/android"><uses-permission android:name="android.permission.INTERNET"/><application android:usesCleartextTraffic="true"/></manifest>
MANIFEST
printf '%s\n' '{"dependencies":{}}' > "$project/Packages/manifest.json"
printf 'm_EditorVersion: %s\n' "${UNITY_EDITOR_VERSION:-6000.5.8f1}" > "$project/ProjectSettings/ProjectVersion.txt"
printf 'Prepared consumer: %s\n' "$project"
printf '%s\n' 'NOT_RUN: Unity import, Android Player build, and device execution still require an active license and Android Build Support.'
