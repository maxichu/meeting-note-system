import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "meetings.db")


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    conn.execute(
        """CREATE TABLE IF NOT EXISTS meetings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            raw_text TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )"""
    )
    conn.commit()
    conn.close()


def save_meeting(raw_text):
    conn = get_connection()
    cursor = conn.execute("INSERT INTO meetings (raw_text) VALUES (?)", (raw_text,))
    meeting_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return meeting_id


def get_all_meetings():
    conn = get_connection()
    rows = conn.execute(
        "SELECT id, raw_text, created_at FROM meetings ORDER BY created_at DESC"
    ).fetchall()
    conn.close()
    return rows
