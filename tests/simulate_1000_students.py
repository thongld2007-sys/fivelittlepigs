"""Reproducible 1,000-student BKT+KG versus linear-test simulation."""

from __future__ import annotations

import argparse
import json
import random
import statistics
import time
from pathlib import Path


SKILLS = ["MATH_G5_LCM", "MATH_G5", "MATH_G7"]
P_LEARN = 0.12
P_SLIP = 0.10
P_GUESS = 0.20


def observe(rng: random.Random, mastered: bool, slip: float, guess: float) -> bool:
    return rng.random() < ((1 - slip) if mastered else guess)


def posterior(prior: float, correct: bool, slip: float, guess: float) -> float:
    if correct:
        evidence = prior * (1 - slip) + (1 - prior) * guess
        updated = prior * (1 - slip) / evidence
    else:
        evidence = prior * slip + (1 - prior) * (1 - guess)
        updated = prior * slip / evidence
    return updated + (1 - updated) * P_LEARN


def simulate_adaptive(rng: random.Random, gap_index: int, slip: float, guess: float) -> tuple[int, int]:
    questions = 0
    for skill_index in range(len(SKILLS)):
        belief = 0.5
        mastered = skill_index < gap_index
        for attempt in range(5):
            started = time.perf_counter_ns()
            correct = observe(rng, mastered, slip, guess)
            belief = posterior(belief, correct, slip, guess)
            _ = time.perf_counter_ns() - started
            questions += 1
            if attempt >= 2 and belief < 0.40:
                return skill_index, questions
            if attempt >= 2 and belief > 0.75:
                break
    return len(SKILLS) - 1, questions


def simulate_linear(rng: random.Random, gap_index: int, slip: float, guess: float) -> tuple[int, int]:
    beliefs = [0.5] * len(SKILLS)
    for skill_index in reversed(range(len(SKILLS))):
        mastered = skill_index < gap_index
        for _ in range(5):
            beliefs[skill_index] = posterior(
                beliefs[skill_index], observe(rng, mastered, slip, guess), slip, guess
            )
    prediction = next((index for index, value in enumerate(beliefs) if value < 0.40), len(SKILLS) - 1)
    return prediction, len(SKILLS) * 5


def run_simulation(students: int = 1000, seed: int = 20260717) -> dict:
    rng = random.Random(seed)
    adaptive_questions, linear_questions = [], []
    adaptive_correct = linear_correct = 0
    started = time.perf_counter()
    for _ in range(students):
        gap_index = rng.randrange(len(SKILLS))
        slip = min(0.22, max(0.04, rng.gauss(P_SLIP, 0.025)))
        guess = min(0.35, max(0.10, rng.gauss(P_GUESS, 0.04)))
        adaptive_prediction, adaptive_n = simulate_adaptive(rng, gap_index, slip, guess)
        linear_prediction, linear_n = simulate_linear(rng, gap_index, slip, guess)
        adaptive_correct += adaptive_prediction == gap_index
        linear_correct += linear_prediction == gap_index
        adaptive_questions.append(adaptive_n)
        linear_questions.append(linear_n)
    elapsed_ms = (time.perf_counter() - started) * 1000
    adaptive_avg = statistics.mean(adaptive_questions)
    linear_avg = statistics.mean(linear_questions)
    return {
        "methodology": {
            "type": "engineering simulation, not a real-school pilot",
            "students": students, "seed": seed, "skills": SKILLS,
            "slip_mean": P_SLIP, "guess_mean": P_GUESS,
        },
        "adaptive_bkt_kg": {
            "root_gap_accuracy": round(adaptive_correct / students, 4),
            "questions_avg": round(adaptive_avg, 2),
            "questions_p95": statistics.quantiles(adaptive_questions, n=20, method="inclusive")[18],
        },
        "linear_test": {
            "root_gap_accuracy": round(linear_correct / students, 4),
            "questions_avg": round(linear_avg, 2),
            "questions_p95": statistics.quantiles(linear_questions, n=20, method="inclusive")[18],
        },
        "comparison": {
            "question_reduction_percent": round((1 - adaptive_avg / linear_avg) * 100, 2),
            "simulation_latency_ms_total": round(elapsed_ms, 2),
            "simulation_latency_ms_per_student": round(elapsed_ms / students, 4),
            "estimated_ai_tokens_per_socratic_turn": 900,
            "token_note": "Estimate only; provider usage is recorded on live agent responses.",
        },
    }


def svg_chart(report: dict) -> str:
    adaptive = report["adaptive_bkt_kg"]["questions_avg"]
    linear = report["linear_test"]["questions_avg"]
    scale = 24
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="760" height="360" viewBox="0 0 760 360">
<rect width="760" height="360" fill="#fffaf0"/><text x="40" y="45" font-family="Arial" font-size="24" font-weight="700">1,000-student diagnostic simulation</text>
<text x="40" y="72" font-family="Arial" font-size="14">Average questions to identify the root knowledge gap (lower is better)</text>
<text x="40" y="145" font-family="Arial" font-size="16">Adaptive BKT + KG</text><rect x="220" y="115" width="{adaptive * scale:.1f}" height="45" rx="8" fill="#557AFA"/><text x="{235 + adaptive * scale:.1f}" y="145" font-family="Arial" font-size="18">{adaptive:.2f}</text>
<text x="40" y="225" font-family="Arial" font-size="16">Traditional linear test</text><rect x="220" y="195" width="{linear * scale:.1f}" height="45" rx="8" fill="#EF5350"/><text x="{235 + linear * scale:.1f}" y="225" font-family="Arial" font-size="18">{linear:.2f}</text>
<text x="40" y="305" font-family="Arial" font-size="18" font-weight="700">Question reduction: {report['comparison']['question_reduction_percent']:.2f}%</text>
<text x="40" y="332" font-family="Arial" font-size="12">Engineering simulation; not evidence from a real-school pilot.</text></svg>'''


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--students", type=int, default=1000)
    parser.add_argument("--output-dir", default="artifacts")
    args = parser.parse_args()
    report = run_simulation(args.students)
    output = Path(args.output_dir)
    output.mkdir(parents=True, exist_ok=True)
    (output / "benchmark_1000.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    (output / "benchmark_1000.svg").write_text(svg_chart(report), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
