-- CricPredict Database Schema (PostgreSQL)

-- Teams Table
CREATE TABLE IF NOT EXISTS teams (
    team_id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE,
    short_name VARCHAR(10),
    country VARCHAR(100),
    league VARCHAR(100), -- 'IPL', 'International', etc.
    format VARCHAR(50) -- 'T20', 'ODI', 'Test'
);

-- Players Table
CREATE TABLE IF NOT EXISTS players (
    player_id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    team_id INTEGER REFERENCES teams(team_id),
    role VARCHAR(100), -- 'Batsman', 'Bowler', 'All-rounder', 'Wicketkeeper'
    batting_style VARCHAR(100),
    bowling_style VARCHAR(100),
    nationality VARCHAR(100),
    dob DATE
);

-- Venues Table
CREATE TABLE IF NOT EXISTS venues (
    venue_id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    city VARCHAR(100),
    country VARCHAR(100),
    avg_1st_innings_score INTEGER,
    pitch_type VARCHAR(100) -- 'Flat', 'Spin', 'Green', etc.
);

-- Matches Table
CREATE TABLE IF NOT EXISTS matches (
    match_id SERIAL PRIMARY KEY,
    team_a_id INTEGER REFERENCES teams(team_id),
    team_b_id INTEGER REFERENCES teams(team_id),
    venue_id INTEGER REFERENCES venues(venue_id),
    date DATE,
    format VARCHAR(50),
    toss_winner_id INTEGER REFERENCES teams(team_id),
    toss_decision VARCHAR(10), -- 'bat' or 'field'
    winner_id INTEGER REFERENCES teams(team_id),
    win_margin VARCHAR(100),
    is_dl_applied BOOLEAN DEFAULT FALSE
);

-- Ball-by-Ball Data (for Phase 2 models)
CREATE TABLE IF NOT EXISTS deliveries (
    delivery_id SERIAL PRIMARY KEY,
    match_id INTEGER REFERENCES matches(match_id),
    innings INTEGER,
    over INTEGER,
    ball INTEGER,
    batting_team_id INTEGER REFERENCES teams(team_id),
    bowling_team_id INTEGER REFERENCES teams(team_id),
    batsman_id INTEGER REFERENCES players(player_id),
    non_striker_id INTEGER REFERENCES players(player_id),
    bowler_id INTEGER REFERENCES players(player_id),
    runs_off_bat INTEGER,
    extras INTEGER,
    wicket_type VARCHAR(100),
    player_dismissed_id INTEGER REFERENCES players(player_id)
);

-- Player Performance Index (Calculated weekly/monthly)
CREATE TABLE IF NOT EXISTS player_form (
    form_id SERIAL PRIMARY KEY,
    player_id INTEGER REFERENCES players(player_id),
    format VARCHAR(50),
    form_score FLOAT, -- Composite score based on weighted recency
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
