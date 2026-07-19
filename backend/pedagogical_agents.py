"""Grounded agent workflows with persisted, inspectable traces."""

import json

from backend.config import Config
from backend.database import (
    get_common_wrong_questions,
    get_gap_cohort,
    get_recent_wrong_count,
    get_student_mastery,
    record_agent_run,
    record_ai_usage,
    db_session,
)
from backend.fpt_ai import fpt_ai_client
from backend.knowledge_graph import KNOWLEDGE_GRAPH
from backend.models import ChatMessage
from backend.rag import rag_retriever


def _question_bank() -> list[dict]:
    with open(Config.QUESTIONS_JSON_PATH, "r", encoding="utf-8") as file:
        return json.load(file)


class SocraticPedagogicalAgent:
    def run(self, *, student_id: str, question: dict, message: str) -> dict:
        skill_id = question["skill_id"]
        mastery = get_student_mastery(student_id, skill_id)
        wrong_count = get_recent_wrong_count(student_id, skill_id)
        sources = rag_retriever.retrieve(f"{question.get('text', '')} {message}", skill_id=skill_id)
        context = "\n".join(f"[{item['id']}] {item['content']}" for item in sources)
        system = (
            "Bạn là Socratic Pedagogical Agent cho học sinh Việt Nam. Chỉ dùng CONTEXT đã truy xuất. "
            "Không đưa đáp án cuối, không làm hộ. Mỗi lượt: (1) xác định bước có thể sai, "
            "(2) đặt đúng một câu hỏi gợi mở, (3) đề nghị một phép kiểm tra ngắn. "
            "Nếu context không đủ hoặc không liên quan trực tiếp, hãy nói rõ cần giáo viên hỗ trợ để tránh sai lệch tri thức. "
            "KHÔNG ĐƯỢC sinh câu hỏi bị trùng lặp hoặc lặp lại từ lịch sử chat. "
            "TUÂN THỦ TUYỆT ĐỐI ĐỘ CHÍNH XÁC TRI THỨC và chỉ dẫn của CONTEXT.\nCONTEXT:\n" + context
        )
        prompt = (
            f"Kỹ năng={skill_id}; mastery={mastery:.3f}; số lần sai gần đây={wrong_count}. "
            f"Câu hỏi={question.get('text', '')}. Học sinh nói: {message}"
        )
        result = fpt_ai_client.complete(system_prompt=system, user_prompt=prompt)
        record_ai_usage("socratic_tutor", result.model, result.usage, result.latency_ms)
        trace = [
            {"step": "diagnose", "mastery": round(mastery, 4), "recent_wrong": wrong_count},
            {"step": "retrieve", "source_ids": [item["id"] for item in sources]},
            {"step": "socratic_generate", "answer_policy": "no-final-answer"},
        ]
        source_summary = [
            {"id": item["id"], "title": item["title"], "source": item["source"]}
            for item in sources
        ]
        run_id = record_agent_run(
            "socratic_tutor", result.model, trace, source_summary, student_id=student_id
        )
        return {
            "content": result.content,
            "model": result.model,
            "usage": result.usage,
            "latency_ms": result.latency_ms,
            "agent_run_id": run_id,
            "agent_trace": trace,
            "sources": source_summary,
        }


class LessonPlannerAgent:
    def run(self, *, skill_id: str, group_context: str = "") -> dict:
        skill = KNOWLEDGE_GRAPH[skill_id]
        gap_rows = get_gap_cohort(skill_id)
        wrong_rows = get_common_wrong_questions(skill_id)
        bank = {item["id"]: item for item in _question_bank()}
        common_errors = [
            {"question": bank.get(row[0], {}).get("text", row[0]), "wrong_count": row[1]}
            for row in wrong_rows
        ]
        sources = rag_retriever.retrieve(f"{skill['name']} giáo án đánh giá", skill_id=skill_id)
        context = "\n".join(f"[{item['id']}] {item['content']}" for item in sources)
        system = (
            "Bạn là AI Lesson Planner Agent theo GDPT 2018. Tạo giáo án can thiệp 15 phút từ dữ liệu nhóm thật. "
            "Văn bản thuần gồm: Mục tiêu đo được; Chẩn đoán lỗi chung; Khởi động; Hoạt động phân hóa; "
            "2 câu exit ticket; Tiêu chí thành công. "
            "TUYỆT ĐỐI KHÔNG bịa số liệu, nguồn hay kiến thức sai lệch. Bám sát CONTEXT RAG để đảm bảo tính chuẩn xác và khoa học.\nCONTEXT:\n" + context
        )
        prompt = json.dumps(
            {
                "skill": skill,
                "gap_student_count": len(gap_rows),
                "mastery_values": [round(row[2], 3) for row in gap_rows],
                "common_errors": common_errors,
                "teacher_context": group_context,
            },
            ensure_ascii=False,
        )
        result = fpt_ai_client.complete(system_prompt=system, user_prompt=prompt)
        record_ai_usage("lesson_planner", result.model, result.usage, result.latency_ms)
        trace = [
            {"step": "scan_database", "gap_students": len(gap_rows)},
            {"step": "aggregate_errors", "patterns": len(common_errors)},
            {"step": "retrieve", "source_ids": [item["id"] for item in sources]},
            {"step": "generate_lesson_plan", "duration_minutes": 15},
        ]
        source_summary = [
            {"id": item["id"], "title": item["title"], "source": item["source"]}
            for item in sources
        ]
        run_id = record_agent_run("lesson_planner", result.model, trace, source_summary)
        return {
            "content": result.content,
            "model": result.model,
            "usage": result.usage,
            "latency_ms": result.latency_ms,
            "agent_run_id": run_id,
            "cohort": {
                "skill_id": skill_id,
                "student_count": len(gap_rows),
                "common_errors": common_errors,
            },
            "agent_trace": trace,
            "sources": source_summary,
        }


socratic_agent = SocraticPedagogicalAgent()
lesson_planner_agent = LessonPlannerAgent()

class GeneralLearningAssistant:
    def run(self, *, student_id: str, mode: str, message: str) -> dict:
        prompts = {
            "explain": "Bạn là gia sư AI PorcusAI. Hãy giải thích nội dung học sinh gửi một cách dễ hiểu, có ví dụ minh họa nếu cần. Lời lẽ thân thiện, khuyến khích. Đảm bảo độ chính xác tuyệt đối của tri thức.",
            "find_error": "Bạn là gia sư AI PorcusAI. Hãy tìm lỗi sai trong bài làm của học sinh (nếu có). Chỉ ra bước sai, giải thích vì sao sai và gợi ý cách sửa từng bước. Cần độ chính xác tri thức cao nhất.",
            "similar_question": "Bạn là gia sư AI PorcusAI. Dựa trên nội dung học sinh gửi, hãy tạo ra MỘT câu hỏi tương tự cùng độ khó để học sinh luyện tập. KHÔNG trùng lặp hoặc lặp lại các câu hỏi đã có trong lịch sử trò chuyện hoặc ngữ cảnh của học sinh. Phải đảm bảo đề bài và đáp án đúng 100% về mặt tri thức.",
            "step_hint": "Bạn là gia sư AI PorcusAI. Hãy đưa ra gợi ý từng bước (Socratic method) để học sinh tự tìm ra đáp án, tuyệt đối KHÔNG nói thẳng kết quả cuối cùng. Gợi mở chính xác tri thức.",
            "summarize": "Bạn là gia sư AI PorcusAI. Hãy tóm tắt nội dung học sinh gửi thành các ý chính ngắn gọn, dễ nhớ. Độ chính xác tri thức được ưu tiên hàng đầu."
        }
        
        formatting_rule = (
            "\n\nQUY TẮC TRÌNH BÀY & CHẤT LƯỢNG:\n"
            "1. Cực kỳ ngắn gọn, súc tích, đi thẳng vào vấn đề.\n"
            "2. Trình bày bố cục rõ ràng, chia đoạn hoặc dùng gạch đầu dòng gọn gàng.\n"
            "3. Tuyệt đối không dùng các ký tự thừa thãi như ###, --- hoặc lạm dụng in đậm (**) nếu không thực sự cần nhấn mạnh.\n"
            "4. ĐỘ CHÍNH XÁC TRI THỨC: Phải đảm bảo mọi thông tin đưa ra chính xác 100%, không bịa đặt kiến thức không có cơ sở.\n"
            "5. KHÔNG LẶP CÂU HỎI: Khi sinh câu hỏi hoặc bài tập mới, đối chiếu với lịch sử hội thoại để tạo ra câu hỏi có số liệu và nội dung hoàn toàn mới, không lặp lại câu hỏi cũ."
        )
        
        system = prompts.get(mode, prompts["explain"]) + formatting_rule
        
        with db_session() as session:
            recent_msgs = session.query(ChatMessage).filter(
                ChatMessage.student_id == student_id
            ).order_by(ChatMessage.created_at.desc()).limit(20).all()
            
            history = [{"role": msg.role, "content": msg.content} for msg in reversed(recent_msgs)]
            
            result = fpt_ai_client.complete(system_prompt=system, user_prompt=message, history=history)
            
            user_msg = ChatMessage(student_id=student_id, role="user", content=message, mode=mode)
            ai_msg = ChatMessage(student_id=student_id, role="robot", content=result.content, mode=mode)
            session.add(user_msg)
            session.add(ai_msg)
            
        record_ai_usage("general_tutor", result.model, result.usage, result.latency_ms)
        
        trace = [
            {"step": "general_chat", "mode": mode}
        ]
        run_id = record_agent_run(
            "general_tutor", result.model, trace, [], student_id=student_id
        )
        return {
            "content": result.content,
            "model": result.model,
            "usage": result.usage,
            "latency_ms": result.latency_ms,
            "agent_run_id": run_id,
            "agent_trace": trace,
            "sources": [],
        }

general_assistant = GeneralLearningAssistant()
