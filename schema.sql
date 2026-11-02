CREATE TABLE IF NOT EXISTS matches (
 id INTEGER PRIMARY KEY, provider_match_id TEXT UNIQUE, kickoff_utc TEXT,
 competition TEXT, season TEXT, home_team TEXT, away_team TEXT,
 home_goals INTEGER, away_goals INTEGER, status TEXT
);
CREATE TABLE IF NOT EXISTS team_match_stats (
 match_id INTEGER, team_id TEXT, is_home INTEGER, xg REAL, shots INTEGER,
 shots_on_target INTEGER, corners INTEGER, yellow_cards INTEGER, red_cards INTEGER,
 FOREIGN KEY(match_id) REFERENCES matches(id)
);
CREATE TABLE IF NOT EXISTS player_match_stats (
 match_id INTEGER, player_id TEXT, team_id TEXT, minutes INTEGER,
 goals INTEGER, assists INTEGER, shots INTEGER, shots_on_target INTEGER,
 FOREIGN KEY(match_id) REFERENCES matches(id)
);
CREATE TABLE IF NOT EXISTS odds (
 match_id INTEGER, bookmaker TEXT, market TEXT, selection TEXT,
 decimal_odds REAL, captured_at_utc TEXT, FOREIGN KEY(match_id) REFERENCES matches(id)
);
