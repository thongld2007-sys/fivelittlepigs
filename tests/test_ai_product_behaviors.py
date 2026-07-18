import json
import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient

from backend.app import app


class _FakeAIResult:
    def __init__(self, content):
        self.content = content
        self.model = "DeepSeek-V4-Flash"
        self.usage = {"total_tokens": 42}


class TestAIProductBehaviors(unittest.TestCase):
    def setUp(self):
        from backend.app import fpt_ai_client
        fpt_ai_client.api_key = "test-key"
        fpt_ai_client.model = "test-model"
        fpt_ai_client.base_url = "https://example.com"
        
        self.client = TestClient(app)
        self.client.post("/api/students", json={
            "student_id": "ai_behavior_student",
            "name": "AI Behavior Student",
            "grade": 7,
        })

    def test_tutor_intro_is_constrained_to_learning_assistant_identity(self):
        response = self.client.post("/api/ai/student/ai_behavior_student/tutor", json={
            "question_id": "q_math_g7_1",
            "message": "Bạn là ai, giới thiệu đi",
        })

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["provider"], "PorcusAI policy guardrail")
        self.assertIn("AI trợ lý học tập PorcusAI", payload["content"])

    def test_tutor_rejects_non_learning_noise_without_provider_call(self):
        with patch("backend.app.fpt_ai_client.complete") as complete:
            response = self.client.post("/api/ai/student/ai_behavior_student/tutor", json={
                "question_id": "q_math_g7_1",
                "message": "asdf lol???",
            })

        self.assertEqual(response.status_code, 200)
        self.assertIn("chỉ hỗ trợ nội dung học tập", response.json()["content"])
        complete.assert_not_called()

    def test_tutor_mode_prompt_is_not_misclassified_as_intro(self):
        ai_reply = "Lỗi sai là cộng mẫu số trực tiếp. Hãy quy đồng mẫu trước."
        with patch("backend.app.fpt_ai_client.complete", return_value=_FakeAIResult(ai_reply)) as complete:
            response = self.client.post("/api/ai/student/ai_behavior_student/tutor", json={
                "question_id": "q_math_g7_1",
                "message": (
                    "Chế độ AI: Tìm lỗi sai.\n"
                    "Yêu cầu: Hãy tìm lỗi sai trong bài làm.\n"
                    "Nội dung học sinh gửi: 1/2 + 2/3 = 3/5"
                ),
            })

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["provider"], "FPT AI Factory")
        self.assertIn("Lỗi sai", response.json()["content"])
        complete.assert_called_once()

    def test_ai_question_generator_requires_three_level_difficulty_schema(self):
        generated = {
            "questions": [{
                "id": "ai_math_g7_apply_01",
                "skill_id": "MATH_G7",
                "difficulty_level": 3,
                "difficulty": "Vận dụng",
                "text": "Tính 1/2 + (-2/3).",
                "options": [
                    {"key": "A", "text": "-1/6"},
                    {"key": "B", "text": "1/6"},
                    {"key": "C", "text": "-7/6"},
                    {"key": "D", "text": "7/6"},
                ],
                "correct_answer": "A",
                "hint": "Quy đồng mẫu số trước.",
                "explanation": "1/2 = 3/6 và -2/3 = -4/6 nên tổng là -1/6.",
            }]
        }

        with patch("backend.app.fpt_ai_client.complete", return_value=_FakeAIResult(json.dumps(generated, ensure_ascii=False))):
            response = self.client.post("/api/ai/student/ai_behavior_student/generate-question", json={
                "subject": "Toán",
                "grade": 7,
                "skill_id": "MATH_G7",
                "difficulty_level": 3,
                "count": 1,
            })

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["difficulty_policy"]["1"], "Nhận biết")
        self.assertEqual(payload["difficulty_policy"]["2"], "Thông hiểu")
        self.assertEqual(payload["difficulty_policy"]["3"], "Vận dụng")
        self.assertEqual(payload["questions"][0]["difficulty"], "Vận dụng")

    def test_work_analyzer_returns_misconception_and_remediation_pack(self):
        response = self.client.post("/api/ai/student/ai_behavior_student/analyze-work", json={
            "mode": "find_error",
            "subject": "Toán",
            "grade": 7,
            "skill_id": "MATH_G7",
            "work_text": "1/2 + 2/3 = 3/5",
        })

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        analysis = payload["analysis"]
        self.assertIn("misconception", analysis)
        self.assertIn("remediation_pack", analysis)
        self.assertIn("measurement", analysis)
        self.assertIn("Cộng tử", analysis["misconception"]["detected_error"])
        self.assertGreaterEqual(len(analysis["remediation_pack"]), 3)
        self.assertIn("Rule engine", analysis["why_ai_is_needed"])

    def test_teacher_learning_path_returns_structured_recommendation(self):
        ai_path = {
            "summary": "Ưu tiên lùi về Quy đồng mẫu số trước khi quay lại số hữu tỉ.",
            "steps": [{
                "skill_id": "MATH_G5",
                "skill_name": "Quy đồng mẫu số phân số",
                "recommended_difficulty": "Nhận biết",
                "action": "Dạy lại 10 phút rồi giao 3 câu nền.",
                "success_signal": "Đúng 2/3 câu liên tiếp.",
            }],
            "teacher_notes": "Gom em này vào nhóm hổng phân số lớp 5.",
        }

        with patch("backend.app.fpt_ai_client.complete", return_value=_FakeAIResult(json.dumps(ai_path, ensure_ascii=False))):
            response = self.client.get("/api/ai/teacher/student/ai_behavior_student/learning-path?target_skill=MATH_G7")

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["provider"], "FPT AI Factory")
        self.assertEqual(payload["learning_path"]["steps"][0]["recommended_difficulty"], "Nhận biết")
        self.assertIn("mastery_items", payload["context"])


if __name__ == "__main__":
    unittest.main()
