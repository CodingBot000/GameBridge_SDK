#!/usr/bin/env bash
set -euo pipefail
root="$(cd "$(dirname "$0")/.." && pwd)"
if [[ "${1:-}" != "--mock" || "$#" != 1 ]]; then echo "Usage: build-android.sh --mock" >&2; exit 64; fi
: "${ANDROID_HOME:=$HOME/Library/Android/sdk}"
export ANDROID_HOME
if [[ -n "${GAMEBRIDGE_MAVEN_REPO:-}" ]]; then
  [[ "$GAMEBRIDGE_MAVEN_REPO" == /* ]] || { echo 'GAMEBRIDGE_MAVEN_REPO must be an absolute new path.' >&2; exit 2; }
  [[ ! -e "$GAMEBRIDGE_MAVEN_REPO" ]] || { echo 'Maven output exists; choose a new path.' >&2; exit 2; }
  mkdir -p "$(dirname "$GAMEBRIDGE_MAVEN_REPO")"
  mkdir "$GAMEBRIDGE_MAVEN_REPO"
else
  mkdir -p "$root/artifacts"
  GAMEBRIDGE_MAVEN_REPO="$(mktemp -d "$root/artifacts/maven-build.XXXXXX")"
fi
export GAMEBRIDGE_MAVEN_REPO
printf 'Maven output: %s\n' "$GAMEBRIDGE_MAVEN_REPO"
"$root/android/gradlew" -p "$root/android" :sdk-core:publishReleasePublicationToStagingRepository :sdk-android:publishReleasePublicationToStagingRepository :sdk-unity-bridge:publishReleasePublicationToStagingRepository :sample-app:assembleDebug
"$root/android/gradlew" -p "$root/android/consumer-check" :app:assembleRelease
