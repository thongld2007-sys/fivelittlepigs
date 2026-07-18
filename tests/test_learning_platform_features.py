import os
import unittest

from fastapi.testclient import TestClient

from backend.app import app
from backend.config import Config
from backend.database import get_db_connection, init_db


class TestLearningPlatformFeatures(unittest.TestCase):
    def setUp(self):
        if os.path.exists(Config.DB_PATH):
            os.remove(Config.DB_PATH)
        init_db()
        self.client = TestClient(app)

    def test_student_course_assignment_and_reward_views_are_persisted(self):
        courses = self.client.get("/api/students/emma_std_01/courses")
        assignments = self.client.get("/api/students/emma_std_01/assignments")
        profile = self.client.get("/api/students/emma_std_01/profile")

        self.assertEqual(courses.status_code, 200)
        self.assertGreaterEqual(len(courses.json()["courses"]), 4)
        self.assertTrue(courses.json()["courses"][0]["skills"])
        self.assertEqual(assignments.status_code, 200)
        self.assertGreaterEqual(len(assignments.json()["assignments"]), 2)
        self.assertEqual(profile.status_code, 200)
        self.assertIn("xp", profile.json()["rewards"])

    def test_demo_accounts_use_server_side_password_sessions(self):
        login = self.client.post("/api/auth/login", json={
            "username": "emma_std_01", "password": "123456", "role": "student"
        })
        self.assertEqual(login.status_code, 200)
        token = login.json()["access_token"]
        me = self.client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
        self.assertEqual(me.status_code, 200)
        self.assertEqual(me.json()["user"]["role"], "student")
        self.client.post("/api/auth/logout", headers={"Authorization": f"Bearer {token}"})
        self.assertEqual(
            self.client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"}).status_code,
            401,
        )

    def test_student_can_register_and_login_with_persisted_profile(self):
        registration = self.client.post("/api/auth/student/register", json={
            "username": "minh.anh07",
            "password": "HocTot2026",
            "name": "Nguyễn Minh Anh",
            "grade": 7,
        })
        self.assertEqual(registration.status_code, 201)
        student_id = registration.json()["student"]["student_id"]
        self.assertTrue(registration.json()["access_token"])

        profile = self.client.get(f"/api/students/{student_id}/profile")
        courses = self.client.get(f"/api/students/{student_id}/courses")
        login = self.client.post("/api/auth/login", json={
            "username": "minh.anh07", "password": "HocTot2026", "role": "student"
        })
        self.assertEqual(profile.status_code, 200)
        self.assertEqual(profile.json()["student"]["name"], "Nguyễn Minh Anh")
        self.assertGreaterEqual(len(courses.json()["courses"]), 4)
        self.assertEqual(login.status_code, 200)
        self.assertEqual(login.json()["user"]["student_id"], student_id)

        conn = get_db_connection()
        mastery_count = conn.execute(
            "SELECT COUNT(*) FROM student_mastery WHERE student_id=?", (student_id,)
        ).fetchone()[0]
        skill_count = conn.execute("SELECT COUNT(*) FROM skills").fetchone()[0]
        conn.close()
        self.assertEqual(mastery_count, skill_count)

    def test_registration_rejects_duplicate_username_and_weak_password(self):
        weak = self.client.post("/api/auth/student/register", json={
            "username": "newstudent", "password": "123456", "name": "Học sinh mới", "grade": 7
        })
        self.assertEqual(weak.status_code, 422)
        payload = {"username": "unique.student", "password": "Secure2026", "name": "Học sinh mới", "grade": 7}
        self.assertEqual(self.client.post("/api/auth/student/register", json=payload).status_code, 201)
        self.assertEqual(self.client.post("/api/auth/student/register", json=payload).status_code, 409)

    def test_response_updates_rewards_in_same_workflow(self):
        before = self.client.get("/api/students/emma_std_01/profile").json()["rewards"]
        response = self.client.post("/api/student/emma_std_01/submit", json={
            "question_id": "q_math_g7_1",
            "selected_option": "A",
            "event_id": "reward-test-event",
            "response_time_ms": 18000,
        })
        after = self.client.get("/api/students/emma_std_01/profile").json()["rewards"]

        self.assertEqual(response.status_code, 200)
        self.assertGreater(after["xp"], before["xp"])
        self.assertEqual(response.json()["rewards"]["xp"], after["xp"])

    def test_teacher_can_create_real_assignment_for_gap_group(self):
        response = self.client.post("/api/teacher/assignments", json={
            "skill_id": "MATH_G7",
            "student_ids": ["an_01", "emma_std_01"],
            "title": "Ôn số hữu tỉ",
            "question_count": 6,
        })

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["assigned_student_count"], 2)
        conn = get_db_connection()
        target_count = conn.execute(
            "SELECT COUNT(*) FROM assignment_targets WHERE assignment_id=?",
            (response.json()["assignment_id"],),
        ).fetchone()[0]
        conn.close()
        self.assertEqual(target_count, 2)

    def test_diagnostic_tree_and_classes_come_from_database(self):
        classes = self.client.get("/api/teacher/classes")
        diagnostic = self.client.get(
            "/api/teacher/students/an_01/diagnostic-profile?target_skill=MATH_G7"
        )

        self.assertEqual(classes.status_code, 200)
        self.assertGreaterEqual(classes.json()["classes"][0]["student_count"], 1)
        self.assertEqual(diagnostic.status_code, 200)
        self.assertTrue(diagnostic.json()["nodes"])
        self.assertTrue(diagnostic.json()["edges"])
        self.assertEqual(diagnostic.json()["nodes"][0]["id"], "MATH_G7")


if __name__ == "__main__":
    unittest.main()
