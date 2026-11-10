#!/usr/bin/env bash
set -euo pipefail
root="$(cd "$(dirname "$0")/.." && pwd)"
if [[ -z "${UNITY_EDITOR_PATH:-}" || ! -f "$UNITY_EDITOR_PATH" ]]; then echo 'CONFIG_REQUIRED: UNITY_EDITOR_PATH' >&2; exit 2; fi
contents="$(cd "$(dirname "$UNITY_EDITOR_PATH")/.." && pwd)"
dotnet="$contents/Resources/Scripting/DotNetSdk/dotnet"
export UNITY_MANAGED="$contents/Resources/Scripting/Managed/UnityEngine"
export UNITY_XCODE_DLL="$contents/Resources/BuildPipeline/UnityEditor.iOS.Extensions.Xcode.dll"
if [[ ! -x "$dotnet" || ! -f "$UNITY_XCODE_DLL" ]]; then echo 'Unity iOS Xcode managed assembly unavailable.' >&2; exit 2; fi
project="$root/ios/Framework/GameBridgeSample.xcodeproj/project.pbxproj"
if [[ ! -f "$project" ]]; then echo 'Generate iOS project first: bash scripts/generate-ios-project.sh' >&2; exit 2; fi
mkdir -p "$root/artifacts/dotnet-home"
export DOTNET_CLI_HOME="$root/artifacts/dotnet-home" DOTNET_GENERATE_ASPNET_CERTIFICATE=false DOTNET_CLI_TELEMETRY_OPTOUT=1 DOTNET_SKIP_FIRST_TIME_EXPERIENCE=1 DOTNET_NOLOGO=1
"$dotnet" run --project "$root/tests/UnityIosHook/IosHook.csproj" -- "$project"
