#!/usr/bin/env bash
# Isolated Editor sample consumer; no user project or production provider.
set -euo pipefail
root="$(cd "$(dirname "$0")/.." && pwd)"
stage="${GAMEBRIDGE_UPM_STAGING:-}"; cache="${GAMEBRIDGE_UNITY_PACKAGE_CACHE:-}"
if [[ -z "$stage" || ! -d "$stage/com.gamebridge.sdk" || -z "$cache" || ! -d "$cache" ]]; then echo 'DEFERRED_ENV: staged SDK and exact package cache required' >&2; exit 2; fi
if ! command -v unity >/dev/null 2>&1; then echo 'DEFERRED_ENV: Unity CLI missing' >&2; exit 2; fi
python3 "$root/harness/check-staging.py" "$stage"
python3 - "$root" "$stage" <<'PYMATCH'
import importlib.util,sys
from pathlib import Path
root,stage=map(Path,sys.argv[1:]);spec=importlib.util.spec_from_file_location('android_e2e',root/'harness/run-unity-android-mock-e2e.py');module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
try: module.verify_staged_source_matches_checkout(stage)
except module.GateError: raise SystemExit('FAIL: staged SDK source differs from checkout')
print('Staged SDK source matches checkout')
PYMATCH
mkdir -p "$root/artifacts"; output="$(mktemp -d "$root/artifacts/offline-sample.XXXXXX")"; project="$output/project"
mkdir -p "$project/Assets/Editor" "$project/Assets/Tests/Editor" "$project/Packages" "$project/ProjectSettings"
cp -R "$stage/com.gamebridge.sdk" "$project/Packages/com.gamebridge.sdk"
cp "$root/tests/UnityOfflineSample/Setup/ImportSamples.cs" "$project/Assets/Editor/ImportSamples.cs"
python3 - "$root" "$project" "$cache" <<'PY'
import importlib.util,json,os,shutil,sys
from pathlib import Path
root,project,cache=map(Path,sys.argv[1:]);spec=importlib.util.spec_from_file_location('cache',root/'harness/run-unity-ios-mock-push-e2e.py');module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);module.embed_cached_packages(cache,project)
base=Path('/Applications/Unity/Hub/Editor')/os.environ.get('UNITY_EDITOR_VERSION','6000.5.8f1')/'Unity.app/Contents/Resources/PackageManager/BuiltInPackages'
for name,version in [('com.unity.test-framework','1.7.0'),('com.unity.ext.nunit','2.1.0'),('com.unity.ugui','2.5.0')]:
 source=base/name
 if json.loads((source/'package.json').read_text()).get('version')!=version:raise SystemExit('DEFERRED_ENV: required exact package unavailable')
 shutil.copytree(source,project/'Packages'/name,ignore=shutil.ignore_patterns('Tests','Tests.meta'))
PY
printf '%s\n' '{"dependencies":{"com.unity.test-framework":"1.7.0","com.unity.ugui":"2.5.0"}}' > "$project/Packages/manifest.json"
printf 'm_EditorVersion: %s\n' "${UNITY_EDITOR_VERSION:-6000.5.8f1}" > "$project/ProjectSettings/ProjectVersion.txt"
echo "Evidence directory: $output"
set +e
UNITY_NO_UPDATE_CHECK=1 UNITY_NO_CONSENT_PROMPT=1 unity run "$project" --editor-version "${UNITY_EDITOR_VERSION:-6000.5.8f1}" --timeout 300 --non-interactive -- -executeMethod GameBridgeSampleImporter.Import > "$output/import-cli.log" 2>&1
import_code=$?
set -e
if [[ "$import_code" != 0 ]] || ! grep -q 'GB_SAMPLE_IMPORT PASS Editor Offline Demo' "$project/Logs/Editor.log" || ! grep -q 'GB_SAMPLE_IMPORT PASS Native Mock and Sandbox Demo' "$project/Logs/Editor.log"; then
  echo 'FAIL: Unity Package Manager sample import incomplete' >&2; exit 1
fi
grep -E '^GB_SAMPLE_IMPORT PASS (Editor Offline Demo|Native Mock and Sandbox Demo)$' "$project/Logs/Editor.log" > "$output/import-markers.log"
if [[ "$(grep -Fxc 'GB_SAMPLE_IMPORT PASS Editor Offline Demo' "$output/import-markers.log")" != 1 || "$(grep -Fxc 'GB_SAMPLE_IMPORT PASS Native Mock and Sandbox Demo' "$output/import-markers.log")" != 1 ]]; then
  echo 'FAIL: Unity sample import markers missing or duplicated' >&2; exit 1
fi
cp "$root/tests/UnityOfflineSample/Editor/"* "$project/Assets/Tests/Editor/"
set +e
UNITY_NO_UPDATE_CHECK=1 UNITY_NO_CONSENT_PROMPT=1 unity test "$project" --editor-version "${UNITY_EDITOR_VERSION:-6000.5.8f1}" --mode EditMode --filter OfflineSampleTests --output "$output/results.xml" --timeout 300 --non-interactive > "$output/unity-cli.log" 2>&1
code=$?
set -e
if [[ ! -f "$output/results.xml" ]]; then
  if [[ "$code" == 8 ]] || grep -Eqi 'error CS[0-9]+|compilation failed' "$output/unity-cli.log"; then echo 'FAIL: Unity test or compilation failed' >&2; exit 1; fi
  echo "INCOMPLETE: no Unity test result; CLI exit $code" >&2; exit 2
fi
python3 "$root/harness/check-unity-offline-sample-result.py" "$output/results.xml" "$code"
