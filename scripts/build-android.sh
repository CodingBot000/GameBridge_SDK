#!/usr/bin/env bash
set -euo pipefail
root="$(cd "$(dirname "$0")/.." && pwd)"
if [[ "${1:-}" != "--mock" || "$#" != 1 ]]; then echo "Usage: build-android.sh --mock" >&2; exit 64; fi
: "${ANDROID_HOME:=$HOME/Library/Android/sdk}"
export ANDROID_HOME
"$root/android/gradlew" -p "$root/android" :sdk-core:publishReleasePublicationToStagingRepository :sdk-android:publishReleasePublicationToStagingRepository :sdk-unity-bridge:publishReleasePublicationToStagingRepository :sample-app:assembleDebug
"$root/android/gradlew" -p "$root/android/consumer-check" :app:assembleRelease
