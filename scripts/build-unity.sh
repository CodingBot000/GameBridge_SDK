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
cat > "$project/Packages/manifest.json" <<'JSON'
{"dependencies":{"com.unity.test-framework":"1.4.3"}}
JSON
printf 'm_EditorVersion: %s\n' "${UNITY_EDITOR_VERSION:-6000.5.8f1}" > "$project/ProjectSettings/ProjectVersion.txt"
printf 'Evidence directory: %s\n' "$output"
set +e
UNITY_NO_UPDATE_CHECK=1 UNITY_NO_CONSENT_PROMPT=1 python3 - "$output/unity-cli.log" unity test "$project" --editor-version "${UNITY_EDITOR_VERSION:-6000.5.8f1}" --mode EditMode --filter GameBridgeConsumerTests.ConsumerLifecycleTests --output "$output/results.xml" --timeout 60 --non-interactive <<'PYRUN'
import os, signal, subprocess, sys
with open(sys.argv[1], 'w', encoding='utf-8') as log:
    process = subprocess.Popen(sys.argv[2:], stdout=log, stderr=subprocess.STDOUT, start_new_session=True)
    try:
        sys.exit(process.wait(timeout=65))
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
