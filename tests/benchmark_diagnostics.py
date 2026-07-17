"""Small judge-facing benchmark for the adaptive diagnostic flow.

Run:
    python3 tests/benchmark_diagnostics.py

This is not a replacement for a real school pilot. It creates temporary
students, simulates known answer patterns, and prints metrics that can be used
in the hackathon pitch as an initial engineering benchmark.
"""

from __future__ import annotations

import json
import sqlite3
import statistics
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

import sys

sys.path.append(str(ROOT))

from backend.app import AnswerSubmission, SurveySessionRequest, create_survey_session, get_next_question, submit_answer
from backend.config import Config


BASE_SCENARIOS = [
    {
        "student_id": "bench_gap_fraction",
        "grade": 7,
        "start_skill": "MATH_G7",
        "answers": [("q_math_g7_1", "B"), ("q_math_g7_2", "B"), ("q_math_g7_3", "B")],
        "expected_gap": "MATH_G7",
    },
    {
        "student_id": "bench_gap_integer",
        "grade": 6,
        "start_skill": "MATH_G6",
        "answers": [("q_math_g6_1", "A"), ("q_math_g6_2", "A"), ("q_math_g6_3", "A")],
        "expected_gap": "MATH_G6",
    },
    {
        "student_id": "bench_strong_math7",
        "grade": 7,
        "start_skill": "MATH_G7",
        "answers": [("q_math_g7_1", "A"), ("q_math_g7_2", "D"), ("q_math_g7_3", "D")],
        "expected_gap": None,
    },
]


def build_scenarios(repeats: int = 10) -> list[dict]:
    """Create a 30-case deterministic smoke benchmark from three labeled patterns."""
    scenarios = []
    for repeat_index in range(repeats):
        for base in BASE_SCENARIOS:
            scenario = dict(base)
            scenario["student_id"] = f"{base['student_id']}_{repeat_index + 1:02d}"
            scenarios.append(scenario)
    return scenarios


def cleanup_students(student_ids: list[str]) -> None:
    """Remove temporary benchmark students and their response logs."""
    conn = sqlite3.connect(Config.DB_PATH)
    try:
        placeholders = ",".join("?" for _ in student_ids)
        conn.execute(f"DELETE FROM responses WHERE student_id IN ({placeholders})", student_ids)
        conn.execute(f"DELETE FROM student_mastery WHERE student_id IN ({placeholders})", student_ids)
        conn.execute(f"DELETE FROM students WHERE id IN ({placeholders})", student_ids)
        conn.commit()
    finally:
        conn.close()


def run_scenario(scenario: dict) -> dict:
    """Run a labeled diagnostic scenario and return predicted gap metadata."""
    create_survey_session(
        SurveySessionRequest(
            student_id=scenario["student_id"],
            name=f"Benchmark {scenario['student_id']}",
            grade=scenario["grade"],
        )
    )

    submit_latencies = []
    correctness = []
    for question_id, selected_option in scenario["answers"]:
        started = time.perf_counter()
        result = submit_answer(
            scenario["student_id"],
            AnswerSubmission(question_id=question_id, selected_option=selected_option),
        )
        submit_latencies.append((time.perf_counter() - started) * 1000)
        correctness.append(bool(result["is_correct"]))

    started = time.perf_counter()
    next_payload = get_next_question(scenario["student_id"], current_skill=scenario["start_skill"])
    next_latency = (time.perf_counter() - started) * 1000

    predicted_gap = next_payload.get("active_skill")
    if all(correctness):
        predicted_gap = None

    return {
        "student_id": scenario["student_id"],
        "expected_gap": scenario["expected_gap"],
        "predicted_gap": predicted_gap,
        "submit_latency_ms": submit_latencies,
        "next_question_latency_ms": next_latency,
    }


def compute_metrics(rows: list[dict]) -> dict:
    """Compute accuracy, precision, recall, and latency summaries."""
    correct = sum(row["expected_gap"] == row["predicted_gap"] for row in rows)
    true_positive = sum(bool(row["expected_gap"]) and bool(row["predicted_gap"]) for row in rows)
    false_positive = sum((not row["expected_gap"]) and bool(row["predicted_gap"]) for row in rows)
    false_negative = sum(bool(row["expected_gap"]) and (not row["predicted_gap"]) for row in rows)

    submit_latencies = [latency for row in rows for latency in row["submit_latency_ms"]]
    next_latencies = [row["next_question_latency_ms"] for row in rows]

    precision = true_positive / (true_positive + false_positive) if true_positive + false_positive else 1.0
    recall = true_positive / (true_positive + false_negative) if true_positive + false_negative else 1.0
    submit_p95 = statistics.quantiles(submit_latencies, n=20, method="inclusive")[18]
    next_p95 = statistics.quantiles(next_latencies, n=20, method="inclusive")[18]

    return {
        "diagnostic_accuracy": round(correct / len(rows), 4),
        "gap_alert_precision": round(precision, 4),
        "gap_alert_recall": round(recall, 4),
        "submit_latency_ms_avg": round(statistics.mean(submit_latencies), 2),
        "submit_latency_ms_p95": round(submit_p95, 2),
        "next_question_latency_ms_avg": round(statistics.mean(next_latencies), 2),
        "next_question_latency_ms_p95": round(next_p95, 2),
        "sample_size": len(rows),
    }


def main() -> None:
    scenarios = build_scenarios()
    student_ids = [scenario["student_id"] for scenario in scenarios]
    cleanup_students(student_ids)
    try:
        rows = [run_scenario(scenario) for scenario in scenarios]
        print(json.dumps({"metrics": compute_metrics(rows), "cases": rows}, ensure_ascii=False, indent=2))
    finally:
        cleanup_students(student_ids)


if __name__ == "__main__":
    main()
