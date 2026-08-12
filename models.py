"""models.py — SQLite persistence: schema + save/read functions."""

import sqlite3
import json

DB_NAME = "database.db"


# Open a connection with row access by column name.
def get_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


# Create the two tables if they don't exist. Call once at startup.
def init_db():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS tracks (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            title       TEXT NOT NULL,
            artist      TEXT NOT NULL,
            isrc        TEXT,
            iswc        TEXT,
            publisher   TEXT,
            writers     TEXT,
            risk_score  INTEGER NOT NULL,
            created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # issues linked to tracks by foreign key; cascade delete.
    cur.execute("""
        CREATE TABLE IF NOT EXISTS issues (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            track_id  INTEGER NOT NULL,
            severity  TEXT NOT NULL,
            message   TEXT NOT NULL,
            fix       TEXT NOT NULL,
            FOREIGN KEY (track_id) REFERENCES tracks(id) ON DELETE CASCADE
        )
    """)

    conn.commit()
    conn.close()


# Save a track + its issues; return the new track id.
def save_track(track, score, issues):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO tracks (title, artist, isrc, iswc, publisher, writers, risk_score)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        track.get("title", ""),
        track.get("artist", ""),
        track.get("isrc", ""),
        track.get("iswc", ""),
        track.get("publisher", ""),
        json.dumps(track.get("writers", [])),  # list -> JSON string
        score,
    ))

    track_id = cur.lastrowid

    for issue in issues:
        cur.execute("""
            INSERT INTO issues (track_id, severity, message, fix)
            VALUES (?, ?, ?, ?)
        """, (track_id, issue["severity"], issue["message"], issue["fix"]))

    conn.commit()
    conn.close()
    return track_id


# Read a single track with its issues; None if not found.
def get_track(track_id):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT * FROM tracks WHERE id = ?", (track_id,))
    row = cur.fetchone()

    if row is None:
        conn.close()
        return None

    track = dict(row)
    track["writers"] = json.loads(track["writers"]) if track["writers"] else []

    cur.execute("SELECT * FROM issues WHERE track_id = ?", (track_id,))
    track["issues"] = [dict(i) for i in cur.fetchall()]

    conn.close()
    return track


# List all tracks (newest first). No issues loaded here.
def get_all_tracks():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM tracks ORDER BY created_at DESC")
    tracks = [dict(row) for row in cur.fetchall()]
    conn.close()
    return tracks


# Smoke test: `python models.py`
if __name__ == "__main__":
    init_db()
    print("Database and tables ready (database.db).")

    sample = {
        "title": "Notte a Roma",
        "artist": "Mario Rossi",
        "isrc": "ITB251234567",
        "iswc": "",
        "publisher": "",
        "writers": [{"name": "Mario Rossi", "split": 100, "ipi": ""}],
    }
    issues = [
        {"severity": "red", "message": "ISWC missing", "fix": "Register the composition."},
    ]

    new_id = save_track(sample, 72, issues)
    print(f"Track saved with id {new_id}.")

    reread = get_track(new_id)
    print(f"Read back: '{reread['title']}' with score {reread['risk_score']} "
          f"and {len(reread['issues'])} issue(s).")