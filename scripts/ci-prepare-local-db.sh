#!/usr/bin/env bash
# Only initializes an empty, explicitly named disposable CI database; never drops data.
set -euo pipefail
root="$(cd "$(dirname "$0")/.." && pwd)"
if [[ "${GAMEBRIDGE_CI_DISPOSABLE_DB:-}" != true || "${PGHOST:-}" != 127.0.0.1 || ! "${PGDATABASE:-}" =~ ^gamebridge_ci_[a-z0-9_]+$ || -z "${PGUSER:-}" || -z "${PGPASSWORD:-}" ]]; then
  echo 'CONFIG_REQUIRED: explicit loopback disposable gamebridge_ci_* database and separate credentials' >&2; exit 2
fi
command -v psql >/dev/null || { echo 'DEFERRED_ENV: psql missing' >&2; exit 2; }
tables="$(psql -X -v ON_ERROR_STOP=1 -Atc "SELECT (SELECT count(*) FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace WHERE n.nspname='public' AND c.relkind IN ('r','p','v','m','S','f')) + (SELECT count(*) FROM pg_proc p JOIN pg_namespace n ON n.oid=p.pronamespace WHERE n.nspname='public')")"
if [[ "$tables" != 0 ]]; then echo 'Database is not empty; refusing to initialize.' >&2; exit 2; fi
psql -X -v ON_ERROR_STOP=1 -1 \
  -f "$root/backend/src/main/resources/db/migration/V1__initial_schema.sql" \
  -f "$root/backend/src/main/resources/db/migration/V2__environment_marker.sql" \
  -f "$root/backend/src/main/resources/db/mock-migration/V3__mock_catalog.sql" \
  -f "$root/backend/src/main/resources/db/migration/V4__device_session_ownership.sql" \
  -f "$root/backend/src/main/resources/db/migration/V5__purchase_account_bindings.sql" \
  -f "$root/backend/src/main/resources/db/migration/V6__session_app_scope.sql" \
  -f "$root/backend/src/main/resources/db/migration/V7__push_token_invalidation.sql" \
  -c "INSERT INTO gamebridge_environment(singleton,profile) VALUES (true,'local-mock')"
