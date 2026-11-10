#!/usr/bin/env bash
set -euo pipefail
root="$(cd "$(dirname "$0")/.." && pwd)"
mode="${1:-}"
if [[ "$#" != 1 || ( "$mode" != '--simulator' && "$mode" != '--xcframework' ) ]]; then
  echo 'Usage: build-ios.sh --simulator|--xcframework' >&2; exit 64
fi
bash "$root/scripts/generate-ios-project.sh"
project="$root/ios/Framework/GameBridgeSample.xcodeproj"
if [[ "$mode" == '--simulator' ]]; then
  xcodebuild -project "$project" -scheme GameBridgeSample -configuration Debug -sdk iphonesimulator CODE_SIGNING_ALLOWED=NO build
  exit
fi
output="${GAMEBRIDGE_IOS_OUTPUT_DIR:-$root/artifacts/ios-package}"
if [[ -e "$output" ]]; then echo 'Output already exists; choose a new GAMEBRIDGE_IOS_OUTPUT_DIR.' >&2; exit 2; fi
mkdir -p "$(dirname "$output")"
mkdir "$output"
xcodebuild archive -project "$project" -scheme GameBridgeNative -configuration Release -destination 'generic/platform=iOS' -archivePath "$output/device.xcarchive" SKIP_INSTALL=NO BUILD_LIBRARY_FOR_DISTRIBUTION=YES CODE_SIGNING_ALLOWED=NO
xcodebuild archive -project "$project" -scheme GameBridgeNative -configuration Release -destination 'generic/platform=iOS Simulator' -archivePath "$output/simulator.xcarchive" SKIP_INSTALL=NO BUILD_LIBRARY_FOR_DISTRIBUTION=YES CODE_SIGNING_ALLOWED=NO
xcodebuild -create-xcframework -framework "$output/device.xcarchive/Products/Library/Frameworks/GameBridgeNative.framework" -framework "$output/simulator.xcarchive/Products/Library/Frameworks/GameBridgeNative.framework" -output "$output/GameBridgeNative.xcframework"
