"""Database repository supporting SQLite offline mode and PostgreSQL production."""

import json
import sqlite3
import time
from contextlib import contextmanager

from sqlalchemy import create_engine, delete, desc, event, func, select
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool

from backend.config import Config
from backend.models import (
    AIUsage, AgentRun, Base, DiagnosticSession, MasteryHistory, Question, Response,
    Skill, Student, StudentMastery, UploadedWork,
)


IS_SQLITE = Config.DATABASE_URL.startswith("sqlite")
engine_options = {"echo": Config.DB_ECHO, "pool_pre_ping": True}
if IS_SQLITE:
    engine_options["connect_args"] = {"check_same_thread": False, "timeout": 10}
    # Do not retain Windows file handles between short requests/tests. WAL still
    # provides concurrent readers while PostgreSQL uses the configured pool.
    engine_options["poolclass"] = NullPool
else:
    engine_options.update(pool_size=Config.DB_POOL_SIZE, max_overflow=Config.DB_MAX_OVERFLOW)
engine = create_engine(Config.DATABASE_URL, **engine_options)
SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)


if IS_SQLITE:
    @event.listens_for(engine, "connect")
    def _sqlite_pragmas(connection, _record):
        cursor = connection.cursor()
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.execute("PRAGMA busy_timeout=10000")
        cursor.execute("PRAGMA synchronous=NORMAL")
        cursor.close()


@contextmanager
def db_session():
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()



SCHEMA_VERSION = 4


def _password_hash(password, salt=None):
    salt = salt or os.urandom(16).hex()
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), bytes.fromhex(salt), 120_000).hex()
    return f"pbkdf2_sha256${salt}${digest}"


def get_db_connection():
    """Legacy SQLite handle kept only for migration tools and existing tests."""
    if not IS_SQLITE:
        raise RuntimeError("Raw sqlite connection is unavailable when DATABASE_URL uses PostgreSQL")
    connection = sqlite3.connect(Config.DB_PATH, timeout=10)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA journal_mode=WAL")
    connection.execute("PRAGMA busy_timeout=10000")
    connection.execute("PRAGMA synchronous=NORMAL")
    return connection


def _migrate_legacy_sqlite():
    if not IS_SQLITE or not __import__("os").path.exists(Config.DB_PATH):
        return
    connection = get_db_connection()
    try:
        tables = {row[0] for row in connection.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        if "responses" in tables:
            columns = {row[1] for row in connection.execute("PRAGMA table_info(responses)")}
            additions = {
                "difficulty_level": "INTEGER DEFAULT 2", "selected_option": "TEXT",
                "event_id": "TEXT", "time_spent_ms": "INTEGER DEFAULT 0",
            }
            for name, definition in additions.items():
                if name not in columns:
                    connection.execute(f"ALTER TABLE responses ADD COLUMN {name} {definition}")
            connection.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_responses_event_id ON responses(event_id)")
        if "users" in tables:
            columns = {row[1] for row in connection.execute("PRAGMA table_info(users)")}
            additions = {
                "organization_id": "TEXT",
                "username": "TEXT",
                "email": "TEXT",
                "password_hash": "TEXT",
                "role": "TEXT DEFAULT 'student'",
                "is_active": "BOOLEAN DEFAULT 1",
                "failed_login_count": "INTEGER DEFAULT 0",
                "locked_until": "DATETIME",
                "last_login_at": "DATETIME",
                "created_at": "DATETIME",
                "updated_at": "DATETIME",
            }
            for name, definition in additions.items():
                if name not in columns:
                    connection.execute(f"ALTER TABLE users ADD COLUMN {name} {definition}")
            connection.execute("CREATE UNIQUE INDEX IF NOT EXISTS ix_users_username ON users(username)")
        if "students" in tables:
            columns = {row[1] for row in connection.execute("PRAGMA table_info(students)")}
            if "user_id" not in columns:
                connection.execute("ALTER TABLE students ADD COLUMN user_id TEXT")
            connection.execute("CREATE UNIQUE INDEX IF NOT EXISTS ix_students_user_id ON students(user_id)")
        if "skills" in tables:
            columns = {row[1] for row in connection.execute("PRAGMA table_info(skills)")}
            additions = {
                "subject": "TEXT",
                "grade": "INTEGER",
                "description": "TEXT",
                "prerequisites": "JSON",
            }
            for name, definition in additions.items():
                if name not in columns:
                    connection.execute(f"ALTER TABLE skills ADD COLUMN {name} {definition}")
        if "question_bank" in tables:
            columns = {row[1] for row in connection.execute("PRAGMA table_info(question_bank)")}
            additions = {
                "difficulty_level": "INTEGER DEFAULT 2",
                "metadata_json": "JSON",
            }
            for name, definition in additions.items():
                if name not in columns:
                    connection.execute(f"ALTER TABLE question_bank ADD COLUMN {name} {definition}")
        connection.commit()
    finally:
        connection.close()


def init_db(seed_demo=True):
    _migrate_legacy_sqlite()
    Base.metadata.create_all(engine)
    from backend.knowledge_graph import KNOWLEDGE_GRAPH
    with db_session() as session:
        for skill_id, info in KNOWLEDGE_GRAPH.items():
            skill = session.get(Skill, skill_id) or Skill(id=skill_id)
            skill.name = info["name"]
            skill.subject = info.get("subject", "Toán")
            skill.grade = info.get("grade", 7)
            skill.description = info.get("description", "")
            skill.prerequisites = info.get("prerequisites", [])
            session.add(skill)
        if __import__("os").path.exists(Config.QUESTIONS_JSON_PATH):
            with open(Config.QUESTIONS_JSON_PATH, "r", encoding="utf-8") as file:
                for item in json.load(file):
                    question = session.get(Question, item["id"]) or Question(id=item["id"])
                    question.skill_id = item["skill_id"]
                    question.text = item["text"]
                    question.options = item["options"]
                    question.correct_answer = item["correct_answer"]
                    question.difficulty_level = item.get("difficulty_level", 2)
                    question.metadata_json = {key: value for key, value in item.items() if key not in {
                        "id", "skill_id", "text", "options", "correct_answer", "difficulty_level"
                    }}
                    session.add(question)
        if seed_demo and not session.scalar(select(func.count()).select_from(Student)):
            demos = [
                ("emma_std_01", "Emma", 7), ("an_01", "Nguyễn Văn An", 6),
                ("binh_02", "Trần Bình", 5), ("chi_03", "Lê Chi", 7),
                ("dung_04", "Nguyễn Dũng", 5), ("giang_05", "Phạm Giang", 6),
                ("hoang_06", "Lê Huy Hoàng", 7), ("linh_08", "Phạm Khánh Linh", 6),
            ]
            for student_id, name, grade in demos:
                session.add(Student(id=student_id, name=name, grade=grade))
            session.flush()
            overrides = {("an_01", "MATH_G7"): .1, ("an_01", "MATH_G6"): .3,
                         ("binh_02", "MATH_G5"): .22, ("dung_04", "MATH_G5_LCM"): .15,
                         ("chi_03", "MATH_G7"): .88}
            for student_id, _, _ in demos:
                for skill_id in KNOWLEDGE_GRAPH:
                    session.add(StudentMastery(student_id=student_id, skill_id=skill_id,
                                               mastery_probability=overrides.get((student_id, skill_id), .5)))


def get_student(student_id):
    with db_session() as session:
        student = session.get(Student, student_id)
        return {"id": student.id, "name": student.name, "grade": student.grade} if student else None


def add_student(student_id, name, grade):
    with db_session() as session:
        student = session.get(Student, student_id) or Student(id=student_id)
        student.name, student.grade = name, grade
        session.add(student)
    return get_student(student_id)


def list_students():
    with db_session() as session:
        rows = session.scalars(select(Student).order_by(Student.grade, Student.name)).all()
        return [{"student_id": row.id, "name": row.name, "grade": row.grade} for row in rows]


def reset_student_session(student_id, name, grade, skill_ids):
    with db_session() as session:
        student = session.get(Student, student_id) or Student(id=student_id)
        student.name, student.grade = name, grade
        session.add(student)
        session.flush()
        session.execute(delete(Response).where(Response.student_id == student_id))
        for skill_id in skill_ids:
            mastery = session.get(StudentMastery, (student_id, skill_id)) or StudentMastery(
                student_id=student_id, skill_id=skill_id
            )
            mastery.mastery_probability = .5
            session.add(mastery)
        diagnostic = DiagnosticSession(student_id=student_id)
        session.add(diagnostic)
        session.flush()
        return diagnostic.id


def get_student_mastery(student_id, skill_id):
    with db_session() as session:
        row = session.get(StudentMastery, (student_id, skill_id))
        return row.mastery_probability if row else .5


def update_student_mastery(student_id, skill_id, probability, response_id=None):
    with db_session() as session:
        row = session.get(StudentMastery, (student_id, skill_id)) or StudentMastery(
            student_id=student_id, skill_id=skill_id
        )
        row.mastery_probability = probability
        session.add(row)
        session.add(MasteryHistory(student_id=student_id, skill_id=skill_id,
                                   probability=probability, response_id=response_id))


def record_response(student_id, question_id, skill_id, difficulty_level, is_correct, timestamp,
                    selected_option=None, event_id=None, time_spent_ms=0):
    with db_session() as session:
        if event_id:
            existing = session.scalar(select(Response).where(Response.event_id == event_id))
            if existing:
                return existing.id
        row = Response(student_id=student_id, question_id=question_id, skill_id=skill_id,
                       difficulty_level=difficulty_level, is_correct=int(bool(is_correct)), timestamp=timestamp,
                       selected_option=selected_option, event_id=event_id, time_spent_ms=time_spent_ms)
        session.add(row)
        session.flush()
        return row.id


def get_response_event(event_id):
    if not event_id:
        return None
    with db_session() as session:
        row = session.scalar(select(Response).where(Response.event_id == event_id))
        if not row:
            return None
        return {
            "id": row.id,
            "student_id": row.student_id,
            "question_id": row.question_id,
            "skill_id": row.skill_id,
            "is_correct": bool(row.is_correct),
        }


def get_response_history(student_id, skill_id, limit=None):
    statement = select(Response).where(Response.student_id == student_id, Response.skill_id == skill_id).order_by(desc(Response.id))
    if limit:
        statement = statement.limit(limit)
    with db_session() as session:
        rows = session.scalars(statement).all()
        return [{"question_id": row.question_id, "difficulty_level": row.difficulty_level,
                 "is_correct": row.is_correct, "timestamp": row.timestamp} for row in rows]


def get_answered_question_ids(student_id, skill_id):
    with db_session() as session:
        return set(session.scalars(select(Response.question_id).where(
            Response.student_id == student_id, Response.skill_id == skill_id
        )).all())


def get_consecutive_failed_count(student_id, skill_id):
    count = 0
    for row in get_response_history(student_id, skill_id, 10):
        if row["is_correct"]:
            break
        count += 1
    return count


def get_stuck_time_minutes(student_id, skill_id):
    rows = get_response_history(student_id, skill_id)
    if len(rows) < 2:
        return 2
    return max(2, int((rows[0]["timestamp"] - rows[-1]["timestamp"]) / 60))


def get_recent_wrong_count(student_id, skill_id, limit=5):
    with db_session() as session:
        return len(session.scalars(select(Response.id).where(
            Response.student_id == student_id, Response.skill_id == skill_id, Response.is_correct == 0
        ).order_by(desc(Response.id)).limit(limit)).all())


def get_gap_cohort(skill_id):
    with db_session() as session:
        rows = session.execute(select(Student.id, Student.name, StudentMastery.mastery_probability).join(
            StudentMastery, Student.id == StudentMastery.student_id
        ).where(StudentMastery.skill_id == skill_id, StudentMastery.mastery_probability < .5).order_by(
            StudentMastery.mastery_probability
        )).all()
        return [tuple(row) for row in rows]


def get_common_wrong_questions(skill_id, limit=5):
    with db_session() as session:
        rows = session.execute(select(Response.question_id, func.count(Response.id)).where(
            Response.skill_id == skill_id, Response.is_correct == 0
        ).group_by(Response.question_id).order_by(desc(func.count(Response.id))).limit(limit)).all()
        return [tuple(row) for row in rows]


def get_dashboard_snapshot(skill_ids):
    with db_session() as session:
        total = session.scalar(select(func.count()).select_from(Student)) or 0
        average = session.scalar(select(func.avg(StudentMastery.mastery_probability))) or .5
        gaps, averages = {}, {}
        for skill_id in skill_ids:
            gaps[skill_id] = list(session.scalars(select(Student.name).join(
                StudentMastery, Student.id == StudentMastery.student_id
            ).where(StudentMastery.skill_id == skill_id, StudentMastery.mastery_probability < .5)).all())
            averages[skill_id] = session.scalar(select(func.avg(StudentMastery.mastery_probability)).where(
                StudentMastery.skill_id == skill_id
            ))
        students = [(row.id, row.name) for row in session.scalars(select(Student)).all()]
        last_skills = {}
        for student_id, _ in students:
            last_skills[student_id] = session.scalar(select(Response.skill_id).where(
                Response.student_id == student_id
            ).order_by(desc(Response.id)).limit(1))
        return {"total_students": total, "average_mastery": average, "gaps": gaps,
                "skill_averages": averages, "students": students, "last_skills": last_skills}


def record_ai_usage(operation, model, usage, latency_ms):
    usage = usage or {}
    prompt = int(usage.get("prompt_tokens", usage.get("input_tokens", 0)) or 0)
    completion = int(usage.get("completion_tokens", usage.get("output_tokens", 0)) or 0)
    with db_session() as session:
        session.add(AIUsage(operation=operation, model=model, prompt_tokens=prompt,
                            completion_tokens=completion,
                            total_tokens=int(usage.get("total_tokens", prompt + completion) or 0),
                            latency_ms=float(latency_ms), timestamp=int(time.time())))


def record_agent_run(operation, model, trace, sources, student_id=None):
    with db_session() as session:
        row = AgentRun(operation=operation, model=model, trace=trace, sources=sources, student_id=student_id)
        session.add(row)
        session.flush()
        return row.id


def record_uploaded_work(student_id, question_id, object_key, mime_type, vision_result=None):
    with db_session() as session:
        row = UploadedWork(student_id=student_id, question_id=question_id or None, object_key=object_key,
                           mime_type=mime_type, vision_result=vision_result)
        session.add(row)
        session.flush()
        return row.id


def get_ai_usage_summary():
    with db_session() as session:
        row = session.execute(select(func.count(AIUsage.id), func.avg(AIUsage.total_tokens),
                                     func.avg(AIUsage.latency_ms), func.sum(AIUsage.total_tokens))).one()
        operations = session.execute(select(AIUsage.operation, func.count(AIUsage.id),
                                            func.avg(AIUsage.total_tokens), func.avg(AIUsage.latency_ms)).group_by(
                                                AIUsage.operation).order_by(AIUsage.operation)).all()
        return {"calls": row[0], "avg_tokens_per_call": round(row[1] or 0, 2),
                "avg_latency_ms": round(row[2] or 0, 2), "total_tokens": row[3] or 0,
                "by_operation": [{"operation": item[0], "calls": item[1], "avg_tokens": round(item[2] or 0, 2),
                                  "avg_latency": round(item[3] or 0, 2)} for item in operations]}


def delete_students(student_ids):
    if not student_ids:
        return
    with db_session() as session:
        session.execute(delete(Response).where(Response.student_id.in_(student_ids)))
        session.execute(delete(MasteryHistory).where(MasteryHistory.student_id.in_(student_ids)))
        session.execute(delete(StudentMastery).where(StudentMastery.student_id.in_(student_ids)))
        session.execute(delete(DiagnosticSession).where(DiagnosticSession.student_id.in_(student_ids)))
        session.execute(delete(Student).where(Student.id.in_(student_ids)))
