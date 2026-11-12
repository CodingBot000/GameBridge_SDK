#!/usr/bin/env bash
# Creates a new disposable consumer; never modifies unity/Demo or publishes anything.
set -euo pipefail
root="$(cd "$(dirname "$0")/.." && pwd)"
if [[ "$#" != 1 || "${1:-}" != '--editor-smoke' ]]; then echo 'Usage: build-unity.sh --editor-smoke' >&2; exit 64; fi
if ! command -v unity >/dev/null 2>&1; then echo 'DEFERRED_ENV: Unity CLI is unavailable' >&2; exit 2; fi
if [[ -z "${GAMEBRIDGE_UPM_STAGING:-}" || ! -d "$GAMEBRIDGE_UPM_STAGING/com.gamebridge.sdk" ]]; then
  echo 'CONFIG_REQUIRED: GAMEBRIDGE_UPM_STAGING must name an existing packaged SDK staging directory' >&2; exit 2
fi
python3 "$root/harness/check-staging.py" "$GAMEBRIDGE_UPM_STAGING"
mkdir -p "$root/artifacts"
output="$(mktemp -d "$root/artifacts/unity-consumer.XXXXXX")"
project="$output/project"
mkdir -p "$project/Assets/Tests/Editor" "$project/Packages" "$project/ProjectSettings"
cp -R "$GAMEBRIDGE_UPM_STAGING/com.gamebridge.sdk" "$project/Packages/com.gamebridge.sdk"
cp "$root/tests/UnityConsumer/Editor/"* "$project/Assets/Tests/Editor/"
if [[ -n "${GAMEBRIDGE_UNITY_PACKAGE_CACHE:-}" ]]; then
  # Reuse only previously resolved exact packages, inside this disposable consumer.
  python3 - "$root" "$project" "$GAMEBRIDGE_UNITY_PACKAGE_CACHE" <<'PYCACHE'
import importlib.util, json, shutil, sys
from pathlib import Path
root, project, cache = map(Path, sys.argv[1:])
spec=importlib.util.spec_from_file_location('push_cache',root/'harness/run-unity-ios-mock-push-e2e.py')
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
module.embed_cached_packages(cache,project)
editor=Path('/Applications/Unity/Hub/Editor')/(__import__('os').environ.get('UNITY_EDITOR_VERSION','6000.5.8f1'))/'Unity.app/Contents/Resources/PackageManager/BuiltInPackages'
for name,version in [('com.unity.test-framework','1.7.0'),('com.unity.ext.nunit','2.1.0')]:
    source=editor/name
    if json.loads((source/'package.json').read_text()).get('version') != version: raise SystemExit('CONFIG_REQUIRED: exact Unity Test Framework version unavailable')
    shutil.copytree(source,project/'Packages'/name,ignore=shutil.ignore_patterns('Tests','Tests.meta'))
PYCACHE
  printf '%s\n' '{"dependencies":{"com.unity.test-framework":"1.7.0"}}' > "$project/Packages/manifest.json"
else
  printf '%s\n' '{"dependencies":{"com.unity.test-framework":"1.4.3"}}' > "$project/Packages/manifest.json"
fi
printf 'm_EditorVersion: %s\n' "${UNITY_EDITOR_VERSION:-6000.5.8f1}" > "$project/ProjectSettings/ProjectVersion.txt"
printf 'Evidence directory: %s\n' "$output"
set +e
test_timeout="${GAMEBRIDGE_UNITY_TEST_TIMEOUT_SECONDS:-300}"
[[ "$test_timeout" =~ ^[0-9]+$ ]] && (( test_timeout > 0 )) || { echo 'Invalid test timeout' >&2; exit 64; }
UNITY_NO_UPDATE_CHECK=1 UNITY_NO_CONSENT_PROMPT=1 python3 - "$output/unity-cli.log" "$test_timeout" unity test "$project" --editor-version "${UNITY_EDITOR_VERSION:-6000.5.8f1}" --mode EditMode --filter GameBridgeConsumerTests.ConsumerLifecycleTests --output "$output/results.xml" --timeout "$test_timeout" --non-interactive <<'PYRUN'
import os, signal, subprocess, sys
with open(sys.argv[1], 'w', encoding='utf-8') as log:
    process = subprocess.Popen(sys.argv[3:], stdout=log, stderr=subprocess.STDOUT, start_new_session=True)
    try:
        sys.exit(process.wait(timeout=int(sys.argv[2]) + 30))
    except subprocess.TimeoutExpired:
        log.write('Unity CLI invocation timed out without a test verdict.\n'); log.flush()
        try: os.killpg(process.pid, signal.SIGTERM)
        except ProcessLookupError: pass
        try: process.wait(timeout=3)
        except subprocess.TimeoutExpired:
            try: os.killpg(process.pid, signal.SIGKILL)
            except ProcessLookupError: pass
            process.wait()
        sys.exit(124)
PYRUN
code=$?
set -e
if [[ -f "$output/results.xml" ]]; then
  python3 "$root/scripts/check-unity-test-result.py" "$output/results.xml" || exit 1
  if [[ "$code" != 0 ]]; then echo "Unity CLI returned $code despite a passing report." >&2; exit 1; fi
  exit 0
fi
if [[ "$code" == 8 ]] || grep -Eqi 'error CS[0-9]+|compilation failed' "$output/unity-cli.log"; then
  echo 'Unity consumer compile or tests FAILED; see evidence log.' >&2; exit 1
fi
echo "INCOMPLETE: Unity CLI returned $code without a test verdict; see evidence log." >&2
exit 2
