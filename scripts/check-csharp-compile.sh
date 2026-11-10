#!/usr/bin/env bash
# Compiler-only check, not Unity Editor, Android JNI or iOS IL2CPP validation.
set -euo pipefail
root="$(cd "$(dirname "$0")/.." && pwd)"
if [[ -z "${UNITY_EDITOR_PATH:-}" || ! -f "$UNITY_EDITOR_PATH" ]]; then
  echo 'CONFIG_REQUIRED: UNITY_EDITOR_PATH (Unity executable)' >&2; exit 2
fi
contents="$(cd "$(dirname "$UNITY_EDITOR_PATH")/.." && pwd)"
dotnet="$contents/Resources/Scripting/DotNetSdk/dotnet"
managed="$contents/Resources/Scripting/Managed/UnityEngine"
if [[ ! -x "$dotnet" || ! -f "$managed/UnityEngine.CoreModule.dll" || ! -f "$managed/UnityEngine.AndroidJNIModule.dll" ]]; then
  echo 'Unity bundled .NET SDK or managed reference assemblies unavailable.' >&2; exit 2
fi
mkdir -p "$root/artifacts/csharp-check" "$root/artifacts/dotnet-home"
cat > "$root/artifacts/csharp-check/BridgeCheck.csproj" <<'PROJECT'
<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup><TargetFramework>net8.0</TargetFramework><EnableDefaultCompileItems>false</EnableDefaultCompileItems><Nullable>disable</Nullable></PropertyGroup>
  <ItemGroup>
    <Compile Include="$(GAMEBRIDGE_ROOT)/unity/Packages/com.gamebridge.sdk/Runtime/Platforms/AndroidTransport.cs" />
    <Compile Include="$(GAMEBRIDGE_ROOT)/unity/Packages/com.gamebridge.sdk/Runtime/Platforms/IosTransport.cs" />
    <Compile Include="$(GAMEBRIDGE_ROOT)/unity/Packages/com.gamebridge.sdk/Runtime/Core/RequestRegistry.cs" />
    <Reference Include="Newtonsoft.Json"><HintPath>$(GAMEBRIDGE_NEWTONSOFT_DLL)</HintPath></Reference>
    <Reference Include="UnityEngine.CoreModule"><HintPath>$(GAMEBRIDGE_UNITY_MANAGED)/UnityEngine.CoreModule.dll</HintPath></Reference>
    <Reference Include="UnityEngine.AndroidJNIModule"><HintPath>$(GAMEBRIDGE_UNITY_MANAGED)/UnityEngine.AndroidJNIModule.dll</HintPath></Reference>
  </ItemGroup>
</Project>
PROJECT
export DOTNET_ROOT="$contents/Resources/Scripting/DotNetSdk" DOTNET_CLI_HOME="$root/artifacts/dotnet-home"
export DOTNET_CLI_TELEMETRY_OPTOUT=1 DOTNET_GENERATE_ASPNET_CERTIFICATE=false DOTNET_SKIP_FIRST_TIME_EXPERIENCE=1 DOTNET_NOLOGO=1
export GAMEBRIDGE_ROOT="$root" GAMEBRIDGE_UNITY_MANAGED="$managed"
export GAMEBRIDGE_NEWTONSOFT_DLL="${NEWTONSOFT_DLL:-$root/artifacts/unity-newtonsoft/package/Runtime/Newtonsoft.Json.dll}"
if [[ ! -f "$GAMEBRIDGE_NEWTONSOFT_DLL" ]]; then echo 'CONFIG_REQUIRED: NEWTONSOFT_DLL (Unity package 3.2.2)' >&2; exit 2; fi
"$dotnet" build "$root/artifacts/csharp-check/BridgeCheck.csproj" -p:DefineConstants=UNITY_ANDROID --nologo
"$dotnet" build "$root/artifacts/csharp-check/BridgeCheck.csproj" -p:DefineConstants=UNITY_IOS --nologo
