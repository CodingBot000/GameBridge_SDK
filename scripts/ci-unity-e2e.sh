#!/usr/bin/env bash
# Explicit self-hosted isolated runner gate. Missing infrastructure is never PASS.
set -euo pipefail
root="$(cd "$(dirname "$0")/.." && pwd)"
cd "$root"
for name in UNITY_EDITOR_PATH GAMEBRIDGE_UPM_STAGING GAMEBRIDGE_ANDROID_SERIAL GAMEBRIDGE_TEST_AVD_NAME GAMEBRIDGE_PUSH_ANDROID_SERIAL GAMEBRIDGE_PUSH_TEST_AVD_NAME; do
  if [[ -z "${!name:-}" ]]; then echo "DEFERRED_ENV: $name is required" >&2; exit 2; fi
done
if [[ "${GAMEBRIDGE_TEST_AVD_NAME}" != GameBridge_V2_* || "${GAMEBRIDGE_PUSH_TEST_AVD_NAME}" != GameBridge_V2_* || "$GAMEBRIDGE_ANDROID_SERIAL" == "$GAMEBRIDGE_PUSH_ANDROID_SERIAL" ]]; then echo 'DEFERRED_ENV: dedicated GameBridge_V2_ AVD required' >&2; exit 2; fi
if [[ ! -f "$UNITY_EDITOR_PATH" ]]; then echo 'DEFERRED_ENV: UNITY_EDITOR_PATH must be an installed Unity Editor executable' >&2; exit 2; fi
if ! command -v unity >/dev/null 2>&1; then echo 'DEFERRED_ENV: Unity CLI missing' >&2; exit 2; fi
set +e
license_json="$(UNITY_NO_UPDATE_CHECK=1 unity license status --format json)"
license_exit=$?
set -e
if [[ "$license_exit" != 0 ]] || ! python3 -c 'import json,sys; x=json.load(sys.stdin); sys.exit(0 if x.get("success") and (x.get("data") or {}).get("active") is True else 1)' <<< "$license_json"; then
  echo 'DEFERRED_ENV: active Unity license required' >&2; exit 2
fi
export GAMEBRIDGE_RUN_UNITY_EDITOR=true GAMEBRIDGE_RUN_UNITY_PUSH_E2E=true
bash scripts/build-unity.sh --editor-smoke
android_args=(--run-local --staging "$GAMEBRIDGE_UPM_STAGING" --serial "$GAMEBRIDGE_ANDROID_SERIAL" --expected-avd "$GAMEBRIDGE_TEST_AVD_NAME")
ios_args=(--run-local --adhoc --staging "$GAMEBRIDGE_UPM_STAGING")
if [[ -n "${GAMEBRIDGE_UNITY_PACKAGE_CACHE:-}" ]]; then
  android_args+=(--package-cache "$GAMEBRIDGE_UNITY_PACKAGE_CACHE")
  ios_args+=(--package-cache "$GAMEBRIDGE_UNITY_PACKAGE_CACHE")
fi
python3 harness/run-unity-android-mock-e2e.py "${android_args[@]}"
python3 harness/run-unity-ios-mock-e2e.py "${ios_args[@]}"
# The complete strict suite must execute in this run; missing fixtures or
# remaining PARTIAL scenarios cannot be replaced by prior evidence.
bash scripts/verify-all.sh --strict-local
