CREATE TABLE users (
    id UUID PRIMARY KEY,
    display_name TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE TABLE auth_identities (
    user_id UUID NOT NULL REFERENCES users(id),
    provider TEXT NOT NULL, issuer TEXT NOT NULL, subject TEXT NOT NULL, app_scope TEXT NOT NULL,
    UNIQUE (provider, issuer, subject, app_scope)
);
CREATE TABLE auth_challenges (
    id UUID PRIMARY KEY, provider TEXT NOT NULL, nonce_hash BYTEA NOT NULL,
    app_id TEXT NOT NULL, expires_at TIMESTAMPTZ NOT NULL, used_at TIMESTAMPTZ
);
CREATE TABLE sessions (
    id UUID PRIMARY KEY, user_id UUID NOT NULL REFERENCES users(id),
    access_hash BYTEA NOT NULL UNIQUE, refresh_hash BYTEA NOT NULL UNIQUE,
    expires_at TIMESTAMPTZ NOT NULL, refresh_expires_at TIMESTAMPTZ NOT NULL,
    revoked_at TIMESTAMPTZ, family_id UUID NOT NULL
);
CREATE TABLE session_refresh_history (
    consumed_refresh_hash BYTEA PRIMARY KEY, family_id UUID NOT NULL, consumed_at TIMESTAMPTZ NOT NULL
);
CREATE TABLE products (
    app_id TEXT NOT NULL, logical_id TEXT NOT NULL, platform TEXT NOT NULL, store_id TEXT NOT NULL,
    type TEXT NOT NULL CHECK (type IN ('CONSUMABLE', 'NON_CONSUMABLE')), grant_amount BIGINT NOT NULL CHECK (grant_amount >= 0),
    PRIMARY KEY (app_id, platform, logical_id), UNIQUE (app_id, platform, store_id)
);
CREATE TABLE purchases (
    id UUID PRIMARY KEY, app_id TEXT NOT NULL, environment TEXT NOT NULL, platform TEXT NOT NULL,
    proof_key_hash BYTEA NOT NULL, user_id UUID NOT NULL REFERENCES users(id), product_id TEXT NOT NULL,
    store_state TEXT NOT NULL, fulfillment_state TEXT NOT NULL, finalization_state TEXT NOT NULL,
    evidence_encrypted BYTEA, created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (app_id, environment, platform, proof_key_hash)
);
CREATE TABLE wallet_ledger (
    id UUID PRIMARY KEY, purchase_id UUID NOT NULL UNIQUE REFERENCES purchases(id),
    user_id UUID NOT NULL REFERENCES users(id), delta BIGINT NOT NULL, reason TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE TABLE entitlements (
    user_id UUID NOT NULL REFERENCES users(id), product_id TEXT NOT NULL, active BOOLEAN NOT NULL,
    source_purchase_id UUID NOT NULL REFERENCES purchases(id), PRIMARY KEY (user_id, product_id)
);
CREATE TABLE store_finalization_jobs (
    purchase_id UUID PRIMARY KEY REFERENCES purchases(id), action TEXT NOT NULL,
    attempt_count INTEGER NOT NULL DEFAULT 0, next_attempt_at TIMESTAMPTZ NOT NULL,
    status TEXT NOT NULL, last_error TEXT
);
CREATE TABLE idempotency_records (
    user_id UUID NOT NULL REFERENCES users(id), operation TEXT NOT NULL, key TEXT NOT NULL,
    body_hash BYTEA NOT NULL, purchase_id UUID REFERENCES purchases(id), state TEXT NOT NULL,
    PRIMARY KEY (user_id, operation, key)
);
CREATE TABLE device_tokens (
    app_id TEXT NOT NULL, environment TEXT NOT NULL, platform TEXT NOT NULL, installation_id UUID NOT NULL,
    user_id UUID REFERENCES users(id), provider TEXT NOT NULL, token_encrypted BYTEA NOT NULL,
    token_hash BYTEA NOT NULL, updated_at TIMESTAMPTZ NOT NULL,
    PRIMARY KEY (app_id, environment, platform, installation_id)
);
