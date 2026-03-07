-- ============================================================
-- Max's F1 League — Supabase Setup
-- Paste this into your Supabase project's SQL Editor and run it.
-- ============================================================

-- Players (the 5 fantasy team managers)
CREATE TABLE IF NOT EXISTS players (
    id   SERIAL PRIMARY KEY,
    name TEXT NOT NULL UNIQUE
);

-- F1 Drivers (the real 2025 grid)
CREATE TABLE IF NOT EXISTS drivers (
    id          SERIAL PRIMARY KEY,
    name        TEXT NOT NULL UNIQUE,
    constructor TEXT NOT NULL
);

-- Which drivers each player drafted, and in which round
CREATE TABLE IF NOT EXISTS player_drivers (
    player_id  INTEGER REFERENCES players(id)  ON DELETE CASCADE,
    driver_id  INTEGER REFERENCES drivers(id)  ON DELETE CASCADE,
    draft_round INTEGER NOT NULL CHECK (draft_round BETWEEN 1 AND 4),
    PRIMARY KEY (player_id, driver_id)
);

-- Race calendar
CREATE TABLE IF NOT EXISTS races (
    id           SERIAL PRIMARY KEY,
    round_number INTEGER NOT NULL UNIQUE,
    name         TEXT    NOT NULL UNIQUE,
    circuit      TEXT    NOT NULL
);

-- Per-driver results for each race
CREATE TABLE IF NOT EXISTS race_results (
    id            SERIAL PRIMARY KEY,
    race_id       INTEGER REFERENCES races(id)   ON DELETE CASCADE,
    driver_id     INTEGER REFERENCES drivers(id) ON DELETE CASCADE,
    qualifying_pos INTEGER CHECK (qualifying_pos BETWEEN 1 AND 22),
    grid_pos       INTEGER CHECK (grid_pos       BETWEEN 1 AND 22),
    race_pos       INTEGER CHECK (race_pos       BETWEEN 1 AND 22),
    dnf            BOOLEAN NOT NULL DEFAULT FALSE,
    base_points    FLOAT   NOT NULL DEFAULT 0,
    UNIQUE(race_id, driver_id)
);

-- ── Seed Data ─────────────────────────────────────────────────────────────────

INSERT INTO players (name) VALUES
    ('Max'), ('Jack'), ('Andrew'), ('Richie'), ('Al')
ON CONFLICT (name) DO NOTHING;

INSERT INTO drivers (name, constructor) VALUES
    ('Max Verstappen',   'Red Bull'),
    ('Liam Lawson',      'Red Bull'),
    ('Charles Leclerc',  'Ferrari'),
    ('Lewis Hamilton',   'Ferrari'),
    ('George Russell',   'Mercedes'),
    ('Kimi Antonelli',   'Mercedes'),
    ('Lando Norris',     'McLaren'),
    ('Oscar Piastri',    'McLaren'),
    ('Fernando Alonso',  'Aston Martin'),
    ('Lance Stroll',     'Aston Martin'),
    ('Pierre Gasly',     'Alpine'),
    ('Jack Doohan',      'Alpine'),
    ('Esteban Ocon',     'Haas'),
    ('Oliver Bearman',   'Haas'),
    ('Alexander Albon',  'Williams'),
    ('Carlos Sainz',     'Williams'),
    ('Isack Hadjar',     'Racing Bulls'),
    ('Yuki Tsunoda',     'Racing Bulls'),
    ('Nico Hülkenberg',  'Kick Sauber'),
    ('Gabriel Bortoleto','Kick Sauber')
ON CONFLICT (name) DO NOTHING;
