#!/usr/bin/env bash
# Fresh isolated coordinate-only Maven consumer; does not install the APK.
set -euo pipefail
root="$(cd "$(dirname "$0")/.." && pwd)"
repo="${GAMEBRIDGE_MAVEN_REPO:-}"
if [[ "$repo" != /* || ! -f "$repo/com/gamebridge/sdk-unity-bridge/0.1.0-dev/sdk-unity-bridge-0.1.0-dev.pom" ]]; then echo 'DEFERRED_ENV: absolute Maven staging repository required' >&2; exit 2; fi
: "${ANDROID_HOME:=$HOME/Library/Android/sdk}"; export ANDROID_HOME GAMEBRIDGE_MAVEN_REPO="$repo"
mkdir -p "$root/artifacts"; output="$(mktemp -d "$root/artifacts/android-maven-consumer.XXXXXX")"
python3 - "$root/android/consumer-check" "$output/project" <<'PY'
import shutil,sys
shutil.copytree(sys.argv[1],sys.argv[2],ignore=shutil.ignore_patterns('build','.gradle','local.properties'))
PY
echo "Evidence directory: $output"
set +e
"$root/android/gradlew" -p "$output/project" --rerun-tasks :app:assembleRelease > "$output/build.log" 2>&1
code=$?
set -e
apk="$output/project/app/build/outputs/apk/release/app-release-unsigned.apk"
mapping="$output/project/app/build/outputs/mapping/release/mapping.txt"
if [[ "$code" != 0 || ! -s "$apk" || ! -s "$mapping" ]]; then echo 'FAIL: clean Maven R8 consumer build incomplete' >&2; exit 1; fi
aapt="$ANDROID_HOME/build-tools/36.0.0/aapt"
if [[ ! -x "$aapt" ]]; then echo 'DEFERRED_ENV: Android build-tools 36.0.0 aapt missing' >&2; exit 2; fi
"$aapt" dump xmltree "$apk" AndroidManifest.xml > "$output/manifest.txt"
for expected in 'com.android.vending.BILLING' 'android.permission.INTERNET' 'com.gamebridge.consumer.MainActivity'; do
  if ! grep -Fq "$expected" "$output/manifest.txt"; then echo 'FAIL: expected merged manifest entry missing' >&2; exit 1; fi
done
echo 'Android clean Maven R8 consumer PASS: unsigned APK; device execution separate.'
