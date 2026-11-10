#!/usr/bin/env bash
set -euo pipefail
if [[ "${1:-}" != "--check-config" || "$#" != 1 ]]; then
  echo 'Usage: bash scripts/verify-external.sh --check-config' >&2
  exit 2
fi
exec python3 "$(dirname "$0")/verify-external-config.py"
