-- Forward-only: legacy Google/Apple challenges keep their ID-token contract.
ALTER TABLE auth_challenges ADD COLUMN proof_type TEXT NOT NULL DEFAULT 'ID_TOKEN';
