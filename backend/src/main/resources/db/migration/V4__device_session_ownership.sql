ALTER TABLE device_tokens ADD COLUMN session_id UUID REFERENCES sessions(id);
CREATE INDEX device_tokens_session_id_idx ON device_tokens(session_id);
