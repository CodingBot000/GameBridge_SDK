#!/usr/bin/env bash
set -euo pipefail
root="$(cd "$(dirname "$0")/.." && pwd)"
if [[ -n "${XCODEGEN_BIN:-}" ]]; then
  generator="$XCODEGEN_BIN"
elif command -v xcodegen >/dev/null 2>&1; then
  generator="$(command -v xcodegen)"
elif [[ -x "$root/artifacts/tools/xcodegen/2.46.0/bin/xcodegen" ]]; then
  generator="$root/artifacts/tools/xcodegen/2.46.0/bin/xcodegen"
else
  echo 'XcodeGen 2.46.0 is required; set XCODEGEN_BIN or install it from its official source.' >&2
  exit 2
fi
"$generator" generate --spec "$root/ios/Framework/project.yml"
