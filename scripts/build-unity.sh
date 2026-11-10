#!/usr/bin/env bash
set -euo pipefail
if [[ "${1:-}" != '--editor-smoke' ]]; then echo 'Usage: build-unity.sh --editor-smoke' >&2; exit 64; fi
echo 'Unity demo and smoke tests are not yet implemented.' >&2
exit 1
