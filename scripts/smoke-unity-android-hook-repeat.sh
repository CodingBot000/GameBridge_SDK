#!/usr/bin/env bash
# Isolated Unity Android Gradle export hook idempotence; no user projects.
set -euo pipefail
root="$(cd "$(dirname "$0")/.." && pwd)"
if [[ -z "${GAMEBRIDGE_UPM_STAGING:-}" || -z "${GAMEBRIDGE_UNITY_PACKAGE_CACHE:-}" ]]; then echo 'DEFERRED_ENV: staging and exact package cache required' >&2; exit 2; fi
if ! command -v unity >/dev/null 2>&1; then echo 'DEFERRED_ENV: Unity CLI missing' >&2; exit 2; fi
python3 "$root/harness/check-staging.py" "$GAMEBRIDGE_UPM_STAGING"
python3 - "$root" "$GAMEBRIDGE_UPM_STAGING" <<'PYMATCH'
import importlib.util,sys
from pathlib import Path
root,stage=map(Path,sys.argv[1:]);spec=importlib.util.spec_from_file_location('android_e2e',root/'harness/run-unity-android-mock-e2e.py');module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
try: module.verify_staged_source_matches_checkout(stage)
except module.GateError: raise SystemExit('FAIL: staged SDK source differs from checkout')
PYMATCH
prepared="$(bash "$root/scripts/prepare-unity-android-mock.sh" --prepare)"
project="$(printf '%s\n' "$prepared" | sed -n 's/^Prepared consumer: //p')"
[[ "$project" == "$root"/artifacts/unity-android-mock.*/project && -d "$project" ]] || { echo 'FAIL: invalid isolated project' >&2; exit 1; }
python3 - "$root" "$project" "$GAMEBRIDGE_UNITY_PACKAGE_CACHE" <<'PY'
import importlib.util,sys
from pathlib import Path
root,project,cache=map(Path,sys.argv[1:]);spec=importlib.util.spec_from_file_location('cache',root/'harness/run-unity-ios-mock-push-e2e.py');module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);module.embed_cached_packages(cache,project)
PY
cp "$root/tests/UnityHookIdempotence/Editor/AndroidHookIdempotence.cs" "$project/Assets/Editor/AndroidHookIdempotence.cs"
output="$(dirname "$project")"; export GAMEBRIDGE_UNITY_ANDROID_EXPORT="$output/gradle-export"
echo "Evidence directory: $output"
set +e
UNITY_NO_UPDATE_CHECK=1 unity run "$project" --editor-version "${UNITY_EDITOR_VERSION:-6000.5.8f1}" --timeout 900 --non-interactive -- -buildTarget Android -executeMethod AndroidHookIdempotence.Run > "$output/hook-cli.log" 2>&1
code=$?
set -e
if [[ "$code" != 0 || ! -f "$project/Logs/Editor.log" ]] || ! grep -Fxq 'GB_ANDROID_HOOK_REPEAT PASS' "$project/Logs/Editor.log"; then
  echo 'FAIL: actual Unity Android hook repeat did not pass' >&2; exit 1
fi
printf '%s\n' 'GB_ANDROID_HOOK_REPEAT PASS' > "$output/hook-markers.log"
echo 'Unity Android Gradle export hook repeat PASS; APK and Player are separate.'
