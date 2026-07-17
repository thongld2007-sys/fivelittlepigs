"""FastAPI server for the offline-first Adaptive Tutoring System."""

from __future__ import annotations

import gzip
import json
import math
import random
import urllib.error
import urllib.request
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from uuid import UUID, uuid4

from fastapi import FastAPI, HTTPException, Query, status
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

import backend.database as db
from backend.config import (
    BASE_DIR,
    CLOUD_SYNC_URL,
    DEVICE_ID,
    MAX_SYNC_BATCH,
    QUESTIONS_PATH,
    REPO_QUESTIONS_PATH,
    SYNC_TIMEOUT_SECONDS,
)
from backend.diagnostic_engine import BKTProcessor
from backend.knowledge_graph import KnowledgeGraph


def _load_questions() -> tuple[list[dict], dict[str, dict]]:
    questions: list[dict] = []
    for path in (QUESTIONS_PATH, REPO_QUESTIONS_PATH):
        if not path.is_file():
            continue
        with path.open("r", encoding="utf-8") as handle:
            source_questions = json.load(handle)
        for source in source_questions:
            option_values = source.get("options", [])
            options = [
                option.get("text", "") if isinstance(option, dict) else str(option)
                for option in option_values
            ]
            correct_index = source.get("correct_index")
            if correct_index is None:
                correct_key = source.get("correct_answer")
                correct_index = next(
                    (
                        index for index, option in enumerate(option_values)
                        if isinstance(option, dict) and option.get("key") == correct_key
                    ),
                    -1,
                )
            questions.append({
                "question_id": source.get("question_id") or source.get("id"),
                "skill_id": source.get("skill_id"),
                "content": source.get("content") or source.get("text"),
                "options": options,
                "correct_index": correct_index,
                "difficulty": source.get("difficulty_level", source.get("difficulty", 1)),
                "difficulty_label": (
                    source.get("difficulty") if isinstance(source.get("difficulty"), str) else None
                ),
                "hint": source.get("hint", ""),
                "distractor_explanations": source.get("distractor_explanations", {}),
            })
    required = {"question_id", "skill_id", "content", "options", "correct_index"}
    ids: set[str] = set()
    for question in questions:
        missing = required - question.keys()
        if missing:
            raise RuntimeError(f"Question is missing fields: {sorted(missing)}")
        if question["question_id"] in ids:
            raise RuntimeError(f"Duplicate question_id: {question['question_id']}")
        if not KnowledgeGraph.is_valid_skill(question["skill_id"]):
            raise RuntimeError(f"Question uses unknown skill: {question['skill_id']}")
        if not 0 <= question["correct_index"] < len(question["options"]):
            raise RuntimeError(f"Invalid correct_index: {question['question_id']}")
        ids.add(question["question_id"])
    return questions, {question["question_id"]: question for question in questions}


KnowledgeGraph.validate()
QUESTIONS_DB, QUESTIONS_BY_ID = _load_questions()


@asynccontextmanager
async def lifespan(_: FastAPI):
    db.init_db()
    yield


app = FastAPI(
    title="Adaptive Tutoring System API",
    version="1.0.0",
    description="Offline-first BKT diagnostic backend for GDPT 2018.",
    lifespan=lifespan,
)


class StudentCreate(BaseModel):
    student_id: str = Field(min_length=1, max_length=64, pattern=r"^[A-Za-z0-9_.-]+$")
    name: str = Field(min_length=1, max_length=120)
    grade: int = Field(ge=1, le=12)


class SubmitAnswer(BaseModel):
    question_id: str = Field(min_length=1, max_length=64)
    selected_index: int = Field(ge=0)
    time_spent: int = Field(ge=0, le=86400)
    event_id: UUID = Field(default_factory=uuid4)


def _require_student(student_id: str) -> dict:
    student = db.get_student(student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Không tìm thấy học sinh.")
    return student


@app.get("/api/health")
def health() -> dict:
    return {"status": "ok", "mode": "offline-first", "questions": len(QUESTIONS_DB)}


@app.get("/api/skills")
def list_skills() -> list[dict]:
    return KnowledgeGraph.all_skills()


@app.get("/api/knowledge-graph")
def get_knowledge_graph() -> dict[str, dict]:
    """Dictionary form used by the interactive frontend path visualizer."""
    return {
        skill["skill_id"]: {**skill, "subject": "Toán"}
        for skill in KnowledgeGraph.all_skills()
    }


@app.post("/api/students", status_code=status.HTTP_201_CREATED)
def create_student(student: StudentCreate) -> dict:
    return db.add_student(student.student_id, student.name.strip(), student.grade)


@app.get("/api/students")
def list_students() -> list[dict]:
    return db.list_students()


@app.get("/api/student/{student_id}/next-question")
def get_next_question(
    student_id: str,
    current_skill_id: str = Query(default="MATH7_ADD_RATIONAL", max_length=64),
) -> dict:
    _require_student(student_id)
    if not KnowledgeGraph.is_valid_skill(current_skill_id):
        raise HTTPException(status_code=422, detail="Mã kỹ năng không hợp lệ.")
    diagnostic = BKTProcessor.diagnose_next_step(student_id, current_skill_id)
    target_skill = diagnostic["target_skill"]
    if target_skill is None:
        return {"message": "Học sinh đã thành thạo kỹ năng này.", "diagnostic_status": diagnostic}
    available = [q for q in QUESTIONS_DB if q["skill_id"] == target_skill]
    if not available:
        raise HTTPException(status_code=404, detail="Không có câu hỏi cho kỹ năng mục tiêu.")
    question = random.SystemRandom().choice(available)
    public_question = {key: value for key, value in question.items() if key != "correct_index"}
    return {"diagnostic_status": diagnostic, "question": public_question}


@app.post("/api/student/{student_id}/submit")
def submit_answer(student_id: str, submission: SubmitAnswer) -> dict:
    _require_student(student_id)
    event_id = str(submission.event_id)
    replay = db.get_response_by_event(event_id)
    if replay:
        if replay["student_id"] != student_id:
            raise HTTPException(status_code=409, detail="event_id đã thuộc về học sinh khác.")
        question = QUESTIONS_BY_ID.get(replay["question_id"])
        mastery = db.get_student_mastery(student_id, question["skill_id"]) if question else None
        return {
            "message": "Yêu cầu đã được xử lý trước đó.",
            "event_id": event_id,
            "replayed": True,
            "is_correct": bool(replay["is_correct"]),
            "new_probability": round(mastery["current_probability"], 4) if mastery else None,
        }
    question = QUESTIONS_BY_ID.get(submission.question_id)
    if not question:
        raise HTTPException(status_code=404, detail="Không tìm thấy câu hỏi.")
    if submission.selected_index >= len(question["options"]):
        raise HTTPException(status_code=422, detail="Lựa chọn nằm ngoài danh sách đáp án.")
    is_correct = submission.selected_index == question["correct_index"]
    skill_id = question["skill_id"]
    update = BKTProcessor.evaluate_answer(student_id, skill_id, is_correct)
    diagnostic = BKTProcessor.diagnose_next_step(
        student_id, skill_id, probability=update.new_probability
    )
    _, created = db.record_answer(
        event_id=event_id,
        student_id=student_id,
        question_id=submission.question_id,
        selected_index=submission.selected_index,
        is_correct=is_correct,
        time_spent=submission.time_spent,
        skill_id=skill_id,
        previous_probability=update.previous_probability,
        new_probability=update.new_probability,
        consecutive_fails=update.consecutive_fails,
        action=diagnostic["action"],
        target_skill=diagnostic["target_skill"],
        reason=diagnostic["reason"],
    )
    return {
        "message": "Đã ghi nhận kết quả.",
        "event_id": event_id,
        "replayed": not created,
        "is_correct": is_correct,
        "skill_id": skill_id,
        "previous_probability": round(update.previous_probability, 4),
        "new_probability": round(update.new_probability, 4),
        "consecutive_fails": update.consecutive_fails,
        "diagnostic": diagnostic,
    }


@app.get("/api/teacher/students/{student_id}/reasoning-tree")
def get_reasoning_tree(student_id: str, limit: int = Query(default=100, ge=1, le=500)) -> dict:
    _require_student(student_id)
    return {"student_id": student_id, "events": db.get_reasoning_tree(student_id, limit)}


def _mastery_rows() -> list:
    with db.get_db_connection() as conn:
        return conn.execute(
            """SELECT m.student_id, s.name, m.skill_id, m.current_probability,
                      m.consecutive_fails, m.last_updated
               FROM Student_Mastery m JOIN Students s ON s.student_id=m.student_id"""
        ).fetchall()


@app.get("/api/teacher/priority-list")
def get_priority_list(limit: int = Query(default=3, ge=1, le=40)) -> list[dict]:
    now = datetime.now(timezone.utc)
    result = []
    for row in _mastery_rows():
        probability = row["current_probability"]
        if probability >= BKTProcessor.THRESHOLD_MASTERED:
            continue
        try:
            updated = datetime.fromisoformat(row["last_updated"]).replace(tzinfo=timezone.utc)
            stuck_minutes = max((now - updated).total_seconds() / 60, 0)
        except (TypeError, ValueError):
            stuck_minutes = 0
        score = ((1 - probability) * (1 + row["consecutive_fails"])
                 * math.log(stuck_minutes + 2))
        result.append({
            "student_id": row["student_id"], "student_name": row["name"],
            "skill_id": row["skill_id"], "current_probability": round(probability, 4),
            "consecutive_fails": row["consecutive_fails"],
            "t_stuck_minutes": round(stuck_minutes, 1), "priority_score": round(score, 4),
        })
    return sorted(result, key=lambda item: item["priority_score"], reverse=True)[:limit]


def _weak_groups() -> tuple[int, list[dict]]:
    with db.get_db_connection() as conn:
        total = conn.execute("SELECT COUNT(*) AS total FROM Students").fetchone()["total"]
        rows = conn.execute(
            """SELECT m.skill_id, COUNT(*) AS weak_count,
                      GROUP_CONCAT(m.student_id) AS student_ids
               FROM Student_Mastery m WHERE m.current_probability < 0.50
               GROUP BY m.skill_id ORDER BY weak_count DESC, m.skill_id"""
        ).fetchall()
    groups = [{
        "skill_id": row["skill_id"],
        "skill_name": KnowledgeGraph.get_skill_info(row["skill_id"])["name"],
        "weak_students": row["weak_count"],
        "student_ids": row["student_ids"].split(",") if row["student_ids"] else [],
        "percentage": round(row["weak_count"] / total * 100, 1) if total else 0,
    } for row in rows]
    return total, groups


@app.get("/api/teacher/groups")
def get_student_groups() -> dict:
    total, groups = _weak_groups()
    return {"total_students": total, "groups": groups}


@app.get("/api/teacher/gap-alerts")
def get_gap_alerts() -> dict:
    total, groups = _weak_groups()
    alerts = [{**group, "message": (
        f"Cần giảng lại {group['skill_name']}: {group['weak_students']}/{total} "
        f"học sinh ({group['percentage']:.1f}%) đang dưới mức 0.50."
    )} for group in groups if group["percentage"] >= 20]
    return {"total_students": total, "alerts": alerts}


@app.get("/api/teacher/dashboard")
def get_teacher_dashboard() -> dict:
    """Aggregated payload optimized for the teacher dashboard frontend."""
    total, weak_groups = _weak_groups()
    students = {student["student_id"]: student for student in db.list_students()}
    groups = []
    for group in weak_groups:
        member_names = [
            students.get(student_id, {}).get("name", student_id)
            for student_id in group["student_ids"]
        ]
        groups.append({
            "title": f"Nhóm hổng: {group['skill_name']}",
            "skill_id": group["skill_id"],
            "count": group["weak_students"],
            "members": member_names[:5] + (
                [f"+{len(member_names) - 5} học sinh khác"] if len(member_names) > 5 else []
            ),
            "percentage": group["percentage"],
        })
    priority = [{
        "id": item["student_id"],
        "name": item["student_name"],
        "current_skill": (
            KnowledgeGraph.get_skill_info(item["skill_id"])["name"]
            if KnowledgeGraph.get_skill_info(item["skill_id"]) else item["skill_id"]
        ),
        "n_failed": item["consecutive_fails"],
        "t_stuck": item["t_stuck_minutes"],
        "mastery": item["current_probability"],
        "priority_score": item["priority_score"],
    } for item in get_priority_list(limit=40)]
    with db.get_db_connection() as conn:
        average = conn.execute(
            "SELECT COALESCE(AVG(current_probability), 0.5) FROM Student_Mastery"
        ).fetchone()[0]
    alert_group = next((group for group in weak_groups if group["percentage"] >= 20), None)
    return {
        "metrics": {
            "total_students": total,
            "average_mastery": f"{round(average * 100)}%",
            "gap_groups_count": f"{len(groups)} nhóm",
            "re_teach_alert": alert_group["skill_name"] if alert_group else None,
        },
        "groups": groups,
        "priority_list": priority,
    }


@app.get("/api/sync/status")
def sync_status() -> dict:
    queued = db.get_unsynced_responses(MAX_SYNC_BATCH)
    return {"device_id": DEVICE_ID, "cloud_configured": bool(CLOUD_SYNC_URL), "queued": len(queued)}


@app.post("/api/sync/push")
def push_sync_logs() -> dict:
    logs = db.get_unsynced_responses(MAX_SYNC_BATCH)
    if not logs:
        return {"message": "Không có dữ liệu mới để đồng bộ.", "synced_count": 0}
    if not CLOUD_SYNC_URL:
        raise HTTPException(status_code=503, detail="Chưa cấu hình TUTOR_CLOUD_SYNC_URL; dữ liệu vẫn an toàn trong hàng đợi.")
    payload = {
        "device_id": DEVICE_ID,
        "sync_timestamp": datetime.now(timezone.utc).isoformat(),
        "logs": logs,
    }
    compressed = gzip.compress(json.dumps(payload, ensure_ascii=False).encode("utf-8"))
    request = urllib.request.Request(
        CLOUD_SYNC_URL, data=compressed, method="POST",
        headers={"Content-Type": "application/json", "Content-Encoding": "gzip"},
    )
    try:
        with urllib.request.urlopen(request, timeout=SYNC_TIMEOUT_SECONDS) as response:
            if not 200 <= response.status < 300:
                raise HTTPException(status_code=502, detail=f"Cloud trả về HTTP {response.status}.")
    except (urllib.error.URLError, TimeoutError) as exc:
        raise HTTPException(status_code=503, detail=f"Không thể kết nối Cloud Hub: {exc}") from exc
    count = db.mark_responses_as_synced([log["event_id"] for log in logs])
    return {"message": "Đồng bộ thành công.", "synced_count": count, "compressed_bytes": len(compressed)}


FRONTEND_DIR = BASE_DIR / "frontend"
if FRONTEND_DIR.is_dir():
    app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")
