-- Legacy sessions remain unchanged and cannot access app-scoped binding APIs.
ALTER TABLE sessions ADD COLUMN app_scope TEXT;
