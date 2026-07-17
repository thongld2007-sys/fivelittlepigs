"""SQLite persistence for the offline-first tutoring server."""

from __future__ import annotations

import sqlite3
import uuid
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator, Sequence

from backend.config import DB_PATH


class TutorConnection(sqlite3.Connection):
    """Connection that commits/rolls back and also closes after a with block."""

    def __exit__(self, exc_type, exc_value, traceback):
        try:
            return super().__exit__(exc_type, exc_value, traceback)
        finally:
            self.close()


def get_db_connection() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH, timeout=10, factory=TutorConnection)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA journal_mode = WAL")
    conn.execute("PRAGMA busy_timeout = 10000")
    return conn


@contextmanager
def transaction() -> Iterator[sqlite3.Connection]:
    conn = get_db_connection()
    try:
        conn.execute("BEGIN IMMEDIATE")
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_db() -> None:
    with get_db_connection() as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS Students (
                student_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                grade INTEGER NOT NULL CHECK (grade BETWEEN 1 AND 12),
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS Responses (
                response_id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_id TEXT NOT NULL UNIQUE,
                student_id TEXT NOT NULL,
                question_id TEXT NOT NULL,
                selected_index INTEGER NOT NULL CHECK (selected_index >= 0),
                is_correct INTEGER NOT NULL CHECK (is_correct IN (0, 1)),
                time_spent INTEGER NOT NULL CHECK (time_spent BETWEEN 0 AND 86400),
                timestamp TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                is_synced INTEGER NOT NULL DEFAULT 0 CHECK (is_synced IN (0, 1)),
                FOREIGN KEY (student_id) REFERENCES Students(student_id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS Student_Mastery (
                student_id TEXT NOT NULL,
                skill_id TEXT NOT NULL,
                current_probability REAL NOT NULL CHECK (current_probability BETWEEN 0 AND 1),
                consecutive_fails INTEGER NOT NULL DEFAULT 0 CHECK (consecutive_fails >= 0),
                last_updated TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (student_id, skill_id),
                FOREIGN KEY (student_id) REFERENCES Students(student_id) ON DELETE CASCADE
            );

            """
        )
        _migrate_legacy_schema(conn)
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS Diagnostic_Events (
                diagnostic_id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_id TEXT NOT NULL,
                student_id TEXT NOT NULL,
                skill_id TEXT NOT NULL,
                previous_probability REAL NOT NULL,
                new_probability REAL NOT NULL,
                action TEXT NOT NULL,
                target_skill TEXT,
                reason TEXT NOT NULL,
                timestamp TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (event_id) REFERENCES Responses(event_id) ON DELETE CASCADE,
                FOREIGN KEY (student_id) REFERENCES Students(student_id) ON DELETE CASCADE
            );
            CREATE INDEX IF NOT EXISTS idx_responses_sync ON Responses(is_synced, response_id);
            CREATE INDEX IF NOT EXISTS idx_mastery_skill ON Student_Mastery(skill_id, current_probability);
            CREATE INDEX IF NOT EXISTS idx_diagnostics_student ON Diagnostic_Events(student_id, timestamp);
            """
        )


def _columns(conn: sqlite3.Connection, table: str) -> set[str]:
    return {row["name"] for row in conn.execute(f"PRAGMA table_info({table})")}


def _migrate_legacy_schema(conn: sqlite3.Connection) -> None:
    """Add safe defaults for databases created by the original prototype."""
    student_columns = _columns(conn, "Students")
    if "created_at" not in student_columns:
        conn.execute("ALTER TABLE Students ADD COLUMN created_at TEXT")
        conn.execute("UPDATE Students SET created_at = CURRENT_TIMESTAMP WHERE created_at IS NULL")
    response_columns = _columns(conn, "Responses")
    additions = {
        "event_id": "TEXT",
        "selected_index": "INTEGER NOT NULL DEFAULT 0",
        "is_synced": "INTEGER NOT NULL DEFAULT 0",
    }
    for name, definition in additions.items():
        if name not in response_columns:
            conn.execute(f"ALTER TABLE Responses ADD COLUMN {name} {definition}")
    conn.execute(
        "UPDATE Responses SET event_id = lower(hex(randomblob(16))) "
        "WHERE event_id IS NULL OR event_id = ''"
    )
    conn.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_responses_event ON Responses(event_id)")


def add_student(student_id: str, name: str, grade: int) -> dict:
    with transaction() as conn:
        conn.execute(
            """INSERT INTO Students(student_id, name, grade) VALUES (?, ?, ?)
               ON CONFLICT(student_id) DO UPDATE SET name=excluded.name, grade=excluded.grade""",
            (student_id, name, grade),
        )
    return get_student(student_id)


def get_student(student_id: str) -> dict | None:
    with get_db_connection() as conn:
        row = conn.execute(
            "SELECT student_id, name, grade, created_at FROM Students WHERE student_id = ?",
            (student_id,),
        ).fetchone()
    return dict(row) if row else None


def list_students() -> list[dict]:
    with get_db_connection() as conn:
        rows = conn.execute(
            "SELECT student_id, name, grade, created_at FROM Students ORDER BY name, student_id"
        ).fetchall()
    return [dict(row) for row in rows]


def get_student_mastery(student_id: str, skill_id: str, conn: sqlite3.Connection | None = None) -> dict | None:
    owns_connection = conn is None
    conn = conn or get_db_connection()
    try:
        row = conn.execute(
            """SELECT current_probability, consecutive_fails, last_updated
               FROM Student_Mastery WHERE student_id = ? AND skill_id = ?""",
            (student_id, skill_id),
        ).fetchone()
        return dict(row) if row else None
    finally:
        if owns_connection:
            conn.close()


def record_answer(
    *, student_id: str, question_id: str, selected_index: int, is_correct: bool,
    time_spent: int, skill_id: str, previous_probability: float,
    new_probability: float, consecutive_fails: int, action: str,
    target_skill: str | None, reason: str, event_id: str | None = None,
) -> tuple[str, bool]:
    """Atomically persist an answer, mastery update, and explainability event.

    Returns (event_id, created). Replayed event IDs are idempotent.
    """
    event_id = event_id or str(uuid.uuid4())
    with transaction() as conn:
        existing = conn.execute(
            "SELECT event_id FROM Responses WHERE event_id = ?", (event_id,)
        ).fetchone()
        if existing:
            return event_id, False
        conn.execute(
            """INSERT INTO Responses
               (event_id, student_id, question_id, selected_index, is_correct, time_spent)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (event_id, student_id, question_id, selected_index, int(is_correct), time_spent),
        )
        conn.execute(
            """INSERT INTO Student_Mastery
               (student_id, skill_id, current_probability, consecutive_fails)
               VALUES (?, ?, ?, ?)
               ON CONFLICT(student_id, skill_id) DO UPDATE SET
                 current_probability=excluded.current_probability,
                 consecutive_fails=excluded.consecutive_fails,
                 last_updated=CURRENT_TIMESTAMP""",
            (student_id, skill_id, new_probability, consecutive_fails),
        )
        conn.execute(
            """INSERT INTO Diagnostic_Events
               (event_id, student_id, skill_id, previous_probability, new_probability,
                action, target_skill, reason)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (event_id, student_id, skill_id, previous_probability, new_probability,
             action, target_skill, reason),
        )
    return event_id, True


def get_unsynced_responses(limit: int = 500) -> list[dict]:
    with get_db_connection() as conn:
        rows = conn.execute(
            """SELECT event_id, student_id, question_id, selected_index, is_correct,
                      time_spent, timestamp
               FROM Responses WHERE is_synced = 0 ORDER BY response_id LIMIT ?""",
            (limit,),
        ).fetchall()
    return [dict(row) for row in rows]


def get_response_by_event(event_id: str) -> dict | None:
    with get_db_connection() as conn:
        row = conn.execute(
            """SELECT event_id, student_id, question_id, selected_index, is_correct,
                      time_spent, timestamp, is_synced
               FROM Responses WHERE event_id = ?""",
            (event_id,),
        ).fetchone()
    return dict(row) if row else None


def mark_responses_as_synced(event_ids: Sequence[str]) -> int:
    if not event_ids:
        return 0
    placeholders = ",".join("?" for _ in event_ids)
    with transaction() as conn:
        cursor = conn.execute(
            f"UPDATE Responses SET is_synced = 1 WHERE event_id IN ({placeholders})",
            tuple(event_ids),
        )
    return cursor.rowcount


def get_reasoning_tree(student_id: str, limit: int = 100) -> list[dict]:
    with get_db_connection() as conn:
        rows = conn.execute(
            """SELECT event_id, skill_id, previous_probability, new_probability,
                      action, target_skill, reason, timestamp
               FROM Diagnostic_Events WHERE student_id = ?
               ORDER BY diagnostic_id DESC LIMIT ?""",
            (student_id, limit),
        ).fetchall()
    return [dict(row) for row in reversed(rows)]
