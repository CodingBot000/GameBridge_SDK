CREATE TABLE purchase_account_bindings (
    user_id UUID NOT NULL REFERENCES users(id),
    app_id TEXT NOT NULL,
    apple_account_token UUID NOT NULL UNIQUE,
    google_obfuscated_id UUID NOT NULL UNIQUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    PRIMARY KEY (user_id, app_id),
    CHECK (apple_account_token <> google_obfuscated_id)
);
