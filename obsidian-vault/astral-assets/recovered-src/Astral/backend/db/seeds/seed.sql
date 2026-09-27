-- seed.sql: minimal local seed for SQLite cache
-- apply with: sqlite3 astral.db < db/seeds/seed.sql

INSERT OR REPLACE INTO profiles (id, email, full_name, tz, lat, lon, chart_system)
VALUES ('00000000-0000-0000-0000-000000000001', 'dev@example.com', 'Mark', 'Asia/Bangkok', 13.36, 100.98, 'tropical');

INSERT OR REPLACE INTO research_corpus (id, category, name, data)
VALUES ('asteroids_ephe_guide', 'data', 'Asteroids Ephemeris Guide', '{"source":"ephe","status":"ok"}');

INSERT OR REPLACE INTO research_corpus (id, category, name, data)
VALUES ('results', 'results', 'Research Results', '{"status":"ok"}');
