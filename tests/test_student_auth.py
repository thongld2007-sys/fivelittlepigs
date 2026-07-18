from uuid import uuid4

from fastapi.testclient import TestClient
from sqlalchemy import func, select

from backend.app import app
from backend.database import SessionLocal, get_student_mastery
from backend.models import Student, StudentMastery, User


def credentials(prefix="student"):
    return f"{prefix}_{uuid4().hex[:10]}", "Secure12345"


def test_register_login_refresh_me_and_logout():
    client = TestClient(app)
    username, password = credentials("new")
    response = client.post("/api/auth/student/register", json={
        "username": username,
        "password": password,
        "name": "Học Sinh Mới",
        "grade": 7,
        "remember_me": True,
    })
    assert response.status_code == 201, response.text
    payload = response.json()
    assert payload["student"]["username"] == username
    assert "refresh_token" not in payload
    assert "HttpOnly" in response.headers["set-cookie"]

    access_token = payload["access_token"]
    original_refresh = client.cookies.get("vgap_refresh")
    me = client.get("/api/auth/me", headers={"Authorization": f"Bearer {access_token}"})
    assert me.status_code == 200
    assert me.json()["student"]["id"] == payload["student"]["id"]

    refreshed = client.post("/api/auth/refresh")
    assert refreshed.status_code == 200
    assert refreshed.json()["access_token"] != access_token
    replay = TestClient(app).post(
        "/api/auth/refresh", headers={"Cookie": f"vgap_refresh={original_refresh}"}
    )
    assert replay.status_code == 401

    student_id = payload["student"]["id"]
    with SessionLocal() as session:
        user = session.scalar(select(User).where(User.username == username))
        assert user.password_hash != password
        assert user.password_hash.startswith("$argon2")
        assert session.scalar(select(func.count()).select_from(StudentMastery).where(
            StudentMastery.student_id == student_id
        )) > 0

    assert client.post("/api/auth/logout").status_code == 204
    assert client.post("/api/auth/refresh").status_code == 401

    bad_login = client.post("/api/auth/student/login", json={
        "username": username, "password": "WrongPassword1"
    })
    assert bad_login.status_code == 401
    good_login = client.post("/api/auth/student/login", json={
        "username": username, "password": password
    })
    assert good_login.status_code == 200


def test_duplicate_username_is_rejected():
    client = TestClient(app)
    username, password = credentials("duplicate")
    body = {"username": username, "password": password, "name": "Học Sinh", "grade": 6}
    assert client.post("/api/auth/student/register", json=body).status_code == 201
    duplicate = client.post("/api/auth/student/register", json=body)
    assert duplicate.status_code == 409


def test_activate_existing_student_preserves_mastery():
    client = TestClient(app)
    student_id = "an_01"
    before = get_student_mastery(student_id, "MATH_G7")
    code_response = client.post("/api/auth/student/activation-code", json={"student_id": student_id})
    assert code_response.status_code == 200, code_response.text
    username, password = credentials("existing")
    activated = client.post("/api/auth/student/activate", json={
        "student_id": student_id,
        "activation_code": code_response.json()["activation_code"],
        "username": username,
        "password": password,
    })
    assert activated.status_code == 201, activated.text
    assert activated.json()["student"]["id"] == student_id
    assert get_student_mastery(student_id, "MATH_G7") == before
    with SessionLocal() as session:
        student = session.get(Student, student_id)
        assert student.user_id is not None

    reused = client.post("/api/auth/student/activate", json={
        "student_id": student_id,
        "activation_code": code_response.json()["activation_code"],
        "username": f"second_{uuid4().hex[:8]}",
        "password": password,
    })
    assert reused.status_code == 409


def test_repeated_wrong_password_temporarily_locks_account():
    client = TestClient(app)
    username, password = credentials("lock")
    assert client.post("/api/auth/student/register", json={
        "username": username, "password": password, "name": "Lock Test", "grade": 7
    }).status_code == 201
    client.post("/api/auth/logout")
    for _ in range(5):
        assert client.post("/api/auth/student/login", json={
            "username": username, "password": "WrongPassword1"
        }).status_code == 401
    locked = client.post("/api/auth/student/login", json={"username": username, "password": password})
    assert locked.status_code == 423
