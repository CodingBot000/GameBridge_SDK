#!/usr/bin/env bash
# This writes uniquely identified mock purchases/installations to the dedicated local DB.
set -u
root="$(cd "$(dirname "$0")/.." && pwd)"
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
# Mandatory flows not yet implemented; keep aggregate fail-closed.
echo 'NOT_RUN: Unity player end-to-end push delivery and routing' >&2
exit 1
