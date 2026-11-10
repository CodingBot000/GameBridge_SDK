#!/usr/bin/env bash
set -euo pipefail
root="$(cd "$(dirname "$0")/.." && pwd)"
if ! command -v unity >/dev/null 2>&1; then
  echo 'Unity CLI is required.' >&2
  exit 2
fi
if [ -e "$root/unity/Demo" ]; then
  echo 'unity/Demo already exists; refusing to overwrite it.' >&2
  exit 1
fi
unity projects create Demo --path "$root/unity" --editor-version "${UNITY_EDITOR_VERSION:-6000.5.8f1}" --template com.unity.template.3d --no-cloud --non-interactive
