import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "meetings.db")


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute(
        """CREATE TABLE IF NOT EXISTS meetings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            raw_text TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )"""
    )
    conn.execute(
        """CREATE TABLE IF NOT EXISTS speakers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            meeting_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            statement_count INTEGER NOT NULL
        )"""
    )
    conn.execute(
        """CREATE TABLE IF NOT EXISTS action_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            meeting_id INTEGER NOT NULL,
            text TEXT NOT NULL
        )"""
    )
    try:
        conn.execute("ALTER TABLE action_items ADD COLUMN owner TEXT")
    except sqlite3.OperationalError:
        pass
    try:
        conn.execute("ALTER TABLE action_items ADD COLUMN deadline TEXT")
    except sqlite3.OperationalError:
        pass
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


def save_speakers(meeting_id, speaker_counts):
    conn = get_connection()
    conn.execute("DELETE FROM speakers WHERE meeting_id = ?", (meeting_id,))
    for name, count in speaker_counts.items():
        conn.execute(
            "INSERT INTO speakers (meeting_id, name, statement_count) VALUES (?, ?, ?)",
            (meeting_id, name, count),
        )
    conn.commit()
    conn.close()


def get_speakers_by_meeting(meeting_id):
    conn = get_connection()
    rows = conn.execute(
        "SELECT name, statement_count FROM speakers WHERE meeting_id = ? ORDER BY statement_count DESC",
        (meeting_id,),
    ).fetchall()
    conn.close()
    return rows


def save_action_items(meeting_id, items):
    conn = get_connection()
    conn.execute("DELETE FROM action_items WHERE meeting_id = ?", (meeting_id,))
    for item in items:
        if isinstance(item, str):
            text, owner, deadline = item, "Unassigned", None
        else:
            text = item["text"]
            owner = item.get("owner", "Unassigned")
            deadline = item.get("deadline", None)
        conn.execute(
            "INSERT INTO action_items (meeting_id, text, owner, deadline) VALUES (?, ?, ?, ?)",
            (meeting_id, text, owner, deadline),
        )
    conn.commit()
    conn.close()


def get_action_items_by_meeting(meeting_id):
    conn = get_connection()
    rows = conn.execute(
        "SELECT text, owner, deadline FROM action_items WHERE meeting_id = ? ORDER BY id",
        (meeting_id,),
    ).fetchall()
    conn.close()
    return rows
