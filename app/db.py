# app/db.py
import sqlite3
from datetime import datetime
from typing import Optional

DB_PATH = "resume_results.db"

def init_db(db_path: Optional[str] = None):
    path = db_path or DB_PATH
    conn = sqlite3.connect(path)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            filename TEXT,
            jd_text TEXT,
            ats_score REAL,
            breakdown TEXT,
            missing_skills TEXT,
            matched_skills TEXT,
            ai_feedback TEXT
        )
    """)
    conn.commit()
    conn.close()

def save_result(filename: str, jd_text: str, ats_score: float, breakdown: dict,
                missing_skills: list, matched_skills: list, ai_feedback: str,
                db_path: Optional[str] = None):
    """
    Save a single result. This is transactional; it commits only if insert succeeds.
    """
    path = db_path or DB_PATH
    conn = sqlite3.connect(path)
    try:
        c = conn.cursor()
        c.execute("""
            INSERT INTO results
            (timestamp, filename, jd_text, ats_score, breakdown, missing_skills, matched_skills, ai_feedback)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            datetime.utcnow().isoformat(),
            filename,
            jd_text,
            ats_score,
            str(breakdown),
            ", ".join(missing_skills) if missing_skills else "",
            ", ".join(matched_skills) if matched_skills else "",
            ai_feedback or ""
        ))
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

def fetch_recent(limit: int = 100, db_path: Optional[str] = None):
    path = db_path or DB_PATH
    conn = sqlite3.connect(path)
    c = conn.cursor()
    c.execute("SELECT id, timestamp, filename, ats_score, missing_skills, matched_skills FROM results ORDER BY id DESC LIMIT ?", (limit,))
    rows = c.fetchall()
    conn.close()
    return rows
