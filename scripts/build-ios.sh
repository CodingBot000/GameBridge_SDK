#!/usr/bin/env bash
set -euo pipefail
if [[ "${1:-}" != '--simulator' ]]; then echo 'Usage: build-ios.sh --simulator' >&2; exit 64; fi
echo 'iOS simulator project and sample are not yet ready.' >&2
exit 1
