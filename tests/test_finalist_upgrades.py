import sqlite3

import backend.auth as auth
from backend.config import Config
from backend.rag import rag_retriever
from tests.simulate_1000_students import run_simulation


def test_rag_retrieval_is_grounded_and_cited():
    rows = rag_retriever.retrieve("quy đồng mẫu số phân số", skill_id="MATH_G5")
    assert rows and rows[0]["source"]
    assert "content" in rows[0]


def test_sqlite_uses_wal():
    conn = sqlite3.connect(Config.DB_PATH)
    try:
        assert conn.execute("PRAGMA journal_mode").fetchone()[0].lower() == "wal"
    finally:
        conn.close()


def test_simulation_has_1000_students_and_adaptive_reduces_questions():
    report = run_simulation(1000)
    assert report["methodology"]["students"] == 1000
    assert report["comparison"]["question_reduction_percent"] > 0
    assert report["adaptive_bkt_kg"]["questions_avg"] < report["linear_test"]["questions_avg"]


def test_hs256_token_round_trip_and_tamper_rejection(monkeypatch):
    monkeypatch.setattr(auth, "APP_JWT_SECRET", "test-only-secret")
    token = auth.create_access_token("teacher")
    assert auth.verify_access_token(token)["sub"] == "teacher"
    try:
        auth.verify_access_token(token[:-1] + ("A" if token[-1] != "A" else "B"))
        assert False, "tampered token must fail"
    except Exception as exc:
        assert getattr(exc, "status_code", None) == 401
