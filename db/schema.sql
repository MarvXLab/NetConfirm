-- NetConfirm Database Schema
-- Run this once on your Neon PostgreSQL instance

CREATE TABLE IF NOT EXISTS detections (
    id              SERIAL PRIMARY KEY,
    article_snippet TEXT NOT NULL,
    source_url      TEXT,
    trust_score     FLOAT,
    follower_count  INTEGER,
    account_age     INTEGER,
    sentiment       FLOAT,
    readability     FLOAT,
    prediction      VARCHAR(10) NOT NULL,  -- 'REAL' or 'FAKE'
    confidence      FLOAT NOT NULL,
    created_at      TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS model_runs (
    id          SERIAL PRIMARY KEY,
    model_name  VARCHAR(100),
    accuracy    FLOAT,
    f1_score    FLOAT,
    precision   FLOAT,
    recall      FLOAT,
    train_date  TIMESTAMP DEFAULT NOW(),
    notes       TEXT
);

CREATE INDEX IF NOT EXISTS idx_detections_created_at ON detections(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_detections_prediction ON detections(prediction);

CREATE TABLE IF NOT EXISTS domain_reputation (
    id              SERIAL PRIMARY KEY,
    domain          VARCHAR(255) NOT NULL UNIQUE,
    trust_score     FLOAT NOT NULL DEFAULT 0.5,
    category        VARCHAR(100) DEFAULT 'Unknown',
    country         VARCHAR(100) DEFAULT 'Unknown',
    description     TEXT DEFAULT '',
    fake_count      INTEGER NOT NULL DEFAULT 0,
    real_count      INTEGER NOT NULL DEFAULT 0,
    total_scans     INTEGER NOT NULL DEFAULT 0,
    flagged         BOOLEAN NOT NULL DEFAULT FALSE,
    flagged_reason  TEXT DEFAULT '',
    submitted_by    VARCHAR(100) DEFAULT 'community',
    created_at      TIMESTAMP DEFAULT NOW(),
    updated_at      TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_domain_reputation_domain ON domain_reputation(domain);
CREATE INDEX IF NOT EXISTS idx_domain_reputation_trust  ON domain_reputation(trust_score DESC);
CREATE INDEX IF NOT EXISTS idx_domain_reputation_flagged ON domain_reputation(flagged);

CREATE TABLE IF NOT EXISTS api_keys (
    id          SERIAL PRIMARY KEY,
    name        VARCHAR(100) NOT NULL DEFAULT 'default',
    email       VARCHAR(255) NOT NULL UNIQUE,
    key_hash    VARCHAR(64)  NOT NULL UNIQUE,
    key_prefix  VARCHAR(12)  NOT NULL,
    active      BOOLEAN      NOT NULL DEFAULT TRUE,
    requests    INTEGER      NOT NULL DEFAULT 0,
    created_at  TIMESTAMP DEFAULT NOW(),
    last_used   TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_api_keys_hash   ON api_keys(key_hash);
CREATE INDEX IF NOT EXISTS idx_api_keys_email  ON api_keys(email);
