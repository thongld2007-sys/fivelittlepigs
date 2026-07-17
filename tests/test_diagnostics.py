"""Automated verification of BKT, API scoring, routing, and persistence."""

from __future__ import annotations

import math
import uuid

import pytest
from fastapi.testclient import TestClient

import backend.database as db
from backend.app import app
from backend.diagnostic_engine import BKTProcessor


@pytest.fixture()
def client(tmp_path, monkeypatch):
    monkeypatch.setattr(db, "DB_PATH", tmp_path / "test_tutor.db")
    with TestClient(app) as test_client:
        yield test_client


def create_student(client: TestClient, student_id: str = "std001") -> None:
    response = client.post(
        "/api/students",
        json={"student_id": student_id, "name": "Học sinh ảo", "grade": 7},
    )
    assert response.status_code == 201


def test_bkt_formula_matches_design_report():
    correct = BKTProcessor.calculate_new_probability(0.5, True)
    incorrect = BKTProcessor.calculate_new_probability(0.5, False)
    assert math.isclose(correct, 0.8545454545, rel_tol=1e-8)
    assert math.isclose(incorrect, 0.2888888889, rel_tol=1e-8)


def test_backend_scores_answer_and_hides_correct_index(client: TestClient):
    create_student(client)
    question_response = client.get("/api/student/std001/next-question")
    assert question_response.status_code == 200
    question = question_response.json()["question"]
    assert "correct_index" not in question

    answer = client.post(
        "/api/student/std001/submit",
        json={
            "question_id": "math7_q01",
            "selected_index": 0,
            "time_spent": 12,
        },
    )
    assert answer.status_code == 200
    assert answer.json()["is_correct"] is True
    assert answer.json()["new_probability"] > 0.85


def test_event_replay_is_idempotent(client: TestClient):
    create_student(client)
    event_id = str(uuid.uuid4())
    payload = {
        "question_id": "math7_q01",
        "selected_index": 1,
        "time_spent": 20,
        "event_id": event_id,
    }
    first = client.post("/api/student/std001/submit", json=payload)
    second = client.post("/api/student/std001/submit", json=payload)
    assert first.status_code == second.status_code == 200
    assert second.json()["replayed"] is True
    with db.get_db_connection() as conn:
        count = conn.execute("SELECT COUNT(*) FROM Responses").fetchone()[0]
    assert count == 1


def test_ten_wrong_answers_identify_grade_five_root_gap(client: TestClient):
    create_student(client)
    # First expose the rational-number gap, then follow the diagnostic path to grade 5.
    initial = client.post(
        "/api/student/std001/submit",
        json={"question_id": "math7_q01", "selected_index": 1, "time_spent": 30},
    )
    assert initial.json()["diagnostic"]["action"] == "DOWNGRADE_DIAGNOSTIC"

    latest = None
    for _ in range(10):
        latest = client.post(
            "/api/student/std001/submit",
            json={"question_id": "math5_q01", "selected_index": 0, "time_spent": 30},
        )
        assert latest.status_code == 200
    result = latest.json()
    assert result["skill_id"] == "MATH5_COMMON_FRACTION"
    assert result["new_probability"] < BKTProcessor.THRESHOLD_GAP
    assert result["diagnostic"]["action"] == "ROOT_GAP"

    tree = client.get("/api/teacher/students/std001/reasoning-tree").json()["events"]
    assert len(tree) == 11
    assert tree[-1]["target_skill"] == "MATH5_COMMON_FRACTION"


def test_teacher_grouping_and_gap_alert(client: TestClient):
    for student_id in ("std001", "std002"):
        create_student(client, student_id)
        response = client.post(
            f"/api/student/{student_id}/submit",
            json={"question_id": "math5_q01", "selected_index": 0, "time_spent": 10},
        )
        assert response.status_code == 200
    groups = client.get("/api/teacher/groups").json()
    alerts = client.get("/api/teacher/gap-alerts").json()
    assert groups["groups"][0]["weak_students"] == 2
    assert alerts["alerts"][0]["percentage"] == 100.0


def test_validation_and_missing_student(client: TestClient):
    missing = client.get("/api/student/unknown/next-question")
    assert missing.status_code == 404
    create_student(client)
    invalid_time = client.post(
        "/api/student/std001/submit",
        json={"question_id": "math7_q01", "selected_index": 0, "time_spent": -1},
    )
    assert invalid_time.status_code == 422


def test_frontend_and_compatibility_endpoints(client: TestClient):
    page = client.get("/")
    assert page.status_code == 200
    assert "VGap AI" in page.text

    graph = client.get("/api/knowledge-graph")
    assert graph.status_code == 200
    assert graph.json()["MATH7_ADD_RATIONAL"]["subject"] == "Toán"
    assert len(graph.json()) >= 58

    create_student(client)
    extended_question = client.get(
        "/api/student/std001/next-question",
        params={"current_skill_id": "ENG_G9"},
    )
    assert extended_question.status_code == 200
    assert extended_question.json()["question"]["skill_id"] == "ENG_G9"

    client.post(
        "/api/student/std001/submit",
        json={"question_id": "math7_q01", "selected_index": 1, "time_spent": 15},
    )
    dashboard = client.get("/api/teacher/dashboard")
    assert dashboard.status_code == 200
    payload = dashboard.json()
    assert payload["metrics"]["total_students"] == 1
    assert payload["groups"][0]["count"] == 1
    assert payload["priority_list"][0]["id"] == "std001"
