"""Student account registration, activation and session management."""

from __future__ import annotations

import hashlib
import re
import secrets
from datetime import datetime, timedelta, timezone
from uuid import uuid4

from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerifyMismatchError
from sqlalchemy import select

from backend.auth import create_access_token
from backend.database import db_session
from backend.models import (
    AccountActivationToken,
    AuditLog,
    RefreshToken,
    Skill,
    Student,
    StudentMastery,
    User,
)


password_hasher = PasswordHasher(time_cost=3, memory_cost=65536, parallelism=2)
_DUMMY_HASH = password_hasher.hash("not-a-real-user-password")
USERNAME_PATTERN = re.compile(r"^[a-z0-9][a-z0-9._-]{3,29}$")
MAX_FAILED_LOGINS = 5
LOCK_MINUTES = 15


class StudentAuthError(ValueError):
    def __init__(self, message: str, status_code: int = 400):
        super().__init__(message)
        self.message = message
        self.status_code = status_code


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


def _aware(value: datetime | None) -> datetime | None:
    if value is not None and value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value


def normalize_username(username: str) -> str:
    normalized = username.strip().lower()
    if not USERNAME_PATTERN.fullmatch(normalized):
        raise StudentAuthError(
            "Tên đăng nhập phải có 4-30 ký tự, bắt đầu bằng chữ/số và chỉ gồm chữ thường, số, dấu chấm, gạch ngang hoặc gạch dưới."
        )
    return normalized


def validate_password(password: str) -> None:
    if len(password) < 8 or len(password) > 128:
        raise StudentAuthError("Mật khẩu phải có từ 8 đến 128 ký tự.")
    if not re.search(r"[A-Za-z]", password) or not re.search(r"\d", password):
        raise StudentAuthError("Mật khẩu phải có ít nhất một chữ cái và một chữ số.")


def _token_hash(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def _student_payload(student: Student, user: User) -> dict:
    return {
        "id": student.id,
        "name": student.name,
        "grade": student.grade,
        "username": user.username,
        "initial_assessment_completed": bool(student.initial_assessment_completed)
    }


def _audit(session, user_id: str | None, action: str, entity_id: str | None = None, metadata=None):
    session.add(AuditLog(
        actor_user_id=user_id,
        action=action,
        entity_type="student_account",
        entity_id=entity_id if entity_id is not None else "",
        metadata_json=metadata or {},
    ))


def register_student(*, username: str, password: str, name: str, grade: int, email: str | None = None) -> dict:
    username = normalize_username(username)
    validate_password(password)
    name = " ".join(name.strip().split())
    if len(name) < 2 or len(name) > 100 or not 1 <= grade <= 12:
        raise StudentAuthError("Họ tên hoặc khối lớp không hợp lệ.")
    normalized_email = email.strip().lower() if email else f"{username}@students.local"
    with db_session() as session:
        if session.scalar(select(User.id).where(User.username == username)):
            raise StudentAuthError("Tên đăng nhập đã được sử dụng.", 409)
        if session.scalar(select(User.id).where(User.email == normalized_email)):
            raise StudentAuthError("Email đã được sử dụng.", 409)
        user = User(
            username=username,
            display_name=name,
            email=normalized_email,
            password_hash=password_hasher.hash(password),
            role="student",
            is_active=True,
        )
        session.add(user)
        session.flush()
        student = Student(id=f"std_{uuid4().hex[:16]}", user_id=user.id, name=name, grade=grade)
        session.add(student)
        session.flush()
        for skill_id in session.scalars(select(Skill.id)).all():
            session.add(StudentMastery(student_id=student.id, skill_id=skill_id, mastery_probability=.5))
        _audit(session, user.id, "student_registered", student.id)
        return _student_payload(student, user)


def create_activation_code(student_id: str, ttl_hours: int = 24) -> dict:
    code = "-".join([secrets.token_hex(2).upper(), secrets.token_hex(2).upper()])
    with db_session() as session:
        student = session.get(Student, student_id)
        if not student:
            raise StudentAuthError("Không tìm thấy hồ sơ học sinh.", 404)
        if student.user_id:
            raise StudentAuthError("Hồ sơ học sinh này đã có tài khoản.", 409)
        previous = session.scalars(select(AccountActivationToken).where(
            AccountActivationToken.student_id == student_id,
            AccountActivationToken.used_at.is_(None),
        )).all()
        for token in previous:
            token.used_at = now_utc()
        session.add(AccountActivationToken(
            student_id=student_id,
            token_hash=_token_hash(code),
            expires_at=now_utc() + timedelta(hours=ttl_hours),
        ))
        _audit(session, None, "activation_code_created", student_id)
    return {"student_id": student_id, "activation_code": code, "expires_in_hours": ttl_hours}


def activate_student(*, student_id: str, activation_code: str, username: str,
                     password: str, email: str | None = None) -> dict:
    username = normalize_username(username)
    validate_password(password)
    normalized_email = email.strip().lower() if email else f"{username}@students.local"
    with db_session() as session:
        student = session.get(Student, student_id)
        if not student:
            raise StudentAuthError("Mã học sinh hoặc mã kích hoạt không hợp lệ.", 400)
        if student.user_id:
            raise StudentAuthError("Hồ sơ học sinh này đã được kích hoạt.", 409)
        token = session.scalar(select(AccountActivationToken).where(
            AccountActivationToken.student_id == student_id,
            AccountActivationToken.token_hash == _token_hash(activation_code.strip().upper()),
            AccountActivationToken.used_at.is_(None),
        ).order_by(AccountActivationToken.created_at.desc()))
        if not token or _aware(token.expires_at) <= now_utc():
            raise StudentAuthError("Mã học sinh hoặc mã kích hoạt không hợp lệ.", 400)
        if session.scalar(select(User.id).where(User.username == username)):
            raise StudentAuthError("Tên đăng nhập đã được sử dụng.", 409)
        if session.scalar(select(User.id).where(User.email == normalized_email)):
            raise StudentAuthError("Email đã được sử dụng.", 409)
        user = User(username=username, display_name=student.name, email=normalized_email,
                    password_hash=password_hasher.hash(password), role="student", is_active=True)
        session.add(user)
        session.flush()
        student.user_id = user.id
        token.used_at = now_utc()
        _audit(session, user.id, "existing_student_activated", student.id)
        return _student_payload(student, user)


from sqlalchemy import select, or_
import hmac

def verify_legacy_password(password: str, encoded: str) -> bool:
    try:
        algorithm, salt, expected = encoded.split('$', 2)
        if algorithm != 'pbkdf2_sha256':
            return False
        actual = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), bytes.fromhex(salt), 120_000).hex()
        return hmac.compare_digest(actual, expected)
    except (ValueError, TypeError, AttributeError):
        return False

def authenticate_student(username: str, password: str) -> dict:
    try:
        username = normalize_username(username)
    except StudentAuthError:
        username = "invalid-user"
    error = None
    payload = None
    with db_session() as session:
        user = session.scalar(select(User).where(or_(User.username == username, User.email == username), User.role == "student"))
        if not user:
            try:
                password_hasher.verify(_DUMMY_HASH, password)
            except (VerifyMismatchError, InvalidHashError):
                pass
            error = StudentAuthError("Tên đăng nhập hoặc mật khẩu không chính xác.", 401)
        elif not user.is_active:
            error = StudentAuthError("Tài khoản hiện không hoạt động.", 403)
        elif _aware(user.locked_until) and _aware(user.locked_until) > now_utc():
            error = StudentAuthError("Tài khoản tạm khóa do đăng nhập sai nhiều lần. Vui lòng thử lại sau.", 423)
        else:
            try:
                if user.password_hash.startswith("pbkdf2_sha256$"):
                    valid = verify_legacy_password(password, user.password_hash)
                    if valid:
                        user.password_hash = password_hasher.hash(password)
                else:
                    valid = password_hasher.verify(user.password_hash, password)
            except (VerifyMismatchError, InvalidHashError):
                valid = False
            if not valid:
                user.failed_login_count = (user.failed_login_count or 0) + 1
                if user.failed_login_count >= MAX_FAILED_LOGINS:
                    user.locked_until = now_utc() + timedelta(minutes=LOCK_MINUTES)
                    user.failed_login_count = 0
                _audit(session, user.id, "student_login_failed")
                error = StudentAuthError("Tên đăng nhập hoặc mật khẩu không chính xác.", 401)
            else:
                student = session.scalar(select(Student).where(Student.user_id == user.id))
                if not student:
                    error = StudentAuthError("Tài khoản chưa được liên kết với hồ sơ học sinh.", 409)
                else:
                    user.failed_login_count = 0
                    user.locked_until = None
                    user.last_login_at = now_utc()
                    if password_hasher.check_needs_rehash(user.password_hash):
                        user.password_hash = password_hasher.hash(password)
                    _audit(session, user.id, "student_login_succeeded", student.id)
                    payload = {"user_id": user.id, "student": _student_payload(student, user)}
    if error:
        raise error
    return payload


def create_session(user_id: str, student: dict, remember_me: bool = False) -> dict:
    raw_refresh = secrets.token_urlsafe(48)
    expires = now_utc() + timedelta(days=30 if remember_me else 7)
    with db_session() as session:
        session.add(RefreshToken(user_id=user_id, token_hash=_token_hash(raw_refresh), expires_at=expires))
    access = create_access_token(user_id, {"role": "student", "student_id": student["id"]})
    return {"access_token": access, "refresh_token": raw_refresh,
            "expires_in": 3600, "student": student, "remember_me": remember_me,
            "user": {"id": user_id, "role": "student", "student_id": student["id"], "initial_assessment_completed": student.get("initial_assessment_completed", False)}}


def refresh_session(raw_refresh: str) -> dict:
    replacement = secrets.token_urlsafe(48)
    error = None
    payload = None
    with db_session() as session:
        token = session.scalar(select(RefreshToken).where(
            RefreshToken.token_hash == _token_hash(raw_refresh)
        ).with_for_update())
        if not token or token.revoked_at or _aware(token.expires_at) <= now_utc():
            error = StudentAuthError("Phiên đăng nhập không hợp lệ hoặc đã hết hạn.", 401)
        else:
            user = session.get(User, token.user_id)
            student = session.scalar(select(Student).where(Student.user_id == token.user_id))
            if not user or not user.is_active or not student:
                error = StudentAuthError("Phiên đăng nhập không hợp lệ hoặc đã hết hạn.", 401)
            else:
                token.revoked_at = now_utc()
                original_lifetime = _aware(token.expires_at) - _aware(token.created_at)
                remember_me = original_lifetime > timedelta(days=8)
                expires = now_utc() + timedelta(days=30 if remember_me else 7)
                session.add(RefreshToken(user_id=user.id, token_hash=_token_hash(replacement), expires_at=expires))
                student_data = _student_payload(student, user)
                payload = {
                    "access_token": create_access_token(user.id, {"role": "student", "student_id": student.id}),
                    "refresh_token": replacement,
                    "expires_in": 3600,
                    "student": student_data,
                    "remember_me": remember_me,
                    "user": {"id": user.id, "role": "student", "student_id": student.id, "initial_assessment_completed": student_data.get("initial_assessment_completed", False)}
                }
    if error:
        raise error
    return payload


def revoke_session(raw_refresh: str | None) -> None:
    if not raw_refresh:
        return
    with db_session() as session:
        token = session.scalar(select(RefreshToken).where(RefreshToken.token_hash == _token_hash(raw_refresh)))
        if token and not token.revoked_at:
            token.revoked_at = now_utc()


def get_student_for_user(user_id: str) -> dict | None:
    with db_session() as session:
        user = session.get(User, user_id)
        student = session.scalar(select(Student).where(Student.user_id == user_id))
        return _student_payload(student, user) if user and student else None
