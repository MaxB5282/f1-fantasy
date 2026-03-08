-- ============================================================
-- Migration: Sprint results + Point adjustments
-- Run this in your Supabase SQL Editor.
-- ============================================================

-- Add fastest_lap to race_results (run if upgrading from an earlier version)
ALTER TABLE race_results
    ADD COLUMN IF NOT EXISTS fastest_lap BOOLEAN NOT NULL DEFAULT FALSE;

-- Sprint race results
CREATE TABLE IF NOT EXISTS sprint_results (
    id          SERIAL PRIMARY KEY,
    race_id     INTEGER REFERENCES races(id)   ON DELETE CASCADE,
    driver_id   INTEGER REFERENCES drivers(id) ON DELETE CASCADE,
    grid_pos    INTEGER CHECK (grid_pos   BETWEEN 1 AND 22),
    finish_pos  INTEGER CHECK (finish_pos BETWEEN 1 AND 22),
    fastest_lap BOOLEAN NOT NULL DEFAULT FALSE,
    dnf         BOOLEAN NOT NULL DEFAULT FALSE,
    base_points FLOAT   NOT NULL DEFAULT 0,
    UNIQUE(race_id, driver_id)
);

-- Point adjustments (waiver penalties, manual corrections, etc.)
CREATE TABLE IF NOT EXISTS point_adjustments (
    id         SERIAL PRIMARY KEY,
    player_id  INTEGER REFERENCES players(id) ON DELETE CASCADE,
    amount     INTEGER NOT NULL,
    reason     TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
