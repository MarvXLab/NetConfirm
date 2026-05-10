import os
import psycopg2
from psycopg2.extras import RealDictCursor
import streamlit as st

def get_connection():
    """Get database connection — works both locally and on Streamlit Cloud."""
    url = None
    try:
        url = st.secrets["database"]["url"]
    except Exception:
        pass
    if not url:
        from dotenv import load_dotenv
        load_dotenv()
        url = os.getenv("DATABASE_URL")
    if not url:
        raise ValueError("DATABASE_URL not set")
    return psycopg2.connect(url, cursor_factory=RealDictCursor)


def run_schema():
    """Run schema.sql to create tables if they don't exist."""
    schema_path = os.path.join(os.path.dirname(__file__), "schema.sql")
    with open(schema_path, "r") as f:
        sql = f.read()
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(sql)
        conn.commit()
    finally:
        conn.close()
