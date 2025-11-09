-- Migration: 0001_add_fks_and_indexes.sql
-- Adds foreign keys to user-owned tables and recommended indexes.

BEGIN;

-- Add foreign key constraints (PostgreSQL syntax)
ALTER TABLE IF EXISTS evaluations
  ADD COLUMN IF NOT EXISTS user_id_tmp INTEGER;
-- We assume user_id already exists; add FK directly if possible
ALTER TABLE IF EXISTS evaluations
  ADD CONSTRAINT IF NOT EXISTS fk_evaluations_user_id
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE;

ALTER TABLE IF EXISTS flavors
  ADD CONSTRAINT IF NOT EXISTS fk_flavors_user_id
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE;

ALTER TABLE IF EXISTS analyses
  ADD CONSTRAINT IF NOT EXISTS fk_analyses_user_id
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE;

ALTER TABLE IF EXISTS recipe_runs
  ADD CONSTRAINT IF NOT EXISTS fk_recipe_runs_user_id
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE;

-- Recommended indexes
CREATE INDEX IF NOT EXISTS idx_evaluations_user_id ON evaluations(user_id);
CREATE INDEX IF NOT EXISTS idx_evaluations_created_at ON evaluations(created_at);

CREATE INDEX IF NOT EXISTS idx_flavors_user_id ON flavors(user_id);
CREATE INDEX IF NOT EXISTS idx_flavors_created_at ON flavors(created_at);

CREATE INDEX IF NOT EXISTS idx_analyses_user_id ON analyses(user_id);
CREATE INDEX IF NOT EXISTS idx_analyses_created_at ON analyses(created_at);

CREATE INDEX IF NOT EXISTS idx_recipe_runs_user_id ON recipe_runs(user_id);
CREATE INDEX IF NOT EXISTS idx_recipe_runs_created_at ON recipe_runs(created_at);

COMMIT;
