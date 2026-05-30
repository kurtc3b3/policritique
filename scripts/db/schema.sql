-- policritique SQLite schema
-- Mirrors backend/src/policritique/db/models.py

PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS parties (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    ec_id           TEXT UNIQUE,
    name            TEXT NOT NULL,
    short_name      TEXT,
    register        TEXT,
    collected_at    TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS elections (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    name            TEXT NOT NULL,
    election_type   TEXT NOT NULL,
    election_date   TEXT NOT NULL,
    parliament_period TEXT,
    source          TEXT,
    collected_at    TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS constituencies (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    name            TEXT NOT NULL,
    gss_code        TEXT,
    country         TEXT,
    valid_from      TEXT,
    valid_to        TEXT,
    collected_at    TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS members (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    parliament_member_id INTEGER UNIQUE,
    name                TEXT NOT NULL,
    display_name        TEXT,
    gender              TEXT,
    is_current          INTEGER DEFAULT 0,
    collected_at        TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS member_terms (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    member_id       INTEGER NOT NULL REFERENCES members(id) ON DELETE CASCADE,
    constituency_id INTEGER REFERENCES constituencies(id) ON DELETE SET NULL,
    party_id        INTEGER REFERENCES parties(id) ON DELETE SET NULL,
    house           TEXT NOT NULL DEFAULT 'Commons',
    start_date      TEXT,
    end_date        TEXT,
    collected_at    TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS member_contacts (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    member_id       INTEGER NOT NULL REFERENCES members(id) ON DELETE CASCADE,
    contact_type    TEXT NOT NULL,
    value           TEXT NOT NULL,
    is_primary      INTEGER DEFAULT 0,
    collected_at    TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS election_results (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    election_id     INTEGER NOT NULL REFERENCES elections(id) ON DELETE CASCADE,
    constituency_id INTEGER NOT NULL REFERENCES constituencies(id) ON DELETE CASCADE,
    party_id        INTEGER REFERENCES parties(id) ON DELETE SET NULL,
    member_id       INTEGER REFERENCES members(id) ON DELETE SET NULL,
    candidate_name  TEXT NOT NULL,
    votes           INTEGER,
    vote_share      REAL,
    is_elected      INTEGER DEFAULT 0,
    collected_at    TEXT NOT NULL DEFAULT (datetime('now')),
    UNIQUE (election_id, constituency_id, candidate_name)
);

CREATE TABLE IF NOT EXISTS manifestos (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    party_id        INTEGER NOT NULL REFERENCES parties(id) ON DELETE CASCADE,
    election_id     INTEGER REFERENCES elections(id) ON DELETE SET NULL,
    title           TEXT NOT NULL,
    source_url      TEXT,
    published_at    TEXT,
    text            TEXT,
    collected_at    TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS sync_log (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    entity_type     TEXT NOT NULL,
    entity_ref      TEXT NOT NULL,
    status          TEXT NOT NULL,
    message         TEXT,
    synced_at       TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_parties_ec_id ON parties(ec_id);
CREATE INDEX IF NOT EXISTS idx_elections_date ON elections(election_date);
CREATE INDEX IF NOT EXISTS idx_constituencies_gss_code ON constituencies(gss_code);
CREATE INDEX IF NOT EXISTS idx_members_parliament_id ON members(parliament_member_id);
CREATE INDEX IF NOT EXISTS idx_member_terms_member_id ON member_terms(member_id);
CREATE INDEX IF NOT EXISTS idx_member_contacts_member_id ON member_contacts(member_id);
CREATE INDEX IF NOT EXISTS idx_election_results_election_id ON election_results(election_id);
CREATE INDEX IF NOT EXISTS idx_election_results_constituency_id ON election_results(constituency_id);
CREATE INDEX IF NOT EXISTS idx_manifestos_party_id ON manifestos(party_id);
