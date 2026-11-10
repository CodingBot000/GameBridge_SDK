#!/usr/bin/env bash
# Standalone .NET smoke; does not validate Unity Editor, IL2CPP, JNI or C ABI linking.
set -euo pipefail
root="$(cd "$(dirname "$0")/.." && pwd)"
if [[ -z "${UNITY_EDITOR_PATH:-}" || ! -f "$UNITY_EDITOR_PATH" ]]; then echo 'CONFIG_REQUIRED: UNITY_EDITOR_PATH' >&2; exit 2; fi
contents="$(cd "$(dirname "$UNITY_EDITOR_PATH")/.." && pwd)"
dotnet="$contents/Resources/Scripting/DotNetSdk/dotnet"
export GAMEBRIDGE_NEWTONSOFT_DLL="${NEWTONSOFT_DLL:-$root/artifacts/unity-newtonsoft/package/Runtime/Newtonsoft.Json.dll}"
if [[ ! -x "$dotnet" || ! -f "$GAMEBRIDGE_NEWTONSOFT_DLL" ]]; then echo 'CONFIG_REQUIRED: Unity .NET SDK and NEWTONSOFT_DLL' >&2; exit 2; fi
mkdir -p "$root/artifacts/registry-smoke" "$root/artifacts/dotnet-home"
cat > "$root/artifacts/registry-smoke/RegistrySmoke.csproj" <<'PROJECT'
<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup><OutputType>Exe</OutputType><TargetFramework>net8.0</TargetFramework><EnableDefaultCompileItems>false</EnableDefaultCompileItems><DefineConstants>GAMEBRIDGE_TEST_OFFLINE</DefineConstants></PropertyGroup>
  <ItemGroup>
    <Compile Include="$(GAMEBRIDGE_ROOT)/unity/Packages/com.gamebridge.sdk/Runtime/Core/RequestRegistry.cs" />
    <Compile Include="$(GAMEBRIDGE_ROOT)/unity/Packages/com.gamebridge.sdk/Runtime/Core/WireModels.cs" />
    <Compile Include="$(GAMEBRIDGE_ROOT)/unity/Packages/com.gamebridge.sdk/Runtime/Models.cs" />
    <Compile Include="$(GAMEBRIDGE_ROOT)/scripts/registry-smoke.cs" />
    <Compile Include="$(GAMEBRIDGE_ROOT)/unity/Packages/com.gamebridge.sdk/Runtime/Core/IWireTransport.cs" />
    <Compile Include="$(GAMEBRIDGE_ROOT)/unity/Packages/com.gamebridge.sdk/Runtime/Core/EditorOfflineTransport.cs" />
    <Reference Include="Newtonsoft.Json"><HintPath>$(GAMEBRIDGE_NEWTONSOFT_DLL)</HintPath></Reference>
  </ItemGroup>
</Project>
PROJECT
export GAMEBRIDGE_ROOT="$root" DOTNET_ROOT="$contents/Resources/Scripting/DotNetSdk" DOTNET_CLI_HOME="$root/artifacts/dotnet-home"
export DOTNET_CLI_TELEMETRY_OPTOUT=1 DOTNET_GENERATE_ASPNET_CERTIFICATE=false DOTNET_SKIP_FIRST_TIME_EXPERIENCE=1 DOTNET_NOLOGO=1
"$dotnet" run --project "$root/artifacts/registry-smoke/RegistrySmoke.csproj" --nologo
