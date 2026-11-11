#!/usr/bin/env bash
# Compile-only check; this does not execute the Unity Editor, JNI, or Player.
set -euo pipefail
root="$(cd "$(dirname "$0")/.." && pwd)"
if [[ -z "${UNITY_EDITOR_PATH:-}" || ! -f "$UNITY_EDITOR_PATH" ]]; then echo 'CONFIG_REQUIRED: UNITY_EDITOR_PATH' >&2; exit 2; fi
contents="$(cd "$(dirname "$UNITY_EDITOR_PATH")/.." && pwd)"
export DOTNET_ROOT="$contents/Resources/Scripting/DotNetSdk" DOTNET_CLI_HOME="$root/artifacts/dotnet-home"
export DOTNET_CLI_TELEMETRY_OPTOUT=1 DOTNET_SKIP_FIRST_TIME_EXPERIENCE=1 DOTNET_NOLOGO=1
export GAMEBRIDGE_ROOT="$root" GAMEBRIDGE_UNITY_MANAGED="$contents/Resources/Scripting/Managed/UnityEngine"
export GAMEBRIDGE_NEWTONSOFT_DLL="${NEWTONSOFT_DLL:-$root/artifacts/unity-newtonsoft/package/Runtime/Newtonsoft.Json.dll}"
if [[ ! -x "$DOTNET_ROOT/dotnet" || ! -f "$GAMEBRIDGE_NEWTONSOFT_DLL" || ! -f "$GAMEBRIDGE_UNITY_MANAGED/UnityEngine.CoreModule.dll" ]]; then echo 'CONFIG_REQUIRED: Unity managed references and Newtonsoft.Json' >&2; exit 2; fi
"$DOTNET_ROOT/dotnet" build "$root/tests/UnityAndroidMockConsumer/ScenarioCheck.csproj" -p:DefineConstants=UNITY_ANDROID -p:BaseIntermediateOutputPath="$root/artifacts/v2-scenario-obj/" -p:OutputPath="$root/artifacts/v2-scenario-bin/" --nologo
