import os
import shutil
import sys
import time
import unittest

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.config import Config
from backend.database import (
    get_db_connection,
    get_student_mastery,
    init_db,
    list_unsynced_events,
    mark_events_synced,
)
from backend.app import (
    AnswerSubmission,
    GroundedLessonPlanRequest,
    SpeechCacheRequest,
    ai_grounded_lesson_plan,
    create_speech_cache,
    get_student_explanations,
    submit_answer,
)


class TestProductionFeatures(unittest.TestCase):
    def setUp(self):
        if os.path.exists(Config.DB_PATH):
            os.remove(Config.DB_PATH)
        init_db()

    def tearDown(self):
        speech_cache_dir = os.path.join(Config.DATA_DIR, "speech_cache")
        if os.path.exists(speech_cache_dir):
            shutil.rmtree(speech_cache_dir)

    def test_submit_is_idempotent_and_creates_unsynced_event(self):
        first = submit_answer(
            "emma_std_01",
            AnswerSubmission(
                question_id="q_math_g7_1",
                selected_option="A",
                event_id="device-1-evt-001",
                response_time_ms=18_000,
                client_timestamp=1_700_000_000,
            ),
        )
        second = submit_answer(
            "emma_std_01",
            AnswerSubmission(
                question_id="q_math_g7_1",
                selected_option="A",
                event_id="device-1-evt-001",
                response_time_ms=18_000,
                client_timestamp=1_700_000_000,
            ),
        )

        self.assertTrue(second["idempotent_replay"])
        self.assertEqual(first["response_event_id"], second["response_event_id"])

        conn = get_db_connection()
        response_count = conn.execute(
            "SELECT COUNT(*) FROM responses WHERE event_id = ?",
            ("device-1-evt-001",),
        ).fetchone()[0]
        conn.close()
        self.assertEqual(response_count, 1)

        events = list_unsynced_events(limit=10)
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0]["event_id"], "device-1-evt-001")
        self.assertEqual(events[0]["payload"]["question_id"], "q_math_g7_1")

        mark_events_synced(["device-1-evt-001"])
        self.assertEqual(list_unsynced_events(limit=10), [])

    def test_fast_correct_hard_answer_is_downweighted_as_anomaly(self):
        mastery_before = get_student_mastery("emma_std_01", "MATH_G7")
        result = submit_answer(
            "emma_std_01",
            AnswerSubmission(
                question_id="q_math_g7_3",
                selected_option="D",
                event_id="fast-hard-correct",
                response_time_ms=2_000,
            ),
        )
        mastery_after = get_student_mastery("emma_std_01", "MATH_G7")

        self.assertTrue(result["anomaly"]["flagged"])
        self.assertEqual(result["anomaly"]["bkt_weight"], 0.25)
        self.assertLess(mastery_after - mastery_before, 0.1)

    def test_explanation_log_describes_mastery_and_routing_reason(self):
        submit_answer(
            "emma_std_01",
            AnswerSubmission(
                question_id="q_math_g7_1",
                selected_option="B",
                event_id=f"explain-{int(time.time())}",
                response_time_ms=22_000,
            ),
        )

        payload = get_student_explanations("emma_std_01")

        self.assertGreaterEqual(len(payload["explanations"]), 1)
        latest = payload["explanations"][0]
        self.assertIn("explanation_text", latest)
        self.assertIn("Xác suất thành thạo", latest["explanation_text"])
        self.assertIn("next_skill_id", latest)

    def test_grounded_lesson_plan_returns_citations(self):
        payload = ai_grounded_lesson_plan(
            GroundedLessonPlanRequest(skill_id="MATH_G7", group_context="Sai phân số âm")
        )

        self.assertIn("content", payload)
        self.assertGreaterEqual(len(payload["citations"]), 1)
        self.assertEqual(payload["citations"][0]["source_type"], "local_question_bank")

    def test_speech_cache_returns_stable_cache_key_without_audio_generation(self):
        first = create_speech_cache(
            SpeechCacheRequest(text="Hãy quy đồng mẫu số trước.", question_id="q_math_g7_1")
        )
        second = create_speech_cache(
            SpeechCacheRequest(text="Hãy quy đồng mẫu số trước.", question_id="q_math_g7_1")
        )

        self.assertEqual(first["cache_key"], second["cache_key"])
        self.assertEqual(first["status"], "pending_provider_generation")
        self.assertEqual(first["cache_policy"], "generate_once_then_serve_from_school_lan")


if __name__ == "__main__":
    unittest.main()
