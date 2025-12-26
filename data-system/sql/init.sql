CREATE TABLE IF NOT EXISTS game_events (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP DEFAULT NOW(),
    player_id INTEGER NOT NULL,
    enemy_type VARCHAR(50),
    damage_dealt INTEGER,
    experience_gained INTEGER,
    ability_used VARCHAR(50),
    session_duration_sec INTEGER,
    event_type VARCHAR(50) NOT NULL -- attack, kill, level_up, rest
);