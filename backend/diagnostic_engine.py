import math
import random
from backend.database import get_response_history, get_student_mastery, update_student_mastery
from backend.knowledge_graph import KNOWLEDGE_GRAPH, get_prerequisites

CORRECT_COUNT_STABILITY_THRESHOLD = 3
LEVEL_3_STREAK_THRESHOLD = 3
LEVEL_3_STREAK_WEIGHTS = [10, 90]
RECOVERY_KEEP_DIFFICULTY_WEIGHTS = [45, 55]

class BKTProcessor:
    # Bayesian Knowledge Tracing parameter constants
    P_GUESS = 0.20       # Probability of guessing correctly
    P_SLIP = 0.10        # Probability of slipping (making a mistake despite mastering)
    P_TRANSITION = 0.20  # Probability of learning/transitioning to mastery after a practice step
    
    @classmethod
    def calculate_posterior(cls, p_mastery, is_correct):
        """
        Updates the probability of mastery based on the correctness of the answer.
        """
        if is_correct:
            # P(M | Correct)
            num = p_mastery * (1.0 - cls.P_SLIP)
            den = (p_mastery * (1.0 - cls.P_SLIP)) + ((1.0 - p_mastery) * cls.P_GUESS)
        else:
            # P(M | Incorrect)
            num = p_mastery * cls.P_SLIP
            den = (p_mastery * cls.P_SLIP) + ((1.0 - p_mastery) * (1.0 - cls.P_GUESS))
            
        # Avoid mathematical division issues
        if den == 0:
            return p_mastery
            
        p_posterior = num / den
        
        # Apply transition probability (learning adjustment)
        p_new = p_posterior + (1.0 - p_posterior) * cls.P_TRANSITION
        
        # Clamp between 0.01 and 0.99
        return max(0.01, min(0.99, p_new))

def update_student_skill(student_id, skill_id, is_correct, weight=1.0):
    """
    Updates the student's mastery of the skill using BKT.
    """
    current_p = get_student_mastery(student_id, skill_id)
    raw_new_p = BKTProcessor.calculate_posterior(current_p, is_correct)
    bounded_weight = max(0.0, min(1.0, weight))
    new_p = current_p + ((raw_new_p - current_p) * bounded_weight)
    update_student_mastery(student_id, skill_id, new_p)
    return new_p

def get_next_question_difficulty_and_skill(student_id, current_skill_id):
    """
    Core adaptive selection algorithm:
    1. If no response history for this skill:
       - Serve current skill, difficulty randomly level 2 or 3.
    2. If there is history:
       - Check the last response.
       - If Correct:
         - Calculate streak of consecutive correct level 3 answers.
         - If streak >= 3: next question is level 3 with 90% chance, level 2 with 10% chance.
         - Else: 50% level 2, 50% level 3.
         - Stay on current skill.
         - If Incorrect:
         - If failed at level 2 or 3:
           - Count total correct answers for this skill.
           - If correct count < 3: jump down to level 1.
           - If correct count >= 3: either keep current level or decrease by exactly 1 level.
           - Stay on current skill.
         - If failed at level 1:
           - Move to a prerequisite (parent node) in the KNOWLEDGE_GRAPH DAG.
           - Select the prerequisite with the lowest mastery probability.
           - Serve the prerequisite skill, difficulty randomly level 2 or 3.
    """
    rows = get_response_history(student_id, current_skill_id)
    
    if not rows:
        # No history on this skill: start with random difficulty 2 or 3
        return current_skill_id, random.choice([2, 3])
        
    last_response = rows[0]
    last_correct = bool(last_response["is_correct"])
    last_diff = last_response["difficulty_level"]
    
    if last_correct:
        # Calculate level 3 correct streak
        streak_len = 0
        for r in rows:
            if r["is_correct"] == 1 and r["difficulty_level"] == 3:
                streak_len += 1
            else:
                break
        
        if streak_len >= LEVEL_3_STREAK_THRESHOLD:
            # High probability of level 3 (90% level 3, 10% level 2)
            target_diff = random.choices([2, 3], weights=LEVEL_3_STREAK_WEIGHTS)[0]
        else:
            # Standard random 2 or 3
            target_diff = random.choice([2, 3])
            
        return current_skill_id, target_diff
        
    else:
        # Incorrect answer
        if last_diff in [2, 3]:
            # Count total correct responses for this skill
            correct_count = sum(1 for r in rows if r["is_correct"] == 1)
            if correct_count < CORRECT_COUNT_STABILITY_THRESHOLD:
                # Not many correct answers: jump down to level 1
                return current_skill_id, 1
            else:
                # Many correct answers: avoid overreacting to a single slip.
                # Keep the current level sometimes, or decrease by exactly one level.
                lowered_diff = max(1, last_diff - 1)
                target_diff = random.choices(
                    [lowered_diff, last_diff],
                    weights=RECOVERY_KEEP_DIFFICULTY_WEIGHTS
                )[0]
                return current_skill_id, target_diff
        else:
            # Incorrect at level 1: shift to prerequisite
            prereqs = get_prerequisites(current_skill_id)
            if prereqs:
                # Find prerequisite with the lowest mastery probability
                lowest_prereq = prereqs[0]
                lowest_p = 1.0
                for prereq in prereqs:
                    p = get_student_mastery(student_id, prereq)
                    if p < lowest_p:
                        lowest_p = p
                        lowest_prereq = prereq
                # For the new skill, start with random difficulty 2 or 3
                return lowest_prereq, random.choice([2, 3])
            else:
                # No prerequisite, stay at level 1
                return current_skill_id, 1

def get_next_recommended_skill(student_id, current_skill_id):
    """
    Helper wrapper returning only the next recommended skill.
    """
    skill, _ = get_next_question_difficulty_and_skill(student_id, current_skill_id)
    return skill
