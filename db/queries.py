from db.connection import get_connection


def insert_detection(article_snippet, source_url, trust_score,
                     follower_count, account_age, sentiment,
                     readability, prediction, confidence):
    """Save a detection result to the database."""
    sql = """
        INSERT INTO detections
            (article_snippet, source_url, trust_score, follower_count,
             account_age, sentiment, readability, prediction, confidence)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(sql, (
                article_snippet[:300],  # store snippet only
                source_url or None,
                round(float(trust_score), 4),
                int(follower_count),
                int(account_age),
                round(float(sentiment), 4),
                round(float(readability), 4),
                prediction,
                round(float(confidence), 4),
            ))
        conn.commit()
    finally:
        conn.close()


def get_recent_detections(limit=50):
    """Fetch most recent detections for history tab."""
    sql = """
        SELECT id, article_snippet, prediction, confidence,
               trust_score, created_at
        FROM detections
        ORDER BY created_at DESC
        LIMIT %s
    """
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(sql, (limit,))
            return cur.fetchall()
    finally:
        conn.close()


def get_stats():
    """Get summary stats for overview."""
    sql = """
        SELECT
            COUNT(*) as total,
            SUM(CASE WHEN prediction = 'FAKE' THEN 1 ELSE 0 END) as fake_count,
            SUM(CASE WHEN prediction = 'REAL' THEN 1 ELSE 0 END) as real_count,
            ROUND(AVG(confidence)::numeric, 3) as avg_confidence
        FROM detections
    """
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(sql)
            return cur.fetchone()
    finally:
        conn.close()


def get_daily_trend(days=14):
    """Fake vs Real counts per day for the last N days."""
    sql = """
        SELECT
            DATE(created_at) as day,
            SUM(CASE WHEN prediction = 'FAKE' THEN 1 ELSE 0 END) as fake_count,
            SUM(CASE WHEN prediction = 'REAL' THEN 1 ELSE 0 END) as real_count
        FROM detections
        WHERE created_at >= NOW() - INTERVAL '%s days'
        GROUP BY DATE(created_at)
        ORDER BY day ASC
    """
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(sql, (days,))
            return cur.fetchall()
    finally:
        conn.close()


def get_top_fake_snippets(limit=10):
    """Most recent high-confidence fake detections this week."""
    sql = """
        SELECT article_snippet, source_url, confidence, created_at
        FROM detections
        WHERE prediction = 'FAKE'
          AND created_at >= NOW() - INTERVAL '7 days'
        ORDER BY confidence DESC, created_at DESC
        LIMIT %s
    """
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(sql, (limit,))
            return cur.fetchall()
    finally:
        conn.close()


def get_top_flagged_domains(limit=10):
    """Domains with the most fake detections."""
    sql = """
        SELECT
            REGEXP_REPLACE(source_url, '^https?://([^/]+).*', '\\1') as domain,
            COUNT(*) as fake_count,
            ROUND(AVG(confidence)::numeric, 3) as avg_confidence
        FROM detections
        WHERE prediction = 'FAKE'
          AND source_url IS NOT NULL
          AND source_url != ''
        GROUP BY domain
        ORDER BY fake_count DESC
        LIMIT %s
    """
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(sql, (limit,))
            return cur.fetchall()
    finally:
        conn.close()


def get_hourly_heatmap():
    """Detection counts by hour-of-day and day-of-week (last 30 days)."""
    sql = """
        SELECT
            EXTRACT(DOW FROM created_at)::int  as dow,
            EXTRACT(HOUR FROM created_at)::int as hour,
            COUNT(*) as total
        FROM detections
        WHERE created_at >= NOW() - INTERVAL '30 days'
        GROUP BY dow, hour
        ORDER BY dow, hour
    """
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(sql)
            return cur.fetchall()
    finally:
        conn.close()


def get_confidence_distribution():
    """Confidence score buckets for fake vs real."""
    sql = """
        SELECT
            prediction,
            WIDTH_BUCKET(confidence, 0, 1, 10) as bucket,
            COUNT(*) as cnt
        FROM detections
        GROUP BY prediction, bucket
        ORDER BY prediction, bucket
    """
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(sql)
            return cur.fetchall()
    finally:
        conn.close()


def log_model_run(model_name, accuracy, f1_score, precision, recall, notes=""):
    """Log a training run for model versioning."""
    sql = """
        INSERT INTO model_runs (model_name, accuracy, f1_score, precision, recall, notes)
        VALUES (%s, %s, %s, %s, %s, %s)
    """
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(sql, (model_name, accuracy, f1_score, precision, recall, notes))
        conn.commit()
    finally:
        conn.close()
