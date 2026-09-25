import sqlite3
from datetime import datetime
import os

DB_PATH = "logs/chatbot_logs.db"


def init_db():
    """Create the logs table if it doesn't already exist. Safe to call every app run."""
    os.makedirs("logs", exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            role TEXT NOT NULL,
            question TEXT NOT NULL,
            policy_id TEXT,
            confidence_level TEXT NOT NULL,
            score REAL NOT NULL,
            handoff INTEGER NOT NULL,
            answer_text TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()


def log_interaction(role, question, response):
    """
    Insert one row per chatbot interaction.
    `response` is the dict returned by confidence.build_response().
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO logs (timestamp, role, question, policy_id, confidence_level, score, handoff, answer_text)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        role,
        question,
        response["policy_id"],
        response["confidence_level"],
        response["score"],
        1 if response["handoff"] else 0,
        response["answer_text"],
    ))
    conn.commit()
    conn.close()


def get_all_logs():
    """Return all logs as a list of dicts, newest first — used by the Admin Panel."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # lets us access columns by name
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM logs ORDER BY id DESC")
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return rows


def get_stats():
    """Return simple summary stats for the Admin Panel."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM logs")
    total = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM logs WHERE handoff = 1")
    handoffs = cursor.fetchone()[0]
    conn.close()
    handoff_rate = (handoffs / total * 100) if total > 0 else 0
    return {"total": total, "handoffs": handoffs, "handoff_rate": handoff_rate}