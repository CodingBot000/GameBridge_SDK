#!/usr/bin/env bash
# Explicit self-hosted isolated runner gate. Missing infrastructure is never PASS.
set -euo pipefail
root="$(cd "$(dirname "$0")/.." && pwd)"
cd "$root"
for name in UNITY_EDITOR_PATH GAMEBRIDGE_UPM_STAGING GAMEBRIDGE_UNITY_PACKAGE_CACHE GAMEBRIDGE_ANDROID_SERIAL GAMEBRIDGE_TEST_AVD_NAME GAMEBRIDGE_PUSH_ANDROID_SERIAL GAMEBRIDGE_PUSH_TEST_AVD_NAME; do
  if [[ -z "${!name:-}" ]]; then echo "DEFERRED_ENV: $name is required" >&2; exit 2; fi
done
if [[ "${GAMEBRIDGE_TEST_AVD_NAME}" != GameBridge_V2_* || "${GAMEBRIDGE_PUSH_TEST_AVD_NAME}" != GameBridge_V2_* || "$GAMEBRIDGE_ANDROID_SERIAL" == "$GAMEBRIDGE_PUSH_ANDROID_SERIAL" ]]; then echo 'DEFERRED_ENV: dedicated GameBridge_V2_ AVD required' >&2; exit 2; fi
if [[ ! -f "$UNITY_EDITOR_PATH" ]]; then echo 'DEFERRED_ENV: UNITY_EDITOR_PATH must be an installed Unity Editor executable' >&2; exit 2; fi
if [[ ! -d "$GAMEBRIDGE_UNITY_PACKAGE_CACHE" ]]; then echo 'DEFERRED_ENV: exact Unity package cache is required' >&2; exit 2; fi
if ! command -v unity >/dev/null 2>&1; then echo 'DEFERRED_ENV: Unity CLI missing' >&2; exit 2; fi
set +e
license_json="$(UNITY_NO_UPDATE_CHECK=1 unity license status --format json)"
license_exit=$?
set -e
if [[ "$license_exit" != 0 ]] || ! python3 -c 'import json,sys; x=json.load(sys.stdin); sys.exit(0 if x.get("success") and (x.get("data") or {}).get("active") is True else 1)' <<< "$license_json"; then
  echo 'DEFERRED_ENV: active Unity license required' >&2; exit 2
fi
export GAMEBRIDGE_RUN_UNITY_EDITOR=true GAMEBRIDGE_RUN_UNITY_PUSH_E2E=true
export GAMEBRIDGE_MAVEN_REPO="$GAMEBRIDGE_UPM_STAGING/com.gamebridge.sdk/Editor/GameBridgeArtifacts~/Android/maven-repo"
export GAMEBRIDGE_IOS_XCFRAMEWORK="$GAMEBRIDGE_UPM_STAGING/com.gamebridge.sdk/Editor/GameBridgeArtifacts~/iOS/GameBridgeNative.xcframework"
bash scripts/build-unity.sh --editor-smoke
bash scripts/smoke-unity-offline-sample.sh
bash scripts/smoke-unity-android-hook-repeat.sh
bash scripts/smoke-unity-ios-hook-repeat.sh
pii_nonce="$(python3 -c 'import secrets; print(secrets.token_hex(16))')"
set +e
pii_output="$(python3 harness/run-unity-pii-current.py --run-local --staging "$GAMEBRIDGE_UPM_STAGING" --serial "$GAMEBRIDGE_ANDROID_SERIAL" --expected-avd "$GAMEBRIDGE_TEST_AVD_NAME" --nonce "$pii_nonce" --package-cache "$GAMEBRIDGE_UNITY_PACKAGE_CACHE")"
pii_code=$?
set -e
printf '%s\n' "$pii_output"
if [[ "$pii_code" != 0 ]]; then exit "$pii_code"; fi
pii_directory="$(printf '%s\n' "$pii_output" | sed -n 's/^PII gate result: PASS Evidence directory: //p')"
[[ "$pii_directory" == artifacts/unity-pii-current-* ]] || { echo 'FAIL: PII gate evidence missing' >&2; exit 1; }
export GAMEBRIDGE_UNITY_PII_EVIDENCE="$pii_directory/result.json" GAMEBRIDGE_UNITY_PII_NONCE="$pii_nonce"
# The complete strict suite must execute in this run; missing fixtures or
# remaining PARTIAL scenarios cannot be replaced by prior evidence.
python3 harness/run-strict-local-isolated.py --run-local
