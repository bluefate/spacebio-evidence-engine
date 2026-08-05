-- Enable pgvector on first database initialization (docker-entrypoint-initdb.d).
-- Idempotent: safe if re-run manually.
CREATE EXTENSION IF NOT EXISTS vector;
