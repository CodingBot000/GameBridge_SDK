#!/usr/bin/env bash
set -u
missing=0
for tool in java swift xcodebuild adb docker unity python3; do
  if command -v "$tool" >/dev/null 2>&1; then
    printf '%s: available\n' "$tool"
  else
    printf '%s: unavailable\n' "$tool"
    missing=1
  fi
done
if docker info >/dev/null 2>&1; then echo 'docker engine: available'; else echo 'docker engine: unavailable'; missing=1; fi
if [[ -d "${ANDROID_HOME:-$HOME/Library/Android/sdk}/platforms" ]]; then echo 'Android SDK platforms: available'; else echo 'Android SDK platforms: unavailable'; missing=1; fi
echo 'Availability does not verify Unity licensing, signing, devices, or platform behavior.'
if (( missing )); then exit 2; fi
