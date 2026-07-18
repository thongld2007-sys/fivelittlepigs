import sqlite3
import os
import json
import time
from backend.config import Config

def get_db_connection():
    conn = sqlite3.connect(Config.DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Create students table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            grade INTEGER NOT NULL
        )
    """)
    
    # Create student_mastery table (P(M) for each skill)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS student_mastery (
            student_id TEXT,
            skill_id TEXT,
            mastery_probability REAL DEFAULT 0.5,
            PRIMARY KEY (student_id, skill_id),
            FOREIGN KEY (student_id) REFERENCES students(id)
        )
    """)
    
    # Create responses table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS responses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT,
            question_id TEXT,
            skill_id TEXT,
            difficulty_level INTEGER DEFAULT 2,
            is_correct INTEGER,
            timestamp INTEGER,
            event_id TEXT UNIQUE,
            response_time_ms INTEGER,
            client_timestamp INTEGER,
            bkt_weight REAL DEFAULT 1.0,
            anomaly_flags TEXT DEFAULT '[]',
            synced_at INTEGER,
            FOREIGN KEY (student_id) REFERENCES students(id)
        )
    """)
    
    response_columns = {
        "difficulty_level": "INTEGER DEFAULT 2",
        "event_id": "TEXT",
        "response_time_ms": "INTEGER",
        "client_timestamp": "INTEGER",
        "bkt_weight": "REAL DEFAULT 1.0",
        "anomaly_flags": "TEXT DEFAULT '[]'",
        "synced_at": "INTEGER",
    }
    for column_name, column_type in response_columns.items():
        try:
            cursor.execute(f"ALTER TABLE responses ADD COLUMN {column_name} {column_type}")
        except sqlite3.OperationalError:
            pass

    cursor.execute("""
        CREATE UNIQUE INDEX IF NOT EXISTS idx_responses_event_id
        ON responses(event_id)
        WHERE event_id IS NOT NULL
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sync_events (
            event_id TEXT PRIMARY KEY,
            event_type TEXT NOT NULL,
            aggregate_id TEXT NOT NULL,
            payload_json TEXT NOT NULL,
            vector_clock TEXT NOT NULL,
            created_at INTEGER NOT NULL,
            synced_at INTEGER
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS pedagogical_explanations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT NOT NULL,
            response_event_id TEXT NOT NULL,
            skill_id TEXT NOT NULL,
            next_skill_id TEXT NOT NULL,
            explanation_text TEXT NOT NULL,
            mastery_before REAL NOT NULL,
            mastery_after REAL NOT NULL,
            created_at INTEGER NOT NULL
        )
    """)
        
    conn.commit()
    
    # Insert mock students if database is empty
    cursor.execute("SELECT COUNT(*) FROM students")
    if cursor.fetchone()[0] == 0:
        mock_students = [
            ("emma_std_01", "Emma", 7),
            ("an_01", "Nguyễn Văn An", 6),
            ("binh_02", "Trần Bình", 5),
            ("chi_03", "Lê Chi", 7),
            ("dung_04", "Nguyễn Dũng", 5),
            ("giang_05", "Phạm Giang", 6),
            ("hoang_06", "Lê Huy Hoàng", 7),
            ("linh_08", "Phạm Khánh Linh", 6)
        ]
        cursor.executemany("INSERT INTO students (id, name, grade) VALUES (?, ?, ?)", mock_students)
        conn.commit()
        
        # Initialize default mastery values
        cursor.execute("SELECT id FROM students")
        student_ids = [row[0] for row in cursor.fetchall()]
        
        from backend.knowledge_graph import KNOWLEDGE_GRAPH
        for s_id in student_ids:
            for skill_id in KNOWLEDGE_GRAPH.keys():
                # Set specific gap states for mock students for demo purposes
                prob = 0.5
                if s_id == "an_01" and skill_id == "MATH_G7": prob = 0.1
                elif s_id == "an_01" and skill_id == "MATH_G6": prob = 0.3
                elif s_id == "binh_02" and skill_id == "MATH_G5": prob = 0.22
                elif s_id == "dung_04" and skill_id == "MATH_G5_LCM": prob = 0.15
                elif s_id == "chi_03" and skill_id == "MATH_G7": prob = 0.88
                
                cursor.execute("""
                    INSERT OR REPLACE INTO student_mastery (student_id, skill_id, mastery_probability)
                    VALUES (?, ?, ?)
                """, (s_id, skill_id, prob))
        conn.commit()
        
    conn.close()

def get_student(student_id):
    conn = get_db_connection()
    row = conn.execute("SELECT * FROM students WHERE id = ?", (student_id,)).fetchone()
    conn.close()
    return dict(row) if row else None

def add_student(student_id, name, grade):
    conn = get_db_connection()
    conn.execute("""
        INSERT OR REPLACE INTO students (id, name, grade)
        VALUES (?, ?, ?)
    """, (student_id, name, grade))
    conn.commit()
    conn.close()
    return get_student(student_id)

def list_students():
    conn = get_db_connection()
    rows = conn.execute("""
        SELECT id AS student_id, name, grade
        FROM students
        ORDER BY grade, name
    """).fetchall()
    conn.close()
    return [dict(row) for row in rows]

def get_student_mastery(student_id, skill_id):
    conn = get_db_connection()
    row = conn.execute("""
        SELECT mastery_probability FROM student_mastery 
        WHERE student_id = ? AND skill_id = ?
    """, (student_id, skill_id)).fetchone()
    conn.close()
    return row[0] if row else 0.5

def update_student_mastery(student_id, skill_id, prob):
    conn = get_db_connection()
    conn.execute("""
        INSERT OR REPLACE INTO student_mastery (student_id, skill_id, mastery_probability)
        VALUES (?, ?, ?)
    """, (student_id, skill_id, prob))
    conn.commit()
    conn.close()

def record_response(
    student_id,
    question_id,
    skill_id,
    difficulty_level,
    is_correct,
    timestamp,
    event_id=None,
    response_time_ms=None,
    client_timestamp=None,
    bkt_weight=1.0,
    anomaly_flags=None,
):
    conn = get_db_connection()
    flags = anomaly_flags or []
    conn.execute("""
        INSERT INTO responses (
            student_id, question_id, skill_id, difficulty_level, is_correct, timestamp,
            event_id, response_time_ms, client_timestamp, bkt_weight, anomaly_flags
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        student_id,
        question_id,
        skill_id,
        difficulty_level,
        1 if is_correct else 0,
        timestamp,
        event_id,
        response_time_ms,
        client_timestamp,
        bkt_weight,
        json.dumps(flags, ensure_ascii=False),
    ))
    conn.commit()
    conn.close()

def get_response_by_event_id(event_id):
    if not event_id:
        return None
    conn = get_db_connection()
    row = conn.execute(
        "SELECT * FROM responses WHERE event_id = ?",
        (event_id,),
    ).fetchone()
    conn.close()
    return dict(row) if row else None

def upsert_sync_event(event_id, event_type, aggregate_id, payload, vector_clock):
    conn = get_db_connection()
    conn.execute("""
        INSERT OR IGNORE INTO sync_events (
            event_id, event_type, aggregate_id, payload_json, vector_clock, created_at
        )
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        event_id,
        event_type,
        aggregate_id,
        json.dumps(payload, ensure_ascii=False),
        vector_clock,
        int(time.time()),
    ))
    conn.commit()
    conn.close()

def list_unsynced_events(limit=100):
    conn = get_db_connection()
    rows = conn.execute("""
        SELECT event_id, event_type, aggregate_id, payload_json, vector_clock, created_at
        FROM sync_events
        WHERE synced_at IS NULL
        ORDER BY created_at ASC, event_id ASC
        LIMIT ?
    """, (limit,)).fetchall()
    conn.close()
    events = []
    for row in rows:
        item = dict(row)
        item["payload"] = json.loads(item.pop("payload_json"))
        events.append(item)
    return events

def mark_events_synced(event_ids):
    if not event_ids:
        return 0
    placeholders = ",".join("?" for _ in event_ids)
    now = int(time.time())
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        f"UPDATE sync_events SET synced_at = ? WHERE event_id IN ({placeholders})",
        [now, *event_ids],
    )
    cursor.execute(
        f"UPDATE responses SET synced_at = ? WHERE event_id IN ({placeholders})",
        [now, *event_ids],
    )
    changed = cursor.rowcount
    conn.commit()
    conn.close()
    return changed

def add_pedagogical_explanation(
    student_id,
    response_event_id,
    skill_id,
    next_skill_id,
    explanation_text,
    mastery_before,
    mastery_after,
):
    conn = get_db_connection()
    conn.execute("""
        INSERT INTO pedagogical_explanations (
            student_id, response_event_id, skill_id, next_skill_id, explanation_text,
            mastery_before, mastery_after, created_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        student_id,
        response_event_id,
        skill_id,
        next_skill_id,
        explanation_text,
        mastery_before,
        mastery_after,
        int(time.time()),
    ))
    conn.commit()
    conn.close()

def list_pedagogical_explanations(student_id, limit=10):
    conn = get_db_connection()
    rows = conn.execute("""
        SELECT response_event_id, skill_id, next_skill_id, explanation_text,
               mastery_before, mastery_after, created_at
        FROM pedagogical_explanations
        WHERE student_id = ?
        ORDER BY id DESC
        LIMIT ?
    """, (student_id, limit)).fetchall()
    conn.close()
    return [dict(row) for row in rows]

def get_consecutive_failed_count(student_id, skill_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT is_correct FROM responses 
        WHERE student_id = ? AND skill_id = ?
        ORDER BY id DESC LIMIT 10
    """, (student_id, skill_id))
    rows = cursor.fetchall()
    conn.close()
    
    count = 0
    for row in rows:
        if row[0] == 0:
            count += 1
        else:
            break
    return count

def get_stuck_time_minutes(student_id, skill_id):
    # Returns estimated minutes student has been stuck on a skill (time difference from first response in active streak to now)
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT timestamp FROM responses 
        WHERE student_id = ? AND skill_id = ?
        ORDER BY id DESC
    """, (student_id, skill_id))
    rows = cursor.fetchall()
    conn.close()
    
    if not rows:
        return 2  # default fallback mock
    
    # Calculate time between first and last attempt in current session
    last_attempt = rows[0][0]
    # Let's count how far back the failure goes
    failures_time = [r[0] for r in rows]
    if len(failures_time) > 1:
        diff_secs = failures_time[0] - failures_time[-1]
        return max(2, int(diff_secs / 60))
    return 2
