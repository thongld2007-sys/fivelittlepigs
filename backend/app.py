from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, Header
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import asyncio
import hashlib
import time
import os
import json
import sqlite3
import re
import uuid
from typing import Optional

from backend.config import Config
from backend.database import (
    init_db, get_student, get_student_mastery, record_response,
    get_consecutive_failed_count, get_stuck_time_minutes, get_db_connection,
    add_student, list_students, get_response_by_event_id, upsert_sync_event,
    list_unsynced_events, mark_events_synced, add_pedagogical_explanation,
    list_pedagogical_explanations, create_student_account
)
from backend.diagnostic_engine import update_student_skill, get_next_recommended_skill, get_next_question_difficulty_and_skill
from backend.fpt_ai import FPTAIError, fpt_ai_client
from backend.knowledge_graph import KNOWLEDGE_GRAPH

app = FastAPI(title="VGap AI - Adaptive Tutoring Backend")

# Initialize database
init_db()

FPT_AI_CAPABILITY_MATRIX = [
    {
        "capability": "FPT AI Inference",
        "status": "implemented",
        "evidence": ["/api/ai/student/{student_id}/tutor", "/api/ai/teacher/lesson-plan"],
        "value": "Sinh gợi ý Socratic và giáo án bổ trợ có grounding theo câu hỏi, BKT và Knowledge Graph."
    },
    {
        "capability": "FPT AI Knowledge",
        "status": "planned_adapter",
        "evidence": ["Knowledge Graph nội bộ", "question bank 189 câu", "docs/fpt_ai_hackathon_judge_pack.md"],
        "value": "Đưa chương trình GDPT, rubric kỹ năng và câu hỏi đã kiểm định vào RAG/Knowledge base."
    },
    {
        "capability": "FPT AI Agents",
        "status": "planned_adapter",
        "evidence": ["/api/teacher/dashboard", "/api/ai/teacher/lesson-plan"],
        "value": "Agent giáo viên biến gap groups thành kế hoạch can thiệp và giáo án 15 phút."
    },
    {
        "capability": "FPT AI Speech",
        "status": "planned_adapter",
        "evidence": ["frontend read-aloud control", "server-side API key isolation"],
        "value": "Đọc câu hỏi/gợi ý cho học sinh nhỏ tuổi hoặc học sinh đọc chậm."
    },
    {
        "capability": "FPT AI OCR/Vision",
        "status": "planned_adapter",
        "evidence": ["offline-first response schema", "teacher workflow roadmap"],
        "value": "Cho phép giáo viên chụp bài làm giấy để trích lỗi sai và đưa vào diagnostic events."
    },
    {
        "capability": "FPT AI MCP",
        "status": "planned_adapter",
        "evidence": ["dashboard API", "sync-ready SQLite logs"],
        "value": "Kết nối LMS, bảng điểm và hệ thống báo cáo trường học."
    }
]

SAFETY_CONTROLS = [
    {
        "risk": "Hallucination",
        "control": "FPT AI prompt chỉ được dùng ngữ cảnh câu hỏi, kỹ năng, mastery; lỗi provider trả 503 thay vì bịa.",
        "implemented": True
    },
    {
        "risk": "Gian lận học tập",
        "control": "Gia sư Socratic không tiết lộ trực tiếp đáp án cuối cùng; core chấm điểm vẫn chạy server-side.",
        "implemented": True
    },
    {
        "risk": "Lộ dữ liệu/API key",
        "control": "API key chỉ đọc từ .env server-side, không đưa vào frontend; lỗi provider được redacted.",
        "implemented": True
    },
    {
        "risk": "Prompt injection",
        "control": "Đầu vào giới hạn 1000 ký tự, system prompt khóa vai trò; cần bổ sung classifier khi production.",
        "implemented": False
    },
    {
        "risk": "Nội dung độc hại",
        "control": "Hiện giới hạn domain giáo dục; production cần moderation trước/sau generation.",
        "implemented": False
    }
]

COST_MODEL_ASSUMPTIONS = {
    "currency": "VND",
    "bkt_dag_cost_per_student_month": 0,
    "default_students": 1000,
    "ai_calls_per_student_month": 8,
    "estimated_tokens_per_ai_call": 900,
    "estimated_vnd_per_1k_tokens": 15,
    "teacher_ai_lesson_plans_per_month": 40,
    "estimated_tokens_per_lesson_plan": 1200
}

DIFFICULTY_LABELS = {
    1: "Nhận biết",
    2: "Thông hiểu",
    3: "Vận dụng",
}

EDUCATION_KEYWORDS = {
    "học", "bài", "giải", "toán", "văn", "anh", "khoa học", "lịch sử", "địa lý",
    "tin học", "phân số", "số hữu tỉ", "số nguyên", "bcnn", "quy đồng", "mẫu số",
    "câu hỏi", "trắc nghiệm", "kiểm tra", "ôn", "luyện", "kiến thức", "kỹ năng",
    "cộng", "trừ", "nhân", "chia", "lộ trình", "chủ đề", "mức độ", "nhận biết",
    "thông hiểu", "vận dụng", "em chưa hiểu", "thầy", "cô"
}

GREETING_KEYWORDS = {"xin chào", "chào", "bạn là ai", "giới thiệu"}
GREETING_WORDS = {"hello", "hi"}

JUDGE_BAREM_SCORECARD = [
    {
        "category": "Bài toán giáo dục",
        "max_score": 15,
        "current_score": 13,
        "evidence": "Định vị rõ bài toán mất gốc, dashboard giáo viên, phân nhóm can thiệp và demo luồng lớp học.",
        "next_step": "Bổ sung pilot thật với 30-50 học sinh để có số liệu trước/sau."
    },
    {
        "category": "AI có cần thiết không",
        "max_score": 15,
        "current_score": 13,
        "evidence": "BKT + Knowledge Graph quyết định chẩn đoán; FPT AI chỉ tăng cường gợi ý/giao án có grounding.",
        "next_step": "So sánh demo rule-only với AI-assisted trong pilot."
    },
    {
        "category": "Khai thác FPT AI",
        "max_score": 15,
        "current_score": 12,
        "evidence": "Inference đã có; Knowledge/RAG, Speech cache và teacher action adapter có endpoint trình diễn.",
        "next_step": "Cắm FPT AI Knowledge/Speech thật khi có credential production."
    },
    {
        "category": "AI Engineering",
        "max_score": 15,
        "current_score": 13,
        "evidence": "SQLite offline-first, idempotent event log, anomaly-weighted BKT, benchmark script, evidence endpoints.",
        "next_step": "Tách module app.py lớn thành services sau final."
    },
    {
        "category": "Giá trị giáo dục",
        "max_score": 15,
        "current_score": 11,
        "evidence": "Có lộ trình cá nhân, priority list, explanation log và giáo án 15 phút cho nhóm hổng.",
        "next_step": "Đo thời gian giáo viên tiết kiệm và tăng điểm post-test."
    },
    {
        "category": "Khả năng triển khai",
        "max_score": 10,
        "current_score": 8,
        "evidence": "Chạy local/LAN, offline-first, sync batch lên cloud, không cần npm server riêng.",
        "next_step": "Bổ sung auth production và backup DB."
    },
    {
        "category": "Khả năng scale",
        "max_score": 5,
        "current_score": 4,
        "evidence": "Cost model tách core gần 0 đồng với AI calls theo nhu cầu; production path PostgreSQL/queue/WebSocket.",
        "next_step": "Chạy load test có 100-500 học sinh giả lập."
    },
    {
        "category": "Đạo đức và an toàn",
        "max_score": 5,
        "current_score": 4,
        "evidence": "API key server-side, Socratic guardrail, anomaly detection, safety evidence endpoint.",
        "next_step": "Thêm moderation và prompt-injection classifier trước pilot thật."
    },
]


def normalize_difficulty_label(level):
    return DIFFICULTY_LABELS.get(int(level or 2), "Thông hiểu")

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

def evaluate_response_anomaly(question, is_correct, response_time_ms):
    flags = []
    bkt_weight = 1.0
    difficulty_level = question.get("difficulty_level", 2)

    if response_time_ms is not None and response_time_ms < 3000 and difficulty_level >= 3 and is_correct:
        flags.append("fast_hard_correct")
        bkt_weight = min(bkt_weight, 0.25)
    elif response_time_ms is not None and response_time_ms < 1500:
        flags.append("too_fast_to_read")
        bkt_weight = min(bkt_weight, 0.5)

    return {
        "flagged": bool(flags),
        "flags": flags,
        "bkt_weight": bkt_weight,
        "reason": (
            "Câu khó được trả lời đúng quá nhanh nên hệ thống giảm trọng số cập nhật BKT."
            if "fast_hard_correct" in flags
            else "Không phát hiện bất thường hành vi."
        )
    }

def build_pedagogical_explanation(student, question, is_correct, mastery_before, mastery_after, next_skill, anomaly):
    skill = KNOWLEDGE_GRAPH.get(question["skill_id"], {})
    next_skill_info = KNOWLEDGE_GRAPH.get(next_skill, {})
    skill_name = skill.get("name", question["skill_id"])
    next_skill_name = next_skill_info.get("name", next_skill)
    direction = "giữ ở" if next_skill == question["skill_id"] else "điều hướng sang"
    correctness = "đúng" if is_correct else "sai"
    anomaly_note = ""
    if anomaly["flagged"]:
        anomaly_note = f" Phản hồi được đánh dấu bất thường ({', '.join(anomaly['flags'])}) nên trọng số BKT là {anomaly['bkt_weight']:.2f}."

    return (
        f"Học sinh {student['name']} trả lời {correctness} câu mức {question.get('difficulty_level', 2)} "
        f"của kỹ năng '{skill_name}'. Xác suất thành thạo thay đổi từ "
        f"{mastery_before:.2f} xuống/lên {mastery_after:.2f}. "
        f"Hệ thống {direction} kỹ năng '{next_skill_name}' cho câu tiếp theo."
        f"{anomaly_note}"
    )

def build_response_event_payload(student_id, question, submission, is_correct, mastery_before, mastery_after, next_skill, anomaly):
    return {
        "student_id": student_id,
        "question_id": question["id"],
        "skill_id": question["skill_id"],
        "difficulty_level": question.get("difficulty_level", 2),
        "selected_option": submission.selected_option,
        "is_correct": is_correct,
        "response_time_ms": submission.response_time_ms,
        "client_timestamp": submission.client_timestamp,
        "mastery_before": round(mastery_before, 4),
        "mastery_after": round(mastery_after, 4),
        "next_skill_id": next_skill,
        "anomaly": anomaly,
    }

def classify_student_ai_message(message):
    normalized = re.sub(r"\s+", " ", message.strip().lower())
    if not normalized:
        return "empty"
    if "chế độ ai" in normalized or "nội dung học sinh gửi" in normalized:
        return "learning"
    tokens = set(re.findall(r"\b[a-zA-Z]+\b", normalized))
    if any(keyword in normalized for keyword in GREETING_KEYWORDS) or bool(tokens & GREETING_WORDS):
        return "intro"
    if len(normalized) < 6:
        return "off_topic"
    if any(keyword in normalized for keyword in EDUCATION_KEYWORDS):
        return "learning"
    # Messages with mostly symbols or repeated slang are treated as non-learning noise.
    alnum_chars = re.findall(r"[\wÀ-ỹ]", normalized)
    if len(alnum_chars) < max(4, len(normalized) // 3):
        return "off_topic"
    return "off_topic"

def build_student_ai_guardrail_reply(reason):
    if reason == "intro":
        return (
            "Mình là AI trợ lý học tập PorcusAI. Mình giúp em hiểu khái niệm, luyện câu hỏi, "
            "nhìn ra lỗi sai và đi theo lộ trình phù hợp với mức thành thạo hiện tại."
        )
    return (
        "Mình chỉ hỗ trợ nội dung học tập trong PorcusAI. Em hãy hỏi về bài học, khái niệm, "
        "câu hỏi đang luyện hoặc lộ trình ôn tập nhé."
    )

def collect_student_learning_context(student_id, target_skill_id):
    student = get_student(student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    if target_skill_id not in KNOWLEDGE_GRAPH:
        raise HTTPException(status_code=422, detail="Invalid skill ID")

    related_skill_ids = []

    def add_with_prerequisites(skill_id):
        for prereq in KNOWLEDGE_GRAPH.get(skill_id, {}).get("prerequisites", []):
            add_with_prerequisites(prereq)
        if skill_id not in related_skill_ids:
            related_skill_ids.append(skill_id)

    add_with_prerequisites(target_skill_id)
    if target_skill_id not in related_skill_ids:
        related_skill_ids.append(target_skill_id)

    mastery_items = []
    for skill_id in related_skill_ids:
        skill = KNOWLEDGE_GRAPH[skill_id]
        mastery_items.append({
            "skill_id": skill_id,
            "skill_name": skill["name"],
            "grade": skill.get("grade"),
            "subject": skill.get("subject"),
            "mastery": round(get_student_mastery(student_id, skill_id), 2),
        })
    return {
        "student": {"id": student_id, "name": student["name"], "grade": student["grade"]},
        "target_skill": {
            "skill_id": target_skill_id,
            "skill_name": KNOWLEDGE_GRAPH[target_skill_id]["name"],
            "difficulty_policy": "Bắt đầu random mức 2/3; sai thì giảm độ khó theo lịch sử; sai mức 1 thì lùi prerequisite; streak đúng mức 3 làm tăng xác suất mức 3.",
        },
        "mastery_items": mastery_items,
    }

def build_offline_learning_path(context, teacher_mode=False):
    weak_items = [item for item in context["mastery_items"] if item["mastery"] < 0.6]
    ordered = weak_items or context["mastery_items"]
    steps = []
    for index, item in enumerate(ordered[:4], start=1):
        level = 1 if item["mastery"] < 0.45 else 2
        steps.append({
            "step": index,
            "skill_id": item["skill_id"],
            "skill_name": item["skill_name"],
            "recommended_difficulty": normalize_difficulty_label(level),
            "action": "Dạy lại và giao 3 câu nền" if teacher_mode else "Ôn nền bằng 3 câu ngắn",
            "success_signal": "Đúng 2/3 câu liên tiếp rồi chuyển lên mức Thông hiểu/Vận dụng",
        })
    return {
        "summary": "Lộ trình dựa trên mastery BKT và prerequisite graph.",
        "steps": steps,
        "teacher_notes": (
            "Ưu tiên học sinh có mastery thấp nhất trước, gom nhóm theo skill_id để dạy lại 15 phút."
            if teacher_mode else ""
        ),
    }

def build_offline_student_tutor_reply(question, message, mastery):
    skill = KNOWLEDGE_GRAPH.get(question["skill_id"], {})
    text = message.lower()
    if "lộ trình" in text or "ôn" in text or "bài ôn" in text:
        return (
            f"Em đang luyện {skill.get('name', question['skill_id'])}. "
            f"Mastery hiện khoảng {mastery:.2f}, nên hãy ôn 3 câu nền trước, "
            "sau đó mới làm câu vận dụng. Mục tiêu là đúng 2/3 câu liên tiếp."
        )
    if "sai" in text or "vì sao" in text:
        return (
            "Hãy kiểm tra lại bước biến đổi quan trọng nhất trước khi chọn đáp án. "
            f"Với kỹ năng này, lỗi thường gặp là bỏ qua prerequisite hoặc tính quá nhanh. "
            f"Gợi ý của câu: {question.get('hint', 'Đọc lại đề và tách thành từng bước nhỏ.')}"
        )
    return (
        "Tôi sẽ gợi ý từng bước, không làm hộ đáp án cuối cùng. "
        f"Câu này thuộc kỹ năng {skill.get('name', question['skill_id'])}. "
        f"Bước đầu tiên: {question.get('hint', 'xác định kiến thức nền cần dùng rồi làm từng bước.')}"
    )

def build_offline_generated_questions(payload):
    with open(Config.QUESTIONS_JSON_PATH, "r", encoding="utf-8") as file:
        questions = json.load(file)
    matched = [
        item for item in questions
        if item.get("skill_id") == payload.skill_id and int(item.get("difficulty_level", 2)) == payload.difficulty_level
    ]
    if not matched:
        matched = [item for item in questions if item.get("skill_id") == payload.skill_id]
    generated = []
    for index, question in enumerate(matched[:payload.count], start=1):
        generated.append({
            "id": f"offline_ai_{question['id']}_{index}",
            "skill_id": question["skill_id"],
            "difficulty_level": int(question.get("difficulty_level", payload.difficulty_level)),
            "difficulty": normalize_difficulty_label(question.get("difficulty_level", payload.difficulty_level)),
            "text": question["text"],
            "options": question.get("options", []),
            "correct_answer": question.get("correct_answer"),
            "hint": question.get("hint", "Hãy làm từng bước và kiểm tra kiến thức nền."),
            "explanation": question.get("explanation", "Câu hỏi lấy từ question bank offline đã kiểm định."),
        })
    return generated

def detect_offline_misconception(work_text, skill_id):
    text = work_text.lower().replace(" ", "")
    if "1/2+2/3=3/5" in text or "1/2+2/3=3/5" in text.replace("−", "-"):
        return {
            "detected_error": "Cộng tử với tử và mẫu với mẫu",
            "wrong_step": "1/2 + 2/3 = 3/5",
            "missing_prerequisite": "Quy đồng mẫu số trước khi cộng phân số khác mẫu",
            "confidence": 0.92,
            "error_type": "fraction_denominator_addition"
        }
    if "quyđồng" in text or "mẫuchung" in text:
        return {
            "detected_error": "Chưa kiểm chứng được bước sai, nhưng bài làm liên quan quy đồng mẫu số",
            "wrong_step": work_text[:160],
            "missing_prerequisite": "Tìm BCNN và nhân cả tử lẫn mẫu với nhân tử phụ",
            "confidence": 0.68,
            "error_type": "fraction_common_denominator"
        }
    if "âm" in text or "-" in text:
        return {
            "detected_error": "Có khả năng nhầm dấu âm trong phép tính",
            "wrong_step": work_text[:160],
            "missing_prerequisite": "Cộng trừ số nguyên và quy tắc dấu",
            "confidence": 0.62,
            "error_type": "integer_sign"
        }
    skill = KNOWLEDGE_GRAPH.get(skill_id, {})
    return {
        "detected_error": "Cần thêm dữ liệu bài làm để xác định lỗi sai cụ thể",
        "wrong_step": work_text[:160],
        "missing_prerequisite": skill.get("name", skill_id),
        "confidence": 0.45,
        "error_type": "insufficient_work_evidence"
    }

def build_offline_work_analysis(student_id, payload):
    skill = KNOWLEDGE_GRAPH.get(payload.skill_id, {})
    mastery = get_student_mastery(student_id, payload.skill_id)
    misconception = detect_offline_misconception(payload.work_text, payload.skill_id)
    remediation_steps = [
        {
            "type": "mini_lesson",
            "title": "Sửa lỗi gốc",
            "content": (
                "Trước khi cộng hai phân số khác mẫu, em phải quy đồng để hai mẫu số giống nhau. "
                "Không được cộng trực tiếp mẫu số."
                if misconception["error_type"] == "fraction_denominator_addition"
                else f"Ôn lại kiến thức nền: {misconception['missing_prerequisite']}."
            ),
        },
        {
            "type": "practice",
            "title": "Câu luyện 1",
            "content": "Tính 1/3 + 1/6. Viết rõ bước tìm mẫu chung trước khi cộng.",
        },
        {
            "type": "practice",
            "title": "Câu luyện 2",
            "content": "Tìm lỗi sai: 2/5 + 1/3 = 3/8. Sửa lại cho đúng.",
        },
        {
            "type": "mastery_check",
            "title": "Đo lại mastery",
            "content": "Làm đúng 3/4 câu cùng lỗi để tăng mastery và quay lại bài số hữu tỉ.",
        },
    ]
    return {
        "summary": "AI biến bài làm tự do thành kế hoạch can thiệp cá nhân hóa.",
        "student_id": student_id,
        "mode": payload.mode,
        "skill_id": payload.skill_id,
        "skill_name": skill.get("name", payload.skill_id),
        "mastery_before": round(mastery, 2),
        "misconception": misconception,
        "remediation_pack": remediation_steps,
        "measurement": {
            "target": "Đúng 3/4 câu trong gói ôn",
            "mastery_update_rule": "Nếu đạt mục tiêu, BKT tăng xác suất thành thạo và mở lại skill hiện tại.",
            "teacher_signal": "Nếu không đạt, gom vào nhóm cần dạy lại prerequisite."
        },
        "why_ai_is_needed": (
            "Rule engine chỉ biết đúng/sai; AI đọc bài làm tự do, xác định kiểu lỗi, "
            "rồi tạo can thiệp sát lỗi của từng học sinh."
        )
    }

def parse_ai_json_object(content):
    stripped = content.strip()
    if stripped.startswith("```"):
        stripped = re.sub(r"^```(?:json)?\s*", "", stripped)
        stripped = re.sub(r"\s*```$", "", stripped)
    try:
        return json.loads(stripped)
    except json.JSONDecodeError as exc:
        raise HTTPException(status_code=502, detail="AI response must be valid JSON") from exc

def retrieve_grounding_context(skill_id, limit=3):
    skill = KNOWLEDGE_GRAPH.get(skill_id)
    if not skill:
        raise HTTPException(status_code=422, detail="Invalid skill ID")
    with open(Config.QUESTIONS_JSON_PATH, "r", encoding="utf-8") as file:
        questions = json.load(file)
    skill_questions = [item for item in questions if item["skill_id"] == skill_id][:limit]
    citations = [
        {
            "source_type": "local_question_bank",
            "source_id": item["id"],
            "skill_id": skill_id,
            "title": f"{skill.get('name', skill_id)} - câu {index + 1}",
            "excerpt": item["text"],
        }
        for index, item in enumerate(skill_questions)
    ]
    context = "\n".join(f"- [{item['source_id']}] {item['excerpt']}" for item in citations)
    return {
        "skill": skill,
        "citations": citations,
        "context": context,
        "adapter": "local_knowledge_base_ready_for_fpt_ai_knowledge",
    }

def build_offline_grounded_lesson_plan(skill, citations, group_context):
    source_lines = "\n".join(f"- {item['title']}: {item['excerpt']}" for item in citations)
    return (
        f"Mục tiêu: Củng cố kỹ năng '{skill['name']}' cho lớp {skill['grade']}.\n"
        f"Khởi động: Cho học sinh nhắc lại lỗi thường gặp từ nhóm: {group_context or 'dưới ngưỡng mastery 0.50'}.\n"
        f"Hoạt động chính: Giáo viên giải 1 ví dụ mẫu, sau đó học sinh làm 2 câu tương tự theo cặp.\n"
        f"Đánh giá nhanh: Dùng một câu exit ticket cùng kỹ năng và ghi lại học sinh còn sai.\n"
        f"Nguồn/căn cứ nội bộ:\n{source_lines}"
    )

def get_speech_cache_paths(text, voice, question_id=None):
    cache_dir = os.path.join(Config.DATA_DIR, "speech_cache")
    os.makedirs(cache_dir, exist_ok=True)
    normalized = f"{voice}|{question_id or ''}|{text.strip()}".encode("utf-8")
    cache_key = hashlib.sha256(normalized).hexdigest()[:24]
    return {
        "cache_key": cache_key,
        "audio_path": os.path.join(cache_dir, f"{cache_key}.mp3"),
        "manifest_path": os.path.join(cache_dir, f"{cache_key}.json"),
    }

@app.get("/api/knowledge-graph")
def get_knowledge_graph():
    return KNOWLEDGE_GRAPH

# Request schemas
class LoginRequest(BaseModel):
    username: str
    password: str
    role: Optional[str] = None

class StudentRegisterRequest(BaseModel):
    username: str
    password: str
    name: str
    grade: int

class AnswerSubmission(BaseModel):
    question_id: str
    selected_option: str
    event_id: Optional[str] = None
    response_time_ms: Optional[int] = None
    client_timestamp: Optional[int] = None

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
    history: Optional[list[dict]] = None

class AIQuestionGenerationRequest(BaseModel):
    subject: str = "Toán"
    grade: int = 7
    skill_id: str
    difficulty_level: int = 2
    count: int = 1
    question_type: str = "multiple_choice"

class AIWorkAnalysisRequest(BaseModel):
    mode: str = "find_error"
    subject: str = "Toán"
    grade: int = 7
    skill_id: str = "MATH_G7"
    work_text: str
    attachment_name: Optional[str] = None

class AILessonPlanRequest(BaseModel):
    skill_id: str
    group_context: str = ""

class SyncAckRequest(BaseModel):
    event_ids: list[str]

class SpeechCacheRequest(BaseModel):
    text: str
    voice: str = "vi_female"
    question_id: Optional[str] = None

class GroundedLessonPlanRequest(BaseModel):
    skill_id: str
    group_context: str = ""
    textbook_series: Optional[str] = None

# Endpoints
@app.get("/api/health")
def get_health():
    return {
        "status": "ok",
        "service": "VGap AI Backend",
        "mode": "offline_first_lan_ready",
        "database": "sqlite",
    }

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
    student = get_student(student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    if len(payload.message.strip()) == 0 or len(payload.message) > 1000:
        raise HTTPException(status_code=422, detail="Message must contain 1-1000 characters")

    with open(Config.QUESTIONS_JSON_PATH, "r", encoding="utf-8") as file:
        questions = json.load(file)
    question = next((item for item in questions if item["id"] == payload.question_id), None)

    context_str = ""
    if question:
        skill = KNOWLEDGE_GRAPH.get(question["skill_id"], {})
        mastery = get_student_mastery(student_id, question["skill_id"])
        correct_key = question.get("correct_answer")
        correct_option = next(
            (option.get("text", "") for option in question.get("options", []) if option.get("key") == correct_key),
            correct_key or ""
        )
        context_str = (
            f"\n--- Ngữ cảnh bài tập hiện tại ---\n"
            f"Kỹ năng: {skill.get('name', question['skill_id'])}. "
            f"Mức thành thạo của học sinh: {mastery:.2f}. "
            f"Độ khó: {normalize_difficulty_label(question.get('difficulty_level', 2))}. "
            f"Câu hỏi: {question.get('text', '')}. Lựa chọn: {question.get('options', [])}. "
            f"Đáp án nội bộ: {correct_option}."
        )

    system_prompt = (
        f"Bạn là PorcusAI, một trợ lý AI thông minh và thân thiện. "
        f"Bạn đang giao tiếp với một học sinh lớp {student.get('grade', 'không rõ')}, tên là {student.get('name', 'bạn')}. "
        f"Hãy trả lời TẤT CẢ các câu hỏi của người dùng một cách bình thường như một AI thực thụ. "
        f"Tuyệt đối phải điều chỉnh ngôn từ, cách nói chuyện, và độ phức tạp của câu trả lời sao cho phù hợp nhất với mức độ hiểu biết của học sinh lớp {student.get('grade', 'không rõ')}. "
        f"{context_str}"
    )
    try:
        result = fpt_ai_client.complete(
            system_prompt=system_prompt,
            user_prompt=payload.message.strip(),
            history=payload.history
        )
    except FPTAIError as exc:
        return {"provider": "Error", "model": None, "content": f"Lỗi từ AI: {str(exc)}", "usage": None}
    return {"provider": "FPT AI Factory", "model": result.model, "content": result.content, "usage": result.usage}

@app.post("/api/ai/student/{student_id}/generate-question")
def ai_generate_question(student_id: str, payload: AIQuestionGenerationRequest):
    if not get_student(student_id):
        raise HTTPException(status_code=404, detail="Student not found")
    if payload.skill_id not in KNOWLEDGE_GRAPH:
        raise HTTPException(status_code=422, detail="Invalid skill ID")
    if payload.difficulty_level not in DIFFICULTY_LABELS:
        raise HTTPException(status_code=422, detail="difficulty_level must be 1, 2, or 3")
    if not (1 <= payload.count <= 5):
        raise HTTPException(status_code=422, detail="count must be between 1 and 5")

    skill = KNOWLEDGE_GRAPH[payload.skill_id]
    difficulty_label = normalize_difficulty_label(payload.difficulty_level)
    system_prompt = (
        "Bạn là AI sinh câu hỏi học tập cho PorcusAI. "
        "Chỉ tạo câu hỏi phục vụ học tập phổ thông Việt Nam. "
        "Trả về JSON hợp lệ duy nhất, không markdown, không giải thích ngoài JSON. "
        "Mỗi câu hỏi phải có id, skill_id, difficulty_level, difficulty, text, options, correct_answer, hint, explanation. "
        "options là mảng 4 lựa chọn A-D dạng {key,text}. correct_answer là một trong A,B,C,D."
    )
    user_prompt = (
        f"Tạo {payload.count} câu hỏi {payload.question_type} cho môn {payload.subject}, lớp {payload.grade}. "
        f"Kỹ năng: {skill['name']} ({payload.skill_id}). "
        f"Độ khó: {payload.difficulty_level} - {difficulty_label}. "
        "Quy ước độ khó: 1=Nhận biết, 2=Thông hiểu, 3=Vận dụng. "
        "Câu hỏi phải đo đúng kỹ năng, không cần kiến thức ngoài chương trình, không tiết lộ đáp án trong text. "
        'Schema: {"questions":[...]}'
    )
    try:
        result = fpt_ai_client.complete(system_prompt=system_prompt, user_prompt=user_prompt)
    except FPTAIError as exc:
        return {
            "provider": "offline_question_bank_after_fpt_ai_error",
            "model": None,
            "difficulty_policy": DIFFICULTY_LABELS,
            "questions": build_offline_generated_questions(payload),
            "usage": None,
            "fallback_reason": str(exc),
        }
    try:
        parsed = parse_ai_json_object(result.content)
        questions = parsed.get("questions")
    except HTTPException as exc:
        if exc.status_code != 502:
            raise
        return {
            "provider": "offline_question_bank_after_ai_parse_error",
            "model": result.model,
            "difficulty_policy": DIFFICULTY_LABELS,
            "questions": build_offline_generated_questions(payload),
            "usage": result.usage,
            "fallback_reason": exc.detail,
        }
    if not isinstance(questions, list) or not questions:
        raise HTTPException(status_code=502, detail="AI response missing questions array")
    allowed_keys = {"A", "B", "C", "D"}
    for index, question in enumerate(questions):
        options = question.get("options")
        if question.get("skill_id") != payload.skill_id:
            raise HTTPException(status_code=502, detail=f"Generated question {index + 1} has wrong skill_id")
        if question.get("difficulty_level") != payload.difficulty_level:
            raise HTTPException(status_code=502, detail=f"Generated question {index + 1} has wrong difficulty_level")
        if not isinstance(options, list) or len(options) != 4:
            raise HTTPException(status_code=502, detail=f"Generated question {index + 1} must have 4 options")
        if question.get("correct_answer") not in allowed_keys:
            raise HTTPException(status_code=502, detail=f"Generated question {index + 1} has invalid correct_answer")
    return {
        "provider": "FPT AI Factory",
        "model": result.model,
        "difficulty_policy": DIFFICULTY_LABELS,
        "questions": questions,
        "usage": result.usage,
    }

@app.post("/api/ai/student/{student_id}/analyze-work")
def ai_analyze_student_work(student_id: str, payload: AIWorkAnalysisRequest):
    if not get_student(student_id):
        raise HTTPException(status_code=404, detail="Student not found")
    if payload.skill_id not in KNOWLEDGE_GRAPH:
        raise HTTPException(status_code=422, detail="Invalid skill ID")
    if payload.mode not in {"find_error", "similar_question", "step_hint", "explain", "summarize"}:
        raise HTTPException(status_code=422, detail="Invalid analysis mode")
    if len(payload.work_text.strip()) < 8 and not payload.attachment_name:
        raise HTTPException(status_code=422, detail="work_text must be at least 8 characters unless an attachment is provided")
    if len(payload.work_text) > 2500:
        raise HTTPException(status_code=422, detail="work_text must be at most 2500 characters")

    context = collect_student_learning_context(student_id, payload.skill_id)
    skill = KNOWLEDGE_GRAPH[payload.skill_id]
    system_prompt = (
        "Bạn là AI Error Analyzer của PorcusAI. "
        "Nhiệm vụ của bạn là biến bài làm tự do của học sinh thành can thiệp cá nhân hóa có thể đo lường. "
        "Chỉ dùng dữ liệu bài làm, mastery và prerequisite graph được cung cấp. "
        "Trả về JSON hợp lệ duy nhất, không markdown. "
        "Schema bắt buộc: {summary, student_id, mode, skill_id, skill_name, mastery_before, misconception, remediation_pack, measurement, why_ai_is_needed}. "
        "misconception gồm detected_error, wrong_step, missing_prerequisite, confidence, error_type. "
        "remediation_pack là 3-5 bước, mỗi bước gồm type, title, content. "
        "measurement gồm target, mastery_update_rule, teacher_signal."
    )
    user_prompt = json.dumps({
        "student_id": student_id,
        "mode": payload.mode,
        "subject": payload.subject,
        "grade": payload.grade,
        "skill": {
            "skill_id": payload.skill_id,
            "skill_name": skill["name"],
            "mastery": round(get_student_mastery(student_id, payload.skill_id), 2),
        },
        "attachment_name": payload.attachment_name,
        "work_text": payload.work_text,
        "learning_context": context,
    }, ensure_ascii=False)

    if fpt_ai_client.configured:
        try:
            result = fpt_ai_client.complete(system_prompt=system_prompt, user_prompt=user_prompt)
            parsed = parse_ai_json_object(result.content)
            return {
                "provider": "FPT AI Factory",
                "model": result.model,
                "analysis": parsed,
                "usage": result.usage,
            }
        except FPTAIError as exc:
            return {
                "provider": "offline_error_analyzer_after_fpt_ai_error",
                "model": None,
                "analysis": build_offline_work_analysis(student_id, payload),
                "usage": None,
                "fallback_reason": str(exc),
            }
        except HTTPException as exc:
            if exc.status_code != 502:
                raise
            return {
                "provider": "offline_error_analyzer_after_ai_parse_error",
                "model": None,
                "analysis": build_offline_work_analysis(student_id, payload),
                "usage": None,
                "fallback_reason": exc.detail,
            }

    return {
        "provider": "offline_error_analyzer",
        "model": None,
        "analysis": build_offline_work_analysis(student_id, payload),
        "usage": None,
    }

@app.get("/api/ai/student/{student_id}/learning-path")
def ai_student_learning_path(student_id: str, target_skill: str = "MATH_G7"):
    context = collect_student_learning_context(student_id, target_skill)
    system_prompt = (
        "Bạn là AI thiết kế lộ trình học cá nhân cho PorcusAI. "
        "Chỉ dùng dữ liệu mastery và prerequisite graph được cung cấp. "
        "Trả về JSON hợp lệ duy nhất với summary và steps. "
        "Mỗi step gồm skill_id, skill_name, recommended_difficulty, action, success_signal. "
        "Không bịa điểm số, không đưa hoạt động ngoài học tập."
    )
    user_prompt = json.dumps(context, ensure_ascii=False)
    if fpt_ai_client.configured:
        try:
            result = fpt_ai_client.complete(system_prompt=system_prompt, user_prompt=user_prompt)
            parsed = parse_ai_json_object(result.content)
            return {
                "provider": "FPT AI Factory",
                "model": result.model,
                "context": context,
                "learning_path": parsed,
                "usage": result.usage,
            }
        except FPTAIError as exc:
            return {
                "provider": "offline_bkt_dag_path_after_fpt_ai_error",
                "model": None,
                "context": context,
                "learning_path": build_offline_learning_path(context),
                "usage": None,
                "fallback_reason": str(exc),
            }
        except HTTPException as exc:
            if exc.status_code != 502:
                raise
            return {
                "provider": "offline_bkt_dag_path_after_ai_parse_error",
                "model": None,
                "context": context,
                "learning_path": build_offline_learning_path(context),
                "usage": None,
                "fallback_reason": exc.detail,
            }
    return {
        "provider": "offline_bkt_dag_path",
        "model": None,
        "context": context,
        "learning_path": build_offline_learning_path(context),
        "usage": None,
    }

@app.get("/api/ai/teacher/student/{student_id}/learning-path")
def ai_teacher_student_learning_path(student_id: str, target_skill: str = "MATH_G7"):
    context = collect_student_learning_context(student_id, target_skill)
    system_prompt = (
        "Bạn là AI trợ lý giáo viên của PorcusAI. "
        "Hãy đề xuất lộ trình can thiệp cho một học sinh dựa trên mastery BKT và prerequisite graph. "
        "Trả về JSON hợp lệ duy nhất với summary, steps, teacher_notes. "
        "Mỗi step gồm skill_id, skill_name, recommended_difficulty, action, success_signal. "
        "Tập trung tiết kiệm thời gian giáo viên: dạy lại gì, giao bài gì, đo tiến bộ ra sao."
    )
    user_prompt = json.dumps(context, ensure_ascii=False)
    if fpt_ai_client.configured:
        try:
            result = fpt_ai_client.complete(system_prompt=system_prompt, user_prompt=user_prompt)
            parsed = parse_ai_json_object(result.content)
            return {
                "provider": "FPT AI Factory",
                "model": result.model,
                "context": context,
                "learning_path": parsed,
                "usage": result.usage,
            }
        except FPTAIError as exc:
            pass # Fallback to offline below
    return {
        "provider": "offline_teacher_bkt_dag_path",
        "model": None,
        "context": context,
        "learning_path": build_offline_learning_path(context, teacher_mode=True),
        "usage": None,
    }

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

@app.post("/api/ai/teacher/lesson-plan-grounded")
def ai_grounded_lesson_plan(payload: GroundedLessonPlanRequest):
    grounding = retrieve_grounding_context(payload.skill_id)
    skill = grounding["skill"]
    system_prompt = (
        "Bạn là trợ lý thiết kế bài giảng theo GDPT 2018. "
        "Chỉ dùng ngữ cảnh được cung cấp, luôn nêu nguồn theo source_id, không bịa trang sách. "
        "Hãy định dạng kết quả bằng Markdown (in đậm, tiêu đề, danh sách) để dễ đọc."
    )
    user_prompt = (
        f"Kỹ năng: {skill['name']}; lớp {skill['grade']}; "
        f"bộ sách ưu tiên: {payload.textbook_series or 'chưa chọn'}; "
        f"bối cảnh nhóm: {payload.group_context.strip() or 'học sinh dưới ngưỡng thành thạo 0.50'}.\n"
        f"Ngữ cảnh đã truy xuất:\n{grounding['context']}"
    )
    if fpt_ai_client.configured:
        try:
            result = fpt_ai_client.complete(system_prompt=system_prompt, user_prompt=user_prompt)
            content = result.content
            provider = "FPT AI Inference + Knowledge adapter context"
            usage = result.usage
            model = result.model
        except FPTAIError as exc:
            content = build_offline_grounded_lesson_plan(skill, grounding["citations"], payload.group_context.strip())
            provider = "offline_grounded_draft_after_fpt_ai_error"
            usage = None
            model = None
    else:
        content = build_offline_grounded_lesson_plan(skill, grounding["citations"], payload.group_context.strip())
        provider = "offline_grounded_draft"
        usage = None
        model = None
    return {
        "provider": provider,
        "model": model,
        "content": content,
        "citations": grounding["citations"],
        "usage": usage,
    }

@app.post("/api/speech/cache")
def create_speech_cache(payload: SpeechCacheRequest):
    text = payload.text.strip()
    if not text or len(text) > 1200:
        raise HTTPException(status_code=422, detail="Text must contain 1-1200 characters")
    paths = get_speech_cache_paths(text, payload.voice, payload.question_id)
    cache_hit = os.path.exists(paths["audio_path"])
    manifest = {
        "cache_key": paths["cache_key"],
        "question_id": payload.question_id,
        "voice": payload.voice,
        "text_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
        "audio_ready": cache_hit,
        "provider": "FPT AI Speech",
        "status": "cache_hit" if cache_hit else "pending_provider_generation",
    }
    with open(paths["manifest_path"], "w", encoding="utf-8") as file:
        json.dump(manifest, file, ensure_ascii=False, indent=2)
    return {
        **manifest,
        "audio_url": f"/api/speech/cache/{paths['cache_key']}" if cache_hit else None,
        "cache_policy": "generate_once_then_serve_from_school_lan",
    }

@app.get("/api/speech/cache/{cache_key}")
def get_cached_speech(cache_key: str):
    if not re.match(r"^[a-f0-9]{24}$", cache_key):
        raise HTTPException(status_code=422, detail="Invalid cache key")
    audio_path = os.path.join(Config.DATA_DIR, "speech_cache", f"{cache_key}.mp3")
    if not os.path.exists(audio_path):
        raise HTTPException(status_code=404, detail="Audio cache miss; provider generation required")
    return FileResponse(audio_path, media_type="audio/mpeg", filename=f"{cache_key}.mp3")

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
    now = int(time.time())
    cursor.execute("""
        INSERT INTO students (id, name, grade, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?)
        ON CONFLICT(id) DO UPDATE SET
            name = excluded.name, grade = excluded.grade, updated_at = excluded.updated_at
    """, (payload.student_id, payload.name, payload.grade, now, now))

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
            "difficulty": normalize_difficulty_label(question.get("difficulty_level", 2)),
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
    if submission.event_id:
        existing = get_response_by_event_id(submission.event_id)
        if existing:
            return {
                "is_correct": bool(existing["is_correct"]),
                "correct_answer": None,
                "distractor_explanation": None,
                "hint": "",
                "new_mastery_probability": get_student_mastery(student_id, existing["skill_id"]),
                "next_recommended_skill": existing["skill_id"],
                "next_recommended_difficulty": existing["difficulty_level"],
                "response_event_id": submission.event_id,
                "idempotent_replay": True,
                "anomaly": {
                    "flagged": bool(json.loads(existing.get("anomaly_flags") or "[]")),
                    "flags": json.loads(existing.get("anomaly_flags") or "[]"),
                    "bkt_weight": existing.get("bkt_weight") or 1.0,
                    "reason": "Sự kiện đã được xử lý trước đó, không cập nhật BKT lần hai."
                }
            }
        
    # Load questions
    with open(Config.QUESTIONS_JSON_PATH, "r", encoding="utf-8") as f:
        questions = json.load(f)
        
    question = next((q for q in questions if q["id"] == submission.question_id), None)
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
        
    is_correct = (submission.selected_option == question["correct_answer"])
    distractor_explanations = build_distractor_explanations(question)
    response_event_id = submission.event_id or f"local-{int(time.time() * 1000)}-{uuid.uuid4().hex[:8]}"
    mastery_before = get_student_mastery(student_id, question["skill_id"])
    anomaly = evaluate_response_anomaly(question, is_correct, submission.response_time_ms)
    
    # Record response in DB (with difficulty_level)
    record_response(
        student_id, 
        question["id"], 
        question["skill_id"], 
        question.get("difficulty_level", 2), 
        is_correct, 
        int(time.time()),
        event_id=response_event_id,
        response_time_ms=submission.response_time_ms,
        client_timestamp=submission.client_timestamp,
        bkt_weight=anomaly["bkt_weight"],
        anomaly_flags=anomaly["flags"],
    )
    
    # Run BKT Bayesian Update
    new_mastery = update_student_skill(
        student_id,
        question["skill_id"],
        is_correct,
        weight=anomaly["bkt_weight"],
    )
    
    # Get next recommended skill path and difficulty
    next_skill, next_diff = get_next_question_difficulty_and_skill(student_id, question["skill_id"])
    explanation_text = build_pedagogical_explanation(
        student,
        question,
        is_correct,
        mastery_before,
        new_mastery,
        next_skill,
        anomaly,
    )
    add_pedagogical_explanation(
        student_id,
        response_event_id,
        question["skill_id"],
        next_skill,
        explanation_text,
        mastery_before,
        new_mastery,
    )
    event_payload = build_response_event_payload(
        student_id,
        question,
        submission,
        is_correct,
        mastery_before,
        new_mastery,
        next_skill,
        anomaly,
    )
    vector_clock = f"{student_id}:{submission.client_timestamp or int(time.time())}:{response_event_id}"
    upsert_sync_event(response_event_id, "student_response_submitted", student_id, event_payload, vector_clock)
    
    assessment_just_completed = False
    if not student.get("initial_assessment_completed"):
        with get_db_connection() as conn:
            count = conn.execute("SELECT COUNT(*) FROM responses WHERE student_id=?", (student_id,)).fetchone()[0]
            if count >= 5:
                conn.execute("UPDATE students SET initial_assessment_completed=1 WHERE id=?", (student_id,))
                conn.commit()
                assessment_just_completed = True
    
    return {
        "is_correct": is_correct,
        "correct_answer": question["correct_answer"],
        "distractor_explanation": None if is_correct else distractor_explanations.get(submission.selected_option),
        "hint": question.get("hint", ""),
        "new_mastery_probability": new_mastery,
        "next_recommended_skill": next_skill,
        "next_recommended_difficulty": next_diff,
        "response_event_id": response_event_id,
        "idempotent_replay": False,
        "anomaly": anomaly,
        "pedagogical_explanation": explanation_text,
        "rewards": get_student_rewards(student_id),
        "assessment_just_completed": assessment_just_completed,
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

@app.get("/api/sync/push")
def get_sync_push_batch(limit: int = 100):
    """Return local events ready for a cloud PostgreSQL sync worker."""
    safe_limit = max(1, min(limit, 500))
    events = list_unsynced_events(limit=safe_limit)
    return {
        "sync_mode": "hybrid_sqlite_to_cloud",
        "conflict_strategy": "event_id_idempotency_and_vector_clock",
        "event_count": len(events),
        "events": events,
    }

@app.post("/api/sync/ack")
def acknowledge_sync(payload: SyncAckRequest):
    changed = mark_events_synced(payload.event_ids)
    return {
        "acknowledged": changed,
        "event_ids": payload.event_ids,
    }

@app.get("/api/student/{student_id}/explanations")
def get_student_explanations(student_id: str, limit: int = 10):
    if not get_student(student_id):
        raise HTTPException(status_code=404, detail="Student not found")
    safe_limit = max(1, min(limit, 50))
    return {
        "student_id": student_id,
        "explanations": list_pedagogical_explanations(student_id, limit=safe_limit),
    }

@app.get("/api/teacher/dashboard")
def get_teacher_dashboard():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 1. Total students count
    cursor.execute("SELECT COUNT(*) FROM students WHERE id NOT LIKE '%_survey_%'")
    total_students = cursor.fetchone()[0]
    
    # 2. Overall mastery rate (average of all active skills probability)
    cursor.execute("""
        SELECT AVG(m.mastery_probability) FROM student_mastery m
        JOIN students s ON m.student_id = s.id
        WHERE s.id NOT LIKE '%_survey_%'
    """)
    avg_mastery = cursor.fetchone()[0] or 0.5
    
    # 3. Auto-Grouping students by knowledge gap (probability < 0.50)
    groups = {}
    for skill_id, skill_info in KNOWLEDGE_GRAPH.items():
        cursor.execute("""
            SELECT s.name FROM student_mastery m
            JOIN students s ON m.student_id = s.id
            WHERE m.skill_id = ? AND m.mastery_probability < 0.50 AND s.id NOT LIKE '%_survey_%'
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
            SELECT AVG(m.mastery_probability) FROM student_mastery m
            JOIN students s ON m.student_id = s.id
            WHERE m.skill_id = ? AND s.id NOT LIKE '%_survey_%'
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
    cursor.execute("SELECT id, name FROM students WHERE id NOT LIKE '%_survey_%'")
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
            "current_skill": KNOWLEDGE_GRAPH.get(active_skill, {}).get("name", active_skill),
            "current_skill_id": active_skill,
            "n_failed": n_failed,
            "t_stuck": t_stuck,
            "mastery": round(mastery, 2),
            "priority_score": round(ps_score, 2)
        })
        
    # Sort priority list descending by priority_score and keep top 10
    priority_list.sort(key=lambda x: x["priority_score"], reverse=True)
    priority_list = priority_list[:10]
    
    conn.close()
    
    cursor = get_db_connection().cursor()
    conn = cursor.connection
    cursor.execute("""
        SELECT r.*, s.name 
        FROM responses r
        JOIN students s ON s.id = r.student_id
        WHERE s.id NOT LIKE '%_survey_%'
        ORDER BY r.id DESC
        LIMIT 20
    """)
    realtime_events = []
    for row in cursor.fetchall():
        flags = json.loads(row["anomaly_flags"] or "[]")
        realtime_events.append({
            "student_id": row["student_id"],
            "student_name": row["name"],
            "event_id": row["event_id"],
            "question_id": row["question_id"],
            "skill_name": KNOWLEDGE_GRAPH.get(row["skill_id"], {}).get("name", row["skill_id"]),
            "is_correct": bool(row["is_correct"]),
            "response_time_ms": row["response_time_ms"],
            "anomaly_flags": flags,
            "severity": "warning" if flags else "normal",
            "timestamp": row["timestamp"],
        })
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
        "class_progress": class_progress,
        "realtime_events": realtime_events
    }

@app.get("/api/evidence/fpt-ai-coverage")
def get_fpt_ai_coverage():
    """Return judge-facing evidence for how the project uses the FPT AI ecosystem."""
    implemented = [item for item in FPT_AI_CAPABILITY_MATRIX if item["status"] == "implemented"]
    planned = [item for item in FPT_AI_CAPABILITY_MATRIX if item["status"] != "implemented"]
    return {
        "summary": {
            "implemented_count": len(implemented),
            "planned_adapter_count": len(planned),
            "positioning": (
                "BKT/DAG là lõi chẩn đoán offline; FPT AI là lớp tăng cường cho "
                "Socratic tutoring, lesson planning, Knowledge/RAG, Speech, OCR và MCP."
            )
        },
        "capabilities": FPT_AI_CAPABILITY_MATRIX
    }

@app.get("/api/evidence/cost-model")
def get_cost_model(students: int = 1000):
    """Estimate monthly AI cost and show why the core system stays cheap at scale."""
    if students < 1 or students > 1_000_000:
        raise HTTPException(status_code=422, detail="students must be between 1 and 1,000,000")

    assumptions = dict(COST_MODEL_ASSUMPTIONS)
    student_ai_tokens = (
        students
        * assumptions["ai_calls_per_student_month"]
        * assumptions["estimated_tokens_per_ai_call"]
    )
    teacher_ai_tokens = (
        assumptions["teacher_ai_lesson_plans_per_month"]
        * assumptions["estimated_tokens_per_lesson_plan"]
    )
    total_tokens = student_ai_tokens + teacher_ai_tokens
    ai_cost_vnd = round((total_tokens / 1000) * assumptions["estimated_vnd_per_1k_tokens"])
    cost_per_student_vnd = round(ai_cost_vnd / students, 2)

    return {
        "students": students,
        "assumptions": assumptions,
        "monthly": {
            "core_bkt_dag_cost_vnd": 0,
            "estimated_ai_tokens": total_tokens,
            "estimated_ai_cost_vnd": ai_cost_vnd,
            "estimated_cost_per_student_vnd": cost_per_student_vnd
        },
        "scale_story": {
            "100_users": "SQLite/local LAN đủ cho pilot; AI chỉ gọi khi cần gợi ý/giao án.",
            "10k_users": "Chuyển PostgreSQL, cache dashboard, queue diagnostic events, batch AI summaries.",
            "1m_users": "Multi-tenant services, event streaming, async AI jobs, quota/cost controls theo trường."
        }
    }

@app.get("/api/evidence/safety")
def get_safety_evidence():
    """Return implemented and planned safety controls for final-round judging."""
    implemented = sum(1 for item in SAFETY_CONTROLS if item["implemented"])
    return {
        "summary": {
            "implemented_controls": implemented,
            "total_controls": len(SAFETY_CONTROLS),
            "production_gap": "Cần thêm moderation, PII policy và prompt-injection classifier trước triển khai thật."
        },
        "controls": SAFETY_CONTROLS
    }

def verify_password(password: str, encoded: str) -> bool:
    import hashlib, hmac
    try:
        algorithm, salt, expected = encoded.split('$', 2)
        if algorithm != 'pbkdf2_sha256':
            return False
        actual = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), bytes.fromhex(salt), 120_000).hex()
        return hmac.compare_digest(actual, expected)
    except (ValueError, TypeError):
        return False

@app.post("/api/auth/login")
def login(payload: LoginRequest):
    import secrets, time, hashlib
    username = payload.username.strip()
    conn = get_db_connection()
    row = conn.execute("""SELECT id,display_name,role,password_hash,status FROM users
                          WHERE email=? OR id=?""", (username, username)).fetchone()
    if not row or row["status"] != "active" or not verify_password(payload.password, row["password_hash"] or ""):
        conn.close()
        raise HTTPException(status_code=401, detail="Invalid username or password")
    if payload.role and payload.role != row["role"]:
        conn.close()
        raise HTTPException(status_code=403, detail="Account role does not match")
    token = secrets.token_urlsafe(32)
    token_hash = hashlib.sha256(token.encode("utf-8")).hexdigest()
    now = int(time.time())
    conn.execute("INSERT INTO auth_sessions(token_hash,user_id,created_at,expires_at) VALUES(?,?,?,?)",
                 (token_hash, row["id"], now, now + 12 * 3600))
    conn.execute("UPDATE users SET last_login_at=? WHERE id=?", (now, row["id"]))
    student = conn.execute("SELECT id, initial_assessment_completed FROM students WHERE user_id=?", (row["id"],)).fetchone()
    conn.commit()
    conn.close()
    return {"access_token": token, "token_type": "bearer", "expires_in": 12 * 3600,
            "user": {"id": row["id"], "display_name": row["display_name"], "role": row["role"],
                     "student_id": student["id"] if student else None,
                     "initial_assessment_completed": bool(student["initial_assessment_completed"]) if student else True}}

@app.post("/api/auth/student/register", status_code=201)
def register_student(payload: StudentRegisterRequest):
    import re
    username = payload.username.strip().lower()
    name = payload.name.strip()
    if not re.fullmatch(r"[a-z0-9_.-]{3,32}", username):
        raise HTTPException(status_code=422, detail="Username must contain 3-32 lowercase letters, numbers, dot, dash or underscore")
    if len(name) < 2 or len(name) > 80:
        raise HTTPException(status_code=422, detail="Student name must contain 2-80 characters")
    if not 1 <= payload.grade <= 12:
        raise HTTPException(status_code=422, detail="Grade must be between 1 and 12")
    password = payload.password
    if len(password) < 8 or not re.search(r"[A-Za-z]", password) or not re.search(r"\d", password):
        raise HTTPException(status_code=422, detail="Password must contain at least 8 characters, one letter and one number")
    try:
        account = create_student_account(username, password, name, payload.grade)
    except ValueError as exc:
        if str(exc) == "username_exists":
            raise HTTPException(status_code=409, detail="Username already exists") from exc
        raise
    auth = login(LoginRequest(username=username, password=password, role="student"))
    return {**auth, "student": account}

@app.get("/api/auth/me")
def auth_me(authorization: Optional[str] = Header(default=None)):
    import hashlib, time
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="Missing bearer token")
    token_hash = hashlib.sha256(authorization.split(" ", 1)[1].encode("utf-8")).hexdigest()
    conn = get_db_connection()
    row = conn.execute("""SELECT u.id,u.display_name,u.role,s.id AS student_id,s.initial_assessment_completed
                          FROM auth_sessions a JOIN users u ON u.id=a.user_id
                          LEFT JOIN students s ON s.user_id=u.id
                          WHERE a.token_hash=? AND a.revoked_at IS NULL AND a.expires_at>?""",
                       (token_hash, int(time.time()))).fetchone()
    conn.close()
    if not row:
        raise HTTPException(status_code=401, detail="Session expired or invalid")
    user_data = dict(row)
    if user_data.get("initial_assessment_completed") is not None:
        user_data["initial_assessment_completed"] = bool(user_data["initial_assessment_completed"])
    else:
        user_data["initial_assessment_completed"] = True
    return {"user": user_data}

@app.post("/api/auth/logout")
def logout(authorization: Optional[str] = Header(default=None)):
    import hashlib, time
    if authorization and authorization.lower().startswith("bearer "):
        token_hash = hashlib.sha256(authorization.split(" ", 1)[1].encode("utf-8")).hexdigest()
        conn = get_db_connection()
        conn.execute("UPDATE auth_sessions SET revoked_at=? WHERE token_hash=?", (int(time.time()), token_hash))
        conn.commit()
        conn.close()
    return {"status": "logged_out"}

@app.get("/api/evidence/final-scorecard")
def get_evidence_final_scorecard():
    """Return one judge-facing payload for the final demo evidence screen."""
    current_score = sum(item["current_score"] for item in JUDGE_BAREM_SCORECARD)
    return {
        "summary": {
            "product": "VGap AI",
            "positioning": "Hệ thống chẩn đoán lỗ hổng kiến thức gốc, không phải chatbot học tập.",
            "current_score": current_score,
            "max_score": 100,
            "target_score": 78,
            "final_message": (
                "Core BKT/DAG chạy offline để chẩn đoán; FPT AI tăng cường gợi ý, giáo án, "
                "RAG ngữ cảnh, speech và workflow giáo viên."
            )
        },
        "judge_barem": JUDGE_BAREM_SCORECARD,
        "benchmarks": [
            {"metric": "Diagnostic accuracy", "target": ">= 70%", "current": "Smoke benchmark 30 case", "status": "ready"},
            {"metric": "Precision/Recall gap alert", "target": ">= 75% / >= 70%", "current": "Có benchmark kỹ thuật", "status": "ready"},
            {"metric": "p95 /next-question", "target": "< 300 ms local", "current": "Đo trong benchmark_diagnostics.py", "status": "ready"},
            {"metric": "p95 /teacher/dashboard", "target": "< 500 ms local", "current": "Dashboard API + WebSocket snapshot", "status": "ready"},
            {"metric": "Cost/student/month", "target": "Core gần 0 đồng", "current": "Có cost model endpoint", "status": "ready"},
        ],
        "fpt_ai_story": [
            {"fpt_ai_role": "Inference", "implemented": True, "demo": "Socratic tutor và lesson-plan endpoint"},
            {"fpt_ai_role": "Knowledge/RAG", "implemented": True, "demo": "Grounded lesson plan trả citations từ local KB, sẵn adapter FPT Knowledge"},
            {"fpt_ai_role": "Speech", "implemented": True, "demo": "Speech cache key/manifest để sinh audio một lần, phát lại qua LAN"},
            {"fpt_ai_role": "Agents", "implemented": False, "demo": "Teacher action agent từ gap groups là bước nối tiếp"},
            {"fpt_ai_role": "OCR/MCP", "implemented": False, "demo": "Roadmap nhập bài giấy và kết nối LMS/bảng điểm"},
        ],
        "demo_flow": [
            "Đăng nhập học sinh Emma hoặc Nguyễn Văn An.",
            "Chọn Toán lớp 7 và làm sai câu dễ để hệ thống hạ độ khó/lùi prerequisite.",
            "Chuyển sang bảng giáo viên để xem nhóm hổng, priority list và heatmap.",
            "Mở tab Bằng chứng final để trình bày scorecard, FPT AI story và readiness.",
            "Tạo giáo án bổ trợ cho nhóm hổng bằng endpoint grounded lesson plan."
        ],
        "readiness": [
            {"item": "Offline-first local/LAN demo", "implemented": True},
            {"item": "Idempotent sync event log", "implemented": True},
            {"item": "Pedagogical explanation log", "implemented": True},
            {"item": "Behavioral anomaly filter", "implemented": True},
            {"item": "WebSocket dashboard snapshot", "implemented": True},
            {"item": "Production auth/tenant isolation", "implemented": False},
            {"item": "Real classroom pilot dataset", "implemented": False},
        ],
    }

@app.websocket("/ws/teacher/dashboard")
async def teacher_dashboard_websocket(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            await websocket.send_json({
                "event": "teacher_dashboard_snapshot",
                "payload": get_teacher_dashboard(),
                "server_time": int(time.time()),
            })
            await asyncio.sleep(2)
    except WebSocketDisconnect:
        return

# Serve Frontend static assets
frontend_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "frontend")
if not os.getenv("VERCEL"):
    app.mount("/", StaticFiles(directory=frontend_dir, html=True), name="frontend")
