-- SQLite / PostgreSQL-совместимая схема (для PostGIS заменить lat/lon на geometry)
CREATE TABLE IF NOT EXISTS source (id TEXT PRIMARY KEY, title TEXT, url TEXT, publisher TEXT, license TEXT, fetched_at TEXT);

CREATE TABLE IF NOT EXISTS atm (id INTEGER PRIMARY KEY, name TEXT, operator TEXT, address TEXT, lat REAL, lon REAL, is_critical INTEGER DEFAULT 0);
CREATE TABLE IF NOT EXISTS shelter (id INTEGER PRIMARY KEY, name TEXT, address TEXT, municipality TEXT, capacity INTEGER, lat REAL, lon REAL);
CREATE TABLE IF NOT EXISTS fuel_station (id INTEGER PRIMARY KEY, viss_id INTEGER UNIQUE, name TEXT, brand TEXT, address TEXT, phone TEXT, email TEXT, lat REAL, lon REAL);

CREATE TABLE IF NOT EXISTS weather_station (id TEXT PRIMARY KEY, name TEXT, road TEXT, lat REAL, lon REAL);
CREATE TABLE IF NOT EXISTS weather_observation (station_id TEXT REFERENCES weather_station(id), observed_at TEXT, air_temp_c REAL, road_temp_c REAL, wind_ms REAL, humidity_pct REAL, precipitation TEXT, PRIMARY KEY (station_id, observed_at));

CREATE TABLE IF NOT EXISTS road_incident (id TEXT PRIMARY KEY, occurred_at TEXT, type TEXT, road TEXT, description TEXT, lat REAL, lon REAL);
CREATE TABLE IF NOT EXISTS traffic_measurement (point_id TEXT, measured_at TEXT, vehicles INTEGER, avg_speed_kmh REAL, PRIMARY KEY (point_id, measured_at));

CREATE TABLE IF NOT EXISTS weather_warning (id TEXT PRIMARY KEY, region TEXT, hazard TEXT, level TEXT, valid_from TEXT, valid_to TEXT, text_lv TEXT);

CREATE TABLE IF NOT EXISTS hydro_station (id TEXT PRIMARY KEY, name TEXT, water_body TEXT, lat REAL, lon REAL);
-- param: UDLIM = ūdens līmenis (m, LAS-2000,5), UDTEMP = ūdens temperatūra (°C)
CREATE TABLE IF NOT EXISTS hydro_forecast (forecast_date TEXT, station_id TEXT, param TEXT, min REAL, v95 REAL, v75 REAL, median REAL, v25 REAL, v5 REAL, max REAL, PRIMARY KEY (forecast_date, station_id, param));
