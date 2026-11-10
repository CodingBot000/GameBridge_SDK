#!/usr/bin/env bash
set -euo pipefail
root="$(cd "$(dirname "$0")/.." && pwd)"
if [[ "${1:-}" != '--mock' ]]; then echo 'Usage: build-android.sh --mock' >&2; exit 64; fi
echo 'Mock providers are not implemented; cannot run the requested mock build.' >&2
exit 1
