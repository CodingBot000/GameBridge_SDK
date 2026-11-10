#!/usr/bin/env bash
set -euo pipefail
root="$(cd "$(dirname "$0")/.." && pwd)"
if [[ -n "${XCODEGEN_BIN:-}" ]]; then
  generator="$XCODEGEN_BIN"
elif command -v xcodegen >/dev/null 2>&1; then
  generator="$(command -v xcodegen)"
elif [[ -x "$root/artifacts/tools/xcodegen/2.46.0/bin/xcodegen" ]]; then
  generator="$root/artifacts/tools/xcodegen/2.46.0/bin/xcodegen"
else
  echo 'XcodeGen 2.46.0 is required; set XCODEGEN_BIN or install it from its official source.' >&2
  exit 2
fi
# Generate a self-contained project layout under a new directory; never rewrite a user's Xcode project.
mkdir -p "$root/artifacts"
workspace="$(mktemp -d "$root/artifacts/ios-project.XXXXXX")"
mkdir -p "$workspace/ios/Framework"
for item in Package.swift Sources UnityBridge SampleApp RecoveryHarness StoreKit StoreKitTests PushTests UITests Tests; do
  ln -s "$root/ios/$item" "$workspace/ios/$item"
done
ln -s "$root/ios/Framework/include" "$workspace/ios/Framework/include"
cp "$root/ios/Framework/project.yml" "$workspace/ios/Framework/project.yml"
"$generator" generate --spec "$workspace/ios/Framework/project.yml" >&2
printf '%s\n' "$workspace/ios/Framework/GameBridgeSample.xcodeproj"
