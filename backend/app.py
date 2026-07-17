from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import time
import os
import json
import sqlite3
import re

from backend.config import Config
from backend.database import (
    init_db, get_student, get_student_mastery, record_response,
    get_consecutive_failed_count, get_stuck_time_minutes, get_db_connection,
    add_student, list_students
)
from backend.diagnostic_engine import update_student_skill, get_next_recommended_skill, get_next_question_difficulty_and_skill
from backend.fpt_ai import FPTAIError, fpt_ai_client
from backend.knowledge_graph import KNOWLEDGE_GRAPH

app = FastAPI(title="VGap AI - Adaptive Tutoring Backend")

# Initialize database
init_db()


def build_distractor_explanations(question):
    """Create concise, grounded feedback for every wrong multiple-choice option."""
    correct_key = question["correct_answer"]
    correct_option = next((opt for opt in question["options"] if opt["key"] == correct_key), None)
    correct_text = correct_option["text"] if correct_option else correct_key
    hint = question.get("hint", "Hãy xem lại kiến thức nền của câu hỏi này.")

    explanations = {}
    for opt in question["options"]:
        if opt["key"] == correct_key:
            continue
        explanations[opt["key"]] = (
            f"Đáp án {opt['key']} chưa đúng. Gợi ý trọng tâm: {hint} "
            f"Kết quả đúng là {correct_key}: {correct_text}."
        )
    return explanations

def get_correct_option_text(question):
    correct_key = question.get("correct_answer")
    correct_option = next((opt for opt in question.get("options", []) if opt.get("key") == correct_key), None)
    return correct_option.get("text", "") if correct_option else ""

def is_short_answer_compatible(question):
    """Short-answer mode only accepts numbers, fractions, equations, or comparison symbols."""
    answer = get_correct_option_text(question).strip()
    if not answer:
        return False

    compact = answer.replace(" ", "")
    if re.match(r"^[<>=≤≥≠]+$", compact):
        return True

    blocked_words = ["hoặc", "và", "ngày", "mét", "tế bào", "hình", "ngón", "bác", "phím", ","]
    lower_answer = answer.lower()
    if any(word in lower_answer for word in blocked_words):
        return False

    numeric_tokens = re.findall(r"-?\d+(?:[.,]\d+)?(?:/\d+(?:[.,]\d+)?)?", compact)
    if len(numeric_tokens) != 1:
        return False

    return bool(re.match(r"^-?\d+(?:[.,]\d+)?(?:/\d+(?:[.,]\d+)?)?%?$", compact))

@app.get("/api/knowledge-graph")
def get_knowledge_graph():
    return KNOWLEDGE_GRAPH

# Request schemas
class AnswerSubmission(BaseModel):
    question_id: str
    selected_option: str

class CheckAnswerRequest(BaseModel):
    question_id: str
    selected_option: str
    student_id: str = "emma_std_01"

class StudentCreate(BaseModel):
    student_id: str
    name: str
    grade: int

class SurveySessionRequest(BaseModel):
    student_id: str
    name: str = "Học sinh khảo sát"
    grade: int = 7

class AITutorRequest(BaseModel):
    question_id: str
    message: str

class AILessonPlanRequest(BaseModel):
    skill_id: str
    group_context: str = ""

# Endpoints
@app.get("/api/students")
def get_students():
    return list_students()

@app.get("/api/ai/status")
def ai_status():
    return {
        "provider": "FPT AI Factory",
        "configured": fpt_ai_client.configured,
        "model": fpt_ai_client.model or None,
        "fallback": "offline"
    }

@app.post("/api/ai/student/{student_id}/tutor")
def ai_tutor(student_id: str, payload: AITutorRequest):
    if not get_student(student_id):
        raise HTTPException(status_code=404, detail="Student not found")
    if len(payload.message.strip()) == 0 or len(payload.message) > 1000:
        raise HTTPException(status_code=422, detail="Message must contain 1-1000 characters")

    with open(Config.QUESTIONS_JSON_PATH, "r", encoding="utf-8") as file:
        questions = json.load(file)
    question = next((item for item in questions if item["id"] == payload.question_id), None)
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")

    skill = KNOWLEDGE_GRAPH.get(question["skill_id"], {})
    mastery = get_student_mastery(student_id, question["skill_id"])
    correct_key = question.get("correct_answer")
    correct_option = next(
        (option.get("text", "") for option in question.get("options", []) if option.get("key") == correct_key),
        correct_key or ""
    )
    system_prompt = (
        "Bạn là gia sư Socratic an toàn cho học sinh phổ thông Việt Nam. "
        "Chỉ dùng dữ kiện trong ngữ cảnh, hướng dẫn ngắn gọn từng bước và ưu tiên một câu hỏi gợi mở. "
        "Không tiết lộ trực tiếp đáp án cuối cùng và không làm hộ toàn bộ bài. "
        f"Kỹ năng: {skill.get('name', question['skill_id'])}. "
        f"Mức thành thạo hiện tại: {mastery:.2f}. "
        f"Câu hỏi: {question.get('text', '')}. Các lựa chọn: {question.get('options', [])}. "
        f"Đáp án nội bộ, không tiết lộ trực tiếp: {correct_option}."
    )
    try:
        result = fpt_ai_client.complete(system_prompt=system_prompt, user_prompt=payload.message.strip())
    except FPTAIError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    return {"provider": "FPT AI Factory", "model": result.model, "content": result.content, "usage": result.usage}

@app.post("/api/ai/teacher/lesson-plan")
def ai_lesson_plan(payload: AILessonPlanRequest):
    skill = KNOWLEDGE_GRAPH.get(payload.skill_id)
    if not skill:
        raise HTTPException(status_code=422, detail="Invalid skill ID")
    prerequisite_names = [
        KNOWLEDGE_GRAPH[item]["name"]
        for item in skill.get("prerequisites", [])
        if item in KNOWLEDGE_GRAPH
    ]
    system_prompt = (
        "Bạn là trợ lý thiết kế bài giảng theo GDPT 2018 cho giáo viên Việt Nam. "
        "Trả về văn bản thuần ngắn gọn với đúng 4 mục: Mục tiêu, Khởi động, Hoạt động chính, Đánh giá nhanh. "
        "Không dùng HTML và không bịa nguồn hay chuẩn chương trình."
    )
    user_prompt = (
        f"Kỹ năng: {skill['name']}; lớp {skill['grade']}; môn {skill.get('subject', 'Toán')}; "
        f"tiên quyết: {prerequisite_names or ['Không có']}. "
        f"Bối cảnh nhóm: {payload.group_context.strip() or 'Học sinh đang dưới ngưỡng thành thạo 0.50.'}"
    )
    try:
        result = fpt_ai_client.complete(system_prompt=system_prompt, user_prompt=user_prompt)
    except FPTAIError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    return {"provider": "FPT AI Factory", "model": result.model, "content": result.content, "usage": result.usage}

@app.post("/api/students")
def create_student(payload: StudentCreate):
    if not (1 <= payload.grade <= 12):
        raise HTTPException(status_code=422, detail="Grade must be between 1 and 12")
    return add_student(payload.student_id, payload.name.strip() or payload.student_id, payload.grade)

@app.post("/api/student/session")
def create_survey_session(payload: SurveySessionRequest):
    """Create a clean student profile for one adaptive survey attempt."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT OR REPLACE INTO students (id, name, grade) VALUES (?, ?, ?)",
        (payload.student_id, payload.name, payload.grade)
    )

    for skill_id in KNOWLEDGE_GRAPH.keys():
        cursor.execute("""
            INSERT OR REPLACE INTO student_mastery (student_id, skill_id, mastery_probability)
            VALUES (?, ?, ?)
        """, (payload.student_id, skill_id, 0.5))

    cursor.execute("DELETE FROM responses WHERE student_id = ?", (payload.student_id,))
    conn.commit()
    conn.close()

    return {
        "student_id": payload.student_id,
        "grade": payload.grade,
        "status": "ready"
    }

@app.get("/api/student/{student_id}/next-question")
def get_next_question(student_id: str, current_skill: str = "MATH_G7", answer_format: str = "choice"):
    student = get_student(student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
        
    # Get adaptive skill and difficulty recommended
    recommended_skill, target_difficulty = get_next_question_difficulty_and_skill(student_id, current_skill)
    
    # Load questions from JSON
    if not os.path.exists(Config.QUESTIONS_JSON_PATH):
        raise HTTPException(status_code=500, detail="Question bank missing")
        
    with open(Config.QUESTIONS_JSON_PATH, "r", encoding="utf-8") as f:
        questions = json.load(f)
        
    def filter_by_answer_format(candidates):
        if answer_format != "short":
            return candidates
        return [q for q in candidates if is_short_answer_compatible(q)]

    # Filter questions for this skill and difficulty
    skill_questions = filter_by_answer_format([
        q for q in questions 
        if q["skill_id"] == recommended_skill and q.get("difficulty_level", 2) == target_difficulty
    ])
    
    if not skill_questions:
        # Fallback to any question for this skill
        skill_questions = filter_by_answer_format([q for q in questions if q["skill_id"] == recommended_skill])

    if not skill_questions and answer_format == "short":
        skill_info = KNOWLEDGE_GRAPH.get(recommended_skill, {})
        same_grade_skill_ids = {
            skill_id for skill_id, info in KNOWLEDGE_GRAPH.items()
            if info.get("subject") == skill_info.get("subject") and info.get("grade") == skill_info.get("grade")
        }
        skill_questions = [
            q for q in questions
            if q["skill_id"] in same_grade_skill_ids and is_short_answer_compatible(q)
        ]
        
    if not skill_questions:
        # Fallback to absolute value
        skill_questions = filter_by_answer_format([q for q in questions if q["skill_id"] == "MATH_G4"]) or [q for q in questions if q["skill_id"] == "MATH_G4"]

    # Avoid serving a question the student has already answered for this skill
    # until all candidates at the chosen level have been exhausted.
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT question_id FROM responses
        WHERE student_id = ? AND skill_id = ?
        ORDER BY id DESC
    """, (student_id, recommended_skill))
    answered_ids = {row[0] for row in cursor.fetchall()}
    conn.close()

    fresh_questions = [q for q in skill_questions if q["id"] not in answered_ids]
    if fresh_questions:
        skill_questions = fresh_questions
        
    # Pick a random question from matching ones to make it dynamic
    import random
    question = random.choice(skill_questions)
    distractor_explanations = build_distractor_explanations(question)
    
    return {
        "question": {
            "id": question["id"],
            "skill_id": question["skill_id"],
            "skill_name": KNOWLEDGE_GRAPH.get(question["skill_id"], {}).get("name", "Môn học"),
            "difficulty_level": question.get("difficulty_level", 2),
            "difficulty": question.get("difficulty", "Vừa"),
            "text": question["text"],
            "options": question["options"],
            "hint": question.get("hint", ""),
            "visual_hint": question.get("visual_hint", question["skill_id"]),
            "distractor_explanations": distractor_explanations
        },
        "active_skill": recommended_skill,
        "target_difficulty": target_difficulty
    }

@app.post("/api/student/{student_id}/submit")
def submit_answer(student_id: str, submission: AnswerSubmission):
    student = get_student(student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
        
    # Load questions
    with open(Config.QUESTIONS_JSON_PATH, "r", encoding="utf-8") as f:
        questions = json.load(f)
        
    question = next((q for q in questions if q["id"] == submission.question_id), None)
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
        
    is_correct = (submission.selected_option == question["correct_answer"])
    distractor_explanations = build_distractor_explanations(question)
    
    # Record response in DB (with difficulty_level)
    record_response(
        student_id, 
        question["id"], 
        question["skill_id"], 
        question.get("difficulty_level", 2), 
        is_correct, 
        int(time.time())
    )
    
    # Run BKT Bayesian Update
    new_mastery = update_student_skill(student_id, question["skill_id"], is_correct)
    
    # Get next recommended skill path and difficulty
    next_skill, next_diff = get_next_question_difficulty_and_skill(student_id, question["skill_id"])
    
    return {
        "is_correct": is_correct,
        "correct_answer": question["correct_answer"],
        "distractor_explanation": None if is_correct else distractor_explanations.get(submission.selected_option),
        "hint": question.get("hint", ""),
        "new_mastery_probability": new_mastery,
        "next_recommended_skill": next_skill,
        "next_recommended_difficulty": next_diff
    }

@app.post("/api/check-answer")
def check_answer(submission: CheckAnswerRequest):
    """Compatibility endpoint for frontend modules that submit answers globally."""
    if not get_student(submission.student_id):
        add_student(submission.student_id, "Học sinh demo", 7)
    return submit_answer(
        submission.student_id,
        AnswerSubmission(
            question_id=submission.question_id,
            selected_option=submission.selected_option
        )
    )

@app.get("/api/teacher/dashboard")
def get_teacher_dashboard():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 1. Total students count
    cursor.execute("SELECT COUNT(*) FROM students")
    total_students = cursor.fetchone()[0]
    
    # 2. Overall mastery rate (average of all active skills probability)
    cursor.execute("SELECT AVG(mastery_probability) FROM student_mastery")
    avg_mastery = cursor.fetchone()[0] or 0.5
    
    # 3. Auto-Grouping students by knowledge gap (probability < 0.50)
    groups = {}
    for skill_id, skill_info in KNOWLEDGE_GRAPH.items():
        cursor.execute("""
            SELECT s.name FROM student_mastery m
            JOIN students s ON m.student_id = s.id
            WHERE m.skill_id = ? AND m.mastery_probability < 0.50
        """, (skill_id,))
        members = [row[0] for row in cursor.fetchall()]
        
        if members:
            groups[skill_id] = {
                "title": f"Nhóm hổng: {skill_info['name']}",
                "skill_id": skill_id,
                "count": len(members),
                "members": members[:5] + ([f"+{len(members)-5} học sinh khác"] if len(members) > 5 else [])
            }
            
    # Convert groups dict to list
    groups_list = list(groups.values())

    class_progress = []
    for skill_id, skill_info in KNOWLEDGE_GRAPH.items():
        cursor.execute("""
            SELECT AVG(mastery_probability) FROM student_mastery
            WHERE skill_id = ?
        """, (skill_id,))
        mastery_ratio = cursor.fetchone()[0]
        if mastery_ratio is None:
            continue
        class_progress.append({
            "skill_id": skill_id,
            "label": skill_info["name"],
            "percent": max(0, min(100, int(round(mastery_ratio * 100))))
        })
    class_progress = sorted(class_progress, key=lambda item: item["skill_id"])[:8]
    
    # Check if a class-wide re-teach is required (> 20% of class in gap)
    reteach_recommendation = None
    if total_students > 0:
        for skill_id, group_info in groups.items():
            if (group_info["count"] / total_students) >= 0.20:
                reteach_recommendation = KNOWLEDGE_GRAPH[skill_id]["name"]
                break
                
    # 4. Priority List calculations
    cursor.execute("SELECT id, name FROM students")
    students = cursor.fetchall()
    
    priority_list = []
    for std_id, std_name in students:
        # Get active skill for this student (look up last response, default to MATH_G7)
        cursor.execute("SELECT skill_id FROM responses WHERE student_id = ? ORDER BY id DESC LIMIT 1", (std_id,))
        active_row = cursor.fetchone()
        active_skill = active_row[0] if (active_row and active_row[0] in KNOWLEDGE_GRAPH) else "MATH_G7"
        
        mastery = get_student_mastery(std_id, active_skill)
        n_failed = get_consecutive_failed_count(std_id, active_skill)
        t_stuck = get_stuck_time_minutes(std_id, active_skill)
        
        # Priority Score formula: PS = (1.0 - mastery) * (1.0 + n_failed) * ln(t_stuck + 2)
        import math
        ps_score = (1.0 - mastery) * (1.0 + n_failed) * math.log(t_stuck + 2)
        
        priority_list.append({
            "id": std_id,
            "name": std_name,
            "current_skill": KNOWLEDGE_GRAPH[active_skill]["name"],
            "n_failed": n_failed,
            "t_stuck": t_stuck,
            "mastery": round(mastery, 2),
            "priority_score": round(ps_score, 2)
        })
        
    # Sort priority descending
    priority_list.sort(key=lambda x: x["priority_score"], reverse=True)
    
    conn.close()
    
    return {
        "metrics": {
            "total_students": total_students,
            "average_mastery": f"{int(avg_mastery * 100)}%",
            "gap_groups_count": f"{len(groups_list)} nhóm",
            "re_teach_alert": reteach_recommendation
        },
        "groups": groups_list,
        "priority_list": priority_list,
        "class_progress": class_progress
    }

# Serve Frontend static assets
frontend_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "frontend")
app.mount("/", StaticFiles(directory=frontend_dir, html=True), name="frontend")
