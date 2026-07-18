import unittest

from backend.app import (
    get_cost_model,
    get_final_scorecard,
    get_fpt_ai_coverage,
    get_health,
    get_safety_evidence,
)


class TestJudgeEvidenceEndpoints(unittest.TestCase):
    def test_health_endpoint_reports_backend_ready(self):
        payload = get_health()

        self.assertEqual(payload["status"], "ok")
        self.assertEqual(payload["service"], "VGap AI Backend")

    def test_fpt_ai_coverage_lists_implemented_and_planned_capabilities(self):
        payload = get_fpt_ai_coverage()

        self.assertGreaterEqual(payload["summary"]["implemented_count"], 1)
        capabilities = {item["capability"] for item in payload["capabilities"]}
        self.assertIn("FPT AI Inference", capabilities)
        self.assertIn("FPT AI Speech", capabilities)
        self.assertIn("FPT AI OCR/Vision", capabilities)

    def test_cost_model_returns_per_student_month_estimate(self):
        payload = get_cost_model(students=1000)

        self.assertEqual(payload["students"], 1000)
        self.assertEqual(payload["monthly"]["core_bkt_dag_cost_vnd"], 0)
        self.assertGreater(payload["monthly"]["estimated_cost_per_student_vnd"], 0)
        self.assertIn("10k_users", payload["scale_story"])

    def test_safety_evidence_marks_remaining_production_gaps(self):
        payload = get_safety_evidence()

        self.assertGreater(payload["summary"]["implemented_controls"], 0)
        self.assertLessEqual(payload["summary"]["implemented_controls"], payload["summary"]["total_controls"])
        self.assertTrue(any(not item["implemented"] for item in payload["controls"]))

    def test_final_scorecard_groups_judge_barem_and_demo_actions(self):
        payload = get_final_scorecard()

        self.assertGreaterEqual(payload["summary"]["target_score"], 75)
        self.assertIn("judge_barem", payload)
        self.assertIn("demo_flow", payload)
        self.assertIn("readiness", payload)
        self.assertTrue(any(item["implemented"] for item in payload["readiness"]))
        self.assertTrue(any(item["fpt_ai_role"] == "Knowledge/RAG" for item in payload["fpt_ai_story"]))


if __name__ == "__main__":
    unittest.main()
