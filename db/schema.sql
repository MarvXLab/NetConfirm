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
