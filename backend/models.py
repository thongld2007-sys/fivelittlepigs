"""Portable SQLAlchemy schema for SQLite pilots and PostgreSQL production."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional
from uuid import uuid4

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Index, Integer, JSON, String, Text, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


def utcnow():
    return datetime.now(timezone.utc)


def uuid_string():
    return str(uuid4())

from sqlalchemy import TypeDecorator, String

class MixedDateTime(TypeDecorator):
    """Handles mixed ISO strings and Unix integers in SQLite, falling back to DateTime for PG."""
    impl = String
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == 'sqlite':
            return dialect.type_descriptor(String())
        return dialect.type_descriptor(MixedDateTime)

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        if not value.tzinfo:
            value = value.replace(tzinfo=timezone.utc)
        if dialect.name == 'sqlite':
            return value.isoformat()
        return value

    def process_result_value(self, value, dialect):
        if value is None:
            return None
        if isinstance(value, (int, float)):
            return datetime.fromtimestamp(value, timezone.utc)
        if isinstance(value, str):
            if value.isdigit():
                return datetime.fromtimestamp(int(value), timezone.utc)
            try:
                dt = datetime.fromisoformat(value)
                if not dt.tzinfo:
                    dt = dt.replace(tzinfo=timezone.utc)
                return dt
            except ValueError:
                pass
        if isinstance(value, datetime):
            if not value.tzinfo:
                value = value.replace(tzinfo=timezone.utc)
            return value
        return value



class Base(DeclarativeBase):
    pass


class Organization(Base):
    __tablename__ = "organizations"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_string)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    created_at: Mapped[datetime] = mapped_column(MixedDateTime, default=utcnow)


class User(Base):
    __tablename__ = "users"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_string)
    organization_id: Mapped[str | None] = mapped_column(ForeignKey("organizations.id"))
    username: Mapped[str | None] = mapped_column(String(30), unique=True, index=True)
    display_name: Mapped[str] = mapped_column(String(100), default="")
    email: Mapped[str] = mapped_column(String(320), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(30), nullable=False, default="student")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    failed_login_count: Mapped[int] = mapped_column(Integer, default=0)
    locked_until: Mapped[datetime | None] = mapped_column(MixedDateTime)
    last_login_at: Mapped[datetime | None] = mapped_column(MixedDateTime)
    created_at: Mapped[datetime] = mapped_column(MixedDateTime, default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(MixedDateTime, default=utcnow, onupdate=utcnow)


class Student(Base):
    __tablename__ = "students"
    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    user_id: Mapped[Optional[str]] = mapped_column(ForeignKey("users.id"), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    grade: Mapped[int] = mapped_column(Integer, nullable=False)
    initial_assessment_completed: Mapped[bool] = mapped_column(Boolean, default=False, server_default="0")


class Classroom(Base):
    __tablename__ = "classrooms"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_string)
    organization_id: Mapped[str] = mapped_column(ForeignKey("organizations.id"), index=True)
    teacher_user_id: Mapped[Optional[str]] = mapped_column(ForeignKey("users.id"))
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    grade: Mapped[int] = mapped_column(Integer, nullable=False)


class Enrollment(Base):
    __tablename__ = "enrollments"
    classroom_id: Mapped[str] = mapped_column(ForeignKey("classrooms.id"), primary_key=True)
    student_id: Mapped[str] = mapped_column(ForeignKey("students.id"), primary_key=True)
    enrolled_at: Mapped[datetime] = mapped_column(MixedDateTime, default=utcnow)


class Skill(Base):
    __tablename__ = "skills"
    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    subject: Mapped[str] = mapped_column(String(120), nullable=False)
    grade: Mapped[int] = mapped_column(Integer, nullable=False)
    description: Mapped[str] = mapped_column(Text, default="")
    prerequisites: Mapped[list] = mapped_column(JSON, default=list)


class Question(Base):
    __tablename__ = "question_bank"
    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    skill_id: Mapped[str] = mapped_column(ForeignKey("skills.id"), index=True)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    options: Mapped[list] = mapped_column(JSON, nullable=False)
    correct_answer: Mapped[str] = mapped_column(String(20), nullable=False)
    difficulty_level: Mapped[int] = mapped_column(Integer, default=2)
    metadata_json: Mapped[dict] = mapped_column(JSON, default=dict)


class DiagnosticSession(Base):
    __tablename__ = "diagnostic_sessions"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_string)
    student_id: Mapped[str] = mapped_column(ForeignKey("students.id"), index=True)
    status: Mapped[str] = mapped_column(String(30), default="active")
    started_at: Mapped[datetime] = mapped_column(MixedDateTime, default=utcnow)
    completed_at: Mapped[datetime | None] = mapped_column(MixedDateTime)


class StudentMastery(Base):
    __tablename__ = "student_mastery"
    student_id: Mapped[str] = mapped_column(ForeignKey("students.id"), primary_key=True)
    skill_id: Mapped[str] = mapped_column(ForeignKey("skills.id"), primary_key=True)
    mastery_probability: Mapped[float] = mapped_column(Float, default=0.5)


class MasteryHistory(Base):
    __tablename__ = "mastery_history"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    student_id: Mapped[str] = mapped_column(ForeignKey("students.id"), index=True)
    skill_id: Mapped[str] = mapped_column(ForeignKey("skills.id"), index=True)
    probability: Mapped[float] = mapped_column(Float, nullable=False)
    response_id: Mapped[int | None] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(MixedDateTime, default=utcnow)


class Response(Base):
    __tablename__ = "responses"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    student_id: Mapped[str] = mapped_column(ForeignKey("students.id"), index=True)
    question_id: Mapped[str] = mapped_column(String(64), index=True)
    skill_id: Mapped[str] = mapped_column(String(64), index=True)
    difficulty_level: Mapped[int] = mapped_column(Integer, default=2)
    is_correct: Mapped[int] = mapped_column(Integer, nullable=False)
    timestamp: Mapped[int] = mapped_column(Integer, nullable=False)
    selected_option: Mapped[Optional[str]] = mapped_column(String(30))
    event_id: Mapped[Optional[str]] = mapped_column(String(36), unique=True)
    time_spent_ms: Mapped[int] = mapped_column(Integer, default=0)
    __table_args__ = (Index("idx_responses_student_skill_time", "student_id", "skill_id", "timestamp"),)


class UploadedWork(Base):
    __tablename__ = "uploaded_works"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_string)
    student_id: Mapped[str] = mapped_column(ForeignKey("students.id"), index=True)
    question_id: Mapped[Optional[str]] = mapped_column(String(64))
    object_key: Mapped[str] = mapped_column(String(500), nullable=False)
    mime_type: Mapped[str] = mapped_column(String(80), nullable=False)
    vision_result: Mapped[dict | None] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(MixedDateTime, default=utcnow)
    expires_at: Mapped[datetime | None] = mapped_column(MixedDateTime)


class AgentRun(Base):
    __tablename__ = "agent_runs"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_string)
    student_id: Mapped[Optional[str]] = mapped_column(ForeignKey("students.id"), index=True)
    operation: Mapped[str] = mapped_column(String(60), nullable=False)
    model: Mapped[Optional[str]] = mapped_column(String(120))
    trace: Mapped[list] = mapped_column(JSON, default=list)
    sources: Mapped[list] = mapped_column(JSON, default=list)
    created_at: Mapped[datetime] = mapped_column(MixedDateTime, default=utcnow)


class AIUsage(Base):
    __tablename__ = "ai_usage"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    operation: Mapped[str] = mapped_column(String(60), nullable=False)
    model: Mapped[Optional[str]] = mapped_column(String(120))
    prompt_tokens: Mapped[int] = mapped_column(Integer, default=0)
    completion_tokens: Mapped[int] = mapped_column(Integer, default=0)
    total_tokens: Mapped[int] = mapped_column(Integer, default=0)
    latency_ms: Mapped[float] = mapped_column(Float, default=0)
    timestamp: Mapped[int] = mapped_column(Integer, nullable=False)


class AuditLog(Base):
    __tablename__ = "audit_logs"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    actor_user_id: Mapped[Optional[str]] = mapped_column(String(36), index=True)
    action: Mapped[str] = mapped_column(String(100), nullable=False)
    entity_type: Mapped[str] = mapped_column(String(80), nullable=False)
    entity_id: Mapped[Optional[str]] = mapped_column(String(80))
    metadata_json: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(MixedDateTime, default=utcnow)


class RefreshToken(Base):
    __tablename__ = "refresh_tokens"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_string)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True)
    token_hash: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    expires_at: Mapped[datetime] = mapped_column(MixedDateTime, nullable=False)
    revoked_at: Mapped[datetime | None] = mapped_column(MixedDateTime)
    created_at: Mapped[datetime] = mapped_column(MixedDateTime, default=utcnow)


class AccountActivationToken(Base):
    __tablename__ = "account_activation_tokens"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_string)
    student_id: Mapped[str] = mapped_column(ForeignKey("students.id"), index=True)
    token_hash: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    expires_at: Mapped[datetime] = mapped_column(MixedDateTime, nullable=False)
    used_at: Mapped[datetime | None] = mapped_column(MixedDateTime)
    created_at: Mapped[datetime] = mapped_column(MixedDateTime, default=utcnow)
