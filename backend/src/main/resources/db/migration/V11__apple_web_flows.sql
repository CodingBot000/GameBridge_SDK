CREATE TABLE apple_web_flows (
    id uuid PRIMARY KEY,
    app_id text NOT NULL,
    services_id text NOT NULL,
    callback_uri text NOT NULL,
    return_uri text NOT NULL,
    state_hash bytea NOT NULL UNIQUE,
    nonce_hash bytea NOT NULL,
    verifier_challenge text NOT NULL,
    expires_at timestamptz NOT NULL,
    stage text NOT NULL DEFAULT 'STARTED',
    code_hash bytea UNIQUE,
    handle_hash bytea UNIQUE,
    handle_expires_at timestamptz,
    issuer text,
    subject text,
    audience text,
    consumed_at timestamptz
);
