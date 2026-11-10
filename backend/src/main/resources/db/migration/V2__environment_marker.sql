CREATE TABLE gamebridge_environment (
    singleton BOOLEAN PRIMARY KEY DEFAULT TRUE CHECK (singleton),
    profile TEXT NOT NULL CHECK (profile IN ('local-mock', 'sandbox', 'production'))
);
