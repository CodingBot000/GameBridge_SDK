#!/usr/bin/env bash
# This writes uniquely identified mock purchases/installations to the dedicated local DB.
set -u
root="$(cd "$(dirname "$0")/.." && pwd)"
if [[ "${GAMEBRIDGE_LOCAL_SMOKE_OPT_IN:-}" != "1" ]]; then
  echo 'CONFIG_REQUIRED: GAMEBRIDGE_LOCAL_SMOKE_OPT_IN=1 for dedicated local backend and DB' >&2
  exit 2
fi
if [[ -z "${GAMEBRIDGE_DEV_AUTH_KEY:-}" ]]; then
  echo 'CONFIG_REQUIRED: GAMEBRIDGE_DEV_AUTH_KEY' >&2
  exit 2
fi
failed=0
for check in smoke-auth-local.py smoke-purchase-local.py smoke-device-local.py; do
  python3 "$root/scripts/$check"
  result=$?
  if (( result != 0 )); then
    printf '%s: exit %s\n' "$check" "$result" >&2
    failed=1
  fi
done
if (( failed != 0 )); then
  echo 'LOCAL_MOCK backend smoke: FAIL' >&2
  exit 1
fi
echo 'LOCAL_MOCK backend smoke: PASS (auth, purchase, device/config checks)'
echo 'NOT_RUN: Unity player, real platform providers and remote push'
