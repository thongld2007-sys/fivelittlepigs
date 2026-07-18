"""SQLite persistence for the offline-first adaptive tutoring application.

The module owns schema migrations, reference-data synchronisation and the small
repository API used by the FastAPI/diagnostic layers.  Migrations are additive
so an existing ``tutor.db`` can be upgraded without deleting learner data.
"""

import json
import os
import sqlite3
import time
from contextlib import contextmanager

from backend.config import Config


SCHEMA_VERSION = 3


def get_db_connection():
    conn = sqlite3.connect(Config.DB_PATH, timeout=30)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA busy_timeout = 30000")
    return conn


@contextmanager
def db_transaction():
    conn = get_db_connection()
    try:
        with conn:
            yield conn
    finally:
        conn.close()


def _columns(conn, table):
    return {row["name"] for row in conn.execute(f'PRAGMA table_info("{table}")')}


def _add_columns(conn, table, definitions):
    existing = _columns(conn, table)
    for name, sql_type in definitions.items():
        if name not in existing:
            conn.execute(f'ALTER TABLE "{table}" ADD COLUMN "{name}" {sql_type}')


def _create_schema(conn):
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS schema_migrations (
            version INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            applied_at INTEGER NOT NULL
        );

        CREATE TABLE IF NOT EXISTS schools (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            code TEXT UNIQUE,
            address TEXT,
            timezone TEXT NOT NULL DEFAULT 'Asia/Ho_Chi_Minh',
            created_at INTEGER NOT NULL,
            updated_at INTEGER NOT NULL
        );

        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            school_id TEXT,
            email TEXT UNIQUE,
            password_hash TEXT,
            display_name TEXT NOT NULL,
            role TEXT NOT NULL CHECK (role IN ('admin','teacher','student','guardian')),
            status TEXT NOT NULL DEFAULT 'active' CHECK (status IN ('active','inactive','locked')),
            created_at INTEGER NOT NULL,
            updated_at INTEGER NOT NULL,
            last_login_at INTEGER,
            FOREIGN KEY (school_id) REFERENCES schools(id) ON DELETE SET NULL
        );

        CREATE TABLE IF NOT EXISTS teachers (
            id TEXT PRIMARY KEY,
            user_id TEXT UNIQUE,
            school_id TEXT,
            employee_code TEXT,
            name TEXT NOT NULL,
            email TEXT,
            created_at INTEGER NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL,
            FOREIGN KEY (school_id) REFERENCES schools(id) ON DELETE SET NULL,
            UNIQUE (school_id, employee_code)
        );

        CREATE TABLE IF NOT EXISTS students (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            grade INTEGER NOT NULL CHECK (grade BETWEEN 1 AND 12),
            user_id TEXT,
            school_id TEXT,
            student_code TEXT,
            date_of_birth TEXT,
            guardian_name TEXT,
            guardian_contact TEXT,
            status TEXT NOT NULL DEFAULT 'active',
            created_at INTEGER,
            updated_at INTEGER,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL,
            FOREIGN KEY (school_id) REFERENCES schools(id) ON DELETE SET NULL,
            UNIQUE (school_id, student_code)
        );

        CREATE TABLE IF NOT EXISTS classes (
            id TEXT PRIMARY KEY,
            school_id TEXT,
            homeroom_teacher_id TEXT,
            name TEXT NOT NULL,
            grade INTEGER NOT NULL CHECK (grade BETWEEN 1 AND 12),
            academic_year TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'active',
            created_at INTEGER NOT NULL,
            updated_at INTEGER NOT NULL,
            FOREIGN KEY (school_id) REFERENCES schools(id) ON DELETE SET NULL,
            FOREIGN KEY (homeroom_teacher_id) REFERENCES teachers(id) ON DELETE SET NULL,
            UNIQUE (school_id, name, academic_year)
        );

        CREATE TABLE IF NOT EXISTS class_enrollments (
            class_id TEXT NOT NULL,
            student_id TEXT NOT NULL,
            enrolled_at INTEGER NOT NULL,
            left_at INTEGER,
            status TEXT NOT NULL DEFAULT 'active',
            PRIMARY KEY (class_id, student_id),
            FOREIGN KEY (class_id) REFERENCES classes(id) ON DELETE CASCADE,
            FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS subjects (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL UNIQUE,
            created_at INTEGER NOT NULL
        );

        CREATE TABLE IF NOT EXISTS skills (
            id TEXT PRIMARY KEY,
            subject_id TEXT NOT NULL,
            name TEXT NOT NULL,
            description TEXT,
            grade INTEGER NOT NULL CHECK (grade BETWEEN 1 AND 12),
            mastery_threshold REAL NOT NULL DEFAULT 0.8 CHECK (mastery_threshold BETWEEN 0 AND 1),
            is_active INTEGER NOT NULL DEFAULT 1 CHECK (is_active IN (0,1)),
            updated_at INTEGER NOT NULL,
            FOREIGN KEY (subject_id) REFERENCES subjects(id)
        );

        CREATE TABLE IF NOT EXISTS skill_prerequisites (
            skill_id TEXT NOT NULL,
            prerequisite_skill_id TEXT NOT NULL,
            weight REAL NOT NULL DEFAULT 1.0 CHECK (weight > 0),
            PRIMARY KEY (skill_id, prerequisite_skill_id),
            CHECK (skill_id <> prerequisite_skill_id),
            FOREIGN KEY (skill_id) REFERENCES skills(id) ON DELETE CASCADE,
            FOREIGN KEY (prerequisite_skill_id) REFERENCES skills(id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS questions (
            id TEXT PRIMARY KEY,
            skill_id TEXT NOT NULL,
            text TEXT NOT NULL,
            difficulty_level INTEGER NOT NULL CHECK (difficulty_level BETWEEN 1 AND 3),
            hint TEXT,
            visual_hint TEXT,
            answer_format TEXT NOT NULL DEFAULT 'choice',
            correct_answer TEXT,
            metadata_json TEXT NOT NULL DEFAULT '{}',
            is_active INTEGER NOT NULL DEFAULT 1 CHECK (is_active IN (0,1)),
            updated_at INTEGER NOT NULL,
            FOREIGN KEY (skill_id) REFERENCES skills(id)
        );

        CREATE TABLE IF NOT EXISTS question_options (
            question_id TEXT NOT NULL,
            option_key TEXT NOT NULL,
            option_text TEXT NOT NULL,
            display_order INTEGER NOT NULL,
            is_correct INTEGER NOT NULL DEFAULT 0 CHECK (is_correct IN (0,1)),
            feedback TEXT,
            PRIMARY KEY (question_id, option_key),
            FOREIGN KEY (question_id) REFERENCES questions(id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS learning_sessions (
            id TEXT PRIMARY KEY,
            student_id TEXT NOT NULL,
            class_id TEXT,
            device_id TEXT,
            started_at INTEGER NOT NULL,
            ended_at INTEGER,
            status TEXT NOT NULL DEFAULT 'active' CHECK (status IN ('active','completed','abandoned')),
            initial_skill_id TEXT,
            summary_json TEXT NOT NULL DEFAULT '{}',
            FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
            FOREIGN KEY (class_id) REFERENCES classes(id) ON DELETE SET NULL,
            FOREIGN KEY (initial_skill_id) REFERENCES skills(id) ON DELETE SET NULL
        );

        CREATE TABLE IF NOT EXISTS student_mastery (
            student_id TEXT NOT NULL,
            skill_id TEXT NOT NULL,
            mastery_probability REAL NOT NULL DEFAULT 0.5 CHECK (mastery_probability BETWEEN 0 AND 1),
            attempts_count INTEGER NOT NULL DEFAULT 0,
            correct_count INTEGER NOT NULL DEFAULT 0,
            last_practiced_at INTEGER,
            updated_at INTEGER,
            PRIMARY KEY (student_id, skill_id),
            FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
            FOREIGN KEY (skill_id) REFERENCES skills(id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS responses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT NOT NULL,
            question_id TEXT NOT NULL,
            skill_id TEXT NOT NULL,
            difficulty_level INTEGER NOT NULL DEFAULT 2 CHECK (difficulty_level BETWEEN 1 AND 3),
            is_correct INTEGER NOT NULL CHECK (is_correct IN (0,1)),
            timestamp INTEGER NOT NULL,
            event_id TEXT UNIQUE,
            session_id TEXT,
            selected_answer TEXT,
            response_time_ms INTEGER CHECK (response_time_ms IS NULL OR response_time_ms >= 0),
            client_timestamp INTEGER,
            bkt_weight REAL NOT NULL DEFAULT 1.0 CHECK (bkt_weight BETWEEN 0 AND 1),
            anomaly_flags TEXT NOT NULL DEFAULT '[]',
            mastery_before REAL,
            mastery_after REAL,
            synced_at INTEGER,
            FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
            FOREIGN KEY (session_id) REFERENCES learning_sessions(id) ON DELETE SET NULL
        );

        CREATE TABLE IF NOT EXISTS mastery_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT NOT NULL,
            skill_id TEXT NOT NULL,
            response_id INTEGER,
            probability_before REAL NOT NULL CHECK (probability_before BETWEEN 0 AND 1),
            probability_after REAL NOT NULL CHECK (probability_after BETWEEN 0 AND 1),
            model_name TEXT NOT NULL DEFAULT 'BKT',
            model_parameters_json TEXT NOT NULL DEFAULT '{}',
            created_at INTEGER NOT NULL,
            FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
            FOREIGN KEY (skill_id) REFERENCES skills(id) ON DELETE CASCADE,
            FOREIGN KEY (response_id) REFERENCES responses(id) ON DELETE SET NULL
        );

        CREATE TABLE IF NOT EXISTS sync_events (
            event_id TEXT PRIMARY KEY,
            event_type TEXT NOT NULL,
            aggregate_id TEXT NOT NULL,
            payload_json TEXT NOT NULL,
            vector_clock TEXT NOT NULL,
            created_at INTEGER NOT NULL,
            synced_at INTEGER,
            retry_count INTEGER NOT NULL DEFAULT 0,
            last_error TEXT
        );

        CREATE TABLE IF NOT EXISTS pedagogical_explanations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT NOT NULL,
            response_event_id TEXT NOT NULL,
            skill_id TEXT NOT NULL,
            next_skill_id TEXT NOT NULL,
            explanation_text TEXT NOT NULL,
            mastery_before REAL NOT NULL,
            mastery_after REAL NOT NULL,
            created_at INTEGER NOT NULL,
            FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS intervention_plans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT,
            class_id TEXT,
            skill_id TEXT NOT NULL,
            teacher_id TEXT,
            title TEXT NOT NULL,
            plan_text TEXT NOT NULL,
            priority TEXT NOT NULL DEFAULT 'medium' CHECK (priority IN ('low','medium','high','urgent')),
            status TEXT NOT NULL DEFAULT 'planned' CHECK (status IN ('planned','active','completed','cancelled')),
            due_at INTEGER,
            created_at INTEGER NOT NULL,
            updated_at INTEGER NOT NULL,
            FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
            FOREIGN KEY (class_id) REFERENCES classes(id) ON DELETE CASCADE,
            FOREIGN KEY (skill_id) REFERENCES skills(id),
            FOREIGN KEY (teacher_id) REFERENCES teachers(id) ON DELETE SET NULL,
            CHECK (student_id IS NOT NULL OR class_id IS NOT NULL)
        );

        CREATE TABLE IF NOT EXISTS audit_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            actor_id TEXT,
            action TEXT NOT NULL,
            entity_type TEXT NOT NULL,
            entity_id TEXT NOT NULL,
            details_json TEXT NOT NULL DEFAULT '{}',
            ip_address TEXT,
            created_at INTEGER NOT NULL
        );

        CREATE UNIQUE INDEX IF NOT EXISTS idx_responses_event_id ON responses(event_id) WHERE event_id IS NOT NULL;
        CREATE INDEX IF NOT EXISTS idx_responses_student_skill_time ON responses(student_id, skill_id, timestamp DESC);
        CREATE INDEX IF NOT EXISTS idx_responses_question ON responses(question_id);
        CREATE INDEX IF NOT EXISTS idx_mastery_skill_probability ON student_mastery(skill_id, mastery_probability);
        CREATE INDEX IF NOT EXISTS idx_mastery_history_student_skill ON mastery_history(student_id, skill_id, created_at DESC);
        CREATE INDEX IF NOT EXISTS idx_sessions_student_started ON learning_sessions(student_id, started_at DESC);
        CREATE INDEX IF NOT EXISTS idx_enrollments_student ON class_enrollments(student_id, status);
        CREATE INDEX IF NOT EXISTS idx_questions_skill_difficulty ON questions(skill_id, difficulty_level, is_active);
        CREATE INDEX IF NOT EXISTS idx_sync_pending ON sync_events(synced_at, created_at) WHERE synced_at IS NULL;
        CREATE INDEX IF NOT EXISTS idx_explanations_student_created ON pedagogical_explanations(student_id, created_at DESC);
        CREATE INDEX IF NOT EXISTS idx_interventions_status_due ON intervention_plans(status, due_at);
        CREATE INDEX IF NOT EXISTS idx_audit_entity ON audit_logs(entity_type, entity_id, created_at DESC);
    """)

    # Upgrade databases created by older releases.
    _add_columns(conn, "students", {
        "user_id": "TEXT", "school_id": "TEXT", "student_code": "TEXT",
        "date_of_birth": "TEXT", "guardian_name": "TEXT", "guardian_contact": "TEXT",
        "status": "TEXT NOT NULL DEFAULT 'active'", "created_at": "INTEGER", "updated_at": "INTEGER",
    })
    _add_columns(conn, "student_mastery", {
        "attempts_count": "INTEGER NOT NULL DEFAULT 0", "correct_count": "INTEGER NOT NULL DEFAULT 0",
        "last_practiced_at": "INTEGER", "updated_at": "INTEGER",
    })
    _add_columns(conn, "responses", {
        "difficulty_level": "INTEGER DEFAULT 2", "event_id": "TEXT", "session_id": "TEXT",
        "selected_answer": "TEXT", "response_time_ms": "INTEGER", "client_timestamp": "INTEGER",
        "bkt_weight": "REAL DEFAULT 1.0", "anomaly_flags": "TEXT DEFAULT '[]'",
        "mastery_before": "REAL", "mastery_after": "REAL", "synced_at": "INTEGER",
    })
    _add_columns(conn, "sync_events", {"retry_count": "INTEGER NOT NULL DEFAULT 0", "last_error": "TEXT"})
    conn.execute("CREATE INDEX IF NOT EXISTS idx_mastery_student_updated ON student_mastery(student_id, updated_at DESC)")


def _sync_reference_data(conn):
    from backend.knowledge_graph import KNOWLEDGE_GRAPH

    now = int(time.time())
    subjects = sorted({info["subject"] for info in KNOWLEDGE_GRAPH.values()})
    subject_ids = {name: f"SUBJECT_{index + 1:02d}" for index, name in enumerate(subjects)}
    conn.executemany(
        "INSERT INTO subjects(id,name,created_at) VALUES(?,?,?) ON CONFLICT(name) DO UPDATE SET name=excluded.name",
        [(subject_ids[name], name, now) for name in subjects],
    )
    for skill_id, info in KNOWLEDGE_GRAPH.items():
        conn.execute("""
            INSERT INTO skills(id,subject_id,name,description,grade,updated_at)
            VALUES(?,?,?,?,?,?)
            ON CONFLICT(id) DO UPDATE SET subject_id=excluded.subject_id,name=excluded.name,
                description=excluded.description,grade=excluded.grade,updated_at=excluded.updated_at
        """, (skill_id, subject_ids[info["subject"]], info["name"], info.get("description"), info["grade"], now))
    conn.execute("DELETE FROM skill_prerequisites")
    for skill_id, info in KNOWLEDGE_GRAPH.items():
        conn.executemany(
            "INSERT INTO skill_prerequisites(skill_id,prerequisite_skill_id) VALUES(?,?)",
            [(skill_id, prerequisite) for prerequisite in info.get("prerequisites", [])],
        )

    if os.path.exists(Config.QUESTIONS_JSON_PATH):
        with open(Config.QUESTIONS_JSON_PATH, "r", encoding="utf-8") as file:
            questions = json.load(file)
        for question in questions:
            if question.get("skill_id") not in KNOWLEDGE_GRAPH:
                continue
            metadata = {key: value for key, value in question.items() if key not in {
                "id", "skill_id", "text", "difficulty_level", "hint", "visual_hint", "correct_answer", "options"
            }}
            conn.execute("""
                INSERT INTO questions(id,skill_id,text,difficulty_level,hint,visual_hint,correct_answer,metadata_json,updated_at)
                VALUES(?,?,?,?,?,?,?,?,?)
                ON CONFLICT(id) DO UPDATE SET skill_id=excluded.skill_id,text=excluded.text,
                    difficulty_level=excluded.difficulty_level,hint=excluded.hint,visual_hint=excluded.visual_hint,
                    correct_answer=excluded.correct_answer,metadata_json=excluded.metadata_json,updated_at=excluded.updated_at
            """, (question["id"], question["skill_id"], question["text"], question.get("difficulty_level", 2),
                  question.get("hint"), question.get("visual_hint"), question.get("correct_answer"),
                  json.dumps(metadata, ensure_ascii=False), now))
            conn.execute("DELETE FROM question_options WHERE question_id = ?", (question["id"],))
            options = question.get("options", [])
            conn.executemany("""
                INSERT INTO question_options(question_id,option_key,option_text,display_order,is_correct)
                VALUES(?,?,?,?,?)
            """, [(question["id"], option.get("key", str(i)), option.get("text", ""), i,
                    int(option.get("key") == question.get("correct_answer"))) for i, option in enumerate(options)])


def _seed_demo_students(conn):
    if conn.execute("SELECT COUNT(*) FROM students").fetchone()[0]:
        return
    now = int(time.time())
    students = [
        ("emma_std_01", "Emma", 7), ("an_01", "Nguyễn Văn An", 6),
        ("binh_02", "Trần Bình", 5), ("chi_03", "Lê Chi", 7),
        ("dung_04", "Nguyễn Dũng", 5), ("giang_05", "Phạm Giang", 6),
        ("hoang_06", "Lê Huy Hoàng", 7), ("linh_08", "Phạm Khánh Linh", 6),
    ]
    conn.executemany("INSERT INTO students(id,name,grade,created_at,updated_at) VALUES(?,?,?,?,?)",
                     [(sid, name, grade, now, now) for sid, name, grade in students])
    skill_ids = [row[0] for row in conn.execute("SELECT id FROM skills")]
    special = {("an_01", "MATH_G7"): .1, ("an_01", "MATH_G6"): .3,
               ("binh_02", "MATH_G5"): .22, ("dung_04", "MATH_G5_LCM"): .15,
               ("chi_03", "MATH_G7"): .88}
    conn.executemany("""
        INSERT INTO student_mastery(student_id,skill_id,mastery_probability,updated_at) VALUES(?,?,?,?)
    """, [(sid, skill, special.get((sid, skill), .5), now) for sid, _, _ in students for skill in skill_ids])


def init_db():
    os.makedirs(os.path.dirname(os.path.abspath(Config.DB_PATH)), exist_ok=True)
    with db_transaction() as conn:
        _create_schema(conn)
        _sync_reference_data(conn)
        _seed_demo_students(conn)
        conn.execute("INSERT OR IGNORE INTO schema_migrations(version,name,applied_at) VALUES(?,?,?)",
                     (SCHEMA_VERSION, "complete_learning_platform_schema", int(time.time())))


def get_student(student_id):
    with db_transaction() as conn:
        row = conn.execute("SELECT * FROM students WHERE id = ?", (student_id,)).fetchone()
        return dict(row) if row else None


def add_student(student_id, name, grade):
    now = int(time.time())
    with db_transaction() as conn:
        conn.execute("""
            INSERT INTO students(id,name,grade,created_at,updated_at) VALUES(?,?,?,?,?)
            ON CONFLICT(id) DO UPDATE SET name=excluded.name,grade=excluded.grade,updated_at=excluded.updated_at
        """, (student_id, name, grade, now, now))
        conn.execute("""
            INSERT OR IGNORE INTO student_mastery(student_id,skill_id,mastery_probability,updated_at)
            SELECT ?,id,0.5,? FROM skills
        """, (student_id, now))
    return get_student(student_id)


def list_students():
    with db_transaction() as conn:
        return [dict(row) for row in conn.execute(
            "SELECT id AS student_id,name,grade FROM students WHERE status='active' ORDER BY grade,name")]


def get_student_mastery(student_id, skill_id):
    with db_transaction() as conn:
        row = conn.execute("SELECT mastery_probability FROM student_mastery WHERE student_id=? AND skill_id=?",
                           (student_id, skill_id)).fetchone()
        return row[0] if row else 0.5


def update_student_mastery(student_id, skill_id, prob):
    probability = max(0.0, min(1.0, float(prob)))
    now = int(time.time())
    with db_transaction() as conn:
        # Diagnostic unit tests use synthetic learner IDs; preserve that supported workflow.
        conn.execute("INSERT OR IGNORE INTO students(id,name,grade,created_at,updated_at) VALUES(?,?,?,?,?)",
                     (student_id, student_id, 7, now, now))
        before_row = conn.execute("SELECT mastery_probability FROM student_mastery WHERE student_id=? AND skill_id=?",
                                  (student_id, skill_id)).fetchone()
        before = before_row[0] if before_row else 0.5
        conn.execute("""
            INSERT INTO student_mastery(student_id,skill_id,mastery_probability,updated_at) VALUES(?,?,?,?)
            ON CONFLICT(student_id,skill_id) DO UPDATE SET mastery_probability=excluded.mastery_probability,
                updated_at=excluded.updated_at
        """, (student_id, skill_id, probability, now))
        conn.execute("""
            INSERT INTO mastery_history(student_id,skill_id,probability_before,probability_after,created_at)
            VALUES(?,?,?,?,?)
        """, (student_id, skill_id, before, probability, now))


def record_response(student_id, question_id, skill_id, difficulty_level, is_correct, timestamp,
                    event_id=None, response_time_ms=None, client_timestamp=None, bkt_weight=1.0,
                    anomaly_flags=None, session_id=None, selected_answer=None,
                    mastery_before=None, mastery_after=None):
    now = int(time.time())
    flags = anomaly_flags or []
    with db_transaction() as conn:
        conn.execute("INSERT OR IGNORE INTO students(id,name,grade,created_at,updated_at) VALUES(?,?,?,?,?)",
                     (student_id, student_id, 7, now, now))
        cursor = conn.execute("""
            INSERT INTO responses(student_id,question_id,skill_id,difficulty_level,is_correct,timestamp,event_id,
                session_id,selected_answer,response_time_ms,client_timestamp,bkt_weight,anomaly_flags,
                mastery_before,mastery_after)
            VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
        """, (student_id, question_id, skill_id, difficulty_level, int(bool(is_correct)), timestamp, event_id,
              session_id, selected_answer, response_time_ms, client_timestamp, bkt_weight,
              json.dumps(flags, ensure_ascii=False), mastery_before, mastery_after))
        conn.execute("""
            INSERT INTO student_mastery(student_id,skill_id,mastery_probability,attempts_count,correct_count,last_practiced_at,updated_at)
            VALUES(?,?,0.5,1,?,?,?)
            ON CONFLICT(student_id,skill_id) DO UPDATE SET attempts_count=attempts_count+1,
                correct_count=correct_count+excluded.correct_count,last_practiced_at=excluded.last_practiced_at,
                updated_at=excluded.updated_at
        """, (student_id, skill_id, int(bool(is_correct)), timestamp, now))
        return cursor.lastrowid


def get_response_by_event_id(event_id):
    if not event_id:
        return None
    with db_transaction() as conn:
        row = conn.execute("SELECT * FROM responses WHERE event_id=?", (event_id,)).fetchone()
        return dict(row) if row else None


def upsert_sync_event(event_id, event_type, aggregate_id, payload, vector_clock):
    with db_transaction() as conn:
        conn.execute("""INSERT OR IGNORE INTO sync_events(event_id,event_type,aggregate_id,payload_json,vector_clock,created_at)
                        VALUES(?,?,?,?,?,?)""",
                     (event_id, event_type, aggregate_id, json.dumps(payload, ensure_ascii=False), vector_clock, int(time.time())))


def list_unsynced_events(limit=100):
    with db_transaction() as conn:
        rows = conn.execute("""SELECT event_id,event_type,aggregate_id,payload_json,vector_clock,created_at
                               FROM sync_events WHERE synced_at IS NULL ORDER BY created_at,event_id LIMIT ?""", (limit,)).fetchall()
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
    with db_transaction() as conn:
        cursor = conn.execute(f"UPDATE sync_events SET synced_at=? WHERE event_id IN ({placeholders})", [now, *event_ids])
        changed = cursor.rowcount
        conn.execute(f"UPDATE responses SET synced_at=? WHERE event_id IN ({placeholders})", [now, *event_ids])
        return changed


def add_pedagogical_explanation(student_id, response_event_id, skill_id, next_skill_id,
                                explanation_text, mastery_before, mastery_after):
    with db_transaction() as conn:
        conn.execute("""INSERT INTO pedagogical_explanations(student_id,response_event_id,skill_id,next_skill_id,
                        explanation_text,mastery_before,mastery_after,created_at) VALUES(?,?,?,?,?,?,?,?)""",
                     (student_id, response_event_id, skill_id, next_skill_id, explanation_text,
                      mastery_before, mastery_after, int(time.time())))


def list_pedagogical_explanations(student_id, limit=10):
    with db_transaction() as conn:
        return [dict(row) for row in conn.execute("""SELECT response_event_id,skill_id,next_skill_id,explanation_text,
            mastery_before,mastery_after,created_at FROM pedagogical_explanations WHERE student_id=?
            ORDER BY id DESC LIMIT ?""", (student_id, limit))]


def get_consecutive_failed_count(student_id, skill_id):
    with db_transaction() as conn:
        rows = conn.execute("SELECT is_correct FROM responses WHERE student_id=? AND skill_id=? ORDER BY id DESC LIMIT 10",
                            (student_id, skill_id)).fetchall()
    count = 0
    for row in rows:
        if row[0] != 0:
            break
        count += 1
    return count


def get_stuck_time_minutes(student_id, skill_id):
    with db_transaction() as conn:
        rows = conn.execute("SELECT timestamp,is_correct FROM responses WHERE student_id=? AND skill_id=? ORDER BY id DESC",
                            (student_id, skill_id)).fetchall()
    if not rows:
        return 2
    active = []
    for row in rows:
        active.append(row["timestamp"])
        if row["is_correct"]:
            break
    return max(2, int((active[0] - active[-1]) / 60)) if len(active) > 1 else 2
