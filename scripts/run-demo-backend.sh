#!/usr/bin/env bash
set -euo pipefail
root="$(cd "$(dirname "$0")/.." && pwd)"
if ! command -v docker >/dev/null 2>&1 || ! docker info >/dev/null 2>&1; then
  echo 'Docker engine is required.' >&2; exit 2
fi
if [[ -z "${GAMEBRIDGE_DB_PASSWORD:-}" ]]; then
  echo 'CONFIG_REQUIRED: GAMEBRIDGE_DB_PASSWORD' >&2; exit 2
fi
# The named volume is intentionally retained; this script never removes it.
docker compose -p gamebridge-sdk-local -f "$root/infra/compose.yaml" up -d --wait
export SPRING_PROFILES_ACTIVE=local-mock
export DATABASE_URL='jdbc:postgresql://127.0.0.1:54329/gamebridge_local'
export DATABASE_USERNAME=gamebridge
export DATABASE_PASSWORD="$GAMEBRIDGE_DB_PASSWORD"
exec "$root/backend/gradlew" -p "$root/backend" bootRun
