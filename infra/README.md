# Local database

`GAMEBRIDGE_DB_PASSWORD` must be provided in the local environment. Run `bash scripts/run-demo-backend.sh` to start the explicitly local-mock backend and the `gamebridge-sdk-local` Compose project. PostgreSQL listens only on 127.0.0.1:54329; the backend defaults to 127.0.0.1:18080. Neither service is a production deployment.

The named volume `gamebridge-sdk-local_gamebridge-db` persists across restarts. Changing the password environment variable does not change the password already stored in an initialized PostgreSQL volume. The script never deletes the volume or touches an existing personal database. Stopping the server does not stop PostgreSQL; use `docker compose -p gamebridge-sdk-local -f infra/compose.yaml stop` when finished. Deleting data requires an explicit user decision.

Local mock authentication additionally requires a locally supplied `GAMEBRIDGE_DEV_AUTH_KEY` of at least 32 characters. With the server running, `python3 scripts/smoke-auth-local.py` exercises test identities A and B and creates session records; it does not print tokens. The mock endpoint is absent in the sandbox profile. Request rate limiting and real identity providers are not yet implemented.

`python3 scripts/smoke-purchase-local.py` exercises synthetic purchases against the running local-mock service. It intentionally persists test purchases and balance changes in this dedicated volume; it does not perform store purchases.

Mock device registration requires `SERVER_TOKEN_ENCRYPTION_KEY` containing a Base64-encoded 32-byte key. `python3 scripts/smoke-device-local.py` creates a dedicated mock installation and retains encrypted test data. New local-mock registrations are tied to their session and deleted on unregister or logout; old test rows without session ownership are not automatically assigned or deleted. This is not remote push validation.
