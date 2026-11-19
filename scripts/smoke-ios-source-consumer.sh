#!/usr/bin/env bash
# Independent SwiftPM source consumer; does not build an iOS device app.
set -euo pipefail
root="$(cd "$(dirname "$0")/.." && pwd)"
command -v swift >/dev/null 2>&1 || { echo 'DEFERRED_ENV: Swift toolchain missing' >&2; exit 2; }
mkdir -p "$root/artifacts"; output="$(mktemp -d "$root/artifacts/ios-source-consumer.XXXXXX")"
echo "Evidence directory: $output"
set +e
swift run --package-path "$root/ios/consumer-source-check" --scratch-path "$output/build" GameBridgeSourceConsumer > "$output/consumer.log" 2>&1
code=$?
set -e
if [[ "$code" != 0 ]] || ! grep -Fxq 'GameBridge independent SwiftPM source consumer PASS' "$output/consumer.log"; then
  echo 'FAIL: independent SwiftPM source consumer did not pass' >&2; exit 1
fi
echo 'SwiftPM source consumer PASS: macOS host only; iOS binary/device separate.'
