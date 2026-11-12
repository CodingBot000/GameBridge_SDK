#!/usr/bin/env bash
# Basic CI is separate; release requires an actually successful Unity gate
# and complete required scenario inventory from this checkout.
set -euo pipefail
root="$(cd "$(dirname "$0")/.." && pwd)"
if [[ "${BASIC_RESULT:-}" != success ]]; then echo "FAIL: basic CI is ${BASIC_RESULT:-missing}" >&2; exit 1; fi
if [[ "${UNITY_RESULT:-}" != success ]]; then echo "DEFERRED_ENV: real Unity E2E is ${UNITY_RESULT:-missing}; release is not ready" >&2; exit 2; fi
python3 "$root/harness/check-required-coverage.py"
echo 'Release readiness checks passed for this run.'
