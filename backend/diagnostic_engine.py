"""Offline Bayesian Knowledge Tracing and adaptive routing."""

from __future__ import annotations

from dataclasses import dataclass

import backend.database as db
from backend.knowledge_graph import KnowledgeGraph


@dataclass(frozen=True)
class BKTUpdate:
    previous_probability: float
    new_probability: float
    consecutive_fails: int


class BKTProcessor:
    P_L0 = 0.5
    P_G = 0.2
    P_S = 0.1
    P_T = 0.2
    THRESHOLD_MASTERED = 0.85
    THRESHOLD_GAP = 0.40

    @classmethod
    def calculate_new_probability(cls, current_prob: float, is_correct: bool) -> float:
        if not 0 <= current_prob <= 1:
            raise ValueError("current_prob must be between 0 and 1")
        if is_correct:
            numerator = current_prob * (1 - cls.P_S)
            denominator = numerator + (1 - current_prob) * cls.P_G
        else:
            numerator = current_prob * cls.P_S
            denominator = numerator + (1 - current_prob) * (1 - cls.P_G)
        posterior = numerator / denominator if denominator else 0.0
        return posterior + (1 - posterior) * cls.P_T

    @classmethod
    def evaluate_answer(cls, student_id: str, skill_id: str, is_correct: bool) -> BKTUpdate:
        mastery = db.get_student_mastery(student_id, skill_id)
        previous = mastery["current_probability"] if mastery else cls.P_L0
        old_fails = mastery["consecutive_fails"] if mastery else 0
        fails = 0 if is_correct else old_fails + 1
        return BKTUpdate(previous, cls.calculate_new_probability(previous, is_correct), fails)

    @classmethod
    def choose_prerequisite(cls, student_id: str, skill_id: str) -> str | None:
        prerequisites = KnowledgeGraph.get_prerequisites(skill_id)
        if not prerequisites:
            return None
        ranked = []
        for order, prerequisite in enumerate(prerequisites):
            state = db.get_student_mastery(student_id, prerequisite)
            probability = state["current_probability"] if state else cls.P_L0
            tested = state is not None
            ranked.append((tested, probability, order, prerequisite))
        # Diagnose an untested prerequisite first, then the weakest known one.
        return min(ranked)[3]

    @classmethod
    def diagnose_next_step(
        cls, student_id: str, current_skill_id: str, probability: float | None = None
    ) -> dict:
        if not KnowledgeGraph.is_valid_skill(current_skill_id):
            raise ValueError(f"Unknown skill: {current_skill_id}")
        mastery = db.get_student_mastery(student_id, current_skill_id)
        current_prob = probability if probability is not None else (
            mastery["current_probability"] if mastery else None
        )
        if current_prob is None:
            return {
                "action": "CONTINUE_CURRENT",
                "target_skill": current_skill_id,
                "probability": cls.P_L0,
                "reason": "Chưa có dữ liệu lịch sử; bắt đầu kiểm tra kỹ năng hiện tại.",
            }
        if current_prob >= cls.THRESHOLD_MASTERED:
            return {
                "action": "MASTERED",
                "target_skill": None,
                "probability": current_prob,
                "reason": f"Xác suất {current_prob:.2f} đạt ngưỡng thành thạo 0.85.",
            }
        if current_prob < cls.THRESHOLD_GAP:
            prerequisite = cls.choose_prerequisite(student_id, current_skill_id)
            if prerequisite:
                return {
                    "action": "DOWNGRADE_DIAGNOSTIC",
                    "target_skill": prerequisite,
                    "probability": current_prob,
                    "reason": (
                        f"Xác suất {current_prob:.2f} dưới ngưỡng 0.40; "
                        f"kiểm tra kỹ năng tiên quyết {prerequisite}."
                    ),
                }
            return {
                "action": "ROOT_GAP",
                "target_skill": current_skill_id,
                "probability": current_prob,
                "reason": "Đã xác định lỗ hổng gốc ở kỹ năng không còn tiên quyết.",
            }
        return {
            "action": "CONTINUE_CURRENT",
            "target_skill": current_skill_id,
            "probability": current_prob,
            "reason": f"Xác suất {current_prob:.2f}; tiếp tục rèn luyện kỹ năng hiện tại.",
        }
