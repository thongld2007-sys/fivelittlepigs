import os
import sys
import unittest
import sqlite3
import random

# Add workspace to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.config import Config
from backend.database import init_db, get_student_mastery, update_student_mastery, record_response
from backend.diagnostic_engine import BKTProcessor, get_next_question_difficulty_and_skill

class TestAdaptiveDiagnostics(unittest.TestCase):
    def setUp(self):
        # Re-initialize database
        if os.path.exists(Config.DB_PATH):
            try:
                os.remove(Config.DB_PATH)
            except PermissionError:
                pass
        init_db()
        
    def test_bkt_updating_correct(self):
        p_initial = 0.50
        p_new = BKTProcessor.calculate_posterior(p_initial, is_correct=True)
        self.assertGreater(p_new, p_initial)
        
    def test_bkt_updating_incorrect(self):
        p_initial = 0.50
        p_new = BKTProcessor.calculate_posterior(p_initial, is_correct=False)
        self.assertLess(p_new, p_initial)
        
    def test_initial_difficulty_is_random_2_or_3(self):
        student_id = "test_std_initial"
        skill_id = "MATH_G7"
        
        # Call multiple times to verify it returns either 2 or 3
        difficulties = set()
        for _ in range(20):
            _, diff = get_next_question_difficulty_and_skill(student_id, skill_id)
            difficulties.add(diff)
            
        # Should contain at least 2 or 3 (both can be returned)
        self.assertTrue(difficulties.issubset({2, 3}))
        
    def test_streak_increases_level_3_probability(self):
        student_id = "test_std_streak"
        skill_id = "MATH_G7"
        
        # Record 3 consecutive correct level 3 answers to create a streak
        import time
        for i in range(3):
            record_response(student_id, f"q_{i}", skill_id, 3, True, int(time.time()) + i)
            
        # Draw next difficulty 100 times, count level 3
        l3_count = 0
        for _ in range(100):
            _, diff = get_next_question_difficulty_and_skill(student_id, skill_id)
            if diff == 3:
                l3_count += 1
                
        # With streak >= 3, level 3 probability is 90%, so count should be high
        self.assertGreaterEqual(l3_count, 80)
        
    def test_incorrect_under_threshold_drops_to_1(self):
        student_id = "test_std_drop1"
        skill_id = "MATH_G7"
        
        # Student has only 1 correct answer (under threshold of 3)
        import time
        record_response(student_id, "q_c1", skill_id, 2, True, int(time.time()))
        # Student gets a level 3 question wrong
        record_response(student_id, "q_w1", skill_id, 3, False, int(time.time()) + 1)
        
        _, next_diff = get_next_question_difficulty_and_skill(student_id, skill_id)
        # Should jump down directly to level 1
        self.assertEqual(next_diff, 1)
        
    def test_incorrect_above_threshold_keeps_or_drops_by_one_level(self):
        student_id = "test_std_drop_one"
        skill_id = "MATH_G7"
        
        # Student has 3 correct answers (reaches threshold)
        import time
        for i in range(3):
            record_response(student_id, f"q_c{i}", skill_id, 2, True, int(time.time()) + i)
            
        # Student gets a level 3 question wrong
        record_response(student_id, "q_w1", skill_id, 3, False, int(time.time()) + 10)
        
        next_difficulties = set()
        for _ in range(40):
            _, next_diff = get_next_question_difficulty_and_skill(student_id, skill_id)
            next_difficulties.add(next_diff)

        # With enough prior correct answers, one slip should keep level 3
        # or decrease by exactly one level to 2, never jump to level 1.
        self.assertTrue(next_difficulties.issubset({2, 3}))
        self.assertNotIn(1, next_difficulties)
        
    def test_incorrect_at_level_1_shifts_to_prerequisite(self):
        student_id = "test_std_prereq"
        skill_id = "MATH_G7" # Has prerequisites MATH_G6 and MATH_G5
        
        # Student gets a level 1 question wrong
        import time
        record_response(student_id, "q_w1", skill_id, 1, False, int(time.time()))
        
        next_skill, _ = get_next_question_difficulty_and_skill(student_id, skill_id)
        # Should shift to a prerequisite of MATH_G7: either MATH_G6 or MATH_G5
        self.assertIn(next_skill, ["MATH_G6", "MATH_G5"])

    def test_backend_question_payload_contains_wrong_answer_feedback(self):
        from backend.app import get_next_question

        payload = get_next_question("emma_std_01", current_skill="MATH_G7")
        question = payload["question"]

        self.assertIn("distractor_explanations", question)
        self.assertIn("hint", question)
        self.assertIn("visual_hint", question)
        self.assertTrue(question["distractor_explanations"])

    def test_backend_avoids_repeating_answered_question_when_possible(self):
        from backend.app import get_next_question

        student_id = "emma_std_01"
        skill_id = "MATH_G7"

        first = get_next_question(student_id, current_skill=skill_id)["question"]
        record_response(student_id, first["id"], skill_id, first["difficulty_level"], True, 100)

        # Force the next selection rules to stay on the same skill/difficulty level.
        second = get_next_question(student_id, current_skill=skill_id)["question"]
        self.assertNotEqual(first["id"], second["id"])

if __name__ == "__main__":
    unittest.main()
