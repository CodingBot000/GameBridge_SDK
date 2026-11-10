-- Preserve token records; only a provider-confirmed invalid token is marked inactive.
ALTER TABLE device_tokens ADD COLUMN invalidated_at TIMESTAMPTZ;
