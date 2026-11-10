#!/usr/bin/env bash
set -euo pipefail
root="$(cd "$(dirname "$0")/.." && pwd)"
if [[ -z "${UNITY_EDITOR_PATH:-}" || ! -f "$UNITY_EDITOR_PATH" ]]; then echo 'CONFIG_REQUIRED: UNITY_EDITOR_PATH' >&2; exit 2; fi
contents="$(cd "$(dirname "$UNITY_EDITOR_PATH")/.." && pwd)"
dotnet="$contents/Resources/Scripting/DotNetSdk/dotnet"
export UNITY_MANAGED="$contents/Resources/Scripting/Managed/UnityEngine"
export UNITY_UI_DLL="${UNITY_UI_DLL:-$contents/Resources/PackageManager/ProjectTemplates/libcache/com.unity.template.3d-cross-platform-17.0.14/ScriptAssemblies/UnityEngine.UI.dll}"
export GAMEBRIDGE_NEWTONSOFT_DLL="${NEWTONSOFT_DLL:-$root/artifacts/unity-newtonsoft/package/Runtime/Newtonsoft.Json.dll}"
if [[ ! -x "$dotnet" || ! -f "$UNITY_UI_DLL" || ! -f "$GAMEBRIDGE_NEWTONSOFT_DLL" ]]; then echo 'CONFIG_REQUIRED: Unity bundled .NET, Unity UI and Newtonsoft assemblies' >&2; exit 2; fi
mkdir -p "$root/artifacts/dotnet-home"
export DOTNET_CLI_HOME="$root/artifacts/dotnet-home" DOTNET_GENERATE_ASPNET_CERTIFICATE=false DOTNET_CLI_TELEMETRY_OPTOUT=1 DOTNET_SKIP_FIRST_TIME_EXPERIENCE=1 DOTNET_NOLOGO=1
"$dotnet" build "$root/tests/UnityOfflineDemo/UnityOfflineDemo.csproj" --nologo
