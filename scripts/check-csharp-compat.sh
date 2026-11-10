#!/usr/bin/env bash
set -euo pipefail
root="$(cd "$(dirname "$0")/.." && pwd)"
if [[ -z "${UNITY_EDITOR_PATH:-}" || ! -f "$UNITY_EDITOR_PATH" ]]; then echo 'CONFIG_REQUIRED: UNITY_EDITOR_PATH' >&2; exit 2; fi
contents="$(cd "$(dirname "$UNITY_EDITOR_PATH")/.." && pwd)"
dotnet="$contents/Resources/Scripting/DotNetSdk/dotnet"
managed="$contents/Resources/Scripting/Managed/UnityEngine"
if [[ ! -x "$dotnet" || ! -f "$managed/UnityEngine.CoreModule.dll" ]]; then echo 'DEFERRED_ENV: Unity managed references unavailable' >&2; exit 2; fi
bash "$root/scripts/check-unity-ios-host.sh"
mkdir -p "$root/artifacts" "$root/artifacts/dotnet-home"
out="$(mktemp -d "$root/artifacts/csharp-compat.XXXXXX")"
cat > "$out/LegacyConsumer.csproj" <<'PROJECT'
<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup><OutputType>Exe</OutputType><TargetFramework>net8.0</TargetFramework><EnableDefaultCompileItems>false</EnableDefaultCompileItems></PropertyGroup>
  <ItemGroup>
    <Compile Include="$(GAMEBRIDGE_ROOT)/tests/ApiCompatibility/LegacyConsumer.cs" />
    <Reference Include="GameBridge.Runtime"><HintPath>$(GAMEBRIDGE_ROOT)/tests/UnityIosHost/bin/GameBridgeReference/net8.0/GameBridge.Runtime.dll</HintPath></Reference>
    <Reference Include="UnityEngine.CoreModule"><HintPath>$(GAMEBRIDGE_UNITY_MANAGED)/UnityEngine.CoreModule.dll</HintPath></Reference>
  </ItemGroup>
</Project>
PROJECT
export GAMEBRIDGE_ROOT="$root" GAMEBRIDGE_UNITY_MANAGED="$managed" DOTNET_CLI_HOME="$root/artifacts/dotnet-home" DOTNET_GENERATE_ASPNET_CERTIFICATE=false DOTNET_CLI_TELEMETRY_OPTOUT=1 DOTNET_SKIP_FIRST_TIME_EXPERIENCE=1 DOTNET_NOLOGO=1
"$dotnet" run --project "$out/LegacyConsumer.csproj" --configuration Release --nologo
printf 'Evidence directory: %s\n' "$out"
