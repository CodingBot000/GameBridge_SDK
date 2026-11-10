#!/usr/bin/env bash
set -euo pipefail
root="$(cd "$(dirname "$0")/.." && pwd)"
if [[ -z "${UNITY_EDITOR_PATH:-}" || ! -f "$UNITY_EDITOR_PATH" ]]; then echo 'CONFIG_REQUIRED: UNITY_EDITOR_PATH' >&2; exit 2; fi
contents="$(cd "$(dirname "$UNITY_EDITOR_PATH")/.." && pwd)"
dotnet="$contents/Resources/Scripting/DotNetSdk/dotnet"
newtonsoft="${NEWTONSOFT_DLL:-$root/artifacts/unity-newtonsoft/package/Runtime/Newtonsoft.Json.dll}"
if [[ ! -x "$dotnet" || ! -f "$newtonsoft" ]]; then echo 'DEFERRED_ENV: .NET or Newtonsoft unavailable' >&2; exit 2; fi
mkdir -p "$root/artifacts" "$root/artifacts/dotnet-home"
output="$(mktemp -d "$root/artifacts/lifecycle-stress.XXXXXX")"
cat > "$output/LifecycleStress.csproj" <<'PROJECT'
<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup><OutputType>Exe</OutputType><TargetFramework>net8.0</TargetFramework><EnableDefaultCompileItems>false</EnableDefaultCompileItems><DefineConstants>GAMEBRIDGE_TEST_OFFLINE</DefineConstants><Optimize>true</Optimize></PropertyGroup>
  <ItemGroup>
    <Compile Include="$(GAMEBRIDGE_ROOT)/unity/Packages/com.gamebridge.sdk/Runtime/Core/RequestRegistry.cs" />
    <Compile Include="$(GAMEBRIDGE_ROOT)/unity/Packages/com.gamebridge.sdk/Runtime/Core/WireModels.cs" />
    <Compile Include="$(GAMEBRIDGE_ROOT)/unity/Packages/com.gamebridge.sdk/Runtime/Core/IWireTransport.cs" />
    <Compile Include="$(GAMEBRIDGE_ROOT)/unity/Packages/com.gamebridge.sdk/Runtime/Core/EditorOfflineTransport.cs" />
    <Compile Include="$(GAMEBRIDGE_ROOT)/unity/Packages/com.gamebridge.sdk/Runtime/Models.cs" />
    <Compile Include="$(GAMEBRIDGE_ROOT)/unity/Packages/com.gamebridge.sdk/Runtime/GameBridgeConfig.cs" />
    <Compile Include="$(GAMEBRIDGE_ROOT)/unity/Packages/com.gamebridge.sdk/Runtime/GameBridgeClient.cs" />
    <Compile Include="$(GAMEBRIDGE_ROOT)/tests/LifecycleStress/Program.cs" />
    <Reference Include="Newtonsoft.Json"><HintPath>$(GAMEBRIDGE_NEWTONSOFT_DLL)</HintPath></Reference>
  </ItemGroup>
</Project>
PROJECT
export GAMEBRIDGE_ROOT="$root" GAMEBRIDGE_NEWTONSOFT_DLL="$newtonsoft" GAMEBRIDGE_STRESS_OUTPUT="$output/result.json"
export GAMEBRIDGE_SOURCE_HEAD="$(git -C "$root" rev-parse HEAD)" DOTNET_CLI_HOME="$root/artifacts/dotnet-home" DOTNET_GENERATE_ASPNET_CERTIFICATE=false DOTNET_CLI_TELEMETRY_OPTOUT=1 DOTNET_SKIP_FIRST_TIME_EXPERIENCE=1 DOTNET_NOLOGO=1
"$dotnet" run --project "$output/LifecycleStress.csproj" --configuration Release --nologo
printf 'Evidence directory: %s\n' "$output"
