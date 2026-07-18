from uuid import uuid4

from fastapi.testclient import TestClient
from sqlalchemy import inspect

from backend.app import app
from backend.database import engine


client = TestClient(app)


def test_complete_platform_schema_exists():
    tables = set(inspect(engine).get_table_names())
    assert {
        "organizations", "users", "classrooms", "enrollments", "students", "skills",
        "question_bank", "diagnostic_sessions", "student_mastery", "mastery_history",
        "responses", "uploaded_works", "agent_runs", "ai_usage", "audit_logs",
    }.issubset(tables)


def test_answer_event_is_idempotent():
    student_id = f"idempotent-{uuid4().hex[:10]}"
    event_id = str(uuid4())
    session = client.post(
        "/api/student/session",
        json={"student_id": student_id, "name": "Idempotent Test", "grade": 7},
    )
    assert session.status_code == 200
    question_response = client.get(f"/api/student/{student_id}/next-question")
    assert question_response.status_code == 200
    question = question_response.json()["question"]
    payload = {
        "question_id": question["id"],
        "selected_option": question["options"][0]["key"],
        "event_id": event_id,
        "time_spent_ms": 1200,
    }
    first = client.post(f"/api/student/{student_id}/submit", json=payload)
    second = client.post(f"/api/student/{student_id}/submit", json=payload)
    assert first.status_code == 200
    assert second.status_code == 200
    assert second.json()["idempotent_replay"] is True
    assert second.json()["new_mastery_probability"] == first.json()["new_mastery_probability"]
